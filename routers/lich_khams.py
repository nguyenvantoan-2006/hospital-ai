# routers/lich_khams.py
# Router quản lý Đặt lịch khám bệnh cho FastAPI

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
import models
import schemas

router = APIRouter()

# Schema Pydantic cho Đặt lịch khám
class LichKhamCreateInput(BaseModel):
    benh_nhan_id: int
    bac_si_id: Optional[int] = None
    thoi_gian: datetime
    ly_do_kham: Optional[str] = None
    trang_thai: str = "cho_kham"


@router.get("/", status_code=status.HTTP_200_OK)
def get_all_lich_khams(db: Session = Depends(get_db)):
    """
    Lấy danh sách tất cả lịch khám trong hệ thống.
    """
    lich_khams = db.query(models.LichKham).all()
    results = []
    for lk in lich_khams:
        benh_nhan = lk.benh_nhan
        results.append({
            "id": lk.id,
            "benh_nhan_id": lk.benh_nhan_id,
            "ho_ten": benh_nhan.ho_ten if benh_nhan else "Không xác định",
            "ma_bhyt": benh_nhan.ma_bhyt if benh_nhan else None,
            "thoi_gian": lk.thoi_gian.strftime("%Y-%m-%d %H:%M"),
            "ly_do_kham": lk.ly_do_kham,
            "trang_thai": lk.trang_thai
        })
    return results


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_lich_kham(data: LichKhamCreateInput, db: Session = Depends(get_db)):
    """
    Tạo lịch khám bệnh mới & kiểm tra trùng lịch.
    """
    # 1. Kiểm tra bệnh nhân có tồn tại không
    benh_nhan = db.query(models.BenhNhan).filter(models.BenhNhan.id == data.benh_nhan_id).first()
    if not benh_nhan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bệnh nhân có ID: {data.benh_nhan_id}"
        )

    # 2. Kiểm tra trùng lịch khám cùng khung giờ
    existing = db.query(models.LichKham).filter(
        models.LichKham.benh_nhan_id == data.benh_nhan_id,
        models.LichKham.thoi_gian == data.thoi_gian,
        models.LichKham.trang_thai.in_(["cho_kham", "dang_kham"])
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bệnh nhân đã có lịch khám vào khung giờ này!"
        )

    # 3. Tạo mới lịch khám
    new_lich_kham = models.LichKham(
        benh_nhan_id=data.benh_nhan_id,
        bac_si_id=data.bac_si_id,
        thoi_gian=data.thoi_gian,
        trang_thai=data.trang_thai,
        ly_do_kham=data.ly_do_kham
    )
    db.add(new_lich_kham)
    db.commit()
    db.refresh(new_lich_kham)

    return {
        "message": "Đặt lịch khám thành công!",
        "lich_kham_id": new_lich_kham.id,
        "benh_nhan_id": new_lich_kham.benh_nhan_id,
        "thoi_gian": new_lich_kham.thoi_gian.strftime("%Y-%m-%d %H:%M"),
        "trang_thai": new_lich_kham.trang_thai
    }
