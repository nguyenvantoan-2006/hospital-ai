---
name: llm-prompt-optimize
description: >
  Tối ưu hóa System Prompt và Guardrails trong routers/ai.py của hospital-ai.
  Áp dụng các kỹ thuật prompt engineering y tế: Chain-of-Thought, Constitutional AI,
  Few-Shot examples, và cấu trúc rõ ràng để giảm hallucination.
source: antigravity/community
date_added: "2026-08-17"
project: hospital-ai
---

# LLM Prompt Optimization — Hospital-AI

## Khi nào dùng skill này

- Cải thiện chất lượng AI Summary trong `/ai/summary`
- Tối ưu Post-Exam Guide trong `/ai/post-exam-guide`
- Thêm endpoint AI mới cần Guardrails y tế
- Giảm hallucination và tăng tính nhất quán của response

## Nguyên tắc Prompt Y tế (Medical Guardrails)

### 4 Quy tắc bất biến (đã có trong code, cần giữ nguyên)
1. ❌ Không tự chẩn đoán bệnh mới
2. ❌ Không kê đơn thuốc
3. ❌ Không đề xuất phác đồ điều trị
4. ❌ Không đưa ra lời khuyên y tế cụ thể

### Cấu trúc Prompt Chuẩn (RISEN Framework)

```
[ROLE]       → Bạn là ai? (Trợ lý AI Hành chính Y tế)
[INSTRUCTION] → Nhiệm vụ cụ thể là gì?
[SCOPE]      → Phạm vi được phép làm gì?
[EXCLUSIONS] → Tuyệt đối KHÔNG làm gì?
[NPUT DATA]  → Dữ liệu đầu vào (đã mask)
[NSTRUCTIONS] → Format output mong muốn
```

## Cải thiện AI Summary Prompt (hiện tại → tối ưu)

### Hiện tại (basic)
```python
system_prompt = f"""
Bạn là Trợ lý AI Hành chính Y tế chuyên nghiệp...
RÀNG BUỘC Y ĐỨC: [4 rules]
THÔNG TIN BỆNH NHÂN: {masked_data}
LỊCH SỬ: {history_info}
Hãy viết tóm tắt ngắn gọn (dưới 150 từ)
"""
```

### Tối ưu (Structured + Few-Shot)
```python
system_prompt = f"""
## VAI TRÒ
Bạn là Trợ lý AI Hành chính Y tế. Nhiệm vụ: TÓM TẮT hồ sơ để hỗ trợ bác sĩ tra cứu nhanh.

## GIỚI HẠN TUYỆT ĐỐI (Constitutional AI)
- KHÔNG chẩn đoán | KHÔNG kê thuốc | KHÔNG tư vấn điều trị | KHÔNG đưa ra kết luận lâm sàng

## VÍ DỤ MẪU (Few-Shot)
INPUT: Bệnh nhân N*** A, 45 tuổi, tiền sử: tăng huyết áp. Đã khám 2 lần: đau đầu (2024-01), chóng mặt (2024-06).
OUTPUT: "Bệnh nhân nam, 45 tuổi, có tiền sử tăng huyết áp. Đã khám 2 lần trong năm 2024 với triệu chứng đau đầu và chóng mặt được ghi nhận. Khuyến nghị bác sĩ tham khảo hồ sơ chi tiết."

## DỮ LIỆU THỰC TẾ
Bệnh nhân: {masked_data['ho_ten']} | Sinh: {masked_data['ngay_sinh']} | BHYT: {masked_data['ma_bhyt']}
Tiền sử: {masked_data['tien_su_benh']}

Lịch sử khám:
{history_info}

## YÊU CẦU OUTPUT
Viết 1 đoạn tóm tắt hành chính, dưới 150 từ, không bullet points, ngôn ngữ trung tính y tế.
"""
```

## Tối ưu Post-Exam Guide Prompt

```python
guide_prompt = f"""
## VAI TRÒ
Bạn là Trợ lý Y tế hỗ trợ Bác sĩ soạn BẢN NHÁP hướng dẫn chăm sóc sau khám.

## RÀNG BUỘC (SEC-AI-02)
- Đây là BẢN NHÁP — Bác sĩ phải xem xét, chỉnh sửa và phê duyệt
- Chỉ đưa ra lời khuyên sinh hoạt chung, KHÔNG kê thuốc
- Dựa HOÀN TOÀN vào chẩn đoán của bác sĩ, không suy diễn thêm

## INPUT
Chẩn đoán: {request.chan_doan}
Triệu chứng: {request.trieu_chung or "Đã ghi nhận"}

## OUTPUT FORMAT (bắt buộc 3 phần)
**1. Chế độ ăn uống & Nghỉ ngơi:**
[nội dung]

**2. Lưu ý sinh hoạt & Dùng thuốc:**
[nội dung - nhắc tuân thủ đơn thuốc của bác sĩ]

**3. Dấu hiệu cần tái khám ngay:**
[nội dung - dấu hiệu bất thường cụ thể]

---
⚠️ BẢN NHÁP - Cần bác sĩ phê duyệt trước khi in cho bệnh nhân
"""
```

## Kỹ thuật Giảm Hallucination

### 1. Temperature thấp hơn cho tác vụ y tế
```python
response = model.generate_content(
    prompt,
    generation_config=genai.types.GenerationConfig(
        temperature=0.2,     # Thấp = ít sáng tạo, ít hallucinate
        max_output_tokens=400,
        top_p=0.8,
    )
)
```

### 2. Output validation sau khi nhận response
```python
FORBIDDEN_PHRASES = [
    "tôi chẩn đoán", "bệnh nhân bị", "nên uống thuốc",
    "kê đơn", "phác đồ điều trị", "tôi đề xuất điều trị"
]

def validate_ai_output(text: str) -> bool:
    """Kiểm tra AI không vượt guardrails."""
    text_lower = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in text_lower:
            logger.warning(f"[GUARDRAIL] Phát hiện nội dung vi phạm: '{phrase}'")
            return False
    return True
```

### 3. Fallback khi vi phạm Guardrails
```python
ai_output = await call_llm_api(prompt)

if not validate_ai_output(ai_output):
    # Fallback an toàn
    ai_output = f"[TÓM TẮT HỆ THỐNG] Bệnh nhân {masked_data['ho_ten']}, " \
                f"tiền sử: {masked_data['tien_su_benh']}. Vui lòng tham khảo hồ sơ chi tiết."
```

## Metrics Đánh giá Prompt Quality

| Metric | Mục tiêu | Cách đo |
|--------|---------|---------|
| Tuân thủ Guardrails | 100% | Manual review + keyword check |
| Độ ngắn gọn | < 150 từ | `len(text.split()) < 150` |
| Thông tin đủ | Có đủ 4 yếu tố | Checklist tên, tiền sử, lịch sử, khuyến nghị |
| Không hallucination | 0 phát hiện | Forbidden phrases check |

## Giới hạn

- Không thể đảm bảo 100% chính xác y tế từ AI — luôn cần bác sĩ review
- Temperature thấp có thể làm output lặp lại hoặc cứng nhắc
- Few-shot examples cần được cập nhật theo phản hồi thực tế của bác sĩ
