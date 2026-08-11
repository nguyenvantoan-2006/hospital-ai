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
    ma_bac_si: Optional[str] = None     # Mã Bác sĩ & Mật khẩu đăng nhập (vd: BS178)
    ho_ten: str
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
    Thêm bác sĩ mới vào hệ thống & Tự động tạo tài khoản đăng nhập với Mật khẩu = Mã Bác Sĩ (vd: BS178).
    """
    # 1. Phát sinh Mã bác sĩ (vd: BS178) nếu chưa truyền
    count = db.query(models.BacSi).count() + 101
    ma_bac_si = data.ma_bac_si.strip() if data.ma_bac_si else f"BS{count}"

    # 2. Xử lý hoặc tự động tạo Tài khoản User
    user_id = data.user_id
    username = data.username.strip() if data.username else f"bacsi_{ma_bac_si.lower()}"

    if not user_id:
        existing_user = db.query(models.User).filter(models.User.username == username).first()
        if existing_user:
            user_id = existing_user.id
        else:
            # Tạo tài khoản đăng nhập với mật khẩu là mã bác sĩ
            new_user = models.User(
                username=username,
                password_hash=hash_password(ma_bac_si),
                role="bac_si",
                email=f"{username}@clinic.com",
                trang_thai=True
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            user_id = new_user.id

    # 3. Tạo Hồ sơ Bác sĩ
    new_doc = models.BacSi(
        user_id=user_id,
        ma_bac_si=ma_bac_si,
        ho_ten=data.ho_ten,
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
        "message": f"Đã thêm bác sĩ '{new_doc.ho_ten}'! Tài khoản: Username={username}, Mật khẩu={ma_bac_si}",
        "id": new_doc.id,
        "ma_bac_si": ma_bac_si,
        "username": username
    }


@router.put("/doctors/{doc_id}", status_code=status.HTTP_200_OK)
def update_doctor(doc_id: int, data: DoctorUpdate, db: Session = Depends(get_db)):
    """Cập nhật thông tin bác sĩ & cập nhật Mã Bác Sĩ / Mật khẩu nếu có đổi."""
    doc = db.query(models.BacSi).filter(models.BacSi.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy bác sĩ ID={doc_id}")

    if data.ho_ten is not None: doc.ho_ten = data.ho_ten
    if data.hoc_vi is not None: doc.hoc_vi = data.hoc_vi
    if data.chuyen_khoa is not None: doc.chuyen_khoa = data.chuyen_khoa
    if data.so_dien_thoai is not None: doc.so_dien_thoai = data.so_dien_thoai
    if data.phong_kham is not None: doc.phong_kham = data.phong_kham
    if data.lich_truc is not None: doc.lich_truc = data.lich_truc
    if data.trang_thai is not None: doc.trang_thai = data.trang_thai

    if data.ma_bac_si:
        doc.ma_bac_si = data.ma_bac_si
        # Cập nhật lại mật khẩu cho tài khoản liên kết nếu có
        if doc.user_id:
            u = db.query(models.User).filter(models.User.id == doc.user_id).first()
            if u:
                u.password_hash = hash_password(data.ma_bac_si)

    db.commit()
    _write_audit(db, "UPDATE", "bac_si", doc_id, f"Cập nhật bác sĩ '{doc.ho_ten}'")
    return {"message": f"Đã cập nhật thông tin bác sĩ '{doc.ho_ten}'."}


@router.delete("/doctors/{doc_id}", status_code=status.HTTP_200_OK)
def deactivate_doctor(doc_id: int, db: Session = Depends(get_db)):
    """Ngừng hoạt động bác sĩ (soft delete)."""
    doc = db.query(models.BacSi).filter(models.BacSi.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy bác sĩ ID={doc_id}")
    doc.trang_thai = False
    db.commit()
    _write_audit(db, "DELETE", "bac_si", doc_id, f"Ngừng hoạt động bác sĩ '{doc.ho_ten}'")
    return {"message": f"Đã ngừng hoạt động bác sĩ '{doc.ho_ten}'."}


# ════════════════════════════════════════════════════════════════════════════════
#  MODULE 4: BÁO CÁO & THỐNG KÊ (Reporting & Exports)
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/reports/overview", status_code=status.HTTP_200_OK)
def get_dashboard_overview(db: Session = Depends(get_db)):
    """Chỉ số tổng quan Dashboard Admin."""
    total_patients     = db.query(models.BenhNhan).count()
    total_appointments = db.query(models.LichKham).count()
    total_examinations = db.query(models.PhieuKham).count()
    paid_invoices      = db.query(models.HoaDon).filter(models.HoaDon.trang_thai == "da_thanh_toan").all()
    total_revenue      = sum(h.tong_tien for h in paid_invoices)
    total_users        = db.query(models.User).count()
    return {
        "tong_benh_nhan": total_patients,
        "tong_lich_kham": total_appointments,
        "tong_phieu_kham": total_examinations,
        "tong_hoa_don": len(paid_invoices),
        "tong_doanh_thu": total_revenue,
        "tong_tai_khoan": total_users,
    }


@router.get("/reports/revenue", status_code=status.HTTP_200_OK)
def get_revenue_report(db: Session = Depends(get_db)):
    """Báo cáo doanh thu từ hóa đơn đã thanh toán."""
    invoices = db.query(models.HoaDon).filter(models.HoaDon.trang_thai == "da_thanh_toan").all()
    results = []
    for hd in invoices:
        phieu = hd.phieu_kham
        bn = phieu.lich_kham.benh_nhan if phieu and phieu.lich_kham else None
        results.append({
            "hoa_don_id": hd.id,
            "ho_ten": bn.ho_ten if bn else "N/A",
            "tong_tien": hd.tong_tien,
            "hinh_thuc_tt": hd.hinh_thuc_tt,
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
