# routers/ke_toan.py
# Router Quản lý Kế toán, Tài chính, Phát lương, Kho dược & Thống kê Ngày/Tháng/Quý

from typing import List, Optional, Literal
from datetime import datetime, date, timedelta
from io import StringIO
import csv

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from pydantic import BaseModel

from database import get_db
import models
import schemas

router = APIRouter()


# ════════════════════════════════════════════════════════════════════════════════
#  1. QUẢN LÝ VÀ PHÁT LƯƠNG NHÂN VIÊN (PAYROLL)
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/luong", response_model=List[schemas.BangLuongResponse])
def get_bang_luong(
    thang: Optional[int] = Query(None, ge=1, le=12),
    nam: Optional[int] = Query(None),
    trang_thai: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Lấy danh sách bảng lương theo bộ lọc tháng, năm, trạng thái."""
    current_year = nam or datetime.now().year
    current_month = thang or datetime.now().month

    query = db.query(models.BangLuong).filter(models.BangLuong.nam == current_year)
    if thang:
        query = query.filter(models.BangLuong.thang == thang)
    if trang_thai:
        query = query.filter(models.BangLuong.trang_thai == trang_thai)

    bang_luongs = query.order_by(models.BangLuong.thang.desc(), models.BangLuong.id.asc()).all()
    return bang_luongs


@router.post("/luong/khoi-tao")
def auto_generate_payroll(
    thang: int = Query(..., ge=1, le=12),
    nam: int = Query(...),
    db: Session = Depends(get_db)
):
    """
    Tự động lập bảng tính lương tháng cho toàn bộ nhân viên/bác sĩ trong hệ thống.
    Nếu nhân viên đã có bảng lương trong tháng đó sẽ bỏ qua.
    """
    users = db.query(models.User).filter(models.User.trang_thai == True).all()
    created_count = 0

    # Bảng mức lương cơ bản tiêu chuẩn theo vai trò
    base_salary_map = {
        "admin": 18000000.0,
        "bac_si": 22000000.0,
        "ke_toan": 12000000.0,
        "le_tan": 9500000.0
    }
    role_name_map = {
        "admin": "Quản trị viên",
        "bac_si": "Bác sĩ Chuyên khoa",
        "ke_toan": "Kế toán Tổng hợp",
        "le_tan": "Lễ tân Tiếp đón"
    }

    for u in users:
        # Kiểm tra nếu đã có bảng lương tháng này
        exist = db.query(models.BangLuong).filter(
            models.BangLuong.user_id == u.id,
            models.BangLuong.thang == thang,
            models.BangLuong.nam == nam
        ).first()

        if not exist:
            # Tìm họ tên bác sĩ nếu là bác sĩ
            full_name = u.username
            if u.role == "bac_si":
                doc = db.query(models.BacSi).filter(models.BacSi.user_id == u.id).first()
                if doc and doc.ho_ten:
                    full_name = f"{doc.hoc_vi or 'BS.'} {doc.ho_ten}"

            luong_cb = base_salary_map.get(u.role, 10000000.0)
            phu_cap = 1500000.0 if u.role == "bac_si" else 800000.0
            thuong = 1000000.0
            khau_tru = 500000.0  # BHXH, BHYT trích lương
            thuc_linh = luong_cb + phu_cap + thuong - khau_tru

            bl = models.BangLuong(
                user_id=u.id,
                ho_ten=full_name,
                chuc_vu=role_name_map.get(u.role, u.role),
                thang=thang,
                nam=nam,
                luong_co_ban=luong_cb,
                phu_cap=phu_cap,
                thuong=thuong,
                khau_tru=khau_tru,
                thuc_linh=thuc_linh,
                trang_thai="chua_chi",
                ghi_chu=f"Lương định kỳ tháng {thang}/{nam}"
            )
            db.add(bl)
            created_count += 1

    db.commit()
    return {
        "message": f"Đã khởi tạo bảng lương thành công cho tháng {thang}/{nam}!",
        "so_luong_tao_moi": created_count
    }


@router.post("/luong/{bang_luong_id}/chi-tra")
def pay_salary(
    bang_luong_id: int,
    payload: schemas.BangLuongChiTraInput,
    db: Session = Depends(get_db)
):
    """Xác nhận phát lương cho nhân viên."""
    bl = db.query(models.BangLuong).filter(models.BangLuong.id == bang_luong_id).first()
    if not bl:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi bảng lương.")

    bl.trang_thai = payload.trang_thai
    bl.ngay_tra = datetime.utcnow() if payload.trang_thai == "da_chi" else None
    if payload.ghi_chu:
        bl.ghi_chu = payload.ghi_chu

    db.commit()
    db.refresh(bl)

    # Ghi log hoạt động
    log = models.AuditLog(
        action="PAY_SALARY",
        target_table="bang_luong",
        target_id=bl.id,
        mo_ta=f"Kế toán đã phát lương tháng {bl.thang}/{bl.nam} cho {bl.ho_ten} số tiền {bl.thuc_linh:,.0f} VNĐ"
    )
    db.add(log)
    db.commit()

    return {
        "message": f"Đã xác nhận phát lương cho {bl.ho_ten} thành công!",
        "thuc_linh": bl.thuc_linh,
        "trang_thai": bl.trang_thai,
        "ngay_tra": bl.ngay_tra
    }


# ════════════════════════════════════════════════════════════════════════════════
#  2. QUẢN LÝ XUẤT NHẬP HÀNG HÓA & KHO DƯỢC
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/kho/ton-kho")
def get_inventory_status(db: Session = Depends(get_db)):
    """Lấy danh sách tồn kho thuốc, giá nhập, giá bán và giá trị hàng tồn."""
    thuocs = db.query(models.Thuoc).all()
    results = []
    tong_gia_tri_ton = 0.0

    for t in thuocs:
        gia_nhap = t.gia_nhap if t.gia_nhap and t.gia_nhap > 0 else round(t.don_gia * 0.7, 0)
        gia_tri_ton = (t.so_luong_ton or 0) * gia_nhap
        tong_gia_tri_ton += gia_tri_ton

        results.append({
            "id": t.id,
            "ten_thuoc": t.ten_thuoc,
            "don_vi_tinh": t.don_vi_tinh or "Đơn vị",
            "gia_nhap": gia_nhap,
            "don_gia_ban": t.don_gia,
            "so_luong_ton": t.so_luong_ton or 0,
            "gia_tri_ton_kho": gia_tri_ton,
            "canh_bao": "Sắp hết hàng" if (t.so_luong_ton or 0) < 20 else "Đủ hàng"
        })

    return {
        "data": results,
        "tong_mat_hang": len(results),
        "tong_gia_tri_ton_kho": tong_gia_tri_ton
    }


@router.post("/kho/nhap-kho")
def create_import_receipt(
    payload: schemas.PhieuNhapKhoCreate,
    db: Session = Depends(get_db)
):
    """
    Lập phiếu nhập kho thuốc từ nhà cung cấp:
    - Tự động sinh mã phiếu
    - Tăng số lượng tồn kho của từng thuốc
    - Cập nhật giá nhập mới nhất
    - Tính tổng giá trị vốn nhập hàng
    """
    if not payload.chi_tiets:
        raise HTTPException(status_code=400, detail="Phiếu nhập kho phải có ít nhất 1 mặt hàng.")

    # Sinh mã phiếu dạng PNK-YYYYMMDD-STT
    today_str = datetime.now().strftime("%Y%m%d")
    count_today = db.query(models.PhieuNhapKho).filter(
        func.date(models.PhieuNhapKho.ngay_nhap) == date.today()
    ).count()
    ma_phieu = f"PNK-{today_str}-{count_today + 1:03d}"

    phieu = models.PhieuNhapKho(
        ma_phieu=ma_phieu,
        nha_cung_cap=payload.nha_cung_cap,
        ngay_nhap=datetime.utcnow(),
        nguoi_nhap=payload.nguoi_nhap or "Kế toán kho",
        ghi_chu=payload.ghi_chu,
        tong_tien=0.0
    )
    db.add(phieu)
    db.flush()

    tong_tien = 0.0
    for item in payload.chi_tiets:
        thuoc = db.query(models.Thuoc).filter(models.Thuoc.id == item.thuoc_id).first()
        if not thuoc:
            continue

        thanh_tien = item.so_luong * item.don_gia_nhap
        tong_tien += thanh_tien

        # Cập nhật số lượng tồn kho và giá nhập
        thuoc.so_luong_ton = (thuoc.so_luong_ton or 0) + item.so_luong
        thuoc.gia_nhap = item.don_gia_nhap

        ct = models.ChiTietNhapKho(
            phieu_nhap_id=phieu.id,
            thuoc_id=thuoc.id,
            so_luong=item.so_luong,
            don_gia_nhap=item.don_gia_nhap,
            thanh_tien=thanh_tien
        )
        db.add(ct)

    phieu.tong_tien = tong_tien
    db.commit()

    return {
        "message": f"Nhập kho thành công phiếu {ma_phieu}!",
        "ma_phieu": ma_phieu,
        "tong_tien": tong_tien
    }


@router.get("/kho/lich-su-nhap")
def get_import_history(db: Session = Depends(get_db)):
    """Lấy danh sách các phiếu nhập kho đã thực hiện."""
    phieus = db.query(models.PhieuNhapKho).order_by(models.PhieuNhapKho.ngay_nhap.desc()).all()
    results = []
    for p in phieus:
        results.append({
            "id": p.id,
            "ma_phieu": p.ma_phieu,
            "nha_cung_cap": p.nha_cung_cap,
            "ngay_nhap": p.ngay_nhap.strftime("%Y-%m-%d %H:%M:%S") if p.ngay_nhap else None,
            "tong_tien": p.tong_tien,
            "nguoi_nhap": p.nguoi_nhap,
            "ghi_chu": p.ghi_chu,
            "so_mat_hang": len(p.chi_tiets)
        })
    return results


@router.get("/kho/bao-cao-xuat")
def get_medicine_export_report(db: Session = Depends(get_db)):
    """
    Thống kê doanh thu và chi phí xuất bán thuốc qua đơn khám bệnh.
    Doanh thu xuất = số lượng bán * đơn giá bán.
    Giá vốn xuất = số lượng bán * giá nhập.
    Lãi gộp thuốc = Doanh thu xuất - Giá vốn xuất.
    """
    don_thuocs = db.query(models.DonThuoc).join(models.PhieuKham).join(models.HoaDon).filter(
        models.HoaDon.trang_thai == "da_thanh_toan"
    ).all()

    from collections import defaultdict
    summary = defaultdict(lambda: {"so_luong_xuat": 0, "doanh_thu_xuat": 0.0, "gia_von": 0.0, "don_vi_tinh": ""})

    for dt in don_thuocs:
        if not dt.thuoc:
            continue
        t_name = dt.thuoc.ten_thuoc
        qty = dt.so_luong
        don_gia = dt.thuoc.don_gia
        gia_nhap = dt.thuoc.gia_nhap if dt.thuoc.gia_nhap and dt.thuoc.gia_nhap > 0 else don_gia * 0.7

        summary[t_name]["so_luong_xuat"] += qty
        summary[t_name]["doanh_thu_xuat"] += qty * don_gia
        summary[t_name]["gia_von"] += qty * gia_nhap
        summary[t_name]["don_vi_tinh"] = dt.thuoc.don_vi_tinh or "Đơn vị"

    report_list = []
    tong_doanh_thu = 0.0
    tong_gia_von = 0.0

    for ten, data in summary.items():
        lai = data["doanh_thu_xuat"] - data["gia_von"]
        tong_doanh_thu += data["doanh_thu_xuat"]
        tong_gia_von += data["gia_von"]
        report_list.append({
            "ten_thuoc": ten,
            "don_vi_tinh": data["don_vi_tinh"],
            "so_luong_xuat": data["so_luong_xuat"],
            "doanh_thu_xuat": data["doanh_thu_xuat"],
            "gia_von": data["gia_von"],
            "lai_gop": lai
        })

    return {
        "data": sorted(report_list, key=lambda x: x["doanh_thu_xuat"], reverse=True),
        "tong_doanh_thu_xuat": tong_doanh_thu,
        "tong_gia_von_xuat": tong_gia_von,
        "tong_lai_gop_thuoc": tong_doanh_thu - tong_gia_von
    }


# ════════════════════════════════════════════════════════════════════════════════
#  3. THỐNG KÊ DOANH THU ĐA CHIỀU (NGÀY / THÁNG / QUÝ) & BỆNH NHÂN
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/thong-ke")
def get_financial_summary(
    period: Literal["ngay", "thang", "quy", "nam"] = "quy",
    nam: Optional[int] = Query(None),
    thang: Optional[int] = Query(None, ge=1, le=12),
    quy: Optional[int] = Query(None, ge=1, le=4),
    ngay: Optional[str] = Query(None, description="Định dạng YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    Thống kê doanh thu toàn diện:
    - Theo Ngày (ngày cụ thể hoặc 7 ngày gần nhất)
    - Theo Tháng (tháng trong năm)
    - Theo Quý (Quý 1: T1-T3, Quý 2: T4-T6, Quý 3: T7-T9, Quý 4: T10-T12)
    - Theo Năm
    Tổng hợp: Tổng doanh thu khám, tiền thuốc, chi phí nhập hàng, chi lương và lợi nhuận ròng.
    """
    target_year = nam or datetime.now().year
    
    # ── 1. Lọc Hóa đơn đã thanh toán ──────────────────────────────────────────
    invoices = db.query(models.HoaDon).filter(models.HoaDon.trang_thai == "da_thanh_toan").all()
    if not invoices:
        invoices = db.query(models.HoaDon).all() # Fallback nếu chưa có hóa đơn thanh toán

    filtered_invoices = []
    for hd in invoices:
        # Lấy ngày của hóa đơn thông qua lịch khám
        hd_date = None
        if hd.phieu_kham and hd.phieu_kham.lich_kham and hd.phieu_kham.lich_kham.thoi_gian:
            hd_date = hd.phieu_kham.lich_kham.thoi_gian.date()
        else:
            hd_date = date.today()

        if hd_date.year != target_year:
            continue

        if period == "ngay" and ngay:
            try:
                target_d = datetime.strptime(ngay, "%Y-%m-%d").date()
                if hd_date != target_d:
                    continue
            except ValueError:
                pass
        elif period == "thang" and thang and isinstance(thang, int):
            if hd_date.month != thang:
                continue
        elif period == "quy" and quy and isinstance(quy, int):
            # Quý 1: 1, 2, 3 | Quý 2: 4, 5, 6 | Quý 3: 7, 8, 9 | Quý 4: 10, 11, 12
            quarter = (hd_date.month - 1) // 3 + 1
            if quarter != quy:
                continue

        filtered_invoices.append((hd, hd_date))

    # Tính toán doanh thu
    tong_doanh_thu = 0.0
    tong_tien_kham = 0.0
    tong_tien_thuoc = 0.0
    benh_nhan_ids = set()

    for hd, _ in filtered_invoices:
        tong_doanh_thu += hd.tong_tien
        pk = hd.phieu_kham
        if pk:
            # Tính tiền thuốc của phiếu
            t_thuoc = sum((dt.so_luong * (dt.thuoc.don_gia if dt.thuoc else 0.0)) for dt in pk.don_thuocs)
            t_kham = max(0.0, hd.tong_tien - t_thuoc)
            tong_tien_thuoc += t_thuoc
            tong_tien_kham += t_kham

            if pk.lich_kham and pk.lich_kham.benh_nhan_id:
                benh_nhan_ids.add(pk.lich_kham.benh_nhan_id)

    # ── 2. Lọc Chi phí Lương đã chi trả ───────────────────────────────────────
    query_luong = db.query(models.BangLuong).filter(
        models.BangLuong.nam == target_year,
        models.BangLuong.trang_thai == "da_chi"
    )
    if period == "thang" and thang and isinstance(thang, int):
        query_luong = query_luong.filter(models.BangLuong.thang == thang)
    elif period == "quy" and quy and isinstance(quy, int):
        start_m = (quy - 1) * 3 + 1
        end_m = start_m + 2
        query_luong = query_luong.filter(models.BangLuong.thang >= start_m, models.BangLuong.thang <= end_m)

    bang_luongs = query_luong.all()
    tong_chi_luong = sum(bl.thuc_linh for bl in bang_luongs)

    # ── 3. Lọc Chi phí Nhập Hàng Kho Dược ──────────────────────────────────────
    phieu_nhaps = db.query(models.PhieuNhapKho).all()
    tong_chi_nhap_hang = 0.0
    for pn in phieu_nhaps:
        pn_date = pn.ngay_nhap.date() if pn.ngay_nhap else date.today()
        if pn_date.year != target_year:
            continue
        if period == "thang" and thang and isinstance(thang, int) and pn_date.month != thang:
            continue
        if period == "quy" and quy and isinstance(quy, int):
            quarter = (pn_date.month - 1) // 3 + 1
            if quarter != quy:
                continue
        tong_chi_nhap_hang += pn.tong_tien

    # ── 4. Phân rã dữ liệu biểu đồ theo Quý (4 quý trong năm) ─────────────────
    quarters_data = [
        {"quy": 1, "ten": f"Quý 1/{target_year} (T1-T3)", "doanh_thu": 0.0, "chi_phi": 0.0, "loi_nhuan": 0.0},
        {"quy": 2, "ten": f"Quý 2/{target_year} (T4-T6)", "doanh_thu": 0.0, "chi_phi": 0.0, "loi_nhuan": 0.0},
        {"quy": 3, "ten": f"Quý 3/{target_year} (T7-T9)", "doanh_thu": 0.0, "chi_phi": 0.0, "loi_nhuan": 0.0},
        {"quy": 4, "ten": f"Quý 4/{target_year} (T10-T12)", "doanh_thu": 0.0, "chi_phi": 0.0, "loi_nhuan": 0.0},
    ]

    # Tính theo 4 quý của năm
    all_year_invoices = [
        hd for hd in invoices
        if (hd.phieu_kham and hd.phieu_kham.lich_kham and hd.phieu_kham.lich_kham.thoi_gian and hd.phieu_kham.lich_kham.thoi_gian.year == target_year)
    ]
    for hd in all_year_invoices:
        m = hd.phieu_kham.lich_kham.thoi_gian.month
        q_idx = (m - 1) // 3
        quarters_data[q_idx]["doanh_thu"] += hd.tong_tien

    for bl in db.query(models.BangLuong).filter(models.BangLuong.nam == target_year, models.BangLuong.trang_thai == "da_chi").all():
        q_idx = (bl.thang - 1) // 3
        if 0 <= q_idx < 4:
            quarters_data[q_idx]["chi_phi"] += bl.thuc_linh

    for qd in quarters_data:
        qd["loi_nhuan"] = qd["doanh_thu"] - qd["chi_phi"]

    # ── 5. Lợi nhuận ròng ─────────────────────────────────────────────────────
    tong_chi_phi = tong_chi_luong + tong_chi_nhap_hang
    loi_nhuan_rong = tong_doanh_thu - tong_chi_phi

    return {
        "tieu_chi": {
            "period": period,
            "nam": target_year,
            "thang": thang,
            "quy": quy,
            "ngay": ngay
        },
        "tong_quan": {
            "tong_doanh_thu": tong_doanh_thu,
            "tong_tien_kham": tong_tien_kham,
            "tong_tien_thuoc": tong_tien_thuoc,
            "so_hoa_don": len(filtered_invoices),
            "so_benh_nhan": len(benh_nhan_ids),
            "tong_chi_luong": tong_chi_luong,
            "tong_chi_nhap_hang": tong_chi_nhap_hang,
            "tong_chi_phi": tong_chi_phi,
            "loi_nhuan_rong": loi_nhuan_rong,
            "ty_suat_loi_nhuan": round((loi_nhuan_rong / tong_doanh_thu * 100), 1) if tong_doanh_thu > 0 else 0.0
        },
        "bieu_do_quy": quarters_data
    }


# ════════════════════════════════════════════════════════════════════════════════
#  4. XUẤT FILE BÁO CÁO THỰC TẾ (EXCEL/CSV CHUẨN UTF-8-BOM)
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/export")
def export_accounting_report(
    type: Literal["doanh_thu", "luong", "kho", "tong_hop"] = "doanh_thu",
    period: Literal["ngay", "thang", "quy", "nam"] = "quy",
    nam: Optional[int] = Query(None),
    quy: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Xuất file báo cáo tài chính thực tế dưới dạng CSV chuẩn UTF-8-BOM.
    Mở trực tiếp trên Microsoft Excel tiếng Việt không bị lỗi font chữ.
    """
    target_year = nam or datetime.now().year
    output = StringIO()
    
    # Ghi byte order mark (BOM) để Microsoft Excel nhận diện UTF-8 chuẩn
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)

    filename = f"BaoCao_{type}_{target_year}.csv"

    if type == "doanh_thu":
        filename = f"BaoCao_DoanhThu_BenhNhan_{target_year}.csv"
        writer.writerow(["MÃ HÓA ĐƠN", "HỌ TÊN BỆNH NHÂN", "MÃ BHYT", "NGÀY KHÁM", "CHẨN ĐOÁN", "TIỀN KHÁM (VNĐ)", "TIỀN THUỐC (VNĐ)", "TỔNG TIỀN (VNĐ)", "HÌNH THỨC TT", "TRẠNG THÁI"])
        
        invoices = db.query(models.HoaDon).all()
        for hd in invoices:
            pk = hd.phieu_kham
            lk = pk.lich_kham if pk else None
            bn = lk.benh_nhan if lk else None

            ngay_kham_str = lk.thoi_gian.strftime("%d/%m/%Y") if lk and lk.thoi_gian else datetime.now().strftime("%d/%m/%Y")
            t_thuoc = sum((dt.so_luong * (dt.thuoc.don_gia if dt.thuoc else 0.0)) for dt in pk.don_thuocs) if pk else 0.0
            t_kham = max(0.0, hd.tong_tien - t_thuoc)

            writer.writerow([
                f"HD{hd.id:04d}",
                bn.ho_ten if bn else "Khách vãng lai",
                bn.ma_bhyt if bn and bn.ma_bhyt else "---",
                ngay_kham_str,
                pk.chan_doan if pk and pk.chan_doan else "Khám sức khỏe",
                f"{t_kham:,.0f}",
                f"{t_thuoc:,.0f}",
                f"{hd.tong_tien:,.0f}",
                hd.hinh_thuc_tt or "tien_mat",
                "Đã thanh toán" if hd.trang_thai == "da_thanh_toan" else "Chưa thanh toán"
            ])

    elif type == "luong":
        filename = f"BaoCao_BangLuong_NhanVien_{target_year}.csv"
        writer.writerow(["MÃ BẢNG LƯƠNG", "HỌ VÀ TÊN", "CHỨC VỤ", "THÁNG/NĂM", "LƯƠNG CƠ BẢN", "PHỤ CẤP", "THƯỞNG", "KHẤU TRỪ", "THỰC LĨNH (VNĐ)", "TRẠNG THÁI", "NGÀY CHI TRẢ"])
        
        bang_luongs = db.query(models.BangLuong).filter(models.BangLuong.nam == target_year).all()
        for bl in bang_luongs:
            writer.writerow([
                f"BL{bl.id:04d}",
                bl.ho_ten,
                bl.chuc_vu,
                f"{bl.thang}/{bl.nam}",
                f"{bl.luong_co_ban:,.0f}",
                f"{bl.phu_cap:,.0f}",
                f"{bl.thuong:,.0f}",
                f"{bl.khau_tru:,.0f}",
                f"{bl.thuc_linh:,.0f}",
                "Đã phát lương" if bl.trang_thai == "da_chi" else "Chưa phát",
                bl.ngay_tra.strftime("%d/%m/%Y %H:%M") if bl.ngay_tra else "---"
            ])

    elif type == "kho":
        filename = f"BaoCao_KhoDuoc_TonKho_{target_year}.csv"
        writer.writerow(["MÃ THUỐC", "TÊN THUỐC / VẬT TƯ", "ĐƠN VỊ TÍNH", "GIÁ NHẬP VỐN (VNĐ)", "GIÁ BÁN LẺ (VNĐ)", "TỒN KHO", "GIÁ TRỊ TỒN KHO (VNĐ)", "CẢNH BÁO"])
        
        thuocs = db.query(models.Thuoc).all()
        for t in thuocs:
            gia_nhap = t.gia_nhap if t.gia_nhap and t.gia_nhap > 0 else round(t.don_gia * 0.7, 0)
            val = (t.so_luong_ton or 0) * gia_nhap
            writer.writerow([
                f"TH{t.id:03d}",
                t.ten_thuoc,
                t.don_vi_tinh or "Đơn vị",
                f"{gia_nhap:,.0f}",
                f"{t.don_gia:,.0f}",
                t.so_luong_ton or 0,
                f"{val:,.0f}",
                "Cần nhập thêm" if (t.so_luong_ton or 0) < 20 else "An toàn"
            ])

    elif type == "tong_hop":
        filename = f"BaoCao_TaiChinh_TheoQuy_{target_year}.csv"
        writer.writerow(["BÁO CÁO KẾT QUẢ TÀI CHÍNH THEO CÁC QUÝ TRONG NĂM", f"NĂM {target_year}"])
        writer.writerow([])
        writer.writerow(["DANH MỤC", "QUÝ 1 (T1-T3)", "QUÝ 2 (T4-T6)", "QUÝ 3 (T7-T9)", "QUÝ 4 (T10-T12)", f"CẢ NĂM {target_year}"])
        
        summary = get_financial_summary(period="quy", nam=target_year, db=db)
        bieu_do = summary["bieu_do_quy"]
        
        dt_row = ["1. Tổng Doanh Thu Viện Phí & Thuốc"] + [f"{q['doanh_thu']:,.0f}" for q in bieu_do] + [f"{sum(q['doanh_thu'] for q in bieu_do):,.0f}"]
        cp_row = ["2. Tổng Chi Phí Quỹ Lương & Hàng Hóa"] + [f"{q['chi_phi']:,.0f}" for q in bieu_do] + [f"{sum(q['chi_phi'] for q in bieu_do):,.0f}"]
        ln_row = ["3. LỢI NHUẬN RÒNG (LÃI THUẦN)"] + [f"{q['loi_nhuan']:,.0f}" for q in bieu_do] + [f"{sum(q['loi_nhuan'] for q in bieu_do):,.0f}"]
        
        writer.writerow(dt_row)
        writer.writerow(cp_row)
        writer.writerow(ln_row)

    output.seek(0)
    response = StreamingResponse(
        iter([output.getvalue().encode('utf-8')]),
        media_type="text/csv; charset=utf-8"
    )
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response
