from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import logging
import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    raise ValueError("GEMINI_API_KEY is missing in environment variables.")

import time
import re

# Danh sách models ưu tiên khả dụng (hỗ trợ cả Multimodal Vision & Text)
PREFERRED_MODELS = [
    "gemini-1.5-flash",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-1.5-pro",
    "gemini-pro-latest",
    "gemini-3.1-flash-lite",
    "gemma-4-26b-a4b-it"
]

from database import get_db
import models

# Cấu hình logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Thêm handler để in ra console nếu cần
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

router = APIRouter()

# ─── SCHEMAS ─────────────────────────────────────────────────────────────
class AISummaryRequest(BaseModel):
    benh_nhan_id: int

class AISummaryResponse(BaseModel):
    summary: str

# ─── UTILS & DATA MASKING ────────────────────────────────────────────────
def mask_patient_data(benh_nhan: models.BenhNhan) -> dict:
    """
    Data Masking: Ẩn thông tin định danh (Tên, CCCD/BHYT, Địa chỉ, SĐT...)
    trước khi đưa vào Prompt gửi cho LLM.
    """
    # 1. Ẩn Họ tên: Chỉ giữ lại chữ cái đầu hoặc thay bằng ***
    ho_ten_masked = "***"
    if benh_nhan.ho_ten:
        parts = benh_nhan.ho_ten.strip().split()
        if len(parts) > 1:
            # Ví dụ: Nguyễn Văn A -> N*** A
            ho_ten_masked = f"{parts[0][0]}*** {parts[-1]}"
        else:
            ho_ten_masked = "[HIDDEN]"

    # 2. Ẩn BHYT / CCCD: Chỉ hiện 3 số cuối
    ma_bhyt_masked = "[HIDDEN]"
    if benh_nhan.ma_bhyt and len(benh_nhan.ma_bhyt) > 3:
        ma_bhyt_masked = f"***{benh_nhan.ma_bhyt[-3:]}"

    return {
        "ho_ten": ho_ten_masked,
        "ngay_sinh": str(benh_nhan.ngay_sinh) if benh_nhan.ngay_sinh else "[HIDDEN]",
        "ma_bhyt": ma_bhyt_masked,
        "tien_su_benh": benh_nhan.tien_su_benh or "Không có ghi nhận"
    }

async def call_llm_multimodal_api(
    prompt: str,
    image_base64: Optional[str] = None,
    mime_type: Optional[str] = None
) -> tuple[str, str]:
    """
    Gọi Gemini API hỗ trợ Multimodal (Văn bản + Hình ảnh / Tài liệu PDF)
    với cơ chế thử lại đa mô hình (Multi-model Fallback).
    Trả về (response_text, model_name_used).
    """
    contents = [prompt]
    if image_base64:
        clean_b64 = image_base64.strip()
        detected_mime = mime_type or "image/jpeg"
        if "," in clean_b64:
            header, clean_b64 = clean_b64.split(",", 1)
            if "data:" in header and ";base64" in header:
                detected_mime = header.replace("data:", "").replace(";base64", "").strip()

        contents.append({
            "mime_type": detected_mime,
            "data": clean_b64
        })

    last_error = None
    for model_name in PREFERRED_MODELS:
        try:
            m = genai.GenerativeModel(model_name)
            response = await asyncio.to_thread(m.generate_content, contents)
            if response and response.text:
                return response.text.strip(), model_name
        except Exception as e:
            last_error = e
            logger.warning(f"Thử model {model_name} không thành công ({e}), chuyển sang model tiếp theo...")
            continue

    logger.error(f"Tất cả các Gemini models đều gặp lỗi: {last_error}")
    raise last_error

async def call_llm_api(prompt: str) -> str:
    """
    Gọi API Google Gemini dạng text thuần túy (Backward Compatibility).
    """
    text, _ = await call_llm_multimodal_api(prompt)
    return text


# ─── API ENDPOINT ────────────────────────────────────────────────────────
@router.post("/summary", response_model=AISummaryResponse)
async def generate_ai_summary(request: AISummaryRequest, db: Session = Depends(get_db)):
    """
    API Tóm tắt hồ sơ bệnh án bằng AI.
    - Nhận ID bệnh nhân
    - Trích xuất dữ liệu, mask thông tin cá nhân
    - Gắn prompt nghiêm ngặt (Guardrails)
    - Xử lý ngoại lệ an toàn
    """
    logger.info(f"[AI Summary] Yêu cầu tóm tắt cho Bệnh nhân ID: {request.benh_nhan_id}")
    
    # 1. Trích xuất thông tin bệnh nhân từ DB
    benh_nhan = db.query(models.BenhNhan).filter(models.BenhNhan.id == request.benh_nhan_id).first()
    if not benh_nhan:
        logger.warning(f"[AI Summary] Không tìm thấy bệnh nhân ID {request.benh_nhan_id}")
        raise HTTPException(status_code=404, detail="Không tìm thấy bệnh nhân.")

    # 2. Lấy lịch sử khám và phiếu khám (nếu có)
    lich_khams = db.query(models.LichKham).filter(models.LichKham.benh_nhan_id == request.benh_nhan_id).all()
    
    history_lines = []
    for lk in lich_khams:
        line = f"- Ngày khám: {lk.thoi_gian.strftime('%d/%m/%Y') if lk.thoi_gian else 'N/A'} | Lý do: {lk.ly_do_kham}"
        if lk.phieu_kham:
            line += f" | Triệu chứng ghi nhận: {lk.phieu_kham.trieu_chung} | Chẩn đoán trước đó: {lk.phieu_kham.chan_doan}"
        history_lines.append(line)
        
    history_info = "\n".join(history_lines) if history_lines else "Chưa có lịch sử khám bệnh trước đây."

    # 3. Data Masking (Che thông tin định danh)
    masked_data = mask_patient_data(benh_nhan)
    
    # 4. Prompt System (Ràng buộc Y đức - Guardrails)
    system_prompt = f"""
Bạn là Trợ lý AI Hành chính Y tế chuyên nghiệp. Nhiệm vụ của bạn là TÓM TẮT hồ sơ và lịch sử khám của bệnh nhân.

RÀNG BUỘC Y ĐỨC (TUYỆT ĐỐI TUÂN THỦ 4 QUY TẮC SAU):
1. CHỈ tóm tắt thông tin hành chính, tiền sử bệnh và các triệu chứng/chẩn đoán CŨ từ lịch sử.
2. TUYỆT ĐỐI KHÔNG tự đưa ra chẩn đoán bệnh mới.
3. TUYỆT ĐỐI KHÔNG kê đơn thuốc, không đề xuất thuốc.
4. TUYỆT ĐỐI KHÔNG đưa ra phác đồ điều trị hay bất kỳ lời khuyên y tế nào.

THÔNG TIN BỆNH NHÂN (Đã ẩn danh):
- Họ tên: {masked_data['ho_ten']}
- Ngày sinh: {masked_data['ngay_sinh']}
- BHYT: {masked_data['ma_bhyt']}
- Tiền sử bệnh: {masked_data['tien_su_benh']}

LỊCH SỬ KHÁM BỆNH:
{history_info}

Hãy viết một đoạn tóm tắt hành chính ngắn gọn, súc tích (dưới 150 từ):
"""
    
    # 5. Gọi AI & Fallback Mechanism (Xử lý ngoại lệ)
    try:
        logger.info(f"[AI Summary] Gửi Prompt tới LLM cho Bệnh nhân ID: {request.benh_nhan_id}...")
        summary_result = await call_llm_api(system_prompt)
        logger.info(f"[AI Summary] Hoàn tất tóm tắt cho Bệnh nhân ID: {request.benh_nhan_id}")
        
    except Exception as e:
        # Fallback an toàn: Tránh hiển thị mã lỗi thô cho người dùng, tự động tóm tắt từ dữ liệu DB
        logger.error(f"[AI Summary Fallback] Bệnh nhân {request.benh_nhan_id} - {str(e)}")
        summary_result = (
            f"📋 TÓM TẮT HÀNH CHÍNH & TIỀN SỬ (Tự động từ CSDL):\n"
            f"• Bệnh nhân: {benh_nhan.ho_ten} (Mã BN: #{benh_nhan.id})\n"
            f"• Tiền sử bệnh ghi nhận: {benh_nhan.tien_su_benh or 'Chưa ghi nhận tiền sử dị ứng / mạn tính'}\n"
            f"• Lịch sử các lần khám gần nhất:\n{history_info}\n"
            f"*(Hệ thống AI đang tạm bận/đạt giới hạn kết nối; bản tóm tắt được trích xuất an toàn từ hồ sơ bệnh án)*"
        )

    return AISummaryResponse(summary=summary_result)


# ─── AI POST-EXAM CARE GUIDE (UC-10 & SEC-AI-02) ───────────────────────────
class AIGuideRequest(BaseModel):
    chan_doan: str
    trieu_chung: str = ""

class AIGuideResponse(BaseModel):
    guide: str

@router.post("/post-exam-guide", response_model=AIGuideResponse)
async def generate_post_exam_guide(request: AIGuideRequest):
    """
    API Sinh hướng dẫn chăm sóc sau khám bằng AI.
    - Nhận chẩn đoán và triệu chứng từ bác sĩ.
    - Sinh bản nháp hướng dẫn chăm sóc (Draft) tuân thủ Guardrails (SEC-AI-02).
    """
    if not request.chan_doan or not request.chan_doan.strip():
        raise HTTPException(status_code=400, detail="Vui lòng nhập chẩn đoán trước khi sinh hướng dẫn sau khám.")

    prompt = f"""
Bạn là Trợ lý Y tế hỗ trợ Bác sĩ soạn thảo bản nháp "Hướng dẫn chăm sóc & dặn dò sau khám" cho bệnh nhân.

RÀNG BUỘC GUARDRAILS (SEC-AI-02):
1. Đây là BẢN NHÁP (Draft) để Bác sĩ xem xét, chỉnh sửa và phê duyệt trước khi in cho bệnh nhân.
2. TUYỆT ĐỐI KHÔNG tự chẩn đoán bệnh mới. Dựa hoàn toàn vào chẩn đoán của bác sĩ bên dưới.
3. Đưa ra các lời khuyên sinh hoạt, dinh dưỡng, chế độ nghỉ ngơi, dấu hiệu cần tái khám ngay.

THÔNG TIN BÁC SĨ ĐÃ CHẨN ĐOÁN:
- Triệu chứng: {request.trieu_chung or 'Đã được ghi nhận'}
- Chẩn đoán xác định: {request.chan_doan}

Hãy viết bản nháp Hướng dẫn sau khám ngắn gọn, rõ ràng, dễ hiểu (khoảng 150-200 từ) gồm:
1. Chế độ ăn uống & Nghỉ ngơi
2. Lưu ý khi dùng thuốc & Sinh hoạt
3. Các dấu hiệu bất thường cần tái khám ngay.
"""
    try:
        guide_result = await call_llm_api(prompt)
    except Exception as e:
        logger.error(f"[AI Guide Error] {str(e)}")
        guide_result = (
            f"BẢN NHÁP HƯỚNG DẪN SAU KHÁM (Mẫu mặc định):\n"
            f"- Chẩn đoán: {request.chan_doan}\n"
            f"- Chế độ nghỉ ngơi: Ăn uống đủ chất, uống nhiều nước, nghỉ ngơi hợp lý.\n"
            f"- Dùng thuốc: Tuân thủ đơn thuốc do bác sĩ kê.\n"
            f"- Tái khám: Tái khám khi hết thuốc hoặc có dấu hiệu bất thường."
        )

    return AIGuideResponse(guide=guide_result)


# ─── AI CHATBOT TƯ VẤN QUY TRÌNH HÀNH CHÍNH & ĐỊNH HƯỚNG KHÁM (FR-AI-02, UC-09 & SEC-AI-02) ───
class AIChatbotRequest(BaseModel):
    message: Optional[str] = ""
    image_base64: Optional[str] = None
    image_mime_type: Optional[str] = "image/jpeg"
    file_name: Optional[str] = None
    session_id: Optional[str] = None

class AIChatbotResponse(BaseModel):
    reply: str
    suggested_actions: Optional[List[str]] = None
    specialties_recommended: Optional[List[str]] = None
    preparation_guidelines: Optional[List[str]] = None

def retrieve_rag_context(user_msg: str, db: Session) -> dict:
    """
    Truy vấn Cơ sở dữ liệu nội bộ của Clinova Hospital (Ground Truth)
    để nạp vào Prompt cho Gemini (RAG):
    - Danh mục Chuyên khoa phù hợp & bảng giá
    - Bác sĩ phụ trách & lịch trực
    - Quy định hướng dẫn chuẩn bị trước khám (nhịn ăn, giấy tờ, lưu ý)
    """
    query_lower = (user_msg or "").lower()

    # 1. Tìm hướng dẫn chuẩn bị khám từ bảng huong_dan_chuan_bi_kham
    matched_guides = []
    try:
        all_guides = db.query(models.HuongDanChuanBiKham).filter(models.HuongDanChuanBiKham.trang_thai == True).all()
        for g in all_guides:
            keywords = [k.strip() for k in (g.tu_khoa_nhan_dien or "").lower().split(",") if k.strip()]
            keywords.append(g.ten_dich_vu.lower())
            if any(kw in query_lower for kw in keywords):
                matched_guides.append(g)
    except Exception as e:
        logger.warning(f"Lỗi truy vấn HuongDanChuanBiKham: {e}")

    # 2. Tìm chuyên khoa phù hợp từ bảng chuyen_khoa
    matched_specs = []
    all_specs = []
    try:
        all_specs = db.query(models.ChuyenKhoa).filter(models.ChuyenKhoa.trang_thai == True).all()
        for s in all_specs:
            s_name_lower = s.ten_chuyen_khoa.lower()
            words = [w for w in s_name_lower.replace("-", " ").replace("(", " ").replace(")", " ").split() if len(w) > 2]
            if s_name_lower in query_lower or any(w in query_lower for w in words):
                matched_specs.append(s)
    except Exception as e:
        logger.warning(f"Lỗi truy vấn ChuyenKhoa: {e}")

    # Nếu guide có FK chuyen_khoa thì thêm vào matched_specs
    for g in matched_guides:
        if g.chuyen_khoa and g.chuyen_khoa not in matched_specs:
            matched_specs.append(g.chuyen_khoa)

    # 3. Lấy thông tin Bác sĩ thực tế từ bảng bac_si
    doctors_info = []
    try:
        if matched_specs:
            spec_names = [s.ten_chuyen_khoa for s in matched_specs[:3]]
            doctors = db.query(models.BacSi).filter(
                models.BacSi.chuyen_khoa.in_(spec_names),
                models.BacSi.trang_thai == True
            ).limit(6).all()
        else:
            doctors = db.query(models.BacSi).filter(models.BacSi.trang_thai == True).limit(3).all()

        for d in doctors:
            doctors_info.append(f"- {d.hoc_vi or 'BS.'} {d.ho_ten} (Chuyên khoa: {d.chuyen_khoa} | {d.phong_kham or 'Phòng khám đa khoa'} | Lịch trực: {d.lich_truc or 'Sáng 07:30 - 11:30 | Chiều 13:30 - 17:00'})")
    except Exception as e:
        logger.warning(f"Lỗi truy vấn BacSi: {e}")

    # 4. Tạo khối Factual Context (Ground Truth)
    lines = []
    lines.append("=== DỮ LIỆU THỰC TẾ TRÍCH XUẤT TỪ CƠ SỞ DỮ LIỆU PHÒNG KHÁM CLINOVA (GROUND TRUTH) ===")

    if matched_specs:
        lines.append("1. CÁC CHUYÊN KHOA PHÙ HỢP TẠI CLINOVA:")
        for s in matched_specs[:4]:
            fee_str = f"{int(s.gia_kham_tieu_chuan):,} VNĐ" if s.gia_kham_tieu_chuan else "150.000 VNĐ"
            lines.append(f"   • {s.ten_chuyen_khoa}: Giá khám tiêu chuẩn {fee_str}. Mô tả: {s.mo_ta or 'Khám và tư vấn chuyên sâu'}")
    else:
        lines.append("1. DANH MỤC MỘT SỐ CHUYÊN KHOA TIÊU BIỂU:")
        for s in all_specs[:5]:
            fee_str = f"{int(s.gia_kham_tieu_chuan):,} VNĐ" if s.gia_kham_tieu_chuan else "150.000 VNĐ"
            lines.append(f"   • {s.ten_chuyen_khoa}: Giá khám tiêu chuẩn {fee_str}")

    if doctors_info:
        lines.append("2. BÁC SĨ PHỤ TRÁCH TIÊU BIỂU:")
        lines.extend([f"   {d}" for d in doctors_info])

    if matched_guides:
        lines.append("3. QUY ĐỊNH HƯỚNG DẪN CHUẨN BỊ TRƯỚC KHI KHÁM (BẮT BUỘC TUÂN THỦ TỪ DB):")
        for g in matched_guides:
            lines.append(f"   📌 Dịch vụ: {g.ten_dich_vu}")
            if g.huong_dan_nhin_an:
                lines.append(f"      - Nhịn ăn / uống: {g.huong_dan_nhin_an}")
            if g.giay_to_can_mang:
                lines.append(f"      - Giấy tờ cần mang: {g.giay_to_can_mang}")
            if g.luu_y_quan_trong:
                lines.append(f"      - Lưu ý quan trọng: {g.luu_y_quan_trong}")
    else:
        lines.append("3. QUY ĐỊNH CHUẨN BỊ CHUNG KHI ĐẾN KHÁM:")
        lines.append("   - Giấy tờ cần mang: Căn cước công dân (CCCD) hoặc hộ chiếu gốc, thẻ BHYT (nếu có), sổ khám hoặc đơn thuốc cũ trong 6 tháng gần nhất.")
        lines.append("   - Nhịn ăn uống: Nếu cần làm xét nghiệm máu, nội soi dạ dày hoặc đại tràng, người bệnh cần nhịn ăn ít nhất 8 tiếng trước khi khám (chỉ uống nước lọc).")

    lines.append("4. THÔNG TIN HÀNH CHÍNH & TIẾP NHẬN:")
    lines.append("   - Giờ làm việc: Thứ Hai - Thứ Bảy (Sáng 07:30 - 11:30 | Chiều 13:30 - 17:00). Chủ Nhật: Cấp cứu tiếp nhận 24/7.")
    lines.append("   - Địa chỉ: 123 Đường Sức Khỏe, Quận 1, TP. Hồ Chí Minh. Hotline hỗ trợ & cấp cứu: 1900 6868.")
    lines.append("   - Áp dụng Bảo hiểm Y tế (BHYT) theo quy định hiện hành của Bộ Y tế.")
    lines.append("=============================================================================")

    return {
        "context_text": "\n".join(lines),
        "matched_specs": [s.ten_chuyen_khoa for s in matched_specs],
        "matched_guides": [g.ten_dich_vu for g in matched_guides],
        "first_guide": matched_guides[0] if matched_guides else None,
        "first_spec": matched_specs[0] if matched_specs else None
    }


@router.post("/chatbot", response_model=AIChatbotResponse)
async def ai_chatbot_consult(request: AIChatbotRequest, db: Session = Depends(get_db)):
    """
    API AI Chatbot Đa phương thức (Multimodal) & RAG CSDL Nội bộ (FR-AI-02, UC-09 & SEC-AI-02).
    - Hỗ trợ câu hỏi văn bản (từ gõ tay hoặc Voice-to-Text kiểm duyệt).
    - Hỗ trợ tải lên hình ảnh / tài liệu (kết quả xét nghiệm cũ, đơn thuốc, thẻ BHYT, vùng da...).
    - Truy vấn RAG vào CSDL (chuyen_khoa, bac_si, huong_dan_chuan_bi_kham).
    - Ép Guardrails nghiêm ngặt: Tuyệt đối không chẩn đoán, không kê đơn thuốc.
    - Tự động nhận diện đa ngôn ngữ của người dùng (Tiếng Việt, Tiếng Anh...).
    - Luôn đính kèm câu khuyến cáo miễn trừ trách nhiệm y tế (Disclaimer).
    """
    start_time = time.time()
    user_msg = (request.message or "").strip()
    has_image = bool(request.image_base64)

    if not user_msg and not has_image:
        raise HTTPException(status_code=400, detail="Vui lòng nhập câu hỏi hoặc đính kèm tài liệu/hình ảnh.")

    # 1. RAG Retrieval từ Database
    rag_data = retrieve_rag_context(user_msg, db)

    # 2. Xây dựng System Prompt với Guardrails y đức và Data Grounding
    system_prompt = f"""
Bạn là Trợ lý AI Định hướng Khám bệnh của Hệ thống Phòng khám Đa khoa CLINOVA (Hospital-AI).
Nhiệm vụ cốt lõi: Hướng dẫn người bệnh chuẩn bị chu đáo trước khi đến khám (gợi ý đúng chuyên khoa, bác sĩ phụ trách, bảng giá, giấy tờ cần mang, và dặn dò nhịn ăn/nước uống).

NGUYÊN TẮC 'LẤY DỮ LIỆU THẬT TỪ DATABASE - TUYỆT ĐỐI KHÔNG XUYÊN TẠC' (GROUND TRUTH):
Dưới đây là thông tin thực tế duy nhất được cấp phép từ Cơ sở dữ liệu phòng khám:
{rag_data['context_text']}

RÀNG BUỘC Y ĐỨC & GUARDRAILS (SEC-AI-02 - BẮT BUỘC TUÂN THỦ 5 NGUYÊN TẮC):
1. VAI TRÒ DUY NHẤT LÀ HƯỚNG DẪN CHUẨN BỊ:
   - Gợi ý đúng chuyên khoa nên đăng ký khám và bác sĩ phụ trách từ dữ liệu CSDL ở trên.
   - Nêu rõ bảng giá khám niêm yết của chuyên khoa.
   - Dặn dò đầy đủ giấy tờ cần mang theo (CCCD, BHYT, đơn thuốc/hồ sơ xét nghiệm cũ).
   - Dặn dò lưu ý chuẩn bị (có cần nhịn ăn không, uống nước như thế nào) dựa ĐÚNG vào mục 'QUY ĐỊNH HƯỚNG DẪN CHUẨN BỊ' được cấp ở trên.
2. TUYỆT ĐỐI KHÔNG TỰ CHẨN ĐOÁN BỆNH:
   - Dù người bệnh có mô tả triệu chứng gì hoặc tải lên hình ảnh (kết quả xét nghiệm, đơn thuốc, ảnh vùng da...), bạn KHÔNG ĐƯỢC kết luận người đó mắc bệnh gì.
   - Nếu có hình ảnh kết quả xét nghiệm cũ hay đơn thuốc cũ: Bạn có thể trích xuất các thông số khách quan (ví dụ: 'Trên phiếu ghi nhận chỉ số Glucose là...', 'Đơn thuốc cũ gồm...') nhưng KHÔNG kết luận bệnh hay kê đơn mới, mà định hướng người bệnh đến đúng chuyên khoa để bác sĩ thăm khám.
3. TUYỆT ĐỐI KHÔNG KÊ ĐƠN THUỐC:
   - Không gợi ý, không nhắc tên thuốc điều trị mới cho người bệnh uống.
4. NẾU THÔNG TIN KHÔNG CÓ TRONG CƠ SỞ DỮ LIỆU ĐƯỢC CẤP:
   - Phải thông báo rõ ràng cho người bệnh: 'Hiện tại hệ thống cơ sở dữ liệu của phòng khám chưa có thông tin về nội dung này, bạn vui lòng liên hệ Tổng đài 1900 6868 hoặc trực tiếp tại Quầy Lễ tân để được nhân viên y tế hỗ trợ.'
5. TỰ ĐỘNG NHẬN DIỆN VÀ PHẢN HỒI BẰNG ĐÚNG NGÔN NGỮ CỦA NGƯỜI DÙNG:
   - Nếu người dùng dùng Tiếng Việt -> Trả lời bằng Tiếng Việt văn minh, ấm áp, rõ ràng.
   - Nếu người dùng dùng Tiếng Anh (English) -> Trả lời bằng Tiếng Anh chuẩn mực.
   - Luôn định dạng danh sách gạch đầu dòng rõ ràng, súc tích (dưới 200 từ).

CÂU HỎI HOẶC YÊU CẦU CỦA BỆNH NHÂN:
{user_msg if user_msg else '[Người dùng đã đính kèm hình ảnh / tài liệu đính kèm bên dưới, hãy trích xuất ngữ cảnh khách quan và định hướng chuẩn bị đi khám]'}
"""

    used_model = "unknown"
    log_status = "success"
    disclaimer_str = "Lưu ý: Mọi thông tin chỉ mang tính chất hướng dẫn chuẩn bị trước khi đến cơ sở y tế, không thay thế cho chẩn đoán chuyên môn của bác sĩ."

    try:
        # 3. Gọi Gemini Multimodal API (Hỗ trợ cả Text + Image/File)
        reply_text, used_model = await call_llm_multimodal_api(
            prompt=system_prompt,
            image_base64=request.image_base64,
            mime_type=request.image_mime_type
        )
    except Exception as e:
        logger.error(f"[AI Chatbot Fallback] Lỗi gọi Gemini: {str(e)}")
        log_status = "fallback"
        used_model = "internal-db-fallback"

        # 4. Cơ chế Fallback an toàn lấy trực tiếp từ Database nội bộ
        if rag_data.get("first_guide"):
            g = rag_data["first_guide"]
            s_name = rag_data["first_spec"].ten_chuyen_khoa if rag_data.get("first_spec") else "Chuyên khoa tương ứng"
            reply_text = (
                f"📋 **Hướng dẫn chuẩn bị khám: {g.ten_dich_vu}**\n\n"
                f"• **Chuyên khoa đề xuất:** {s_name}\n"
                f"• **Lưu ý nhịn ăn / uống:** {g.huong_dan_nhin_an or 'Ăn uống nhẹ nhàng.'}\n"
                f"• **Giấy tờ cần mang:** {g.giay_to_can_mang or 'CCCD, thẻ BHYT, đơn thuốc cũ.'}\n"
                f"• **Lưu ý quan trọng:** {g.luu_y_quan_trong or 'Đến đúng giờ hẹn đã đăng ký.'}\n"
                f"• **Giờ làm việc:** Sáng 07:30 - 11:30 | Chiều 13:30 - 17:00 (Thứ 2 - Thứ 7).\n"
                f"Bạn có thể nhấn **Đặt lịch khám ngay** trên website để được xếp số thứ tự ưu tiên nhé!"
            )
        elif any(k in user_msg.lower() for k in ["giờ", "thời gian", "mấy giờ"]):
            reply_text = (
                "🕒 **Thời gian làm việc của Clinova:**\n"
                "- Thứ 2 - Thứ 7: Sáng 07:30 - 11:30 | Chiều 13:30 - 17:00.\n"
                "- Chủ Nhật: Nghỉ định kỳ (Cấp cứu trực 24/7).\n"
                "Bạn có thể đặt lịch trước trên website để chọn khung giờ phù hợp nhé!"
            )
        elif any(k in user_msg.lower() for k in ["giá", "chi phí", "bao nhiêu", "tiền"]):
            reply_text = (
                "💰 **Bảng giá khám tại Clinova:**\n"
                "- Khám chuyên khoa tiêu chuẩn: 150.000 VNĐ - 250.000 VNĐ tùy chuyên khoa.\n"
                "- Phòng khám có áp dụng Bảo hiểm Y tế (BHYT) theo quy định hiện hành."
            )
        else:
            reply_text = (
                "Chào bạn, tôi là Trợ lý AI Hướng dẫn chuẩn bị khám của Clinova Hospital. "
                "Để chuẩn bị tốt nhất trước khi đến viện, bạn vui lòng mang theo Căn cước công dân (CCCD), thẻ BHYT và các đơn thuốc hoặc kết quả khám cũ. "
                "Nếu bạn có dự định làm xét nghiệm máu hoặc nội soi dạ dày, hãy nhịn ăn ít nhất 8 tiếng trước khi đến khám nhé!"
            )

    # 5. Đính kèm Disclaimer y tế bắt buộc
    if "không thay thế cho chẩn đoán" not in reply_text.lower():
        reply_text += f"\n\n---\n⚠️ **Khuyến cáo y tế:** *{disclaimer_str}*"

    # 6. Ghi nhật ký kiểm toán AILog (SEC-AI-04)
    elapsed_ms = int((time.time() - start_time) * 1000)
    try:
        log_entry = models.AILog(
            user_id=None,
            chuc_nang="ai_chatbot",
            prompt_masked=user_msg[:500] if user_msg else "[Multimodal Attachment]",
            response_text=reply_text[:1000],
            model_name=used_model,
            response_time_ms=elapsed_ms,
            trang_thai=log_status,
            thoi_gian=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
    except Exception as log_err:
        logger.warning(f"Không thể ghi nhật ký AILog: {log_err}")

    suggested = ["Đặt lịch khám ngay", "Hướng dẫn nhịn ăn", "Giờ làm việc & Địa chỉ", "Giấy tờ cần mang"]
    if rag_data.get("matched_specs"):
        suggested.insert(0, f"Khám {rag_data['matched_specs'][0]}")

    return AIChatbotResponse(
        reply=reply_text,
        suggested_actions=suggested[:4],
        specialties_recommended=rag_data.get("matched_specs"),
        preparation_guidelines=rag_data.get("matched_guides")
    )


