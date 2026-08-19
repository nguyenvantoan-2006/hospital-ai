---
name: fastapi-pro
description: >
  Xây dựng API hiệu suất cao, bất đồng bộ với FastAPI, SQLAlchemy 2.0 và Pydantic V2.
  Áp dụng cho dự án Hospital-AI: quản lý phòng khám, bệnh nhân, lịch khám, hóa đơn, và AI endpoints.
source: antigravity/community
date_added: "2026-08-17"
project: hospital-ai
---

# FastAPI Pro — Hospital-AI

## Khi nào dùng skill này

- Tạo endpoint mới trong `routers/` (bệnh nhân, lịch khám, hóa đơn, phiếu khám, AI)
- Cần áp dụng async/await đúng cách cho DB queries và AI calls
- Chuẩn hóa Dependency Injection với `get_db`, JWT auth
- Xử lý lỗi và validation cho API y tế

## Không dùng khi

- Làm frontend (HTML templates, static files)
- Cấu hình database schema (dùng skill `pydantic-models-py`)

---

## Cấu trúc Router chuẩn — Hospital-AI

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models, schemas

router = APIRouter(prefix="/benh-nhans", tags=["Bệnh Nhân"])

@router.get("/", response_model=list[schemas.BenhNhanResponse])
async def get_benh_nhans(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lấy danh sách bệnh nhân với phân trang."""
    return db.query(models.BenhNhan).offset(skip).limit(limit).all()
```

## Async Pattern cho AI Calls (ai.py)

```python
import asyncio
import google.generativeai as genai

async def call_llm_api(prompt: str, max_retries: int = 3) -> str:
    """
    Gọi Gemini API với retry + exponential backoff.
    Dùng asyncio.to_thread vì SDK Gemini chưa hỗ trợ async native.
    """
    for attempt in range(max_retries):
        try:
            response = await asyncio.to_thread(model.generate_content, prompt)
            return response.text
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            await asyncio.sleep(wait)
```

## Dependency Injection Patterns

```python
# Tái sử dụng trong mọi router
from fastapi import Security
from fastapi.security import HTTPBearer

security = HTTPBearer()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Xác thực JWT token, trả về user hiện tại."""
    ...

def require_role(role: str):
    """Role-based access: admin, bac_si, le_tan."""
    def _check(user = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(status_code=403, detail="Không có quyền truy cập")
        return user
    return _check
```

## Error Handling Chuẩn

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "Không tìm thấy dữ liệu"})

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    logger.error(f"Server error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Lỗi hệ thống, vui lòng thử lại sau"})
```

## Danh sách Routers trong dự án

| File | Prefix | Chức năng |
|------|--------|-----------|
| `routers/auth.py` | `/auth` | Đăng nhập, JWT |
| `routers/admin.py` | `/admin` | Quản lý hệ thống |
| `routers/benh_nhans.py` | `/benh-nhans` | CRUD bệnh nhân |
| `routers/lich_khams.py` | `/lich-khams` | Lịch hẹn khám |
| `routers/phieu_khams.py` | `/phieu-khams` | Phiếu khám |
| `routers/hoa_dons.py` | `/hoa-dons` | Hóa đơn |
| `routers/ai.py` | `/ai` | AI summary, post-exam guide |

## Performance Tips

- Dùng `select_in_loading` để tránh N+1 query với relationships
- Cache kết quả AI tóm tắt với `functools.lru_cache` (TTL 1 giờ)
- Dùng `BackgroundTasks` cho tác vụ không cần đợi (gửi email, logging)

## Giới hạn

- Skill này chỉ áp dụng cho backend FastAPI trong `hospital-ai`
- Không thay thế cho kiểm tra bảo mật dữ liệu y tế
- Luôn test trên Swagger UI (`/docs`) trước khi deploy
