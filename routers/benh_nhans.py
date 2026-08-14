# routers/benh_nhans.py
# API Router Quản lý Bệnh nhân (Phân hệ Lễ tân - FR-02 & UC-02)

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db
import models
import schemas
from routers.auth import get_current_user, require_roles

router = APIRouter()


# ════════════════════════════════════════════════════════════════════════════════
#  ENDPOINTS BỆNH NHÂN
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/", response_model=List[schemas.BenhNhanResponse])
def read_benh_nhans(
    q: Optional[str] = Query(None, description="Từ khóa tìm kiếm (Tên, SĐT, CCCD, BHYT)"),
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["le_tan", "bac_si", "admin"]))
):
    """
    GET /
    Lấy danh sách tất cả bệnh nhân có hỗ trợ tìm kiếm (Search Bar: Họ tên, Số điện thoại, CCCD, BHYT).
    """
    query = db.query(models.BenhNhan)

    if q and q.strip():
        search_str = f"%{q.strip()}%"
        query = query.filter(
            or_(
                models.BenhNhan.ho_ten.ilike(search_str),
                models.BenhNhan.so_dien_thoai.ilike(search_str),
                models.BenhNhan.cccd.ilike(search_str),
                models.BenhNhan.ma_bhyt.ilike(search_str)
            )
        )

    benh_nhans = query.order_by(models.BenhNhan.id.desc()).offset(skip).limit(limit).all()
    return benh_nhans


@router.post("/", response_model=schemas.BenhNhanResponse, status_code=status.HTTP_201_CREATED)
def create_new_benh_nhan(
    benh_nhan: schemas.BenhNhanCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["le_tan", "admin"]))
):
    """
    POST /
    Tạo mới hồ sơ bệnh nhân (Yêu cầu FR-02 & UC-02).
    Ràng buộc quan trọng: Tự động kiểm tra trùng lặp Số điện thoại, CCCD hoặc Mã BHYT trước khi tạo.
    """
    # 1. Kiểm tra trùng Số điện thoại
    if benh_nhan.so_dien_thoai and benh_nhan.so_dien_thoai.strip():
        existing_phone = db.query(models.BenhNhan).filter(
            models.BenhNhan.so_dien_thoai == benh_nhan.so_dien_thoai.strip()
        ).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Số điện thoại '{benh_nhan.so_dien_thoai}' đã tồn tại cho bệnh nhân '{existing_phone.ho_ten}' (ID: #{existing_phone.id})."
            )

    # 2. Kiểm tra trùng CCCD
    if benh_nhan.cccd and benh_nhan.cccd.strip():
        existing_cccd = db.query(models.BenhNhan).filter(
            models.BenhNhan.cccd == benh_nhan.cccd.strip()
        ).first()
        if existing_cccd:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Số CCCD '{benh_nhan.cccd}' đã tồn tại cho bệnh nhân '{existing_cccd.ho_ten}' (ID: #{existing_cccd.id})."
            )

    # 3. Kiểm tra trùng Mã BHYT
    if benh_nhan.ma_bhyt and benh_nhan.ma_bhyt.strip():
        existing_bhyt = db.query(models.BenhNhan).filter(
            models.BenhNhan.ma_bhyt == benh_nhan.ma_bhyt.strip()
        ).first()
        if existing_bhyt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mã BHYT '{benh_nhan.ma_bhyt}' đã tồn tại cho bệnh nhân '{existing_bhyt.ho_ten}' (ID: #{existing_bhyt.id})."
            )

    # 4. Lưu hồ sơ bệnh nhân vào Database
    new_benh_nhan = models.BenhNhan(
        user_id=benh_nhan.user_id,
        ho_ten=benh_nhan.ho_ten.strip(),
        ngay_sinh=benh_nhan.ngay_sinh,
        gio_tinh=benh_nhan.gio_tinh,
        so_dien_thoai=benh_nhan.so_dien_thoai.strip() if benh_nhan.so_dien_thoai else None,
        cccd=benh_nhan.cccd.strip() if benh_nhan.cccd else None,
        dia_chi=benh_nhan.dia_chi.strip() if benh_nhan.dia_chi else None,
        ma_bhyt=benh_nhan.ma_bhyt.strip() if benh_nhan.ma_bhyt else None,
        tien_su_benh=benh_nhan.tien_su_benh.strip() if benh_nhan.tien_su_benh else None
    )
    db.add(new_benh_nhan)
    db.commit()
    db.refresh(new_benh_nhan)

    # Ghi log Audit
    audit = models.AuditLog(
        user_id=current_user.id,
        action="CREATE",
        target_table="benh_nhans",
        target_id=new_benh_nhan.id,
        mo_ta=f"Lễ tân {current_user.username} thêm bệnh nhân mới: {new_benh_nhan.ho_ten}"
    )
    db.add(audit)
    db.commit()

    return new_benh_nhan


@router.get("/{benh_nhan_id}", response_model=schemas.BenhNhanDetailResponse)
def read_benh_nhan_detail(
    benh_nhan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["le_tan", "bac_si", "admin"]))
):
    """
    GET /{benh_nhan_id}
    Lấy thông tin chi tiết của 1 bệnh nhân theo ID (bao gồm cả lịch sử khám).
    """
    db_benh_nhan = db.query(models.BenhNhan).filter(models.BenhNhan.id == benh_nhan_id).first()
    if db_benh_nhan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bệnh nhân với ID: {benh_nhan_id}"
        )
    return db_benh_nhan


@router.put("/{benh_nhan_id}", response_model=schemas.BenhNhanResponse)
def update_benh_nhan(
    benh_nhan_id: int,
    data: schemas.BenhNhanUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["le_tan", "admin"]))
):
    """
    PUT /{benh_nhan_id}
    Cập nhật thông tin hồ sơ bệnh nhân.
    """
    db_benh_nhan = db.query(models.BenhNhan).filter(models.BenhNhan.id == benh_nhan_id).first()
    if not db_benh_nhan:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ bệnh nhân")

    # Kiểm tra trùng lặp nếu có cập nhật SĐT, CCCD, BHYT
    if data.so_dien_thoai and data.so_dien_thoai.strip() != db_benh_nhan.so_dien_thoai:
        dup = db.query(models.BenhNhan).filter(models.BenhNhan.so_dien_thoai == data.so_dien_thoai.strip(), models.BenhNhan.id != benh_nhan_id).first()
        if dup:
            raise HTTPException(status_code=400, detail="Số điện thoại này đã được sử dụng bởi bệnh nhân khác.")
        db_benh_nhan.so_dien_thoai = data.so_dien_thoai.strip()

    if data.cccd and data.cccd.strip() != db_benh_nhan.cccd:
        dup = db.query(models.BenhNhan).filter(models.BenhNhan.cccd == data.cccd.strip(), models.BenhNhan.id != benh_nhan_id).first()
        if dup:
            raise HTTPException(status_code=400, detail="Số CCCD này đã được sử dụng bởi bệnh nhân khác.")
        db_benh_nhan.cccd = data.cccd.strip()

    if data.ma_bhyt and data.ma_bhyt.strip() != db_benh_nhan.ma_bhyt:
        dup = db.query(models.BenhNhan).filter(models.BenhNhan.ma_bhyt == data.ma_bhyt.strip(), models.BenhNhan.id != benh_nhan_id).first()
        if dup:
            raise HTTPException(status_code=400, detail="Mã BHYT này đã được sử dụng bởi bệnh nhân khác.")
        db_benh_nhan.ma_bhyt = data.ma_bhyt.strip()

    if data.ho_ten: db_benh_nhan.ho_ten = data.ho_ten.strip()
    if data.ngay_sinh is not None: db_benh_nhan.ngay_sinh = data.ngay_sinh
    if data.gio_tinh: db_benh_nhan.gio_tinh = data.gio_tinh
    if data.dia_chi is not None: db_benh_nhan.dia_chi = data.dia_chi.strip()
    if data.tien_su_benh is not None: db_benh_nhan.tien_su_benh = data.tien_su_benh.strip()

    db.commit()
    db.refresh(db_benh_nhan)

    # Ghi log Audit
    audit = models.AuditLog(
        user_id=current_user.id,
        action="UPDATE",
        target_table="benh_nhans",
        target_id=db_benh_nhan.id,
        mo_ta=f"Cập nhật hồ sơ bệnh nhân #{db_benh_nhan.id} ({db_benh_nhan.ho_ten})"
    )
    db.add(audit)
    db.commit()

    return db_benh_nhan


@router.delete("/{benh_nhan_id}")
def delete_benh_nhan(
    benh_nhan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["le_tan", "admin"]))
):
    """
    DELETE /{benh_nhan_id}
    Xóa hồ sơ bệnh nhân khỏi hệ thống.
    """
    db_benh_nhan = db.query(models.BenhNhan).filter(models.BenhNhan.id == benh_nhan_id).first()
    if not db_benh_nhan:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ bệnh nhân")

    ho_ten = db_benh_nhan.ho_ten
    db.delete(db_benh_nhan)
    db.commit()

    audit = models.AuditLog(
        user_id=current_user.id,
        action="DELETE",
        target_table="benh_nhans",
        target_id=benh_nhan_id,
        mo_ta=f"Xóa hồ sơ bệnh nhân #{benh_nhan_id} ({ho_ten})"
    )
    db.add(audit)
    db.commit()

    return {"message": f"Đã xóa thành công bệnh nhân #{benh_nhan_id} ({ho_ten})"}
