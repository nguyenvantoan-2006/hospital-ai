# routers/benh_nhans.py
# API Router xử lý các request liên quan đến Quản lý Bệnh nhân

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
import crud

router = APIRouter()


# ════════════════════════════════════════════════════════════════════════════════
#  ENDPOINTS BỆNH NHÂN
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/", response_model=List[schemas.BenhNhanResponse])
def read_benh_nhans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    GET /
    Lấy danh sách tất cả bệnh nhân (có phân trang skip & limit).
    """
    benh_nhans = crud.get_benh_nhans(db, skip=skip, limit=limit)
    return benh_nhans


@router.post("/", response_model=schemas.BenhNhanResponse, status_code=status.HTTP_201_CREATED)
def create_new_benh_nhan(benh_nhan: schemas.BenhNhanCreate, db: Session = Depends(get_db)):
    """
    POST /
    Tạo mới một hồ sơ bệnh nhân.
    Kiểm tra trùng lặp mã BHYT nếu có.
    """
    if benh_nhan.ma_bhyt:
        existing_bhyt = db.query(models.BenhNhan).filter(models.BenhNhan.ma_bhyt == benh_nhan.ma_bhyt).first()
        if existing_bhyt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã BHYT này đã tồn tại trong hệ thống."
            )
    return crud.create_benh_nhan(db=db, benh_nhan=benh_nhan)


@router.get("/{benh_nhan_id}", response_model=schemas.BenhNhanDetailResponse)
def read_benh_nhan_detail(benh_nhan_id: int, db: Session = Depends(get_db)):
    """
    GET /{benh_nhan_id}
    Lấy thông tin chi tiết của 1 bệnh nhân theo ID (bao gồm cả danh sách lịch khám).
    """
    db_benh_nhan = crud.get_benh_nhan(db, benh_nhan_id=benh_nhan_id)
    if db_benh_nhan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bệnh nhân với ID: {benh_nhan_id}"
        )
    return db_benh_nhan
