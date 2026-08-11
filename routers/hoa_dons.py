# routers/hoa_dons.py
# Router quản lý Hóa đơn & Thanh toán viện phí cho FastAPI

from typing import List, Literal, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
import models
import schemas

router = APIRouter()

# ─── PYDANTIC SCHEMAS CHO INPUT ──────────────────────────────────────────────
class HoaDonCreateInput(BaseModel):
    phieu_kham_id: int
    hinh_thuc_tt: Literal["tien_mat", "chuyen_khoan", "qr"] = "tien_mat"
    tong_tien: Optional[float] = None
    trang_thai: Literal["da_thanh_toan", "chua_thanh_toan"] = "da_thanh_toan"


# ════════════════════════════════════════════════════════════════════════════════
#  ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_hoa_dons(db: Session = Depends(get_db)):
    """
    Lấy danh sách tất cả hóa đơn phục vụ kế toán thống kê doanh thu.
    """
    hoa_dons = db.query(models.HoaDon).all()
    results = []
    
    for hd in hoa_dons:
        phieu = hd.phieu_kham
        lich = phieu.lich_kham if phieu else None
        benh_nhan = lich.benh_nhan if lich else None

        results.append({
            "id": hd.id,
            "phieu_kham_id": hd.phieu_kham_id,
            "benh_nhan_ho_ten": benh_nhan.ho_ten if benh_nhan else "Không xác định",
            "ma_bhyt": benh_nhan.ma_bhyt if benh_nhan else None,
            "tong_tien": hd.tong_tien,
            "trang_thai": hd.trang_thai,
            "hinh_thuc_tt": hd.hinh_thuc_tt,
            "chan_doan": phieu.chan_doan if phieu else "",
        })
        
    return results


@router.get("/cho-thanh-toan", status_code=status.HTTP_200_OK)
def get_phieu_kham_cho_thanh_toan(db: Session = Depends(get_db)):
    """
    Lấy danh sách các phiếu khám chưa tạo hóa đơn hoặc chưa thanh toán.
    Tự động tính toán chi tiết tiền khám và tiền thuốc.
    """
    phieu_khams = db.query(models.PhieuKham).all()
    danh_sach_cho = []

    for pk in phieu_khams:
        # Kiểm tra xem phiếu khám này đã có hóa đơn thanh toán thành công chưa
        existing_hd = db.query(models.HoaDon).filter(
            models.HoaDon.phieu_kham_id == pk.id,
            models.HoaDon.trang_thai == "da_thanh_toan"
        ).first()

        if not existing_hd:
            # Tính tiền thuốc
            tien_thuoc = 0.0
            chi_tiet_thuoc = []
            for dt in pk.don_thuocs:
                gia = dt.thuoc.don_gia if dt.thuoc else 0.0
                thanh_tien = gia * dt.so_luong
                tien_thuoc += thanh_tien
                chi_tiet_thuoc.append({
                    "ten_thuoc": dt.thuoc.ten_thuoc if dt.thuoc else "Thuốc",
                    "so_luong": dt.so_luong,
                    "don_gia": gia,
                    "thanh_tien": thanh_tien
                })

            tien_kham = 100000.0  # Phí khám cố định (ví dụ)
            tong_tien = tien_kham + tien_thuoc

            benh_nhan = pk.lich_kham.benh_nhan if pk.lich_kham else None

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
def create_or_confirm_hoa_don(data: HoaDonCreateInput, db: Session = Depends(get_db)):
    """
    Tạo hoặc Xác nhận thanh toán hóa đơn cho phiếu khám (phieu_kham_id).
    """
    # 1. Kiểm tra phiếu khám có tồn tại không
    phieu_kham = db.query(models.PhieuKham).filter(models.PhieuKham.id == data.phieu_kham_id).first()
    if not phieu_kham:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy phiếu khám có ID: {data.phieu_kham_id}"
        )

    # 2. Tính tổng tiền nếu frontend không gửi lên
    tong_tien = data.tong_tien
    if tong_tien is None or tong_tien <= 0:
        tien_kham = 100000.0
        tien_thuoc = sum((dt.so_luong * (dt.thuoc.don_gia if dt.thuoc else 0.0)) for dt in phieu_kham.don_thuocs)
        tong_tien = tien_kham + tien_thuoc

    # 3. Kiểm tra xem đã có bản ghi Hóa đơn cho phiếu khám này chưa
    hoa_don = db.query(models.HoaDon).filter(models.HoaDon.phieu_kham_id == data.phieu_kham_id).first()

    if hoa_don:
        # Cập nhật hóa đơn hiện tại
        hoa_don.tong_tien = tong_tien
        hoa_don.trang_thai = data.trang_thai
        hoa_don.hinh_thuc_tt = data.hinh_thuc_tt
    else:
        # Tạo hóa đơn mới
        hoa_don = models.HoaDon(
            phieu_kham_id=data.phieu_kham_id,
            tong_tien=tong_tien,
            trang_thai=data.trang_thai,
            hinh_thuc_tt=data.hinh_thuc_tt
        )
        db.add(hoa_don)

    # Cập nhật trạng thái lịch khám thành hoàn thành nếu đã thanh toán
    if data.trang_thai == "da_thanh_toan" and phieu_kham.lich_kham:
        phieu_kham.lich_kham.trang_thai = "hoan_thanh"

    db.commit()
    db.refresh(hoa_don)

    return {
        "message": "Xác nhận thanh toán hóa đơn thành công!",
        "hoa_don_id": hoa_don.id,
        "phieu_kham_id": hoa_don.phieu_kham_id,
        "tong_tien": hoa_don.tong_tien,
        "hinh_thuc_tt": hoa_don.hinh_thuc_tt,
        "trang_thai": hoa_don.trang_thai
    }
