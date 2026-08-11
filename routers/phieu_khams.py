# routers/phieu_khams.py
# Router quản lý Phiếu khám bệnh cho FastAPI

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
import models
import schemas

router = APIRouter()

# Schema bổ sung cho payload linh hoạt từ frontend (chấp nhận cả benh_nhan_id, bác sĩ, triệu chứng, chẩn đoán)
class PhieuKhamInput(BaseModel):
    benh_nhan_id: Optional[int] = None
    lich_kham_id: Optional[int] = None
    trieu_chung: Optional[str] = None
    chan_doan: Optional[str] = None
    bac_si: Optional[str] = None
    ai_summary: Optional[str] = None

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_phieu_khams(db: Session = Depends(get_db)):
    """
    Lấy danh sách tất cả phiếu khám.
    """
    phieu_khams = db.query(models.PhieuKham).all()
    return phieu_khams

@router.get("/cho-thanh-toan", status_code=status.HTTP_200_OK)
def get_phieu_khams_cho_thanh_toan(db: Session = Depends(get_db)):
    """
    Lấy danh sách các phiếu khám đã hoàn tất bởi bác sĩ nhưng chưa thanh toán viện phí.
    """
    phieu_khams = db.query(models.PhieuKham).all()
    danh_sach_cho = []

    for pk in phieu_khams:
        # Kiểm tra nếu chưa có hóa đơn thanh toán thành công
        existing_hd = db.query(models.HoaDon).filter(
            models.HoaDon.phieu_kham_id == pk.id,
            models.HoaDon.trang_thai == "da_thanh_toan"
        ).first()

        if not existing_hd:
            tien_thuoc = sum((dt.so_luong * (dt.thuoc.don_gia if dt.thuoc else 0.0)) for dt in pk.don_thuocs)
            tien_kham = 100000.0  # Phí khám dịch vụ mặc định
            tong_tien = tien_kham + tien_thuoc
            benh_nhan = pk.lich_kham.benh_nhan if pk.lich_kham else None

            chi_tiet_thuoc = []
            for dt in pk.don_thuocs:
                gia = dt.thuoc.don_gia if dt.thuoc else 0.0
                chi_tiet_thuoc.append({
                    "ten_thuoc": dt.thuoc.ten_thuoc if dt.thuoc else "Thuốc",
                    "so_luong": dt.so_luong,
                    "don_gia": gia,
                    "thanh_tien": gia * dt.so_luong
                })

            danh_sach_cho.append({
                "phieu_kham_id": pk.id,
                "benh_nhan_id": benh_nhan.id if benh_nhan else None,
                "ho_ten": benh_nhan.ho_ten if benh_nhan else "Bệnh nhân vô danh",
                "ma_bhyt": benh_nhan.ma_bhyt if benh_nhan else None,
                "trieu_chung": pk.trieu_chung,
                "chan_doan": pk.chan_doan,
                "tien_kham": tien_kham,
                "tien_thuoc": tien_thuoc,
                "tong_tien": tong_tien,
                "chi_tiet_thuoc": chi_tiet_thuoc
            })

    return danh_sach_cho

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_phieu_kham(data: PhieuKhamInput, db: Session = Depends(get_db)):
    """
    Tạo mới phiếu khám bệnh.
    Nếu không truyền lich_kham_id, tự động tạo 1 LichKham tương ứng cho bệnh nhân.
    """
    lich_kham_id = data.lich_kham_id

    # Nếu chưa có lịch khám, tự động tạo 1 lịch khám cho bệnh nhân
    if not lich_kham_id:
        if not data.benh_nhan_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vui lòng chọn Bệnh nhân hoặc cung cấp lich_kham_id"
            )
        
        # Kiểm tra bệnh nhân có tồn tại không
        benh_nhan = db.query(models.BenhNhan).filter(models.BenhNhan.id == data.benh_nhan_id).first()
        if not benh_nhan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy bệnh nhân với ID: {data.benh_nhan_id}"
            )
        
        # Tạo lịch khám tự động với trạng thái 'dang_kham'
        new_lich_kham = models.LichKham(
            benh_nhan_id=data.benh_nhan_id,
            thoi_gian=datetime.now(),
            trang_thai="dang_kham",
            ly_do_kham=data.trieu_chung or "Khám bệnh"
        )
        db.add(new_lich_kham)
        db.commit()
        db.refresh(new_lich_kham)
        lich_kham_id = new_lich_kham.id

    # Tạo PhieuKham mới
    new_phieu_kham = models.PhieuKham(
        lich_kham_id=lich_kham_id,
        trieu_chung=data.trieu_chung,
        chan_doan=data.chan_doan,
        ai_summary=data.ai_summary
    )
    db.add(new_phieu_kham)
    db.commit()
    db.refresh(new_phieu_kham)

    return {
        "message": "Tạo phiếu khám bệnh thành công",
        "phieu_kham_id": new_phieu_kham.id,
        "lich_kham_id": new_phieu_kham.lich_kham_id,
        "trieu_chung": new_phieu_kham.trieu_chung,
        "chan_doan": new_phieu_kham.chan_doan,
        "ai_summary": new_phieu_kham.ai_summary
    }
