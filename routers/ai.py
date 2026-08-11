from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
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

model = genai.GenerativeModel("gemini-1.5-flash")

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
    Gọi API Google Gemini với mô hình gemini-1.5-flash để sinh tóm tắt hồ sơ bệnh nhân.
    """
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text
    except Exception as e:
        logger.error(f"Lỗi khi gọi Gemini API: {e}")
        raise e


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
        # Fallback: Lỗi kết nối API hoặc timeout
        logger.error(f"[AI Summary Error] Bệnh nhân {request.benh_nhan_id} - {str(e)}")
        summary_result = "Dịch vụ AI hiện không khả dụng. Vui lòng xem hồ sơ thủ công."

    return AISummaryResponse(summary=summary_result)
