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
                    "thuoc_id": dt.thuoc_id,
                    "ten_thuoc": dt.thuoc.ten_thuoc if dt.thuoc else "Thuốc",
                    "don_vi_tinh": dt.thuoc.don_vi_tinh if dt.thuoc else "viên",
                    "so_luong": dt.so_luong,
                    "don_gia": gia,
                    "thanh_tien": thanh_tien,
                    "lieu_dung": dt.lieu_dung or "Uống sau ăn",
                    "ton_kho": dt.thuoc.so_luong_ton if dt.thuoc else 0
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


# ════════════════════════════════════════════════════════════════════════════════
#  PHÂN HỆ QUẦY THUỐC & CẤP PHÁT THUỐC (PHARMACY & DISPENSING)
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/don-thuoc-cho-phat", status_code=status.HTTP_200_OK)
def get_don_thuoc_cho_phat(db: Session = Depends(get_db)):
    """
    Lấy danh sách tất cả các đơn thuốc bác sĩ đã kê, phục vụ Quầy Dược:
    - Quản lý thu tiền thuốc
    - Quản lý đóng gói và phát thuốc cho bệnh nhân
    - Hiển thị đầy đủ liều dùng, tồn kho và trạng thái
    """
    phieu_khams = db.query(models.PhieuKham).order_by(models.PhieuKham.id.desc()).all()
    results = []

    for pk in phieu_khams:
        # Chỉ lấy những phiếu khám có kê đơn thuốc (có ít nhất 1 loại thuốc)
        if not pk.don_thuocs or len(pk.don_thuocs) == 0:
            continue

        lich = pk.lich_kham
        benh_nhan = lich.benh_nhan if lich else None
        bac_si = lich.bac_si if lich else None
        hoa_don = pk.hoa_don

        # Tính toán chi tiết thuốc
        tien_thuoc = 0.0
        chi_tiet_thuoc = []
        for dt in pk.don_thuocs:
            don_gia = dt.thuoc.don_gia if dt.thuoc else 0.0
            thanh_tien = don_gia * dt.so_luong
            tien_thuoc += thanh_tien
            chi_tiet_thuoc.append({
                "thuoc_id": dt.thuoc_id,
                "ten_thuoc": dt.thuoc.ten_thuoc if dt.thuoc else "Thuốc",
                "don_vi_tinh": dt.thuoc.don_vi_tinh if dt.thuoc else "viên",
                "so_luong": dt.so_luong,
                "don_gia": don_gia,
                "thanh_tien": thanh_tien,
                "lieu_dung": dt.lieu_dung or "Theo hướng dẫn của bác sĩ",
                "ton_kho": dt.thuoc.so_luong_ton if dt.thuoc else 0
            })

        tien_kham = 100000.0
        tong_tien = tien_kham + tien_thuoc

        # Xác định trạng thái
        trang_thai_tt = hoa_don.trang_thai if hoa_don else "chua_thanh_toan"
        hinh_thuc_tt = hoa_don.hinh_thuc_tt if hoa_don else "tien_mat"
        trang_thai_phat = getattr(hoa_don, "trang_thai_phat_thuoc", "cho_lay_thuoc") if hoa_don else "cho_lay_thuoc"
        thoi_gian_phat = hoa_don.thoi_gian_phat_thuoc.strftime("%d/%m/%Y %H:%M") if (hoa_don and hoa_don.thoi_gian_phat_thuoc) else None
        duoc_si = hoa_don.duoc_si_phat if hoa_don else None
        ghi_chu = hoa_don.ghi_chu_phat if hoa_don else None

        doc_info = db.query(models.BacSi).filter(models.BacSi.user_id == bac_si.id).first() if bac_si else None
        ten_bac_si = f"{doc_info.hoc_vi or 'BS.'} {doc_info.ho_ten}" if doc_info else (bac_si.username if bac_si else "Bác sĩ Chuyên khoa")
        khoa_bac_si = doc_info.chuyen_khoa if doc_info else "Đa khoa"

        results.append({
            "phieu_kham_id": pk.id,
            "thoi_gian_kham": lich.thoi_gian.strftime("%d/%m/%Y %H:%M") if (lich and lich.thoi_gian) else "Hôm nay",
            "benh_nhan": {
                "id": benh_nhan.id if benh_nhan else None,
                "ho_ten": benh_nhan.ho_ten if benh_nhan else "Bệnh nhân vãng lai",
                "so_dien_thoai": benh_nhan.so_dien_thoai if benh_nhan else "---",
                "ngay_sinh": str(benh_nhan.ngay_sinh) if (benh_nhan and benh_nhan.ngay_sinh) else "---",
                "gioi_tinh": benh_nhan.gio_tinh if benh_nhan else "---",
                "ma_bhyt": benh_nhan.ma_bhyt if benh_nhan else "Không có",
                "dia_chi": benh_nhan.dia_chi if benh_nhan else "---"
            },
            "bac_si": {
                "id": bac_si.id if bac_si else None,
                "ho_ten": ten_bac_si,
                "chuyen_khoa": khoa_bac_si
            },
            "chan_doan": pk.chan_doan or "Khám lâm sàng tổng quát",
            "trieu_chung": pk.trieu_chung or "Không có",
            "ai_summary": pk.ai_summary or "",
            "so_loai_thuoc": len(chi_tiet_thuoc),
            "chi_tiet_thuoc": chi_tiet_thuoc,
            "tien_kham": tien_kham,
            "tien_thuoc": tien_thuoc,
            "tong_tien": tong_tien,
            "hoa_don_id": hoa_don.id if hoa_don else None,
            "trang_thai_thanh_toan": trang_thai_tt,
            "hinh_thuc_tt": hinh_thuc_tt,
            "trang_thai_phat_thuoc": trang_thai_phat,
            "thoi_gian_phat_thuoc": thoi_gian_phat,
            "duoc_si_phat": duoc_si,
            "ghi_chu_phat": ghi_chu
        })

    return results


@router.post("/xac-nhan-phat-thuoc", status_code=status.HTTP_200_OK)
def xac_nhan_phat_thuoc(data: schemas.XacNhanPhatThuocInput, db: Session = Depends(get_db)):
    """
    Xác nhận bệnh nhân đã lấy thuốc tại Quầy Dược:
    1. Kiểm tra tồn kho và tự động trừ tồn kho `so_luong_ton` trong bảng `thuocs`.
    2. Cập nhật hóa đơn sang 'da_thanh_toan' (nếu chưa thanh toán) và 'da_lay_thuoc'.
    3. Lưu lại thời gian phát và tên Dược sĩ phụ trách.
    """
    pk = db.query(models.PhieuKham).filter(models.PhieuKham.id == data.phieu_kham_id).first()
    if not pk:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy phiếu khám #{data.phieu_kham_id}")

    if not pk.don_thuocs or len(pk.don_thuocs) == 0:
        raise HTTPException(status_code=400, detail="Phiếu khám này không có đơn thuốc để phát!")

    # 1. Trừ kho dược phẩm
    thuoc_da_tru = []
    for dt in pk.don_thuocs:
        if dt.thuoc:
            sl_tru = dt.so_luong
            ton_cu = dt.thuoc.so_luong_ton
            ton_moi = max(0, ton_cu - sl_tru)
            dt.thuoc.so_luong_ton = ton_moi
            thuoc_da_tru.append({
                "ten_thuoc": dt.thuoc.ten_thuoc,
                "so_luong_phat": sl_tru,
                "ton_kho_con_lai": ton_moi
            })

    # 2. Cập nhật hoặc tạo hóa đơn
    hoa_don = pk.hoa_don
    tien_thuoc = sum((dt.so_luong * (dt.thuoc.don_gia if dt.thuoc else 0.0)) for dt in pk.don_thuocs)
    tien_kham = 100000.0
    tong_tien = tien_kham + tien_thuoc

    now = datetime.now()

    if not hoa_don:
        hoa_don = models.HoaDon(
            phieu_kham_id=pk.id,
            tong_tien=tong_tien,
            trang_thai="da_thanh_toan" if data.da_thanh_toan_ngay else "chua_thanh_toan",
            hinh_thuc_tt=data.hinh_thuc_tt,
            trang_thai_phat_thuoc="da_lay_thuoc",
            thoi_gian_phat_thuoc=now,
            duoc_si_phat=data.duoc_si_phat or "Dược sĩ Quầy Thuốc",
            ghi_chu_phat=data.ghi_chu_phat
        )
        db.add(hoa_don)
    else:
        if data.da_thanh_toan_ngay:
            hoa_don.trang_thai = "da_thanh_toan"
            hoa_don.hinh_thuc_tt = data.hinh_thuc_tt
        hoa_don.trang_thai_phat_thuoc = "da_lay_thuoc"
        hoa_don.thoi_gian_phat_thuoc = now
        hoa_don.duoc_si_phat = data.duoc_si_phat or "Dược sĩ Quầy Thuốc"
        if data.ghi_chu_phat:
            hoa_don.ghi_chu_phat = data.ghi_chu_phat

    if pk.lich_kham:
        pk.lich_kham.trang_thai = "hoan_thanh"

    db.commit()
    db.refresh(hoa_don)

    return {
        "message": "Đã phát thuốc cho bệnh nhân và trừ tồn kho dược thành công!",
        "phieu_kham_id": pk.id,
        "hoa_don_id": hoa_don.id,
        "tong_tien": hoa_don.tong_tien,
        "trang_thai_thanh_toan": hoa_don.trang_thai,
        "trang_thai_phat_thuoc": hoa_don.trang_thai_phat_thuoc,
        "thoi_gian_phat_thuoc": hoa_don.thoi_gian_phat_thuoc.strftime("%d/%m/%Y %H:%M"),
        "duoc_si_phat": hoa_don.duoc_si_phat,
        "chi_tiet_tru_kho": thuoc_da_tru
    }


@router.get("/don-thuoc/{phieu_kham_id}", status_code=status.HTTP_200_OK)
def get_chi_tiet_don_thuoc_in(phieu_kham_id: int, db: Session = Depends(get_db)):
    """
    Lấy thông tin chi tiết một đơn thuốc phục vụ In Hóa Đơn & Đơn Thuốc cho Bệnh nhân
    """
    pk = db.query(models.PhieuKham).filter(models.PhieuKham.id == phieu_kham_id).first()
    if not pk:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiếu khám")

    lich = pk.lich_kham
    bn = lich.benh_nhan if lich else None
    bs = lich.bac_si if lich else None
    hd = pk.hoa_don

    doc_info = db.query(models.BacSi).filter(models.BacSi.user_id == bs.id).first() if bs else None
    ten_bac_si = f"{doc_info.hoc_vi or 'BS.'} {doc_info.ho_ten}" if doc_info else (bs.username if bs else "Bác sĩ Chuyên khoa")
    khoa_bac_si = doc_info.chuyen_khoa if doc_info else "Đa khoa"

    ds_thuoc = []
    tien_thuoc = 0.0
    for dt in pk.don_thuocs:
        dg = dt.thuoc.don_gia if dt.thuoc else 0.0
        tt = dg * dt.so_luong
        tien_thuoc += tt
        ds_thuoc.append({
            "ten_thuoc": dt.thuoc.ten_thuoc if dt.thuoc else "Thuốc",
            "don_vi_tinh": dt.thuoc.don_vi_tinh if dt.thuoc else "viên",
            "so_luong": dt.so_luong,
            "don_gia": dg,
            "thanh_tien": tt,
            "lieu_dung": dt.lieu_dung or "Theo chỉ định"
        })

    return {
        "phieu_kham_id": pk.id,
        "ngay_kham": lich.thoi_gian.strftime("%d/%m/%Y %H:%M") if (lich and lich.thoi_gian) else "",
        "benh_nhan": {
            "ho_ten": bn.ho_ten if bn else "---",
            "so_dien_thoai": bn.so_dien_thoai if bn else "---",
            "ngay_sinh": str(bn.ngay_sinh) if (bn and bn.ngay_sinh) else "---",
            "gioi_tinh": bn.gio_tinh if bn else "---",
            "ma_bhyt": bn.ma_bhyt if bn else "---",
            "dia_chi": bn.dia_chi if bn else "---"
        },
        "bac_si": {
            "ho_ten": ten_bac_si,
            "chuyen_khoa": khoa_bac_si
        },
        "chan_doan": pk.chan_doan or "---",
        "trieu_chung": pk.trieu_chung or "---",
        "loi_dan": "Uống thuốc đúng liều, tái khám theo chỉ định của bác sĩ.",
        "chi_tiet_thuoc": ds_thuoc,
        "tien_kham": 100000.0,
        "tien_thuoc": tien_thuoc,
        "tong_cong": 100000.0 + tien_thuoc,
        "trang_thai_thanh_toan": hd.trang_thai if hd else "chua_thanh_toan",
        "trang_thai_phat_thuoc": getattr(hd, "trang_thai_phat_thuoc", "cho_lay_thuoc") if hd else "cho_lay_thuoc",
        "duoc_si": hd.duoc_si_phat if hd else "Dược sĩ Quầy Thuốc"
    }

