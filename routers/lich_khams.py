# routers/lich_khams.py
# API Router Quản lý và Điều phối Lịch khám (Phân hệ Lễ tân - FR-04 & UC-04)

from typing import List, Optional
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from pydantic import BaseModel

from database import get_db
import models
import schemas
from routers.auth import get_current_user, require_roles

router = APIRouter()


# ─── SCHEMAS ĐẦU VÀO ĐẶT LỊCH ─────────────────────────────────────────────
class LichKhamCreateInput(BaseModel):
    benh_nhan_id: int
    bac_si_id: Optional[int] = None
    chuyen_khoa_id: Optional[int] = None
    thoi_gian: datetime
    ly_do_kham: Optional[str] = None
    trang_thai: str = "cho_xac_nhan"


class LichKhamStatusUpdate(BaseModel):
    trang_thai: str  # cho_xac_nhan | da_dat_lich | cho_kham | dang_kham | hoan_thanh | huy


# ════════════════════════════════════════════════════════════════════════════════
#  ENDPOINTS LỊCH KHÁM
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_lich_khams(
    ngay_kham: Optional[str] = Query(None, description="Lọc theo ngày YYYY-MM-DD"),
    bac_si_id: Optional[int] = Query(None, description="Lọc theo ID bác sĩ"),
    trang_thai: Optional[str] = Query(None, description="Lọc theo trạng thái"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["le_tan", "bac_si", "admin"]))
):
    """
    GET /
    Lấy danh sách tất cả lịch khám trong hệ thống (Có bộ lọc Ngày, Bác sĩ, Trạng thái).
    """
    query = db.query(models.LichKham)

    if ngay_kham:
        try:
            target_date = datetime.strptime(ngay_kham, "%Y-%m-%d").date()
            query = query.filter(func.date(models.LichKham.thoi_gian) == target_date)
        except ValueError:
            pass

    if bac_si_id:
        query = query.filter(models.LichKham.bac_si_id == bac_si_id)

    if trang_thai:
        query = query.filter(models.LichKham.trang_thai == trang_thai)

    lich_khams = query.order_by(models.LichKham.thoi_gian.asc()).all()
    results = []

    for lk in lich_khams:
        benh_nhan = lk.benh_nhan
        
        # Tìm tên Bác sĩ
        ten_bac_si = "Chưa phân công"
        if lk.bac_si_id:
            doc_user = db.query(models.User).filter(models.User.id == lk.bac_si_id).first()
            if doc_user:
                doc_info = db.query(models.BacSi).filter(models.BacSi.user_id == doc_user.id).first()
                ten_bac_si = doc_info.ho_ten if doc_info else doc_user.username

        # Tìm Chuyên khoa
        ten_chuyen_khoa = "Khám tổng quát"
        if lk.chuyen_khoa_id:
            ck = db.query(models.ChuyenKhoa).filter(models.ChuyenKhoa.id == lk.chuyen_khoa_id).first()
            if ck:
                ten_chuyen_khoa = ck.ten_chuyen_khoa

        results.append({
            "id": lk.id,
            "stt": lk.stt,
            "benh_nhan_id": lk.benh_nhan_id,
            "ho_ten": benh_nhan.ho_ten if benh_nhan else "Bệnh nhân vô danh",
            "so_dien_thoai": benh_nhan.so_dien_thoai if benh_nhan else None,
            "ma_bhyt": benh_nhan.ma_bhyt if benh_nhan else None,
            "bac_si_id": lk.bac_si_id,
            "ten_bac_si": ten_bac_si,
            "chuyen_khoa_id": lk.chuyen_khoa_id,
            "ten_chuyen_khoa": ten_chuyen_khoa,
            "thoi_gian": lk.thoi_gian.strftime("%Y-%m-%d %H:%M"),
            "ly_do_kham": lk.ly_do_kham,
            "trang_thai": lk.trang_thai
        })

    return results


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_lich_kham(
    data: LichKhamCreateInput,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["le_tan", "admin"]))
):
    """
    POST /
    Đặt lịch khám mới (Yêu cầu FR-04 & UC-04).
    Kiểm tra xung đột lịch làm việc của Bác sĩ (Conflict Check) & trùng khung giờ khám của Bệnh nhân.
    """
    # 1. Kiểm tra Bệnh nhân tồn tại
    benh_nhan = db.query(models.BenhNhan).filter(models.BenhNhan.id == data.benh_nhan_id).first()
    if not benh_nhan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy Bệnh nhân có ID: {data.benh_nhan_id}"
        )

    # 2. Conflict Check: Kiểm tra Bác sĩ có bị trùng lịch hẹn trong khoảng +- 15 phút không
    if data.bac_si_id:
        start_range = data.thoi_gian - timedelta(minutes=15)
        end_range = data.thoi_gian + timedelta(minutes=15)

        doctor_conflict = db.query(models.LichKham).filter(
            models.LichKham.bac_si_id == data.bac_si_id,
            models.LichKham.thoi_gian >= start_range,
            models.LichKham.thoi_gian <= end_range,
            models.LichKham.trang_thai.in_(["da_dat_lich", "cho_kham", "dang_kham"])
        ).first()

        if doctor_conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Xung đột lịch khám: Bác sĩ đã có lịch hẹn lúc {doctor_conflict.thoi_gian.strftime('%H:%M %d/%m/%Y')}. Vui lòng chọn khung giờ khác!"
            )

    # 3. Trùng lịch của Bệnh nhân
    patient_conflict = db.query(models.LichKham).filter(
        models.LichKham.benh_nhan_id == data.benh_nhan_id,
        models.LichKham.thoi_gian == data.thoi_gian,
        models.LichKham.trang_thai.in_(["cho_xac_nhan", "da_dat_lich", "cho_kham", "dang_kham"])
    ).first()

    if patient_conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bệnh nhân đã có lịch hẹn trong cùng khung giờ này."
        )

    # 4. Lưu lịch khám
    new_lich_kham = models.LichKham(
        benh_nhan_id=data.benh_nhan_id,
        bac_si_id=data.bac_si_id,
        chuyen_khoa_id=data.chuyen_khoa_id,
        thoi_gian=data.thoi_gian,
        trang_thai=data.trang_thai,
        ly_do_kham=data.ly_do_kham
    )
    db.add(new_lich_kham)
    db.commit()
    db.refresh(new_lich_kham)

    # Log audit
    audit = models.AuditLog(
        user_id=current_user.id,
        action="CREATE",
        target_table="lich_khams",
        target_id=new_lich_kham.id,
        mo_ta=f"Lễ tân {current_user.username} đặt lịch khám #{new_lich_kham.id} cho BN {benh_nhan.ho_ten}"
    )
    db.add(audit)
    db.commit()

    return {
        "message": "Đặt lịch khám thành công!",
        "id": new_lich_kham.id,
        "benh_nhan_id": new_lich_kham.benh_nhan_id,
        "thoi_gian": new_lich_kham.thoi_gian.strftime("%Y-%m-%d %H:%M"),
        "trang_thai": new_lich_kham.trang_thai
    }


@router.put("/{lich_kham_id}/trang-thai")
def update_trang_thai_lich_kham(
    lich_kham_id: int,
    data: LichKhamStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["le_tan", "bac_si", "admin"]))
):
    """
    PUT /{lich_kham_id}/trang-thai
    Chuyển trạng thái lịch khám:
    Workflow: "cho_xac_nhan" -> "da_dat_lich" -> "cho_kham" (Đã tiếp nhận tại phòng khám) -> "dang_kham" -> "hoan_thanh" / "huy"
    Tự động sinh Số thứ tự (Queue Number) khi chuyển sang trạng thái "cho_kham"!
    """
    lich_kham = db.query(models.LichKham).filter(models.LichKham.id == lich_kham_id).first()
    if not lich_kham:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch khám!")

    new_status = data.trang_thai
    
    # Nếu chuyển sang "cho_kham" (Lễ tân tiếp nhận bệnh nhân có mặt tại phòng khám)
    # Tự động tính Số thứ tự (Queue STT) lớn nhất trong ngày của phòng khám
    if new_status == "cho_kham" and not lich_kham.stt:
        today_date = lich_kham.thoi_gian.date()
        max_stt = db.query(func.max(models.LichKham.stt)).filter(
            func.date(models.LichKham.thoi_gian) == today_date
        ).scalar() or 0
        lich_kham.stt = max_stt + 1

    lich_kham.trang_thai = new_status
    db.commit()
    db.refresh(lich_kham)

    audit = models.AuditLog(
        user_id=current_user.id,
        action="UPDATE",
        target_table="lich_khams",
        target_id=lich_kham.id,
        mo_ta=f"Chuyển trạng thái lịch khám #{lich_kham.id} sang '{new_status}' (STT: {lich_kham.stt})"
    )
    db.add(audit)
    db.commit()

    return {
        "message": f"Đã cập nhật trạng thái lịch khám sang '{new_status}'",
        "id": lich_kham.id,
        "stt": lich_kham.stt,
        "trang_thai": lich_kham.trang_thai
    }


@router.delete("/{lich_kham_id}")
def delete_lich_kham(
    lich_kham_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["le_tan", "admin"]))
):
    """
    DELETE /{lich_kham_id}
    Hủy / Xóa lịch khám bệnh.
    """
    lich_kham = db.query(models.LichKham).filter(models.LichKham.id == lich_kham_id).first()
    if not lich_kham:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch khám!")

    db.delete(lich_kham)
    db.commit()

    audit = models.AuditLog(
        user_id=current_user.id,
        action="DELETE",
        target_table="lich_khams",
        target_id=lich_kham_id,
        mo_ta=f"Xóa lịch khám #{lich_kham_id}"
    )
    db.add(audit)
    db.commit()

    return {"message": f"Đã xóa thành công lịch khám #{lich_kham_id}"}
