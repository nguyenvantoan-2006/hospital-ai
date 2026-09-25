# routers/phieu_khams.py
# Router quản lý Phiếu khám bệnh & Kê đơn thuốc điện tử cho FastAPI (FR-05, FR-06)

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db
import models
import schemas
from routers.auth import get_current_user, require_roles

router = APIRouter()


# ════════════════════════════════════════════════════════════════════════════════
#  1. API TÌM KIẾM THUỐC PHỤC VỤ KÊ ĐƠN (AUTOCOMPLETE CHO DEV 1)
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/thuocs/search", response_model=List[schemas.ThuocResponse], status_code=status.HTTP_200_OK)
def search_thuocs_for_prescription(
    q: Optional[str] = Query(None, description="Từ khóa tên thuốc"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    API tìm kiếm nhanh danh mục thuốc phục vụ Bác sĩ kê đơn (Autocomplete).
    Trả về ID, Tên thuốc, Đơn vị tính, Đơn giá và Số lượng tồn kho.
    """
    query = db.query(models.Thuoc)
    if q and q.strip():
        search_pattern = f"%{q.strip()}%"
        query = query.filter(models.Thuoc.ten_thuoc.ilike(search_pattern))
    
    thuocs = query.order_by(models.Thuoc.ten_thuoc.asc()).limit(limit).all()
    return thuocs


# ════════════════════════════════════════════════════════════════════════════════
#  2. API LẤY DANH SÁCH & CHI TIẾT PHIẾU KHÁM
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_phieu_khams(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách tất cả phiếu khám kèm thông tin bệnh nhân và bác sĩ.
    """
    phieu_khams = db.query(models.PhieuKham).order_by(models.PhieuKham.id.desc()).limit(limit).all()
    results = []
    for pk in phieu_khams:
        benh_nhan = pk.lich_kham.benh_nhan if pk.lich_kham else None
        bac_si = pk.lich_kham.bac_si if pk.lich_kham else None
        results.append({
            "id": pk.id,
            "lich_kham_id": pk.lich_kham_id,
            "benh_nhan_id": benh_nhan.id if benh_nhan else None,
            "benh_nhan_ho_ten": benh_nhan.ho_ten if benh_nhan else "N/A",
            "so_dien_thoai": benh_nhan.so_dien_thoai if benh_nhan else None,
            "bac_si_ho_ten": bac_si.username if bac_si else None,
            "trieu_chung": pk.trieu_chung,
            "chan_doan": pk.chan_doan,
            "ai_summary": pk.ai_summary,
            "huong_dan_sau_kham": pk.huong_dan_sau_kham,
            "so_luong_thuoc": len(pk.don_thuocs) if pk.don_thuocs else 0,
            "thoi_gian_kham": pk.lich_kham.thoi_gian if pk.lich_kham else None
        })
    return results


@router.get("/cho-thanh-toan", status_code=status.HTTP_200_OK)
def get_phieu_khams_cho_thanh_toan(db: Session = Depends(get_db)):
    """
    Lấy danh sách các phiếu khám đã hoàn tất bởi bác sĩ nhưng chưa thanh toán viện phí.
    """
    phieu_khams = db.query(models.PhieuKham).order_by(models.PhieuKham.id.desc()).all()
    danh_sach_cho = []

    for pk in phieu_khams:
        existing_hd = db.query(models.HoaDon).filter(
            models.HoaDon.phieu_kham_id == pk.id,
            models.HoaDon.trang_thai == "da_thanh_toan"
        ).first()

        if not existing_hd:
            tien_thuoc = sum((dt.so_luong * (dt.thuoc.don_gia if dt.thuoc else 0.0)) for dt in pk.don_thuocs)
            tien_kham = 100000.0  # Phí khám dịch vụ tiêu chuẩn
            tong_tien = tien_kham + tien_thuoc
            benh_nhan = pk.lich_kham.benh_nhan if pk.lich_kham else None

            chi_tiet_thuoc = []
            for dt in pk.don_thuocs:
                gia = dt.thuoc.don_gia if dt.thuoc else 0.0
                chi_tiet_thuoc.append({
                    "thuoc_id": dt.thuoc_id,
                    "ten_thuoc": dt.thuoc.ten_thuoc if dt.thuoc else "Thuốc",
                    "don_vi_tinh": dt.thuoc.don_vi_tinh if dt.thuoc else "viên",
                    "so_luong": dt.so_luong,
                    "don_gia": gia,
                    "thanh_tien": gia * dt.so_luong,
                    "lieu_dung": dt.lieu_dung or ""
                })

            danh_sach_cho.append({
                "phieu_kham_id": pk.id,
                "lich_kham_id": pk.lich_kham_id,
                "benh_nhan_id": benh_nhan.id if benh_nhan else None,
                "ho_ten": benh_nhan.ho_ten if benh_nhan else "Bệnh nhân vô danh",
                "so_dien_thoai": benh_nhan.so_dien_thoai if benh_nhan else None,
                "ma_bhyt": benh_nhan.ma_bhyt if benh_nhan else None,
                "trieu_chung": pk.trieu_chung,
                "chan_doan": pk.chan_doan,
                "huong_dan_sau_kham": pk.huong_dan_sau_kham,
                "tien_kham": tien_kham,
                "tien_thuoc": tien_thuoc,
                "tong_tien": tong_tien,
                "chi_tiet_thuoc": chi_tiet_thuoc
            })

    return danh_sach_cho


@router.get("/{id}", status_code=status.HTTP_200_OK)
def get_phieu_kham_by_id(id: int, db: Session = Depends(get_db)):
    """
    Xem chi tiết 1 phiếu khám theo ID (kèm thông tin đơn thuốc, hướng dẫn sau khám).
    """
    pk = db.query(models.PhieuKham).filter(models.PhieuKham.id == id).first()
    if not pk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy phiếu khám với ID: {id}"
        )

    benh_nhan = pk.lich_kham.benh_nhan if pk.lich_kham else None
    bac_si = pk.lich_kham.bac_si if pk.lich_kham else None

    chi_tiet_thuoc = []
    for dt in pk.don_thuocs:
        gia = dt.thuoc.don_gia if dt.thuoc else 0.0
        chi_tiet_thuoc.append({
            "id": dt.id,
            "thuoc_id": dt.thuoc_id,
            "ten_thuoc": dt.thuoc.ten_thuoc if dt.thuoc else "Thuốc",
            "don_vi_tinh": dt.thuoc.don_vi_tinh if dt.thuoc else "viên",
            "so_luong": dt.so_luong,
            "don_gia": gia,
            "thanh_tien": gia * dt.so_luong,
            "lieu_dung": dt.lieu_dung or ""
        })

    return {
        "id": pk.id,
        "lich_kham_id": pk.lich_kham_id,
        "benh_nhan": {
            "id": benh_nhan.id if benh_nhan else None,
            "ho_ten": benh_nhan.ho_ten if benh_nhan else "N/A",
            "ngay_sinh": str(benh_nhan.ngay_sinh) if benh_nhan and benh_nhan.ngay_sinh else None,
            "gioi_tinh": benh_nhan.gio_tinh if benh_nhan else None,
            "so_dien_thoai": benh_nhan.so_dien_thoai if benh_nhan else None,
            "dia_chi": benh_nhan.dia_chi if benh_nhan else None,
            "ma_bhyt": benh_nhan.ma_bhyt if benh_nhan else None,
            "tien_su_benh": benh_nhan.tien_su_benh if benh_nhan else None,
        } if benh_nhan else None,
        "bac_si": bac_si.username if bac_si else None,
        "trieu_chung": pk.trieu_chung,
        "chan_doan": pk.chan_doan,
        "ai_summary": pk.ai_summary,
        "huong_dan_sau_kham": pk.huong_dan_sau_kham,
        "don_thuocs": chi_tiet_thuoc,
        "thoi_gian_kham": pk.lich_kham.thoi_gian if pk.lich_kham else None
    }


# ════════════════════════════════════════════════════════════════════════════════
#  3. API TẠO PHIẾU KHÁM & KÊ ĐƠN THUỐC (FR-05 & FR-06)
# ════════════════════════════════════════════════════════════════════════════════

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_phieu_kham(data: schemas.PhieuKhamCreateInput, db: Session = Depends(get_db)):
    """
    Tạo mới phiếu khám bệnh kèm kê đơn thuốc điện tử (FR-05, FR-06).
    - Hỗ trợ truyền mảng don_thuocs: [{thuoc_id, so_luong, lieu_dung}].
    - Ràng buộc: Kiểm tra tồn kho, chặn kê vượt số lượng hiện có.
    - Tự động tạo Hóa đơn (chua_thanh_toan) và cập nhật Lịch khám thành hoan_thanh.
    """
    lich_kham_id = data.lich_kham_id

    # 1. Nếu chưa có lịch khám, tự động tạo 1 lịch khám cho bệnh nhân
    if not lich_kham_id:
        if not data.benh_nhan_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vui lòng chọn Bệnh nhân hoặc cung cấp lich_kham_id"
            )
        
        benh_nhan = db.query(models.BenhNhan).filter(models.BenhNhan.id == data.benh_nhan_id).first()
        if not benh_nhan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy bệnh nhân với ID: {data.benh_nhan_id}"
            )
        
        new_lich_kham = models.LichKham(
            benh_nhan_id=data.benh_nhan_id,
            thoi_gian=datetime.now(),
            trang_thai="hoan_thanh",
            ly_do_kham=data.trieu_chung or "Khám bệnh"
        )
        db.add(new_lich_kham)
        db.commit()
        db.refresh(new_lich_kham)
        lich_kham_id = new_lich_kham.id
    else:
        # Cập nhật trạng thái lịch khám hiện tại thành 'hoan_thanh'
        lich_kham = db.query(models.LichKham).filter(models.LichKham.id == lich_kham_id).first()
        if lich_kham:
            lich_kham.trang_thai = "hoan_thanh"
            db.commit()

    # 2. Kiểm tra nếu lịch khám này đã có phiếu khám trước đó
    existing_pk = db.query(models.PhieuKham).filter(models.PhieuKham.lich_kham_id == lich_kham_id).first()
    if existing_pk:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lịch khám ID {lich_kham_id} đã có phiếu khám ID {existing_pk.id} trước đó."
        )

    # 3. Ràng buộc kiểm tra số lượng tồn kho của các thuốc trong đơn (FR-06)
    don_thuoc_items = []
    tong_tien_thuoc = 0.0

    if data.don_thuocs:
        for item in data.don_thuocs:
            thuoc = db.query(models.Thuoc).filter(models.Thuoc.id == item.thuoc_id).first()
            if not thuoc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy thuốc với ID: {item.thuoc_id}"
                )
            
            # Kiểm tra số lượng kê so với tồn kho
            if item.so_luong <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Số lượng kê cho thuốc '{thuoc.ten_thuoc}' phải lớn hơn 0."
                )
            
            if item.so_luong > thuoc.so_luong_ton:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Thuốc '{thuoc.ten_thuoc}' chỉ còn tồn {thuoc.so_luong_ton} {thuoc.don_vi_tinh or 'đơn vị'}, "
                        f"không thể kê vượt quá số lượng tồn ({item.so_luong})."
                    )
                )

            don_thuoc_items.append({
                "thuoc": thuoc,
                "thuoc_id": item.thuoc_id,
                "so_luong": item.so_luong,
                "lieu_dung": item.lieu_dung
            })
            tong_tien_thuoc += (thuoc.don_gia * item.so_luong)

    # 4. Tạo PhieuKham mới
    new_phieu_kham = models.PhieuKham(
        lich_kham_id=lich_kham_id,
        trieu_chung=data.trieu_chung,
        chan_doan=data.chan_doan,
        ai_summary=data.ai_summary,
        huong_dan_sau_kham=data.huong_dan_sau_kham
    )
    db.add(new_phieu_kham)
    db.commit()
    db.refresh(new_phieu_kham)

    # 5. Lưu các dòng chi tiết DonThuoc
    for item in don_thuoc_items:
        new_dt = models.DonThuoc(
            phieu_kham_id=new_phieu_kham.id,
            thuoc_id=item["thuoc_id"],
            so_luong=item["so_luong"],
            lieu_dung=item["lieu_dung"]
        )
        db.add(new_dt)
    
    # 6. Tự động tạo Hóa Đơn ở trạng thái 'chua_thanh_toan'
    tien_kham_tieu_chuan = 100000.0
    tong_tien_hoa_don = tien_kham_tieu_chuan + tong_tien_thuoc
    new_hoa_don = models.HoaDon(
        phieu_kham_id=new_phieu_kham.id,
        tong_tien=tong_tien_hoa_don,
        trang_thai="chua_thanh_toan",
        hinh_thuc_tt="tien_mat",
        trang_thai_phat_thuoc="cho_lay_thuoc" if don_thuoc_items else "khong_co_thuoc"
    )
    db.add(new_hoa_don)
    db.commit()
    db.refresh(new_phieu_kham)

    return {
        "message": "Lập phiếu khám và kê đơn thuốc thành công",
        "phieu_kham_id": new_phieu_kham.id,
        "lich_kham_id": new_phieu_kham.lich_kham_id,
        "trieu_chung": new_phieu_kham.trieu_chung,
        "chan_doan": new_phieu_kham.chan_doan,
        "ai_summary": new_phieu_kham.ai_summary,
        "huong_dan_sau_kham": new_phieu_kham.huong_dan_sau_kham,
        "so_loai_thuoc": len(don_thuoc_items),
        "tong_tien_du_kien": tong_tien_hoa_don
    }


# ════════════════════════════════════════════════════════════════════════════════
#  4. API CẬP NHẬT / XÓA PHIẾU KHÁM
# ════════════════════════════════════════════════════════════════════════════════

@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_phieu_kham(id: int, data: schemas.PhieuKhamUpdate, db: Session = Depends(get_db)):
    """
    Cập nhật thông tin phiếu khám (triệu chứng, chẩn đoán, lời dặn sau khám).
    """
    pk = db.query(models.PhieuKham).filter(models.PhieuKham.id == id).first()
    if not pk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy phiếu khám với ID: {id}"
        )
    
    if data.trieu_chung is not None:
        pk.trieu_chung = data.trieu_chung
    if data.chan_doan is not None:
        pk.chan_doan = data.chan_doan
    if data.ai_summary is not None:
        pk.ai_summary = data.ai_summary
    if data.huong_dan_sau_kham is not None:
        pk.huong_dan_sau_kham = data.huong_dan_sau_kham

    db.commit()
    db.refresh(pk)
    return {
        "message": "Cập nhật phiếu khám thành công",
        "phieu_kham_id": pk.id,
        "chan_doan": pk.chan_doan,
        "huong_dan_sau_kham": pk.huong_dan_sau_kham
    }


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_phieu_kham(id: int, db: Session = Depends(get_db)):
    """
    Xóa phiếu khám (Chỉ được phép khi hóa đơn chưa thanh toán).
    """
    pk = db.query(models.PhieuKham).filter(models.PhieuKham.id == id).first()
    if not pk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy phiếu khám với ID: {id}"
        )
    
    # Kiểm tra hóa đơn
    if pk.hoa_don and pk.hoa_don.trang_thai == "da_thanh_toan":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phiếu khám này đã được thanh toán viện phí, không thể xóa."
        )

    db.delete(pk)
    db.commit()
    return {"message": f"Đã xóa thành công phiếu khám ID {id}"}
