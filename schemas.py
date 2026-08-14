# schemas.py
# Pydantic Schemas cho Hệ thống Quản lý Phòng khám
# Quy ước: [Model]Base → [Model]Create → [Model]Response
# Dùng Pydantic v2: model_config = ConfigDict(from_attributes=True)
# ════════════════════════════════════════════════════════════════════════════════

from datetime import date, datetime
from typing import Optional, List, Literal

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict


# ════════════════════════════════════════════════════════════════════════════════
#  CẤU HÌNH CHUNG
#  Tất cả schema đọc từ ORM (Response) đều kế thừa OrmBase
# ════════════════════════════════════════════════════════════════════════════════
class OrmBase(BaseModel):
    """Base chung cho mọi Response schema — bật from_attributes để đọc từ ORM model."""
    model_config = ConfigDict(from_attributes=True)


# ════════════════════════════════════════════════════════════════════════════════
#  1. USER SCHEMAS
# ════════════════════════════════════════════════════════════════════════════════

VALID_ROLES = {"admin", "le_tan", "bac_si", "ke_toan"}


class UserBase(OrmBase):
    """Các trường cơ bản của tài khoản (dùng chung cho Create & Response)."""
    username:   str
    role:       str
    email:      Optional[str] = None
    trang_thai: bool = True

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in VALID_ROLES:
            raise ValueError(f"Role không hợp lệ. Chọn một trong: {VALID_ROLES}")
        return v


class UserCreate(UserBase):
    """Schema tạo tài khoản mới — bổ sung password plaintext (sẽ hash ở Service layer)."""
    password: str


class UserUpdate(OrmBase):
    """Schema cập nhật tài khoản — tất cả field đều Optional."""
    email:      Optional[str]  = None
    role:       Optional[str]  = None
    trang_thai: Optional[bool] = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_ROLES:
            raise ValueError(f"Role không hợp lệ. Chọn một trong: {VALID_ROLES}")
        return v


class UserResponse(UserBase):
    """Schema trả về — KHÔNG bao gồm password_hash."""
    id: int


class UserProfileResponse(OrmBase):
    """Schema chi tiết hồ sơ nhân sự/người dùng cho Admin view profile."""
    user_id:         int
    username:        str
    role:            str
    email:           Optional[str] = None
    trang_thai:      bool
    ho_ten:          Optional[str] = None
    so_dien_thoai:   Optional[str] = None
    hoc_vi:          Optional[str] = None
    chuc_vu:         Optional[str] = None
    chuyen_khoa:     Optional[str] = None
    phong_kham:      Optional[str] = None
    lich_lam_viec:   Optional[str] = None


# ════════════════════════════════════════════════════════════════════════════════
#  2. BENH NHAN SCHEMAS
# ════════════════════════════════════════════════════════════════════════════════

class BenhNhanBase(OrmBase):
    """Các trường cơ bản của hồ sơ bệnh nhân."""
    ho_ten:        str
    ngay_sinh:     Optional[date] = None
    gio_tinh:      Optional[str]  = None
    so_dien_thoai: Optional[str]  = None
    cccd:          Optional[str]  = None
    dia_chi:       Optional[str]  = None
    ma_bhyt:       Optional[str]  = None
    tien_su_benh:  Optional[str]  = None


class BenhNhanCreate(BenhNhanBase):
    """Schema tạo mới hồ sơ bệnh nhân (Lễ tân sử dụng)."""
    user_id: Optional[int] = None


class BenhNhanUpdate(OrmBase):
    """Schema cập nhật hồ sơ bệnh nhân — tất cả field đều Optional."""
    ho_ten:        Optional[str]  = None
    ngay_sinh:     Optional[date] = None
    gio_tinh:      Optional[str]  = None
    so_dien_thoai: Optional[str]  = None
    cccd:          Optional[str]  = None
    dia_chi:       Optional[str]  = None
    ma_bhyt:       Optional[str]  = None
    tien_su_benh:  Optional[str]  = None


class BenhNhanResponse(BenhNhanBase):
    """Schema trả về hồ sơ bệnh nhân (không kèm danh sách lịch khám)."""
    id:      int
    user_id: Optional[int] = None


class BenhNhanDetailResponse(BenhNhanResponse):
    """Schema trả về đầy đủ — kèm danh sách lịch khám (dùng cho xem hồ sơ chi tiết)."""
    lich_khams: List["LichKhamResponse"] = []


# ════════════════════════════════════════════════════════════════════════════════
#  3. LICH KHAM SCHEMAS
# ════════════════════════════════════════════════════════════════════════════════

VALID_TRANG_THAI_LICH = {"cho_xac_nhan", "da_dat_lich", "cho_kham", "dang_kham", "hoan_thanh", "huy"}


class LichKhamBase(OrmBase):
    """Các trường cơ bản của lịch khám."""
    benh_nhan_id:   int
    bac_si_id:      Optional[int] = None
    chuyen_khoa_id: Optional[int] = None
    stt:            Optional[int] = None
    thoi_gian:      datetime
    trang_thai:     str = "cho_xac_nhan"
    ly_do_kham:     Optional[str] = None

    @field_validator("trang_thai")
    @classmethod
    def validate_trang_thai(cls, v: str) -> str:
        if v not in VALID_TRANG_THAI_LICH:
            raise ValueError(f"Trạng thái không hợp lệ. Chọn: {VALID_TRANG_THAI_LICH}")
        return v


class LichKhamCreate(LichKhamBase):
    """Schema tạo lịch khám mới (Lễ tân hoặc Bệnh nhân tự đặt)."""
    pass


class LichKhamUpdate(OrmBase):
    """Schema cập nhật lịch khám — tất cả field đều Optional."""
    bac_si_id:      Optional[int]      = None
    chuyen_khoa_id: Optional[int]      = None
    thoi_gian:      Optional[datetime] = None
    trang_thai:     Optional[str]      = None
    ly_do_kham:     Optional[str]      = None
    stt:            Optional[int]      = None

    @field_validator("trang_thai")
    @classmethod
    def validate_trang_thai(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_TRANG_THAI_LICH:
            raise ValueError(f"Trạng thái không hợp lệ. Chọn: {VALID_TRANG_THAI_LICH}")
        return v


class LichKhamResponse(LichKhamBase):
    """Schema trả về lịch khám (không kèm phiếu khám)."""
    id: int


class LichKhamDetailResponse(LichKhamResponse):
    """Schema trả về đầy đủ — kèm phiếu khám (dùng cho Bác sĩ xem)."""
    phieu_kham: Optional["PhieuKhamResponse"] = None


# ════════════════════════════════════════════════════════════════════════════════
#  4. PHIEU KHAM SCHEMAS
# ════════════════════════════════════════════════════════════════════════════════

class PhieuKhamBase(OrmBase):
    """Các trường cơ bản của phiếu khám."""
    lich_kham_id: int
    trieu_chung:  Optional[str] = None
    chan_doan:    Optional[str] = None
    ai_summary:   Optional[str] = None  # Do AI sinh ra, không phải Bác sĩ nhập trực tiếp


class PhieuKhamCreate(PhieuKhamBase):
    """Schema tạo phiếu khám mới (Bác sĩ lập sau khi khám)."""
    pass


class PhieuKhamUpdate(OrmBase):
    """Schema cập nhật phiếu khám — tất cả field đều Optional."""
    trieu_chung: Optional[str] = None
    chan_doan:   Optional[str] = None
    ai_summary:  Optional[str] = None


class PhieuKhamResponse(PhieuKhamBase):
    """Schema trả về phiếu khám (không kèm đơn thuốc & hóa đơn)."""
    id: int


class PhieuKhamDetailResponse(PhieuKhamResponse):
    """Schema trả về đầy đủ — kèm đơn thuốc và hóa đơn."""
    don_thuocs: List["DonThuocResponse"] = []
    hoa_don:    Optional["HoaDonResponse"] = None


# ════════════════════════════════════════════════════════════════════════════════
#  5. THUOC SCHEMAS
# ════════════════════════════════════════════════════════════════════════════════

class ThuocBase(OrmBase):
    """Các trường cơ bản của thuốc trong danh mục."""
    ten_thuoc:   str
    don_vi_tinh: Optional[str]  = None  # Ví dụ: viên, chai, ống, gói
    don_gia:     float = 0.0


class ThuocCreate(ThuocBase):
    """Schema thêm thuốc mới vào danh mục (Kế toán / Admin sử dụng)."""
    pass


class ThuocUpdate(OrmBase):
    """Schema cập nhật thông tin thuốc — tất cả field đều Optional."""
    ten_thuoc:   Optional[str]   = None
    don_vi_tinh: Optional[str]   = None
    don_gia:     Optional[float] = None


class ThuocResponse(ThuocBase):
    """Schema trả về thông tin thuốc."""
    id: int


# ════════════════════════════════════════════════════════════════════════════════
#  6. DON THUOC SCHEMAS
# ════════════════════════════════════════════════════════════════════════════════

class DonThuocBase(OrmBase):
    """Các trường cơ bản của một dòng trong đơn thuốc."""
    phieu_kham_id: int
    thuoc_id:      int
    so_luong:      int = 1
    lieu_dung:     Optional[str] = None  # Ví dụ: "2 viên/ngày, sau ăn"


class DonThuocCreate(DonThuocBase):
    """Schema thêm thuốc vào đơn (Bác sĩ kê đơn)."""
    pass


class DonThuocUpdate(OrmBase):
    """Schema cập nhật số lượng / liều dùng trong đơn thuốc."""
    so_luong:  Optional[int] = None
    lieu_dung: Optional[str] = None


class DonThuocResponse(DonThuocBase):
    """Schema trả về chi tiết một dòng đơn thuốc."""
    id:    int
    thuoc: Optional[ThuocResponse] = None  # Trả về thông tin thuốc lồng nhau


# ════════════════════════════════════════════════════════════════════════════════
#  7. HOA DON SCHEMAS
# ════════════════════════════════════════════════════════════════════════════════

VALID_TRANG_THAI_HD = {"chua_thanh_toan", "da_thanh_toan", "huy"}
VALID_HINH_THUC_TT  = {"tien_mat", "chuyen_khoan", "qr"}


class HoaDonBase(OrmBase):
    """Các trường cơ bản của hóa đơn."""
    phieu_kham_id: int
    tong_tien:     float = 0.0
    trang_thai:    str = "chua_thanh_toan"
    hinh_thuc_tt:  Optional[str] = None  # Hình thức thanh toán: 'tien_mat' | 'chuyen_khoan' | 'qr'

    @field_validator("trang_thai")
    @classmethod
    def validate_trang_thai(cls, v: str) -> str:
        if v not in VALID_TRANG_THAI_HD:
            raise ValueError(f"Trạng thái không hợp lệ. Chọn: {VALID_TRANG_THAI_HD}")
        return v

    @field_validator("hinh_thuc_tt")
    @classmethod
    def validate_hinh_thuc_tt(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_HINH_THUC_TT:
            raise ValueError(f"Hình thức không hợp lệ. Chọn: {VALID_HINH_THUC_TT}")
        return v


class HoaDonCreateInput(OrmBase):
    """Schema tạo/xác nhận hóa đơn thanh toán — giới hạn hinh_thuc_tt bằng Literal."""
    phieu_kham_id: int
    hinh_thuc_tt:  Literal["tien_mat", "chuyen_khoan", "qr"] = "tien_mat"
    tong_tien:     Optional[float] = None
    trang_thai:    Literal["da_thanh_toan", "chua_thanh_toan"] = "da_thanh_toan"


class HoaDonCreate(HoaDonBase):
    """Schema tạo hóa đơn mới (Kế toán / hệ thống tự tạo sau khi khám xong)."""
    pass


class HoaDonUpdate(OrmBase):
    """Schema cập nhật hóa đơn — tất cả field đều Optional."""
    tong_tien:    Optional[float] = None
    trang_thai:   Optional[str]   = None
    hinh_thuc_tt: Optional[str]   = None

    @field_validator("trang_thai")
    @classmethod
    def validate_trang_thai(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_TRANG_THAI_HD:
            raise ValueError(f"Trạng thái không hợp lệ. Chọn: {VALID_TRANG_THAI_HD}")
        return v


class HoaDonResponse(HoaDonBase):
    """Schema trả về hóa đơn."""
    id: int


# ════════════════════════════════════════════════════════════════════════════════
#  RESOLVE FORWARD REFERENCES
#  Cần thiết vì BenhNhanDetailResponse, LichKhamDetailResponse,
#  PhieuKhamDetailResponse dùng forward reference ("...Response")
# ════════════════════════════════════════════════════════════════════════════════
BenhNhanDetailResponse.model_rebuild()
LichKhamDetailResponse.model_rebuild()
PhieuKhamDetailResponse.model_rebuild()