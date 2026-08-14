# models.py
# SQLAlchemy ORM Models cho Hệ thống Quản lý Phòng khám
# Tất cả các class kế thừa từ Base (database.py)
# ════════════════════════════════════════════════════════════════════════════════

from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import (
    Boolean, Column, DateTime, Date, Float,
    ForeignKey, Integer, String, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship

from database import Base


# ════════════════════════════════════════════════════════════════════════════════
#  1. USERS — Bảng tài khoản hệ thống
#     Role hợp lệ: 'admin' | 'le_tan' | 'bac_si' | 'ke_toan'
# ════════════════════════════════════════════════════════════════════════════════
class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(50),  unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role          = Column(String(20),  nullable=False)           # RBAC role
    email         = Column(String(100), unique=True, nullable=True)
    trang_thai    = Column(Boolean, default=True, nullable=False)  # True = active

    # Một User (bệnh nhân) có thể có nhiều hồ sơ BenhNhan
    benh_nhans = relationship(
        "BenhNhan",
        back_populates="user",
        foreign_keys="BenhNhan.user_id",
        cascade="all, delete-orphan",
    )

    # Một User (bác sĩ) có thể phụ trách nhiều LichKham
    lich_khams_bac_si = relationship(
        "LichKham",
        back_populates="bac_si",
        foreign_keys="LichKham.bac_si_id",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username='{self.username}' role='{self.role}'>"


# ════════════════════════════════════════════════════════════════════════════════
#  2. BENH_NHANS — Bảng hồ sơ bệnh nhân
# ════════════════════════════════════════════════════════════════════════════════
class BenhNhan(Base):
    __tablename__ = "benh_nhans"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    ho_ten       = Column(String(100), nullable=False)
    ngay_sinh    = Column(Date, nullable=True)
    gio_tinh     = Column(String(10), nullable=True) # Nam/Nữ/Khác
    so_dien_thoai = Column(String(20), nullable=True, index=True)
    cccd         = Column(String(20), unique=True, nullable=True, index=True)
    dia_chi      = Column(String(255), nullable=True)
    ma_bhyt      = Column(String(20), unique=True, nullable=True)
    tien_su_benh = Column(Text, nullable=True)  # Mô tả tự do, dùng Text

    # Quan hệ ngược về User (chủ hồ sơ)
    user = relationship(
        "User",
        back_populates="benh_nhans",
        foreign_keys=[user_id],
    )

    # Một BenhNhan có thể có nhiều LichKham
    lich_khams = relationship(
        "LichKham",
        back_populates="benh_nhan",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<BenhNhan id={self.id} ho_ten='{self.ho_ten}'>"


# ════════════════════════════════════════════════════════════════════════════════
#  3. LICH_KHAMS — Bảng lịch khám bệnh
#     trang_thai hợp lệ: 'cho_kham' | 'dang_kham' | 'hoan_thanh' | 'huy'
# ════════════════════════════════════════════════════════════════════════════════
class LichKham(Base):
    __tablename__ = "lich_khams"

    id              = Column(Integer, primary_key=True, index=True)
    benh_nhan_id    = Column(Integer, ForeignKey("benh_nhans.id", ondelete="CASCADE"), nullable=False)
    bac_si_id       = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    chuyen_khoa_id  = Column(Integer, ForeignKey("chuyen_khoa.id", ondelete="SET NULL"), nullable=True)
    stt             = Column(Integer, nullable=True) # Số thứ tự xếp hàng khám
    thoi_gian       = Column(DateTime, nullable=False)
    trang_thai      = Column(String(30), default="cho_xac_nhan", nullable=False) # cho_xac_nhan | da_dat_lich | cho_kham | dang_kham | hoan_thanh | huy
    ly_do_kham      = Column(Text, nullable=True)

    # Quan hệ ngược về BenhNhan
    benh_nhan = relationship(
        "BenhNhan",
        back_populates="lich_khams",
        foreign_keys=[benh_nhan_id],
    )

    # Quan hệ ngược về User (bác sĩ phụ trách)
    bac_si = relationship(
        "User",
        back_populates="lich_khams_bac_si",
        foreign_keys=[bac_si_id],
    )

    # Quan hệ 1-1: Một LichKham → Một PhieuKham (sau khi khám xong)
    phieu_kham = relationship(
        "PhieuKham",
        back_populates="lich_kham",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<LichKham id={self.id} benh_nhan_id={self.benh_nhan_id} trang_thai='{self.trang_thai}'>"


# ════════════════════════════════════════════════════════════════════════════════
#  4. PHIEU_KHAMS — Bảng phiếu khám (kết quả khám bệnh)
#     ai_summary: bản tóm tắt do AI sinh ra (Bảng chính của tính năng AI)
# ════════════════════════════════════════════════════════════════════════════════
class PhieuKham(Base):
    __tablename__ = "phieu_khams"

    id           = Column(Integer, primary_key=True, index=True)
    lich_kham_id = Column(
        Integer,
        ForeignKey("lich_khams.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # Đảm bảo quan hệ 1-1 ở cấp CSDL
    )
    trieu_chung  = Column(Text, nullable=True)  # Triệu chứng bệnh nhân mô tả
    chan_doan    = Column(Text, nullable=True)  # Chẩn đoán của bác sĩ
    ai_summary   = Column(Text, nullable=True)  # Tóm tắt do AI sinh ra

    # Quan hệ ngược về LichKham
    lich_kham = relationship(
        "LichKham",
        back_populates="phieu_kham",
        foreign_keys=[lich_kham_id],
    )

    # Một PhieuKham có thể có nhiều chi tiết DonThuoc
    don_thuocs = relationship(
        "DonThuoc",
        back_populates="phieu_kham",
        cascade="all, delete-orphan",
    )

    # Quan hệ 1-1: Một PhieuKham → Một HoaDon
    hoa_don = relationship(
        "HoaDon",
        back_populates="phieu_kham",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<PhieuKham id={self.id} lich_kham_id={self.lich_kham_id}>"


# ════════════════════════════════════════════════════════════════════════════════
#  5. THUOCS — Danh mục thuốc
# ════════════════════════════════════════════════════════════════════════════════
class Thuoc(Base):
    __tablename__ = "thuocs"

    id          = Column(Integer, primary_key=True, index=True)
    ten_thuoc   = Column(String(200), nullable=False, index=True)
    don_vi_tinh = Column(String(50),  nullable=True)   # Ví dụ: viên, chai, ống
    don_gia     = Column(Float,       nullable=False, default=0.0)

    # Một Thuoc có thể xuất hiện trong nhiều DonThuoc
    don_thuocs = relationship(
        "DonThuoc",
        back_populates="thuoc",
    )

    def __repr__(self) -> str:
        return f"<Thuoc id={self.id} ten_thuoc='{self.ten_thuoc}' don_gia={self.don_gia}>"


# ════════════════════════════════════════════════════════════════════════════════
#  6. DON_THUOCS — Chi tiết đơn thuốc (Bảng trung gian giữa PhieuKham và Thuoc)
# ════════════════════════════════════════════════════════════════════════════════
class DonThuoc(Base):
    __tablename__ = "don_thuocs"

    id           = Column(Integer, primary_key=True, index=True)
    phieu_kham_id = Column(Integer, ForeignKey("phieu_khams.id", ondelete="CASCADE"), nullable=False)
    thuoc_id      = Column(Integer, ForeignKey("thuocs.id",      ondelete="RESTRICT"), nullable=False)
    so_luong      = Column(Integer, nullable=False, default=1)
    lieu_dung     = Column(String(255), nullable=True)  # Ví dụ: "2 viên/ngày, sau ăn"

    # Ràng buộc: mỗi thuốc chỉ xuất hiện 1 lần trong 1 phiếu khám
    __table_args__ = (
        UniqueConstraint("phieu_kham_id", "thuoc_id", name="uq_don_thuoc_phieu_thuoc"),
    )

    # Quan hệ ngược về PhieuKham
    phieu_kham = relationship(
        "PhieuKham",
        back_populates="don_thuocs",
        foreign_keys=[phieu_kham_id],
    )

    # Quan hệ ngược về Thuoc
    thuoc = relationship(
        "Thuoc",
        back_populates="don_thuocs",
        foreign_keys=[thuoc_id],
    )

    def __repr__(self) -> str:
        return f"<DonThuoc id={self.id} phieu_kham_id={self.phieu_kham_id} thuoc_id={self.thuoc_id} so_luong={self.so_luong}>"


# ════════════════════════════════════════════════════════════════════════════════
#  7. HOA_DONS — Bảng hóa đơn thanh toán
#     trang_thai: 'chua_thanh_toan' | 'da_thanh_toan' | 'huy'
#     hinh_thuc_tt: 'tien_mat' | 'chuyen_khoan' | 'bao_hiem'
# ════════════════════════════════════════════════════════════════════════════════
class HoaDon(Base):
    __tablename__ = "hoa_dons"

    id            = Column(Integer, primary_key=True, index=True)
    phieu_kham_id = Column(
        Integer,
        ForeignKey("phieu_khams.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # Đảm bảo quan hệ 1-1 ở cấp CSDL
    )
    tong_tien     = Column(Float,      nullable=False, default=0.0)
    trang_thai    = Column(String(30), nullable=False, default="chua_thanh_toan")
    hinh_thuc_tt  = Column(String(30), nullable=True)   # Hình thức thanh toán

    # Quan hệ ngược về PhieuKham
    phieu_kham = relationship(
        "PhieuKham",
        back_populates="hoa_don",
        foreign_keys=[phieu_kham_id],
    )

    def __repr__(self) -> str:
        return f"<HoaDon id={self.id} phieu_kham_id={self.phieu_kham_id} tong_tien={self.tong_tien} trang_thai='{self.trang_thai}'>"


# ════════════════════════════════════════════════════════════════════════════════
#  8. BÁC SĨ — Danh mục bác sĩ phòng khám (Admin quản lý)
# ════════════════════════════════════════════════════════════════════════════════
class BacSi(Base):
    __tablename__ = "bac_si"

    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    ma_bac_si      = Column(String(50),  nullable=True, index=True) # Mã Bác Sĩ (vd: BS178)
    ho_ten         = Column(String(100), nullable=False)
    hoc_vi         = Column(String(50),  nullable=True, default="BS.")
    chuyen_khoa    = Column(String(100), nullable=True)
    so_dien_thoai  = Column(String(20),  nullable=True)
    phong_kham     = Column(String(100), nullable=True)
    lich_truc      = Column(String(200), nullable=True)   # VD: "Thứ 2-6 Ca sáng"
    trang_thai     = Column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<BacSi id={self.id} ma='{self.ma_bac_si}' ho_ten='{self.ho_ten}' chuyen_khoa='{self.chuyen_khoa}'>"


# ════════════════════════════════════════════════════════════════════════════════
#  9. CHUYÊN KHOA — Danh mục chuyên khoa (Admin quản lý)
# ════════════════════════════════════════════════════════════════════════════════
class ChuyenKhoa(Base):
    __tablename__ = "chuyen_khoa"

    id                  = Column(Integer, primary_key=True, index=True)
    ten_chuyen_khoa     = Column(String(100), unique=True, nullable=False)
    mo_ta               = Column(Text, nullable=True)
    gia_kham_tieu_chuan = Column(Float, default=100000.0)
    trang_thai          = Column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<ChuyenKhoa id={self.id} ten='{self.ten_chuyen_khoa}'>"


# ════════════════════════════════════════════════════════════════════════════════
#  10. AUDIT LOGS — Nhật ký hoạt động hệ thống
# ════════════════════════════════════════════════════════════════════════════════
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, nullable=True)
    action       = Column(String(50),  nullable=False)   # CREATE | UPDATE | DELETE | LOGIN
    target_table = Column(String(100), nullable=True)
    target_id    = Column(Integer, nullable=True)
    mo_ta        = Column(Text, nullable=True)
    ip_address   = Column(String(50), nullable=True)
    thoi_gian    = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action='{self.action}' table='{self.target_table}'>"
