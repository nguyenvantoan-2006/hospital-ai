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

# Danh sách models ưu tiên khả dụng (đã được kiểm tra hạn ngạch và hỗ trợ trên API v1beta)
PREFERRED_MODELS = [
    "gemini-flash-lite-latest",
    "gemma-4-26b-a4b-it",
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash-lite-preview",
    "gemini-flash-latest",
    "gemini-pro-latest"
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

async def call_llm_api(prompt: str) -> str:
    """
    Gọi API Google Gemini với cơ chế thử lại đa mô hình (Multi-model Fallback).
    """
    last_error = None
    for model_name in PREFERRED_MODELS:
        try:
            m = genai.GenerativeModel(model_name)
            response = await asyncio.to_thread(m.generate_content, prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            last_error = e
            logger.warning(f"Thử model {model_name} không thành công ({e}), chuyển sang model tiếp theo...")
            continue
    
    logger.error(f"Tất cả các Gemini models đều gặp lỗi: {last_error}")
    raise last_error


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


# ─── AI CHATBOT TƯ VẤN QUY TRÌNH HÀNH CHÍNH (FR-AI-02, UC-09 & SEC-AI-02) ───
class AIChatbotRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class AIChatbotResponse(BaseModel):
    reply: str
    suggested_actions: Optional[List[str]] = None

@router.post("/chatbot", response_model=AIChatbotResponse)
async def ai_chatbot_consult(request: AIChatbotRequest):
    """
    API AI Chatbot tư vấn hành chính y tế cho Bệnh nhân (FR-AI-02 / UC-09).
    - Giải đáp: Giờ khám, bảng giá dịch vụ, thủ tục BHYT, quy trình khám bệnh.
    - Tuân thủ Guardrails nghiêm ngặt: Từ chối chẩn đoán, không kê đơn thuốc.
    - Tự động chuyển đổi đa mô hình (Multi-model Fallback) & Fallback nội bộ an toàn.
    """
    user_msg = (request.message or "").strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Nội dung câu hỏi không được để trống.")

    system_prompt = f"""
Bạn là Trợ lý AI Hành chính của Hệ thống Phòng khám Đa khoa Clinova AI Hospital (Hospital-AI).
Nhiệm vụ: Tư vấn, giải đáp thân thiện, ngắn gọn và chính xác các thông tin hành chính, quy trình và dịch vụ của phòng khám cho bệnh nhân.

THÔNG TIN CHÍNH THỨC CỦA PHÒNG KHÁM CLINOVA:
1. Thời gian làm việc:
   - Thứ Hai đến Thứ Bảy:
     * Buổi sáng: 07:30 - 11:30
     * Buổi chiều: 13:30 - 17:00
   - Chủ Nhật: Nghỉ khám định kỳ (Khoa Cấp cứu tiếp nhận 24/7).
2. Chi phí & Giá dịch vụ:
   - Giá khám chuyên khoa tiêu chuẩn: 100.000 VNĐ / lượt khám.
   - Các gói khám tổng quát, xét nghiệm và chẩn đoán hình ảnh từ 150.000 VNĐ tùy chỉ định.
   - Có hỗ trợ tiếp nhận Bảo hiểm Y tế (BHYT) và bảo lãnh viện phí tư nhân.
3. Quy trình khám bệnh chuẩn 4 bước:
   - Bước 1: Đăng ký đặt lịch trực tuyến (tại website) hoặc lấy số tiếp nhận tại Quầy Lễ tân.
   - Bước 2: Chờ gọi số thứ tự (STT) vào phòng khám bác sĩ chuyên khoa.
   - Bước 3: Bác sĩ thăm khám, chẩn đoán và kê đơn thuốc điện tử.
   - Bước 4: Thanh toán viện phí tại Quầy Kế toán và nhận thuốc tại Quầy Dược (hỗ trợ tiền mặt, chuyển khoản VietQR, quẹt thẻ).
4. Địa chỉ & Liên hệ:
   - Địa chỉ: 123 Đường Sức Khỏe, Quận 1, TP. Hồ Chí Minh.
   - Hotline hỗ trợ & Cấp cứu: 1900 6868.
   - Website: Đặt lịch trực tuyến 24/7 qua cổng "Đặt lịch khám".

RÀNG BUỘC Y ĐỨC & BẢO MẬT (SEC-AI-02 - TUYỆT ĐỐI TUÂN THỦ 3 QUY TẮC):
1. TUYỆT ĐỐI KHÔNG TỰ CHẨN ĐOÁN BỆNH: Nếu người dùng mô tả các triệu chứng bệnh hoặc hỏi bệnh gì, hãy đồng cảm nhưng TỪ CHỐI chẩn đoán, đồng thời khuyên họ bấm "Đặt lịch khám" để gặp bác sĩ chuyên khoa hoặc gọi cấp cứu 115 nếu có triệu chứng nguy kịch (khó thở, đau thắt ngực...).
2. TUYỆT ĐỐI KHÔNG KÊ ĐƠN THUỐC: Không gợi ý hoặc đề xuất tên bất kỳ loại thuốc điều trị nào.
3. PHONG CÁCH TRẢ LỜI: Tiếng Việt văn minh, ấm áp, rõ ràng, gạch đầu dòng súc tích (dưới 150 từ).

CÂU HỎI CỦA BỆNH NHÂN:
{user_msg}
"""
    suggested = ["Giờ làm việc", "Bảng giá khám", "Quy trình khám", "Đặt lịch ngay"]
    
    try:
        reply_text = await call_llm_api(system_prompt)
    except Exception as e:
        logger.error(f"[AI Chatbot Fallback] {str(e)}")
        # Cơ chế Fallback thông minh dựa trên từ khóa nếu mất kết nối LLM
        lower_msg = user_msg.lower()
        if "giờ" in lower_msg or "mấy giờ" in lower_msg or "thời gian" in lower_msg or "lịch làm" in lower_msg:
            reply_text = (
                "🕒 **Thời gian làm việc của Clinova:**\n"
                "- Thứ 2 - Thứ 7: Sáng 07:30 - 11:30 | Chiều 13:30 - 17:00.\n"
                "- Chủ Nhật: Nghỉ định kỳ (Cấp cứu trực 24/7).\n"
                "Bạn có thể đặt lịch trước trên website để chọn khung giờ phù hợp nhé!"
            )
        elif "giá" in lower_msg or "chi phí" in lower_msg or "bao nhiêu" in lower_msg or "tiền" in lower_msg:
            reply_text = (
                "💰 **Bảng giá khám tại Clinova:**\n"
                "- Khám chuyên khoa tiêu chuẩn: 100.000 VNĐ / lượt.\n"
                "- Phòng khám có áp dụng Bảo hiểm Y tế (BHYT) theo quy định hiện hành."
            )
        elif "quy trình" in lower_msg or "các bước" in lower_msg or "thủ tục" in lower_msg:
            reply_text = (
                "📝 **Quy trình khám bệnh 4 bước tại Clinova:**\n"
                "1. Đặt lịch khám online hoặc lấy số tại Lễ tân.\n"
                "2. Nhận số thứ tự (STT) và vào phòng khám bác sĩ.\n"
                "3. Bác sĩ thăm khám và kê đơn thuốc điện tử.\n"
                "4. Thanh toán viện phí và nhận thuốc tại quầy dược."
            )
        elif any(k in lower_msg for k in ["đau", "bệnh", "thuốc", "sốt", "uống gì", "bị làm sao"]):
            reply_text = (
                "⚠️ **Lưu ý Y tế:** Trợ lý AI không được phép đưa ra chẩn đoán y khoa hoặc kê đơn thuốc. "
                "Để đảm bảo an toàn sức khỏe, bạn vui lòng nhấn nút **Đặt lịch khám** để được các bác sĩ chuyên khoa thăm khám trực tiếp, hoặc liên hệ Hotline 1900 6868 nếu cần hỗ trợ khẩn cấp."
            )
        else:
            reply_text = (
                "Chào bạn, tôi là Trợ lý AI của Clinova. Tôi có thể hỗ trợ bạn tìm hiểu giờ làm việc, giá dịch vụ khám, quy trình khám và hướng dẫn đặt lịch khám. Bạn cần thông tin gì ạ?"
            )

    return AIChatbotResponse(reply=reply_text, suggested_actions=suggested)

