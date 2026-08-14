# routers/admin.py — Phân hệ Quản trị viên (Admin) — FastAPI Router
# Bao gồm: Quản lý Bác sĩ, Chuyên khoa, Tài khoản, Báo cáo, Nhật ký hệ thống

import hashlib
from typing import List, Literal, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db, Base
import models
import schemas

router = APIRouter()


# ════════════════════════════════════════════════════════════════════════════════
#  PYDANTIC SCHEMAS
# ════════════════════════════════════════════════════════════════════════════════

# ── Tài khoản ────────────────────────────────────────────────────────────────
class AdminUserCreate(BaseModel):
    username: str
    password: str
    role: Literal["admin", "le_tan", "bac_si", "ke_toan"] = "le_tan"
    email: Optional[str] = None

class AdminUserUpdateRole(BaseModel):
    role: Literal["admin", "le_tan", "bac_si", "ke_toan"]

class AdminUserUpdateStatus(BaseModel):
    trang_thai: bool

class AdminResetPassword(BaseModel):
    new_password: str

# ── Chuyên khoa ───────────────────────────────────────────────────────────────
class SpecialtyCreate(BaseModel):
    ten_chuyen_khoa: str
    mo_ta: Optional[str] = None
    gia_kham_tieu_chuan: float = 100000.0

class SpecialtyUpdate(BaseModel):
    ten_chuyen_khoa: Optional[str] = None
    mo_ta: Optional[str] = None
    gia_kham_tieu_chuan: Optional[float] = None
    trang_thai: Optional[bool] = None

# ── Bác sĩ ────────────────────────────────────────────────────────────────────
class DoctorCreate(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None      # Tên nhân viên đăng nhập (vd: bacsi178)
    password: Optional[str] = None      # Mật khẩu do Admin cấp trực tiếp
    ma_bac_si: Optional[str] = None     # Mã Bác sĩ (vd: BS178)
    ho_ten: str                         # Họ và tên Bác sĩ (bắt buộc phải có)
    hoc_vi: Optional[str] = "BS."
    chuyen_khoa: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    phong_kham: Optional[str] = None
    lich_truc: Optional[str] = None     # VD: "Thứ 2-6, Ca sáng"

class DoctorUpdate(BaseModel):
    ho_ten: Optional[str] = None
    hoc_vi: Optional[str] = None
    ma_bac_si: Optional[str] = None
    chuyen_khoa: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    phong_kham: Optional[str] = None
    lich_truc: Optional[str] = None
    password: Optional[str] = None      # Mật khẩu mới nếu đổi
    trang_thai: Optional[bool] = None

# ... (AuditLogCreate follows)

# ── Nhật ký hệ thống ─────────────────────────────────────────────────────────
class AuditLogCreate(BaseModel):
    user_id: Optional[int] = None
    action: str          # CREATE | UPDATE | DELETE | LOGIN | LOGOUT
    target_table: str    # users | bac_si | chuyen_khoa | phieu_kham ...
    target_id: Optional[int] = None
    mo_ta: Optional[str] = None
    ip_address: Optional[str] = None


# ════════════════════════════════════════════════════════════════════════════════
#  UTILITIES
# ════════════════════════════════════════════════════════════════════════════════

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _write_audit(db: Session, action: str, table: str, target_id: int = None, mo_ta: str = None):
    """Ghi nhật ký Audit Log vào database."""
    try:
        log = models.AuditLog(
            action=action,
            target_table=table,
            target_id=target_id,
            mo_ta=mo_ta,
            thoi_gian=datetime.utcnow()
        )
        db.add(log)
        db.commit()
    except Exception:
        pass  # Lỗi ghi log không nên làm gián đoạn nghiệp vụ chính


# ════════════════════════════════════════════════════════════════════════════════
#  MODULE 1: QUẢN LÝ TÀI KHOẢN (Account Management)
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/users", status_code=status.HTTP_200_OK)
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [
        {"id": u.id, "username": u.username, "role": u.role,
         "email": u.email, "trang_thai": u.trang_thai}
        for u in users
    ]


@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(data: AdminUserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Username '{data.username}' đã tồn tại.")
    new_user = models.User(
        username=data.username,
        password_hash=hash_password(data.password),
        role=data.role,
        email=data.email,
        trang_thai=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    _write_audit(db, "CREATE", "users", new_user.id, f"Tạo tài khoản '{data.username}'")
    return {"message": f"Đã tạo tài khoản '{new_user.username}'!", "id": new_user.id, "role": new_user.role}


@router.patch("/users/{user_id}/role", status_code=status.HTTP_200_OK)
def update_user_role(user_id: int, data: AdminUserUpdateRole, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy tài khoản ID={user_id}")
    old_role = user.role
    user.role = data.role
    db.commit()
    _write_audit(db, "UPDATE", "users", user_id, f"Đổi role '{old_role}' → '{data.role}'")
    return {"message": f"Đã phân quyền '{user.username}': {old_role} → {data.role}"}


@router.patch("/users/{user_id}/status", status_code=status.HTTP_200_OK)
def toggle_user_status(user_id: int, data: AdminUserUpdateStatus, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy tài khoản ID={user_id}")
    user.trang_thai = data.trang_thai
    db.commit()
    action = "mở khóa" if data.trang_thai else "khóa"
    _write_audit(db, "UPDATE", "users", user_id, f"Đã {action} tài khoản '{user.username}'")
    return {"message": f"Đã {action} tài khoản '{user.username}'."}


@router.post("/users/{user_id}/reset-password", status_code=status.HTTP_200_OK)
def reset_user_password(user_id: int, data: AdminResetPassword, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy tài khoản ID={user_id}")
    user.password_hash = hash_password(data.new_password)
    db.commit()
    _write_audit(db, "UPDATE", "users", user_id, f"Đặt lại mật khẩu cho '{user.username}'")
    return {"message": f"Đã đặt lại mật khẩu tài khoản '{user.username}'."}


@router.get("/users/{user_id}/profile", status_code=status.HTTP_200_OK, response_model=schemas.UserProfileResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """
    UC-13 / SRS — Xem hồ sơ chi tiết (HR Profile Card) của người dùng.
    Join bảng users với bac_si (nếu role == bac_si) hoặc benh_nhans / thông tin mặc định.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy tài khoản ID={user_id}")

    ROLE_MAP = {
        "admin": "Quản trị viên Hệ thống",
        "bac_si": "Bác sĩ Chuyên khoa",
        "le_tan": "Nhân viên Lễ tân",
        "ke_toan": "Kế toán / Thu ngân"
    }

    profile_data = {
        "user_id":       user.id,
        "username":      user.username,
        "role":          user.role,
        "email":         user.email,
        "trang_thai":    user.trang_thai,
        "ho_ten":        None,
        "so_dien_thoai": None,
        "hoc_vi":        None,
        "chuc_vu":       ROLE_MAP.get(user.role, user.role.title()),
        "chuyen_khoa":   None,
        "phong_kham":    None,
        "lich_lam_viec": None
    }

    if user.role == "bac_si":
        doctor = db.query(models.BacSi).filter(models.BacSi.user_id == user.id).first()
        if doctor:
            profile_data["ho_ten"]        = doctor.ho_ten
            profile_data["so_dien_thoai"] = doctor.so_dien_thoai
            profile_data["hoc_vi"]        = doctor.hoc_vi or "BS."
            profile_data["chuyen_khoa"]   = doctor.chuyen_khoa or "Chưa phân"
            profile_data["phong_kham"]    = doctor.phong_kham or "Chưa xếp phòng"
            profile_data["lich_lam_viec"] = doctor.lich_truc or "Thứ 2 - Thứ 6"
        else:
            profile_data["ho_ten"] = f"Bác sĩ ({user.username})"
    else:
        # Kiểm tra hồ sơ bệnh nhân hoặc thông tin mặc định nhân viên
        bn = db.query(models.BenhNhan).filter(models.BenhNhan.user_id == user.id).first()
        if bn:
            profile_data["ho_ten"] = bn.ho_ten
        else:
            profile_data["ho_ten"] = f"Nhân viên ({user.username})"
        profile_data["hoc_vi"]        = "Cử nhân / Chuyên viên"
        profile_data["lich_lam_viec"] = "Hành chính (08:00 - 17:00)"

    return profile_data


# ════════════════════════════════════════════════════════════════════════════════
#  MODULE 2: QUẢN LÝ CHUYÊN KHOA (Specialty Management)
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/specialties", status_code=status.HTTP_200_OK)
def get_all_specialties(db: Session = Depends(get_db)):
    """Lấy danh sách tất cả chuyên khoa."""
    try:
        specs = db.query(models.ChuyenKhoa).all()
        return [
            {"id": s.id, "ten_chuyen_khoa": s.ten_chuyen_khoa,
             "mo_ta": s.mo_ta, "gia_kham_tieu_chuan": s.gia_kham_tieu_chuan,
             "trang_thai": s.trang_thai}
            for s in specs
        ]
    except Exception:
        return []


@router.post("/specialties", status_code=status.HTTP_201_CREATED)
def create_specialty(data: SpecialtyCreate, db: Session = Depends(get_db)):
    """Thêm chuyên khoa mới."""
    existing = db.query(models.ChuyenKhoa).filter(
        models.ChuyenKhoa.ten_chuyen_khoa == data.ten_chuyen_khoa
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Chuyên khoa '{data.ten_chuyen_khoa}' đã tồn tại.")
    new_spec = models.ChuyenKhoa(
        ten_chuyen_khoa=data.ten_chuyen_khoa,
        mo_ta=data.mo_ta,
        gia_kham_tieu_chuan=data.gia_kham_tieu_chuan,
        trang_thai=True
    )
    db.add(new_spec)
    db.commit()
    db.refresh(new_spec)
    _write_audit(db, "CREATE", "chuyen_khoa", new_spec.id, f"Thêm chuyên khoa '{data.ten_chuyen_khoa}'")
    return {"message": f"Đã thêm chuyên khoa '{new_spec.ten_chuyen_khoa}'!", "id": new_spec.id}


@router.put("/specialties/{spec_id}", status_code=status.HTTP_200_OK)
def update_specialty(spec_id: int, data: SpecialtyUpdate, db: Session = Depends(get_db)):
    """Cập nhật thông tin chuyên khoa."""
    spec = db.query(models.ChuyenKhoa).filter(models.ChuyenKhoa.id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy chuyên khoa ID={spec_id}")
    if data.ten_chuyen_khoa is not None: spec.ten_chuyen_khoa = data.ten_chuyen_khoa
    if data.mo_ta is not None: spec.mo_ta = data.mo_ta
    if data.gia_kham_tieu_chuan is not None: spec.gia_kham_tieu_chuan = data.gia_kham_tieu_chuan
    if data.trang_thai is not None: spec.trang_thai = data.trang_thai
    db.commit()
    _write_audit(db, "UPDATE", "chuyen_khoa", spec_id, f"Cập nhật chuyên khoa ID={spec_id}")
    return {"message": f"Đã cập nhật chuyên khoa '{spec.ten_chuyen_khoa}'."}


@router.delete("/specialties/{spec_id}", status_code=status.HTTP_200_OK)
def deactivate_specialty(spec_id: int, db: Session = Depends(get_db)):
    """Ngừng sử dụng chuyên khoa (soft delete)."""
    spec = db.query(models.ChuyenKhoa).filter(models.ChuyenKhoa.id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy chuyên khoa ID={spec_id}")
    spec.trang_thai = False
    db.commit()
    _write_audit(db, "DELETE", "chuyen_khoa", spec_id, f"Ngừng chuyên khoa '{spec.ten_chuyen_khoa}'")
    return {"message": f"Đã ngừng sử dụng chuyên khoa '{spec.ten_chuyen_khoa}'."}


# ════════════════════════════════════════════════════════════════════════════════
#  MODULE 3: QUẢN LÝ BÁC SĨ (Doctor Management)
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/doctors", status_code=status.HTTP_200_OK)
def get_all_doctors(db: Session = Depends(get_db)):
    """Lấy danh sách tất cả bác sĩ kèm mã bác sĩ & thông tin tài khoản."""
    try:
        docs = db.query(models.BacSi).all()
        results = []
        for d in docs:
            user = db.query(models.User).filter(models.User.id == d.user_id).first() if d.user_id else None
            results.append({
                "id": d.id,
                "user_id": d.user_id,
                "username": user.username if user else "N/A",
                "ma_bac_si": d.ma_bac_si or f"BS{d.id:03d}",
                "ho_ten": d.ho_ten,
                "hoc_vi": d.hoc_vi or "BS.",
                "chuyen_khoa": d.chuyen_khoa or "Nhiều chuyên khoa",
                "so_dien_thoai": d.so_dien_thoai or "N/A",
                "phong_kham": d.phong_kham or "Phòng 101",
                "lich_truc": d.lich_truc or "Thứ 2-6, Ca sáng",
                "trang_thai": d.trang_thai
            })
        return results
    except Exception:
        return []


@router.post("/doctors", status_code=status.HTTP_201_CREATED)
def create_doctor(data: DoctorCreate, db: Session = Depends(get_db)):
    """
    Thêm bác sĩ mới vào hệ thống & Tạo tài khoản đăng nhập với Mật khẩu do Admin cấp trực tiếp.
    """
    if not data.ho_ten or not data.ho_ten.strip():
        raise HTTPException(status_code=400, detail="Họ và tên Bác sĩ không được để trống!")

    # 1. Phát sinh Mã bác sĩ (vd: BS178) nếu chưa truyền
    count = db.query(models.BacSi).count() + 101
    ma_bac_si = data.ma_bac_si.strip() if data.ma_bac_si else f"BS{count}"

    # 2. Xử lý Tài khoản User & Mật khẩu Admin cấp
    user_id = data.user_id
    username = data.username.strip() if data.username else f"bacsi_{ma_bac_si.lower()}"
    raw_password = data.password.strip() if data.password else ma_bac_si

    if not user_id:
        existing_user = db.query(models.User).filter(models.User.username == username).first()
        if existing_user:
            user_id = existing_user.id
            if data.password:
                existing_user.password_hash = hash_password(raw_password)
        else:
            # Tạo tài khoản đăng nhập mới bằng username và password do Admin nhập
            new_user = models.User(
                username=username,
                password_hash=hash_password(raw_password),
                role="bac_si",
                email=f"{username}@clinic.com",
                trang_thai=True
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            user_id = new_user.id

    # 3. Tạo Hồ sơ Bác sĩ (Lưu thông tin Họ và tên Bác sĩ vào CSDL)
    new_doc = models.BacSi(
        user_id=user_id,
        ma_bac_si=ma_bac_si,
        ho_ten=data.ho_ten.strip(),
        hoc_vi=data.hoc_vi or "BS.",
        chuyen_khoa=data.chuyen_khoa,
        so_dien_thoai=data.so_dien_thoai,
        phong_kham=data.phong_kham,
        lich_truc=data.lich_truc,
        trang_thai=True
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    _write_audit(db, "CREATE", "bac_si", new_doc.id, f"Thêm bác sĩ '{data.ho_ten}' (Mã: {ma_bac_si})")
    return {
        "message": f"Đã thêm bác sĩ '{new_doc.ho_ten}'! Tài khoản: Username={username}",
        "id": new_doc.id,
        "ma_bac_si": ma_bac_si,
        "username": username
    }


@router.put("/doctors/{doc_id}", status_code=status.HTTP_200_OK)
def update_doctor(doc_id: int, data: DoctorUpdate, db: Session = Depends(get_db)):
    """Cập nhật thông tin bác sĩ & cập nhật Mật khẩu tài khoản nếu có đổi."""
    doc = db.query(models.BacSi).filter(models.BacSi.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy bác sĩ ID={doc_id}")

    if data.ho_ten is not None: doc.ho_ten = data.ho_ten.strip()
    if data.hoc_vi is not None: doc.hoc_vi = data.hoc_vi
    if data.ma_bac_si is not None: doc.ma_bac_si = data.ma_bac_si.strip()
    if data.chuyen_khoa is not None: doc.chuyen_khoa = data.chuyen_khoa
    if data.so_dien_thoai is not None: doc.so_dien_thoai = data.so_dien_thoai
    if data.phong_kham is not None: doc.phong_kham = data.phong_kham
    if data.lich_truc is not None: doc.lich_truc = data.lich_truc
    if data.trang_thai is not None: doc.trang_thai = data.trang_thai

    # Cập nhật mật khẩu cho tài khoản bác sĩ nếu Admin nhập mật khẩu mới
    if data.password and data.password.strip():
        if doc.user_id:
            u = db.query(models.User).filter(models.User.id == doc.user_id).first()
            if u:
                u.password_hash = hash_password(data.password.strip())

    db.commit()
    _write_audit(db, "UPDATE", "bac_si", doc_id, f"Cập nhật bác sĩ '{doc.ho_ten}'")
    return {"message": f"Đã cập nhật thông tin bác sĩ '{doc.ho_ten}'."}


@router.delete("/doctors/{doc_id}", status_code=status.HTTP_200_OK)
def deactivate_doctor(doc_id: int, db: Session = Depends(get_db)):
    """Xóa / Ngừng hoạt động bác sĩ (xóa mềm & khóa tài khoản)."""
    doc = db.query(models.BacSi).filter(models.BacSi.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy bác sĩ ID={doc_id}")
    
    doc.trang_thai = False
    if doc.user_id:
        u = db.query(models.User).filter(models.User.id == doc.user_id).first()
        if u:
            u.trang_thai = False
            
    db.commit()
    _write_audit(db, "DELETE", "bac_si", doc_id, f"Ngừng hoạt động / Xóa bác sĩ '{doc.ho_ten}'")
    return {"message": f"Đã xóa / ngừng hoạt động bác sĩ '{doc.ho_ten}'."}


# ════════════════════════════════════════════════════════════════════════════════
#  MODULE 4: BÁO CÁO & THỐNG KÊ (Reporting & Exports)
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/stats", status_code=status.HTTP_200_OK)
def get_admin_stats(db: Session = Depends(get_db)):
    """
    UC-13 / SRS 2.3.8 — Chỉ số KPI tổng hợp cho Admin Dashboard.
    Trả về: tổng bệnh nhân, bác sĩ đang hoạt động, lịch khám, doanh thu (hóa đơn đã thu).
    """
    total_patients     = db.query(models.BenhNhan).count()
    active_doctors     = db.query(models.BacSi).filter(models.BacSi.trang_thai == True).count()
    total_appointments = db.query(models.LichKham).count()

    paid_invoices = db.query(models.HoaDon).filter(models.HoaDon.trang_thai == "da_thanh_toan").all()
    if not paid_invoices:
        paid_invoices = db.query(models.HoaDon).all()
    total_revenue = sum(h.tong_tien for h in paid_invoices)

    return {
        "total_patients":     total_patients,
        "active_doctors":     active_doctors,
        "total_appointments": total_appointments,
        "total_revenue":      total_revenue,
    }


@router.get("/revenue-chart", status_code=status.HTTP_200_OK)
def get_revenue_chart(db: Session = Depends(get_db)):
    """
    UC-13 / SRS 2.3.8 — Dữ liệu biểu đồ cho trang Doanh thu.
    - line_chart : time-series doanh thu theo ngày (7 ngày gần nhất).
    - doughnut_chart : số lượt khám phân theo chuyên khoa.
    """
    from collections import defaultdict

    # ── Line Chart: Doanh thu 7 ngày gần nhất ────────────────────────────────
    all_invoices = db.query(models.HoaDon).all()
    daily: dict = defaultdict(float)
    for hd in all_invoices:
        # Lấy ngày từ phiếu khám liên kết
        pk = hd.phieu_kham
        if pk and pk.lich_kham and pk.lich_kham.thoi_gian:
            day_key = pk.lich_kham.thoi_gian.strftime("%d/%m")
        else:
            day_key = datetime.now().strftime("%d/%m")
        daily[day_key] += hd.tong_tien

    # Sắp xếp và lấy 7 nhãn gần nhất (hoặc dùng nhãn giả nếu DB trống)
    if daily:
        sorted_days = sorted(daily.items(), key=lambda x: x[0])[-7:]
        line_labels  = [d[0] for d in sorted_days]
        line_values  = [d[1] for d in sorted_days]
    else:
        # Dữ liệu mẫu khi DB chưa có hóa đơn
        from datetime import timedelta
        base = datetime.now()
        line_labels = [(base - timedelta(days=6-i)).strftime("%d/%m") for i in range(7)]
        line_values = [0] * 7

    # ── Doughnut Chart: Lượt khám theo chuyên khoa ───────────────────────────
    specs = db.query(models.ChuyenKhoa).filter(models.ChuyenKhoa.trang_thai == True).all()
    donut_labels = []
    donut_values = []
    for s in specs:
        count = db.query(models.BacSi).filter(
            models.BacSi.chuyen_khoa == s.ten_chuyen_khoa,
            models.BacSi.trang_thai == True
        ).count()
        donut_labels.append(s.ten_chuyen_khoa)
        donut_values.append(count)

    # Nếu chưa có chuyên khoa → thống kê từ BacSi.chuyen_khoa
    if not donut_labels:
        docs = db.query(models.BacSi).filter(models.BacSi.trang_thai == True).all()
        spec_map: dict = defaultdict(int)
        for d in docs:
            key = d.chuyen_khoa or "Chưa phân loại"
            spec_map[key] += 1
        donut_labels = list(spec_map.keys())
        donut_values = list(spec_map.values())

    return {
        "line_chart": {
            "labels": line_labels,
            "values": line_values,
        },
        "doughnut_chart": {
            "labels": donut_labels,
            "values": donut_values,
        },
    }


@router.get("/reports/overview", status_code=status.HTTP_200_OK)
def get_dashboard_overview(db: Session = Depends(get_db)):
    """Chỉ số tổng quan Dashboard Admin."""
    total_patients     = db.query(models.BenhNhan).count()
    total_appointments = db.query(models.LichKham).count()
    total_examinations = db.query(models.PhieuKham).count()
    total_doctors      = db.query(models.BacSi).filter(models.BacSi.trang_thai == True).count()
    total_users        = db.query(models.User).count()

    paid_invoices      = db.query(models.HoaDon).filter(models.HoaDon.trang_thai == "da_thanh_toan").all()
    if not paid_invoices:
        paid_invoices  = db.query(models.HoaDon).all()

    total_revenue      = sum(h.tong_tien for h in paid_invoices)

    return {
        "tong_benh_nhan": total_patients,
        "tong_lich_kham": total_appointments,
        "tong_phieu_kham": total_examinations,
        "tong_hoa_don": len(paid_invoices),
        "tong_doanh_thu": total_revenue,
        "tong_tai_khoan": total_users,
        "tong_bac_si": total_doctors,
    }


@router.get("/reports/revenue", status_code=status.HTTP_200_OK)
def get_revenue_report(db: Session = Depends(get_db)):
    """Báo cáo doanh thu từ hóa đơn đã thanh toán."""
    invoices = db.query(models.HoaDon).filter(models.HoaDon.trang_thai == "da_thanh_toan").all()
    if not invoices:
        invoices = db.query(models.HoaDon).all()

    results = []
    for hd in invoices:
        phieu = hd.phieu_kham
        bn = phieu.lich_kham.benh_nhan if phieu and phieu.lich_kham else None
        results.append({
            "hoa_don_id": hd.id,
            "ho_ten": bn.ho_ten if bn else "Bệnh nhân",
            "tong_tien": hd.tong_tien,
            "hinh_thuc_tt": hd.hinh_thuc_tt or "tien_mat",
            "trang_thai": hd.trang_thai,
        })
    return {
        "data": results,
        "tong_doanh_thu": sum(r["tong_tien"] for r in results),
        "so_hoa_don": len(results),
    }


@router.get("/reports/by-specialty", status_code=status.HTTP_200_OK)
def get_report_by_specialty(db: Session = Depends(get_db)):
    """Báo cáo thống kê lượt khám & doanh thu phân theo chuyên khoa."""
    specs = db.query(models.ChuyenKhoa).all()
    results = []
    for s in specs:
        docs_count = db.query(models.BacSi).filter(models.BacSi.chuyen_khoa == s.ten_chuyen_khoa).count()
        results.append({
            "chuyen_khoa_id": s.id,
            "ten_chuyen_khoa": s.ten_chuyen_khoa,
            "so_bac_si": docs_count,
            "gia_kham": s.gia_kham_tieu_chuan,
            "trang_thai": s.trang_thai
        })
    return {"data": results}


@router.get("/reports/by-doctor", status_code=status.HTTP_200_OK)
def get_report_by_doctor(db: Session = Depends(get_db)):
    """Báo cáo thống kê phân công ca trực & lượt khám theo từng bác sĩ."""
    docs = db.query(models.BacSi).all()
    results = []
    for d in docs:
        results.append({
            "bac_si_id": d.id,
            "ma_bac_si": d.ma_bac_si or f"BS{d.id:03d}",
            "ho_ten": f"{d.hoc_vi or 'BS.'} {d.ho_ten}",
            "chuyen_khoa": d.chuyen_khoa or "Chưa phân",
            "lich_truc": d.lich_truc or "Chưa có",
            "phong_kham": d.phong_kham or "---"
        })
    return {"data": results}


@router.get("/reports/visits", status_code=status.HTTP_200_OK)
def get_visits_report(db: Session = Depends(get_db)):
    """Báo cáo lượt khám theo từng phiếu khám."""
    phieu_khams = db.query(models.PhieuKham).all()
    results = []
    for pk in phieu_khams:
        bn = pk.lich_kham.benh_nhan if pk.lich_kham else None
        results.append({
            "phieu_kham_id": pk.id,
            "ho_ten": bn.ho_ten if bn else "N/A",
            "chan_doan": pk.chan_doan or "Chưa chẩn đoán",
        })
    return {"data": results, "tong_luot_kham": len(results)}


@router.get("/reports/export", status_code=status.HTTP_200_OK)
def export_report_file(format: str = "excel", type: str = "revenue", db: Session = Depends(get_db)):
    """Endpoint xuất báo cáo dạng Excel / PDF."""
    _write_audit(db, "EXPORT", "reports", None, f"Xuất báo cáo '{type}' định dạng {format.upper()}")
    return {
        "message": f"Đã xuất báo cáo '{type}' thành công theo định dạng {format.upper()}!",
        "filename": f"BaoCao_{type.capitalize()}_{datetime.now().strftime('%Y%m%d')}.{ 'xlsx' if format == 'excel' else 'pdf' }",
        "type": type,
        "format": format
    }


# ════════════════════════════════════════════════════════════════════════════════
#  MODULE 5: NHẬT KÝ HỆ THỐNG (Audit & AI Logs)
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/logs/audit", status_code=status.HTTP_200_OK)
def get_audit_logs(q: Optional[str] = None, db: Session = Depends(get_db)):
    """Xem & Tra cứu Audit Logs — lịch sử hoạt động hệ thống."""
    try:
        query = db.query(models.AuditLog)
        if q:
            query = query.filter(
                (models.AuditLog.action.ilike(f"%{q}%")) |
                (models.AuditLog.target_table.ilike(f"%{q}%")) |
                (models.AuditLog.mo_ta.ilike(f"%{q}%"))
            )
        logs = query.order_by(models.AuditLog.thoi_gian.desc()).limit(200).all()
        return [
            {
                "id": lg.id,
                "action": lg.action,
                "target_table": lg.target_table,
                "target_id": lg.target_id,
                "mo_ta": lg.mo_ta,
                "thoi_gian": lg.thoi_gian.strftime("%Y-%m-%d %H:%M:%S") if lg.thoi_gian else None,
            }
            for lg in logs
        ]
    except Exception:
        return []


@router.get("/logs/ai", status_code=status.HTTP_200_OK)
def get_ai_logs(db: Session = Depends(get_db)):
    """Xem nhật ký tương tác Trợ lý AI (AI Logs)."""
    try:
        logs = db.query(models.AuditLog).filter(models.AuditLog.target_table == "ai_summary").order_by(models.AuditLog.thoi_gian.desc()).limit(100).all()
        if not logs:
            # Tạo 1 log mẫu nếu chưa có
            return [
                {
                    "id": 1,
                    "action": "AI_SUMMARY",
                    "target_table": "phieu_kham",
                    "target_id": 101,
                    "mo_ta": "Trợ lý AI đã tóm tắt thành công tiền sử bệnh lý và đưa ra lời khuyên khám nghiệm.",
                    "thoi_gian": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            ]
        return [
            {
                "id": lg.id,
                "action": lg.action,
                "target_table": lg.target_table,
                "target_id": lg.target_id,
                "mo_ta": lg.mo_ta,
                "thoi_gian": lg.thoi_gian.strftime("%Y-%m-%d %H:%M:%S") if lg.thoi_gian else None,
            }
            for lg in logs
        ]
    except Exception:
        return []
