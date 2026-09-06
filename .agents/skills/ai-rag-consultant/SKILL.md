---
name: ai-rag-consultant
description: Skill tích hợp AI cho Hệ thống Quản lý Phòng Khám — bao gồm AI Summary (tóm tắt hồ sơ), AI Chatbot (hỏi đáp quy trình), AI Post-exam Guide (hướng dẫn sau khám). Tuân thủ Data Masking, Guardrails y đức và Human-in-the-Loop.
---

# AI Consultant Skill — Hospital AI System

## Objective
Triển khai phân hệ trợ lý AI hành chính tuân thủ đầy đủ y đức và bảo mật dữ liệu y tế.

## AI Guardrails (Bất biến — không được vi phạm)
```
AI TUYỆT ĐỐI KHÔNG:
  ❌ Chẩn đoán bệnh
  ❌ Đề xuất phác đồ điều trị
  ❌ Kê đơn thuốc
  ❌ Thay thế quyết định chuyên môn của bác sĩ
  ❌ Nhận/lưu thông tin PII (họ tên, SĐT, CCCD)

AI CHỈ ĐƯỢC:
  ✅ Tóm tắt hồ sơ hành chính (đã masked)
  ✅ Trả lời câu hỏi về quy trình, thủ tục, giá dịch vụ
  ✅ Sinh hướng dẫn sau khám từ ghi chú bác sĩ (cần phê duyệt)
```

## FR-AI-01: AI Summary (Tóm tắt hồ sơ bệnh án)

### Luồng xử lý bắt buộc
```
CSDL hồ sơ bệnh nhân
    → data_masking() ← BẮT BUỘC (SEC-AI-01)
    → Gọi LLM API (Gemini)
    → Kết quả dạng bản nháp (Markdown)
    → Hiển thị cho bác sĩ (chỉ tham khảo)
    → AI Log ghi nhận (SEC-AI-04)
```

### System Prompt (bất biến)
```
Bạn là một trợ lý y tế hành chính thông minh. Nhiệm vụ của bạn là tóm tắt
ngắn gọn lịch sử khám bệnh, các triệu chứng cũ và đơn thuốc của bệnh nhân
để bác sĩ xem nhanh.

TUYỆT ĐỐI KHÔNG đưa ra chẩn đoán y khoa.
KHÔNG đề xuất phác đồ điều trị hay thay đổi đơn thuốc.
Giữ giọng văn trung lập, khách quan và chuyên nghiệp.
```

### User Prompt Template
```
Dựa trên dữ liệu sau, hãy tóm tắt hồ sơ khám bệnh thành 3 phần rõ ràng:
(1) Tiền sử bệnh
(2) Triệu chứng các lần khám trước
(3) Thuốc đã sử dụng

DỮ LIỆU (đã ẩn danh):
{masked_patient_history}
```

### Data Masking (bắt buộc)
```python
def data_masking(patient_data: dict) -> dict:
    """Ẩn PII trước khi gửi LLM — KHÔNG bỏ qua bước này"""
    masked = patient_data.copy()
    masked["full_name"] = "BỆNH NHÂN"
    masked["phone"] = "***"
    masked["cccd"] = "***"
    masked["address"] = "***"
    masked["insurance_number"] = "***"
    return masked
```

### Output
- Định dạng Markdown (bullet points, dễ đọc)
- Trạng thái: **"Bản nháp — chỉ dành cho tham khảo"**
- Bác sĩ phải tự đối chiếu với hồ sơ gốc

## FR-AI-02: AI Chatbot (Hỏi đáp quy trình)

### Luồng xử lý
```
Câu hỏi người dùng
    → Intent Analysis
    → LLM + Knowledge Base (quy trình phòng khám)
    → Phản hồi văn bản thuần
    → Nếu câu hỏi về y tế → TỪ CHỐI lịch sự
```

### System Prompt (bất biến)
```
Bạn là nhân viên lễ tân ảo của phòng khám. Nhiệm vụ của bạn là hỗ trợ bệnh nhân.

Bạn CHỈ ĐƯỢC PHÉP trả lời các câu hỏi về:
- Giờ làm việc của phòng khám
- Quy trình đặt lịch khám
- Bảng giá dịch vụ và thủ tục hành chính
- Hướng dẫn chuẩn bị giấy tờ khi đến khám
- Thanh toán viện phí

Nếu người dùng hỏi về triệu chứng bệnh hoặc xin tư vấn điều trị:
→ TỪ CHỐI lịch sự
→ Giải thích giới hạn của hệ thống
→ Hướng dẫn đặt lịch khám trực tiếp với bác sĩ

Trả lời bằng tiếng Việt, ngắn gọn và thân thiện.
```

### User Prompt Template
```
Câu hỏi của bệnh nhân: {user_question}
Hãy trả lời ngắn gọn, lịch sự và chính xác dựa trên quy định của phòng khám.
```

### Output
- Plain text, tiếng Việt
- Thêm link đặt lịch nếu phù hợp
- **Không** chứa thông tin chẩn đoán, không kê đơn

## FR-AI-03: AI Post-exam Guide (Hướng dẫn sau khám)

### Luồng xử lý
```
Bác sĩ hoàn thành phiếu khám
    → Nhập ghi chú/từ khóa dặn dò
    → LLM sinh văn bản hướng dẫn
    → Hiển thị bản nháp
    → Bác sĩ kiểm tra + chỉnh sửa
    → Bác sĩ phê duyệt (HUMAN-IN-THE-LOOP)
    → Lưu chính thức + gửi bệnh nhân
```

### System Prompt (bất biến)
```
Bạn là trợ lý soạn thảo văn bản y tế cho bác sĩ. Dựa trên các từ khóa
và ghi chú ngắn gọn của bác sĩ, hãy soạn thảo một đoạn văn bản hướng dẫn
chăm sóc sức khỏe sau khám rõ ràng, dễ hiểu dành cho bệnh nhân.

Yêu cầu:
- Giữ nguyên vẹn ý nghĩa chuyên môn của bác sĩ.
- TUYỆT ĐỐI KHÔNG tự sáng tạo, KHÔNG thêm bớt phương pháp điều trị
  hay các loại thuốc không có trong ghi chú.
- Trả lời bằng tiếng Việt.
```

### User Prompt Template
```
Chẩn đoán: {diagnosis}
Ghi chú dặn dò của bác sĩ: {doctor_notes}
Hãy sinh đoạn văn bản hướng dẫn chi tiết theo lời dặn trên.
```

### Output
- Định dạng Markdown/HTML
- Trạng thái: **"BẢN NHÁP — Chờ bác sĩ phê duyệt"**
- Chỉ lưu và gửi sau khi bác sĩ Approve

## Fallback Mechanism (SEC-AI-03)
```python
try:
    result = call_gemini_api(prompt)
    log_ai(function=fn, status="success")
    return result
except (Timeout, APIError) as e:
    log_ai(function=fn, status="fallback", error=str(e))
    return None  # Hệ thống vẫn chạy, thông báo cho người dùng
```

## AI Logs (SEC-AI-04)
Ghi vào bảng `ai_logs`:
```python
{
    "user_id": current_user.id,
    "function_name": "ai_summary" | "chatbot" | "post_exam_guide",
    "input_masked": masked_json_string,  # KHÔNG PII
    "output_text": ai_response,
    "status": "success" | "error" | "fallback",
    "duration_ms": elapsed_ms
}
```

## Rules
- API key từ `GEMINI_API_KEY` env var — không hard-code.
- Không để AI service truy cập Database trực tiếp.
- Data Masking là bước đầu tiên, bắt buộc, không thể bỏ qua.
- Mọi output AI phải được doctor approve trước khi lưu (trừ Chatbot).
