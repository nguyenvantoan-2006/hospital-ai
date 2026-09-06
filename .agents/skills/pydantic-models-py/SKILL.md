---
name: pydantic-models-py
description: >
  Chuẩn hóa Pydantic schemas theo multi-model pattern cho hospital-ai.
  Áp dụng cho schemas.py — định nghĩa rõ ràng Create/Update/Response models
  cho BenhNhan, LichKham, PhieuKham, HoaDon, BacSi.
source: antigravity/community
date_added: "2026-08-17"
project: hospital-ai
---

# Pydantic Models — Hospital-AI

## Khi nào dùng skill này

- Thêm schema mới vào `schemas.py`
- Chuẩn hóa Request/Response cho API endpoints
- Đảm bảo validation dữ liệu nhập vào từ frontend

## Multi-Model Pattern (áp dụng cho Hospital-AI)

| Model | Mục đích | Ví dụ |
|-------|---------|-------|
| `Base` | Các field chung | `BenhNhanBase` |
| `Create` | POST request body | `BenhNhanCreate` |
| `Update` | PUT/PATCH (optional fields) | `BenhNhanUpdate` |
| `Response` | GET response | `BenhNhanResponse` |

## Ví dụ chuẩn — BenhNhan Schemas

```python
# schemas.py
from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional
from enum import Enum

class GioiTinhEnum(str, Enum):
    nam = "nam"
    nu = "nu"
    khac = "khac"

# ── BASE ──────────────────────────────────────────────
class BenhNhanBase(BaseModel):
    ho_ten: str = Field(..., min_length=2, max_length=100, description="Họ và tên đầy đủ")
    ngay_sinh: Optional[date] = None
    gioi_tinh: Optional[GioiTinhEnum] = None
    so_dien_thoai: Optional[str] = Field(None, pattern=r"^(0|\+84)\d{9,10}$")
    dia_chi: Optional[str] = None
    ma_bhyt: Optional[str] = Field(None, max_length=15)
    tien_su_benh: Optional[str] = None

# ── CREATE ────────────────────────────────────────────
class BenhNhanCreate(BenhNhanBase):
    ho_ten: str = Field(..., min_length=2, max_length=100)
    # Các trường bắt buộc khi tạo mới

# ── UPDATE ────────────────────────────────────────────
class BenhNhanUpdate(BaseModel):
    """Tất cả field optional cho PATCH request."""
    ho_ten: Optional[str] = Field(None, min_length=2, max_length=100)
    ngay_sinh: Optional[date] = None
    gioi_tinh: Optional[GioiTinhEnum] = None
    so_dien_thoai: Optional[str] = None
    dia_chi: Optional[str] = None
    ma_bhyt: Optional[str] = None
    tien_su_benh: Optional[str] = None

# ── RESPONSE ──────────────────────────────────────────
class BenhNhanResponse(BenhNhanBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic V2 (thay orm_mode)
```

## Ví dụ — LichKham Schemas

```python
class TrangThaiLichKhamEnum(str, Enum):
    cho_xac_nhan = "cho_xac_nhan"
    da_xac_nhan = "da_xac_nhan"
    hoan_thanh = "hoan_thanh"
    huy = "huy"

class LichKhamBase(BaseModel):
    benh_nhan_id: int
    bac_si_id: Optional[int] = None
    thoi_gian: datetime
    ly_do_kham: str = Field(..., min_length=3, max_length=500)
    trang_thai: TrangThaiLichKhamEnum = TrangThaiLichKhamEnum.cho_xac_nhan

class LichKhamCreate(LichKhamBase):
    pass

class LichKhamUpdate(BaseModel):
    bac_si_id: Optional[int] = None
    thoi_gian: Optional[datetime] = None
    ly_do_kham: Optional[str] = None
    trang_thai: Optional[TrangThaiLichKhamEnum] = None

class LichKhamResponse(LichKhamBase):
    id: int
    benh_nhan: Optional[BenhNhanResponse] = None

    class Config:
        from_attributes = True
```

## Ví dụ — AI Request/Response Schemas

```python
# AI Summary
class AISummaryRequest(BaseModel):
    benh_nhan_id: int = Field(..., gt=0)

class AISummaryResponse(BaseModel):
    summary: str
    is_fallback: bool = False  # True nếu AI lỗi, dùng fallback text

# Post-Exam Guide
class AIGuideRequest(BaseModel):
    chan_doan: str = Field(..., min_length=3, description="Chẩn đoán của bác sĩ")
    trieu_chung: Optional[str] = ""

class AIGuideResponse(BaseModel):
    guide: str
    is_draft: bool = True  # Luôn là bản nháp, cần bác sĩ phê duyệt
```

## Validators Thường Dùng

```python
from pydantic import field_validator

class BenhNhanCreate(BenhNhanBase):
    @field_validator("so_dien_thoai")
    @classmethod
    def validate_phone(cls, v):
        if v and not v.startswith(("0", "+84")):
            raise ValueError("Số điện thoại phải bắt đầu bằng 0 hoặc +84")
        return v

    @field_validator("ngay_sinh")
    @classmethod
    def validate_birth_date(cls, v):
        if v and v > date.today():
            raise ValueError("Ngày sinh không thể là ngày trong tương lai")
        return v
```

## Config chuẩn cho Response Models

```python
class Config:
    from_attributes = True      # Pydantic V2 (bắt buộc để dùng với SQLAlchemy)
    populate_by_name = True     # Chấp nhận cả alias và tên gốc
    json_schema_extra = {
        "example": {
            "ho_ten": "Nguyễn Văn A",
            "ngay_sinh": "1990-01-15",
            "so_dien_thoai": "0901234567"
        }
    }
```

## Giới hạn

- Luôn dùng `from_attributes = True` (không phải `orm_mode` của Pydantic V1)
- Validate đủ cho dữ liệu y tế: số điện thoại, ngày sinh, BHYT number
- Response models không nên trả về thông tin nhạy cảm (password hash, internal IDs)
