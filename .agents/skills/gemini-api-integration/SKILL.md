---
name: gemini-api-integration
description: >
  Tích hợp và tối ưu Google Gemini API trong hospital-ai.
  Bao gồm: model selection, streaming, error handling, exponential backoff,
  safety settings, và production best practices cho môi trường y tế.
source: antigravity/community
date_added: "2026-08-17"
project: hospital-ai
---

# Gemini API Integration — Hospital-AI

## Khi nào dùng skill này

- Cải thiện `call_llm_api()` trong `routers/ai.py`
- Thêm streaming cho UI hiển thị kết quả AI dần dần
- Xử lý rate limit và quota errors
- Chọn model phù hợp (Flash vs Pro)

## Setup hiện tại trong dự án

```python
# Hiện tại trong routers/ai.py
import google.generativeai as genai
model = genai.GenerativeModel("gemini-1.5-flash")
```

## Nâng cấp: Production-Ready Setup

```python
# ai_config.py — tách config ra file riêng
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY chưa được cấu hình trong .env")

genai.configure(api_key=GEMINI_API_KEY)

# Cấu hình Safety Settings cho môi trường y tế
MEDICAL_SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_LOW_AND_ABOVE"
    },
]

# Generation Config cho tác vụ tóm tắt y tế
MEDICAL_GENERATION_CONFIG = genai.types.GenerationConfig(
    temperature=0.2,       # Thấp → ít sáng tạo, ít hallucinate
    max_output_tokens=500, # Giới hạn độ dài
    top_p=0.8,
    top_k=40,
)

# Model cho từng task
SUMMARY_MODEL = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=MEDICAL_GENERATION_CONFIG,
    safety_settings=MEDICAL_SAFETY_SETTINGS,
)

GUIDE_MODEL = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=genai.types.GenerationConfig(
        temperature=0.3,
        max_output_tokens=600,
    ),
    safety_settings=MEDICAL_SAFETY_SETTINGS,
)
```

## Nâng cấp call_llm_api() với Retry Logic

```python
# Thay thế hàm call_llm_api() hiện tại trong routers/ai.py
import asyncio
import logging
from google.api_core import exceptions as google_exceptions

logger = logging.getLogger(__name__)

async def call_llm_api(
    prompt: str,
    model=SUMMARY_MODEL,
    max_retries: int = 3,
    timeout: int = 30
) -> str:
    """
    Gọi Gemini API với:
    - Exponential backoff cho rate limit (429)
    - Timeout handling
    - Safety filter detection
    - Logging chi tiết
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"[Gemini] Attempt {attempt + 1}/{max_retries}")
            
            response = await asyncio.wait_for(
                asyncio.to_thread(model.generate_content, prompt),
                timeout=timeout
            )
            
            # Kiểm tra safety filter
            if response.prompt_feedback.block_reason:
                logger.warning(f"[Gemini] Bị chặn bởi safety filter: {response.prompt_feedback.block_reason}")
                raise ValueError(f"Nội dung bị chặn: {response.prompt_feedback.block_reason}")
            
            # Kiểm tra response hợp lệ
            if not response.text:
                raise ValueError("Gemini trả về response rỗng")
            
            logger.info(f"[Gemini] ✅ Thành công, độ dài: {len(response.text)} chars")
            return response.text
            
        except asyncio.TimeoutError:
            logger.error(f"[Gemini] Timeout sau {timeout}s (attempt {attempt + 1})")
            if attempt == max_retries - 1:
                raise Exception("AI API timeout. Vui lòng thử lại.")
                
        except google_exceptions.ResourceExhausted:
            # Rate limit (429) → chờ với exponential backoff
            wait_time = 2 ** attempt * 2  # 2s, 4s, 8s
            logger.warning(f"[Gemini] Rate limit, chờ {wait_time}s...")
            await asyncio.sleep(wait_time)
            if attempt == max_retries - 1:
                raise Exception("API quá tải. Vui lòng thử lại sau.")
                
        except google_exceptions.InvalidArgument as e:
            logger.error(f"[Gemini] Invalid request: {e}")
            raise Exception(f"Lỗi cấu hình prompt: {str(e)}")
            
        except Exception as e:
            logger.error(f"[Gemini] Unexpected error: {e}")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1)
```

## Streaming Response (cho UI real-time)

```python
# Endpoint mới: /ai/summary-stream
from fastapi.responses import StreamingResponse

@router.post("/summary-stream")
async def generate_summary_stream(request: AISummaryRequest, db: Session = Depends(get_db)):
    """
    Stream AI summary response — UI hiển thị kết quả dần dần như ChatGPT.
    """
    # ... (lấy data, mask, tạo prompt như bình thường) ...
    
    async def stream_generator():
        try:
            response_stream = await asyncio.to_thread(
                SUMMARY_MODEL.generate_content, prompt, stream=True
            )
            for chunk in response_stream:
                if chunk.text:
                    yield f"data: {chunk.text}\n\n"  # SSE format
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
        finally:
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream"
    )
```

## Model Selection Guide

| Model | Dùng cho | Tốc độ | Chi phí |
|-------|---------|--------|---------|
| `gemini-1.5-flash` ✅ | AI Summary, Post-Exam Guide | Nhanh | Thấp |
| `gemini-1.5-pro` | Phân tích phức tạp, RAG | Trung bình | Cao hơn |
| `gemini-2.0-flash` | Nâng cấp, multimodal | Rất nhanh | Thấp |

> **Khuyến nghị:** Giữ `gemini-1.5-flash` cho hospital-ai. Đủ chính xác, nhanh, chi phí thấp.

## .env Configuration

```env
# .env — đã có, thêm config mới
GEMINI_API_KEY=your_api_key_here

# Optional — rate limit config
GEMINI_MAX_RETRIES=3
GEMINI_TIMEOUT=30
GEMINI_TEMPERATURE=0.2
```

## Troubleshooting

| Lỗi | Nguyên nhân | Giải pháp |
|-----|------------|---------|
| `API_KEY_INVALID` | Key sai hoặc hết hạn | Kiểm tra Google AI Studio |
| `RESOURCE_EXHAUSTED` | Vượt quota | Exponential backoff + check quota |
| Response rỗng | Safety filter chặn | Kiểm tra `prompt_feedback.block_reason` |
| Timeout | Prompt quá dài | Giảm `max_output_tokens`, rút ngắn prompt |
| `ValueError: GEMINI_API_KEY missing` | `.env` chưa load | Thêm `load_dotenv()` trước `os.getenv()` |

## Giới hạn

- `asyncio.to_thread()` cần thiết vì SDK chưa hỗ trợ async native
- Streaming cần frontend xử lý SSE format
- Safety settings có thể chặn nội dung y tế hợp lệ → điều chỉnh threshold nếu cần
- Free tier: 15 requests/phút → production cần upgrade plan
