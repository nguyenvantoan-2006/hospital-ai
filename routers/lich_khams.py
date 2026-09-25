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


from email_service import (
    save_otp, verify_stored_otp,
    send_booking_otp_email, send_booking_confirmation_email,
    check_otp_rate_limit
)
import random


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


class LichKhamAssignDoctorInput(BaseModel):
    bac_si_id: int
    phong_kham: Optional[str] = None


class ChuyenPhongInput(BaseModel):
    lich_kham_hien_tai_id: int
    phong_kham_dich: str
    chuyen_khoa_dich_id: Optional[int] = None
    bac_si_dich_id: Optional[int] = None
    chi_dinh_dich_vu: str
    ghi_chu: Optional[str] = None


class TraKetQuaCLSInput(BaseModel):
    lich_kham_cls_id: int
    ket_qua_chi_tiet: str
    ket_luan: str
    ghi_chu: Optional[str] = None


class PatientSendOtpInput(BaseModel):
    email: str
    ho_ten: str
    sdt: str
    ngay_sinh: Optional[str] = None
    gioi_tinh: Optional[str] = None
    chuyen_khoa: Optional[str] = None
    chuyen_khoa_id: Optional[int] = None
    bac_si: Optional[str] = None
    bac_si_id: Optional[int] = None
    thoi_gian: Optional[str] = None
    ly_do_kham: Optional[str] = None


class PatientVerifyOtpAndBookInput(BaseModel):
    email: str
    otp: str
    ho_ten: str
    sdt: str
    ngay_sinh: Optional[str] = None
    gioi_tinh: Optional[str] = None
    cccd: Optional[str] = None
    bhyt: Optional[str] = None
    chuyen_khoa: Optional[str] = None
    chuyen_khoa_id: Optional[int] = None
    bac_si: Optional[str] = None
    bac_si_id: Optional[int] = None
    thoi_gian: str
    ly_do_kham: Optional[str] = None


# ════════════════════════════════════════════════════════════════════════════════
#  ENDPOINTS CÔNG KHAI DÀNH CHO BỆNH NHÂN (KHÔNG CẦN ĐĂNG NHẬP)
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/public/doctors", status_code=status.HTTP_200_OK)
def get_public_doctors(
    chuyen_khoa: Optional[str] = Query(None, description="Lọc theo tên chuyên khoa"),
    db: Session = Depends(get_db)
):
    """
    API công khai cho bệnh nhân: Lấy danh sách bác sĩ để chọn khi đặt lịch.
    Có thể lọc theo chuyên khoa (mỗi chuyên khoa có 5 bác sĩ).
    """
    query = db.query(models.BacSi).filter(models.BacSi.trang_thai == True)
    if chuyen_khoa and chuyen_khoa.strip():
        clean_name = chuyen_khoa.strip()
        query = query.filter(models.BacSi.chuyen_khoa == clean_name)
    
    docs = query.all()
    return [
        {
            "id": d.id,
            "user_id": d.user_id,
            "ma_bac_si": d.ma_bac_si,
            "ho_ten": d.ho_ten,
            "hoc_vi": d.hoc_vi or "BS.",
            "chuyen_khoa": d.chuyen_khoa,
            "phong_kham": d.phong_kham,
            "lich_truc": d.lich_truc,
            "so_dien_thoai": d.so_dien_thoai
        }
        for d in docs
    ]


@router.get("/public/phong-khams", status_code=status.HTTP_200_OK)
def get_public_phong_khams(db: Session = Depends(get_db)):
    """
    Danh sách toàn bộ các phòng khám & phòng cận lâm sàng trong bệnh viện:
    - Phòng khám chuyên khoa (có bác sĩ phụ trách)
    - Phòng cận lâm sàng (X-Quang, Xét nghiệm, Siêu âm, Nội soi...)
    """
    docs = db.query(models.BacSi).filter(models.BacSi.trang_thai == True).all()
    rooms_map = {}
    for d in docs:
        if d.phong_kham:
            room_clean = d.phong_kham.strip()
            if room_clean not in rooms_map:
                rooms_map[room_clean] = {
                    "phong_kham": room_clean,
                    "chuyen_khoa": d.chuyen_khoa or "Đa khoa",
                    "bac_si_id": d.id,
                    "user_id": d.user_id,
                    "bac_si_ho_ten": f"{d.hoc_vi or 'BS.'} {d.ho_ten}",
                    "loai_phong": "kham_chuyen_khoa",
                    "vi_tri": "Tầng 1 - Khu Khám Bệnh" if "1" in room_clean else "Tầng 2 - Khu Chuyên Khoa"
                }

    paraclinical_rooms = [
        {"phong_kham": "Phòng 202 - Chẩn Đoán Hình Ảnh (X-Quang)", "chuyen_khoa": "Chẩn đoán hình ảnh", "loai_phong": "can_lam_sang", "vi_tri": "Tầng 2 - Khu Kỹ Thuật Cao", "bac_si_ho_ten": "BS. CKI Lê Hoàng Long"},
        {"phong_kham": "Phòng 105 - Xét Nghiệm Sinh Hóa - Huyết Học", "chuyen_khoa": "Xét nghiệm", "loai_phong": "can_lam_sang", "vi_tri": "Tầng 1 - Dãy Hành Lang B", "bac_si_ho_ten": "ThS. BS Phạm Minh Tuấn"},
        {"phong_kham": "Phòng 108 - Siêu Âm Màu Doopler & 4D", "chuyen_khoa": "Thăm dò chức năng", "loai_phong": "can_lam_sang", "vi_tri": "Tầng 1 - Dãy Hành Lang A", "bac_si_ho_ten": "BS. Nguyễn Thị Lan"},
        {"phong_kham": "Phòng 206 - Nội Soi Tiêu Hóa & Tai Mũi Họng", "chuyen_khoa": "Nội soi", "loai_phong": "can_lam_sang", "vi_tri": "Tầng 2 - Phòng Vô Trùng", "bac_si_ho_ten": "BS. CKI Trần Văn Nam"}
    ]

    for pr in paraclinical_rooms:
        if pr["phong_kham"] not in rooms_map:
            rooms_map[pr["phong_kham"]] = {
                "phong_kham": pr["phong_kham"],
                "chuyen_khoa": pr["chuyen_khoa"],
                "bac_si_id": None,
                "user_id": None,
                "bac_si_ho_ten": pr["bac_si_ho_ten"],
                "loai_phong": pr["loai_phong"],
                "vi_tri": pr["vi_tri"]
            }

    return list(rooms_map.values())


@router.get("/public/queue-display", status_code=status.HTTP_200_OK)
def get_queue_display(
    phong_kham: Optional[str] = Query(None, description="Tên hoặc mã phòng khám, ví dụ: 'Phòng 101'"),
    chuyen_khoa: Optional[str] = Query(None, description="Tên chuyên khoa"),
    bac_si_id: Optional[int] = Query(None, description="ID bác sĩ hoặc user_id"),
    db: Session = Depends(get_db)
):
    """
    API Công khai cho Màn hình Kiosk hiển thị hàng đợi phòng khám:
    - Bệnh nhân ĐANG KHÁM (hiển thị số thứ tự STT, đầy đủ Họ tên, Ngày tháng năm sinh/Năm sinh).
    - DANH SÁCH CHUẨN BỊ (3 - 5 ca tiếp theo).
    - Thống kê ca khám trong ngày.
    """
    today = date.today()
    
    # 1. Tìm thông tin Bác sĩ / Phòng khám
    doc_info = None
    room_title = phong_kham or "Phòng Khám Đa Khoa"
    spec_title = chuyen_khoa or "Khám Tổng Quát"
    doc_name = "Bác sĩ phụ trách"

    if bac_si_id:
        doc = db.query(models.BacSi).filter(or_(models.BacSi.id == bac_si_id, models.BacSi.user_id == bac_si_id)).first()
        if doc:
            doc_info = doc
            doc_name = f"{doc.hoc_vi or 'BS.'} {doc.ho_ten}"
            if not phong_kham and doc.phong_kham:
                room_title = doc.phong_kham
            if not chuyen_khoa and doc.chuyen_khoa:
                spec_title = doc.chuyen_khoa
    elif phong_kham:
        doc = db.query(models.BacSi).filter(models.BacSi.phong_kham.ilike(f"%{phong_kham.strip()}%")).first()
        if doc:
            doc_info = doc
            doc_name = f"{doc.hoc_vi or 'BS.'} {doc.ho_ten}"
            spec_title = doc.chuyen_khoa or spec_title

    # 2. Xây dựng query lịch khám hôm nay
    query = db.query(models.LichKham).filter(func.date(models.LichKham.thoi_gian) == today)
    if doc_info and doc_info.user_id:
        query = query.filter(models.LichKham.bac_si_id == doc_info.user_id)
    elif chuyen_khoa:
        ck_item = db.query(models.ChuyenKhoa).filter(models.ChuyenKhoa.ten_chuyen_khoa == chuyen_khoa).first()
        if ck_item:
            query = query.filter(models.LichKham.chuyen_khoa_id == ck_item.id)

    all_today = query.all()

    def format_patient_info(lk):
        bn = lk.benh_nhan
        dob_str = ""
        nam_sinh = None
        if bn and bn.ngay_sinh:
            dob_str = bn.ngay_sinh.strftime("%d/%m/%Y")
            nam_sinh = bn.ngay_sinh.year
        return {
            "id": lk.id,
            "stt": lk.stt,
            "ma_lich": f"LK{lk.id:04d}",
            "ho_ten": bn.ho_ten if bn else "Bệnh nhân",
            "ngay_sinh": dob_str,
            "nam_sinh": nam_sinh,
            "gioi_tinh": bn.gio_tinh if bn else "Khác",
            "thoi_gian": lk.thoi_gian.strftime("%H:%M"),
            "trang_thai": lk.trang_thai
        }

    # 3. Lấy ca ĐANG KHÁM (trang_thai == 'dang_kham')
    dang_kham_item = next((lk for lk in all_today if lk.trang_thai == "dang_kham"), None)
    current_exam = format_patient_info(dang_kham_item) if dang_kham_item else None

    # 4. Danh sách CHUẨN BỊ (trang_thai == 'cho_kham' hoặc 'da_co_ket_qua'), sắp xếp theo STT
    cho_kham_list = [lk for lk in all_today if lk.trang_thai in ["cho_kham", "da_co_ket_qua"]]
    cho_kham_list.sort(key=lambda x: (0 if x.trang_thai == "da_co_ket_qua" else 1, x.stt or 9999, x.thoi_gian))
    waiting_queue = [format_patient_info(lk) for lk in cho_kham_list[:6]]

    # 5. Thống kê ca khám trong ngày
    da_kham_count = sum(1 for lk in all_today if lk.trang_thai == "hoan_thanh")
    dang_cho_count = len(cho_kham_list)

    return {
        "phong_kham": room_title,
        "chuyen_khoa": spec_title,
        "bac_si": doc_name,
        "dang_kham": current_exam,
        "danh_sach_cho": waiting_queue,
        "thong_ke": {
            "da_kham": da_kham_count,
            "dang_cho": dang_cho_count,
            "tong_ca": len(all_today)
        }
    }


@router.get("/public/tra-cuu", status_code=status.HTTP_200_OK)
def public_tra_cuu_lich_kham(
    sdt: str = Query(..., description="Số điện thoại bệnh nhân đã đăng ký"),
    ma_lich: Optional[str] = Query(None, description="Mã lịch hẹn (VD: LK0005 hoặc 5)"),
    db: Session = Depends(get_db)
):
    """
    API Công khai cho Bệnh nhân tra cứu lịch khám & kết quả khám cá nhân (FR-10 / UC-11).
    """
    clean_phone = sdt.strip()
    if not clean_phone:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp số điện thoại.")

    benh_nhan = db.query(models.BenhNhan).filter(models.BenhNhan.so_dien_thoai == clean_phone).first()
    if not benh_nhan:
        return {
            "success": True,
            "found": False,
            "message": f"Không tìm thấy hồ sơ bệnh nhân với số điện thoại {clean_phone}.",
            "lich_khams": []
        }

    query = db.query(models.LichKham).filter(models.LichKham.benh_nhan_id == benh_nhan.id)

    if ma_lich and ma_lich.strip():
        clean_code = ma_lich.strip().upper().replace("LK", "")
        if clean_code.isdigit():
            query = query.filter(models.LichKham.id == int(clean_code))

    records = query.order_by(models.LichKham.thoi_gian.desc()).all()

    STATUS_MAP = {
        "cho_xac_nhan": {"text": "Chờ duyệt", "badge": "warning"},
        "da_dat_lich": {"text": "Đã xác nhận", "badge": "info"},
        "cho_kham": {"text": "Đã tiếp nhận (Chờ khám)", "badge": "primary"},
        "dang_kham": {"text": "Đang khám trong phòng", "badge": "success"},
        "hoan_thanh": {"text": "Đã hoàn thành khám", "badge": "secondary"},
        "huy": {"text": "Đã hủy", "badge": "danger"}
    }

    results = []
    for lk in records:
        # Tên Bác sĩ
        ten_bs = "Chưa phân công"
        phong = "Phòng Khám"
        if lk.bac_si_id:
            bs = db.query(models.BacSi).filter(or_(models.BacSi.id == lk.bac_si_id, models.BacSi.user_id == lk.bac_si_id)).first()
            if bs:
                ten_bs = f"{bs.hoc_vi or 'BS.'} {bs.ho_ten}"
                phong = bs.phong_kham or phong

        # Chuyên khoa
        ten_ck = "Đa khoa"
        if lk.chuyen_khoa_id:
            ck = db.query(models.ChuyenKhoa).filter(models.ChuyenKhoa.id == lk.chuyen_khoa_id).first()
            if ck:
                ten_ck = ck.ten_chuyen_khoa

        # Phiếu khám (nếu có)
        pk_info = None
        if lk.phieu_kham:
            pk_info = {
                "trieu_chung": lk.phieu_kham.trieu_chung,
                "chan_doan": lk.phieu_kham.chan_doan,
                "ai_summary": lk.phieu_kham.ai_summary
            }

        st_info = STATUS_MAP.get(lk.trang_thai, {"text": lk.trang_thai, "badge": "secondary"})

        results.append({
            "id": lk.id,
            "ma_lich": f"LK{lk.id:04d}",
            "stt": lk.stt,
            "thoi_gian": lk.thoi_gian.strftime("%H:%M ngày %d/%m/%Y"),
            "trang_thai": lk.trang_thai,
            "trang_thai_text": st_info["text"],
            "trang_thai_badge": st_info["badge"],
            "bac_si": ten_bs,
            "phong_kham": phong,
            "chuyen_khoa": ten_ck,
            "ly_do_kham": lk.ly_do_kham,
            "phieu_kham": pk_info
        })

    return {
        "success": True,
        "found": True,
        "benh_nhan": {
            "ho_ten": benh_nhan.ho_ten,
            "so_dien_thoai": benh_nhan.so_dien_thoai,
            "ngay_sinh": benh_nhan.ngay_sinh.strftime("%d/%m/%Y") if benh_nhan.ngay_sinh else "",
            "ma_bhyt": benh_nhan.ma_bhyt
        },
        "lich_khams": results
    }


@router.post("/send-otp", status_code=status.HTTP_200_OK)
def send_booking_otp(data: PatientSendOtpInput):
    """
    Tạo mã OTP 6 chữ số và gửi về Gmail của bệnh nhân để xác thực trước khi hoàn thành đặt lịch.
    Có bảo vệ Rate Limiting: tối đa 3 lần/email/giờ (FR-09 / AC-09-01).
    """
    clean_email = data.email.strip().lower()
    if not clean_email or "@" not in clean_email:
        raise HTTPException(status_code=400, detail="Địa chỉ email không hợp lệ!")

    # 0. Kiểm tra Rate Limiting chống spam email
    allowed, rate_msg = check_otp_rate_limit(clean_email, max_requests=3, window_minutes=60)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=rate_msg)

    # 1. Phát sinh mã OTP ngẫu nhiên 6 chữ số
    otp_code = f"{random.randint(100000, 999999)}"

    booking_details = {
        "ho_ten": data.ho_ten,
        "sdt": data.sdt,
        "chuyen_khoa": data.chuyen_khoa or "Khám chuyên khoa",
        "bac_si": data.bac_si or "Bác sĩ phụ trách",
        "thoi_gian": data.thoi_gian or "Theo lịch hẹn",
        "ly_do_kham": data.ly_do_kham or "",
    }

    # 2. Lưu trữ OTP trong bộ nhớ đệm (hiệu lực 10 phút)
    save_otp(clean_email, otp_code, booking_details, ttl_minutes=10)

    # 3. Gửi email qua Gmail SMTP
    success, msg = send_booking_otp_email(clean_email, data.ho_ten, otp_code, booking_details)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi gửi email xác thực qua Gmail: {msg}"
        )

    return {
        "success": True,
        "message": f"Mã xác thực OTP đã được gửi đến hộp thư {clean_email}.",
        "email": clean_email
    }


@router.post("/verify-otp-and-book", status_code=status.HTTP_201_CREATED)
def verify_otp_and_book(data: PatientVerifyOtpAndBookInput, db: Session = Depends(get_db)):
    """
    Xác thực mã OTP gửi về Gmail và hoàn tất lưu hồ sơ bệnh nhân + lịch khám vào CSDL.
    """
    clean_email = data.email.strip().lower()
    clean_otp   = data.otp.strip()

    # 1. Kiểm tra OTP
    valid, saved_info, err_msg = verify_stored_otp(clean_email, clean_otp)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

    # 2. Tìm hoặc tạo Hồ sơ Bệnh nhân (BenhNhan) theo SĐT hoặc CCCD
    clean_phone = data.sdt.strip()
    benh_nhan = db.query(models.BenhNhan).filter(
        or_(
            models.BenhNhan.so_dien_thoai == clean_phone,
            models.BenhNhan.cccd == (data.cccd.strip() if data.cccd else None)
        )
    ).first()

    parsed_dob = None
    if data.ngay_sinh:
        try:
            parsed_dob = datetime.strptime(data.ngay_sinh.strip(), "%Y-%m-%d").date()
        except Exception:
            pass

    if not benh_nhan:
        benh_nhan = models.BenhNhan(
            ho_ten=data.ho_ten.strip(),
            ngay_sinh=parsed_dob,
            gio_tinh=data.gioi_tinh or "Khác",
            so_dien_thoai=clean_phone,
            cccd=data.cccd.strip() if data.cccd else None,
            ma_bhyt=data.bhyt.strip() if data.bhyt else None,
            tien_su_benh=data.ly_do_kham or ""
        )
        db.add(benh_nhan)
        db.commit()
        db.refresh(benh_nhan)
    else:
        if data.ho_ten: benh_nhan.ho_ten = data.ho_ten.strip()
        if parsed_dob: benh_nhan.ngay_sinh = parsed_dob
        if data.gioi_tinh: benh_nhan.gio_tinh = data.gioi_tinh
        if data.cccd: benh_nhan.cccd = data.cccd.strip()
        if data.bhyt: benh_nhan.ma_bhyt = data.bhyt.strip()
        db.commit()

    # 3. Phân giải Bác sĩ và Chuyên khoa
    target_user_id = None
    doc_name = data.bac_si or "Bác sĩ phụ trách"
    room_name = "Phòng khám đa khoa"

    if data.bac_si_id:
        doc = db.query(models.BacSi).filter(models.BacSi.id == data.bac_si_id).first()
        if not doc:
            doc = db.query(models.BacSi).filter(models.BacSi.user_id == data.bac_si_id).first()
        if doc:
            target_user_id = doc.user_id
            doc_name = f"{doc.hoc_vi or 'BS.'} {doc.ho_ten}"
            room_name = doc.phong_kham or "Phòng khám"
        else:
            target_user_id = data.bac_si_id

    target_spec_id = data.chuyen_khoa_id
    spec_name = data.chuyen_khoa or "Đa khoa"
    if not target_spec_id and data.chuyen_khoa:
        spec = db.query(models.ChuyenKhoa).filter(models.ChuyenKhoa.ten_chuyen_khoa == data.chuyen_khoa.strip()).first()
        if spec:
            target_spec_id = spec.id
            spec_name = spec.ten_chuyen_khoa

    # 4. Parse thời gian khám
    try:
        if "T" in data.thoi_gian:
            dt_kham = datetime.fromisoformat(data.thoi_gian)
        else:
            dt_kham = datetime.strptime(data.thoi_gian, "%Y-%m-%d %H:%M")
    except Exception:
        dt_kham = datetime.now() + timedelta(days=1)

    # 5. Lưu lịch khám (LichKham)
    new_lich = models.LichKham(
        benh_nhan_id=benh_nhan.id,
        bac_si_id=target_user_id,
        chuyen_khoa_id=target_spec_id,
        thoi_gian=dt_kham,
        trang_thai="cho_xac_nhan",
        ly_do_kham=data.ly_do_kham or "Đặt lịch online qua Cổng Bệnh nhân"
    )
    db.add(new_lich)
    db.commit()
    db.refresh(new_lich)

    # 6. Gửi Email thông báo Xác nhận đặt lịch thành công qua Gmail
    confirm_info = {
        "ma_lich": f"LK{new_lich.id:04d}",
        "chuyen_khoa": spec_name,
        "bac_si": doc_name,
        "phong_kham": room_name,
        "thoi_gian": dt_kham.strftime("%H:%M ngày %d/%m/%Y")
    }
    send_booking_confirmation_email(clean_email, benh_nhan.ho_ten, confirm_info)

    # Ghi nhật ký
    audit = models.AuditLog(
        action="CREATE",
        target_table="lich_khams",
        target_id=new_lich.id,
        mo_ta=f"Bệnh nhân {benh_nhan.ho_ten} xác thực OTP qua Gmail {clean_email} và đặt lịch #{new_lich.id}"
    )
    db.add(audit)
    db.commit()

    return {
        "success": True,
        "message": "Xác thực OTP thành công! Lịch khám đã được ghi nhận vào hệ thống.",
        "appointment_id": new_lich.id,
        "booking_code": f"LK{new_lich.id:04d}",
        "benh_nhan": {
            "id": benh_nhan.id,
            "ho_ten": benh_nhan.ho_ten,
            "so_dien_thoai": benh_nhan.so_dien_thoai,
            "email": clean_email
        },
        "details": confirm_info
    }



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
    
    # Định nghĩa trọng số ưu tiên trạng thái (da_co_ket_qua và dang_kham luôn đứng đầu)
    priority_map = {
        "da_co_ket_qua": 0,
        "dang_kham": 1,
        "cho_kham": 2,
        "cho_ket_qua_cls": 3,
        "da_dat_lich": 4,
        "cho_xac_nhan": 5,
        "hoan_thanh": 6,
        "huy": 7
    }
    lich_khams.sort(key=lambda x: (priority_map.get(x.trang_thai, 99), x.stt or 9999, x.thoi_gian))

    results = []
    for lk in lich_khams:
        benh_nhan = lk.benh_nhan
        
        # Tìm thông tin Bác sĩ & Phòng khám
        ten_bac_si = "Chưa phân công"
        phong_kham = "Phòng khám chung"
        if lk.bac_si_id:
            doc_user = db.query(models.User).filter(models.User.id == lk.bac_si_id).first()
            if doc_user:
                doc_info = db.query(models.BacSi).filter(models.BacSi.user_id == doc_user.id).first()
                if doc_info:
                    ten_bac_si = f"{doc_info.hoc_vi or 'BS.'} {doc_info.ho_ten}"
                    phong_kham = doc_info.phong_kham or phong_kham
                else:
                    ten_bac_si = doc_user.username

        # Tìm Chuyên khoa
        ten_chuyen_khoa = "Khám tổng quát"
        if lk.chuyen_khoa_id:
            ck = db.query(models.ChuyenKhoa).filter(models.ChuyenKhoa.id == lk.chuyen_khoa_id).first()
            if ck:
                ten_chuyen_khoa = ck.ten_chuyen_khoa
                if phong_kham == "Phòng khám chung":
                    phong_kham = f"Phòng khám {ck.ten_chuyen_khoa}"

        # Tính tuổi & format ngày sinh bệnh nhân
        dob_str = benh_nhan.ngay_sinh.strftime("%d/%m/%Y") if (benh_nhan and benh_nhan.ngay_sinh) else None
        nam_sinh = benh_nhan.ngay_sinh.year if (benh_nhan and benh_nhan.ngay_sinh) else None
        tuoi = (datetime.now().year - nam_sinh) if nam_sinh else None

        # Trích xuất kết quả Cận lâm sàng nếu có
        ket_qua_cls = None
        if lk.ly_do_kham and "[KẾT QUẢ CLS" in lk.ly_do_kham:
            idx = lk.ly_do_kham.find("[KẾT QUẢ CLS")
            ket_qua_cls = lk.ly_do_kham[idx:].strip()

        results.append({
            "id": lk.id,
            "stt": lk.stt,
            "benh_nhan_id": lk.benh_nhan_id,
            "ho_ten": benh_nhan.ho_ten if benh_nhan else "Bệnh nhân vô danh",
            "ngay_sinh": dob_str,
            "nam_sinh": nam_sinh,
            "tuoi": tuoi,
            "gioi_tinh": benh_nhan.gio_tinh if benh_nhan else "Khác",
            "so_dien_thoai": benh_nhan.so_dien_thoai if benh_nhan else None,
            "cccd": benh_nhan.cccd if benh_nhan else None,
            "dia_chi": benh_nhan.dia_chi if benh_nhan else None,
            "ma_bhyt": benh_nhan.ma_bhyt if benh_nhan else None,
            "tien_su_benh": benh_nhan.tien_su_benh if benh_nhan else None,
            "bac_si_id": lk.bac_si_id,
            "ten_bac_si": ten_bac_si,
            "phong_kham": phong_kham,
            "chuyen_khoa_id": lk.chuyen_khoa_id,
            "ten_chuyen_khoa": ten_chuyen_khoa,
            "thoi_gian": lk.thoi_gian.strftime("%Y-%m-%d %H:%M"),
            "ly_do_kham": lk.ly_do_kham,
            "ket_qua_cls": ket_qua_cls,
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


@router.put("/{lich_kham_id}/phan-cong-bac-si")
def phan_cong_bac_si_lich_kham(
    lich_kham_id: int,
    data: LichKhamAssignDoctorInput,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["le_tan", "admin", "bac_si"]))
):
    """
    PUT /{lich_kham_id}/phan-cong-bac-si
    Lễ tân / Admin phân công hoặc đổi bác sĩ phụ trách và phòng khám cho lịch khám.
    """
    lich_kham = db.query(models.LichKham).filter(models.LichKham.id == lich_kham_id).first()
    if not lich_kham:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch khám!")

    doc = db.query(models.BacSi).filter(models.BacSi.user_id == data.bac_si_id).first()
    if not doc:
        doc = db.query(models.BacSi).filter(models.BacSi.id == data.bac_si_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy bác sĩ với ID={data.bac_si_id}!")

    lich_kham.bac_si_id = doc.user_id if doc.user_id else doc.id

    # Nếu lịch khám chưa có chuyên khoa hoặc chuyên khoa chưa khớp, tự động gán theo chuyên khoa của bác sĩ
    if doc.chuyen_khoa:
        ck = db.query(models.ChuyenKhoa).filter(
            or_(
                models.ChuyenKhoa.ten_chuyen_khoa.ilike(f"%{doc.chuyen_khoa.strip()}%"),
                func.lower(doc.chuyen_khoa).contains(func.lower(models.ChuyenKhoa.ten_chuyen_khoa))
            )
        ).first()
        if ck:
            lich_kham.chuyen_khoa_id = ck.id

    db.commit()
    db.refresh(lich_kham)

    doc_name = f"{doc.hoc_vi or 'BS.'} {doc.ho_ten}"
    phong_name = doc.phong_kham or data.phong_kham or "Phòng khám"

    audit = models.AuditLog(
        user_id=current_user.id,
        action="UPDATE",
        target_table="lich_khams",
        target_id=lich_kham.id,
        mo_ta=f"Phân công {doc_name} ({phong_name}) cho lịch khám #{lich_kham.id}"
    )
    db.add(audit)
    db.commit()

    return {
        "message": f"Đã phân công {doc_name} ({phong_name}) cho lịch khám #{lich_kham.id} thành công!",
        "id": lich_kham.id,
        "bac_si_id": lich_kham.bac_si_id,
        "ten_bac_si": doc_name,
        "phong_kham": phong_name,
        "chuyen_khoa": doc.chuyen_khoa or "Chuyên khoa"
    }


@router.post("/{lich_kham_id}/goi-vao-kham")
def goi_vao_kham(
    lich_kham_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["bac_si", "le_tan", "admin"]))
):
    """
    POST /{lich_kham_id}/goi-vao-kham
    Bác sĩ gọi bệnh nhân vào phòng khám:
    1. Cập nhật trạng thái lịch khám sang 'dang_kham' (nếu chưa có STT thì tự động cấp STT).
    2. Chuyển các ca đang khám trước đó của bác sĩ này sang 'hoan_thanh'.
    3. Màn hình Kiosk phòng khám và loa Web Speech API sẽ tự động đọc số và hiển thị tên bệnh nhân.
    """
    lich_kham = db.query(models.LichKham).filter(models.LichKham.id == lich_kham_id).first()
    if not lich_kham:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch khám!")

    today_date = date.today()
    if not lich_kham.stt:
        max_stt = db.query(func.max(models.LichKham.stt)).filter(
            func.date(models.LichKham.thoi_gian) == today_date
        ).scalar() or 0
        lich_kham.stt = max_stt + 1

    if lich_kham.bac_si_id:
        db.query(models.LichKham).filter(
            models.LichKham.bac_si_id == lich_kham.bac_si_id,
            models.LichKham.id != lich_kham.id,
            models.LichKham.trang_thai == "dang_kham"
        ).update({"trang_thai": "hoan_thanh"})

    lich_kham.trang_thai = "dang_kham"
    db.commit()
    db.refresh(lich_kham)

    bn = lich_kham.benh_nhan
    dob_str = bn.ngay_sinh.strftime("%d/%m/%Y") if (bn and bn.ngay_sinh) else ""
    nam_sinh = bn.ngay_sinh.year if (bn and bn.ngay_sinh) else None

    phong_kham_name = "Phòng Khám"
    doc = db.query(models.BacSi).filter(models.BacSi.user_id == current_user.id).first()
    if doc and doc.phong_kham:
        phong_kham_name = doc.phong_kham
    elif lich_kham.bac_si_id:
        doc_assigned = db.query(models.BacSi).filter(
            or_(models.BacSi.user_id == lich_kham.bac_si_id, models.BacSi.id == lich_kham.bac_si_id)
        ).first()
        if doc_assigned and doc_assigned.phong_kham:
            phong_kham_name = doc_assigned.phong_kham
    elif lich_kham.chuyen_khoa_id:
        ck = db.query(models.ChuyenKhoa).filter(models.ChuyenKhoa.id == lich_kham.chuyen_khoa_id).first()
        if ck:
            phong_kham_name = f"Phòng khám {ck.ten_chuyen_khoa}"

    audit = models.AuditLog(
        user_id=current_user.id,
        action="UPDATE",
        target_table="lich_khams",
        target_id=lich_kham.id,
        mo_ta=f"Bác sĩ {current_user.username} gọi số khám #{lich_kham.stt} - BN {bn.ho_ten if bn else ''} vào {phong_kham_name}"
    )
    db.add(audit)
    db.commit()

    return {
        "message": f"Đã gọi bệnh nhân {bn.ho_ten if bn else ''} (STT #{lich_kham.stt}) vào phòng khám!",
        "id": lich_kham.id,
        "stt": lich_kham.stt,
        "ho_ten": bn.ho_ten if bn else "Bệnh nhân",
        "ngay_sinh": dob_str,
        "nam_sinh": nam_sinh,
        "phong_kham": phong_kham_name,
        "trang_thai": lich_kham.trang_thai
    }


@router.post("/dieu-phoi-chuyen-phong")
def dieu_phoi_chuyen_phong(
    data: ChuyenPhongInput,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["bac_si", "admin"]))
):
    """
    POST /dieu-phoi-chuyen-phong
    Actor Bác Sĩ điều phối / chuyển bệnh nhân sang phòng khám hoặc phòng cận lâm sàng tiếp theo:
    1. Hoàn tất lượt khám tại phòng hiện tại.
    2. Tự động sinh lịch khám mới tại phòng đích với trạng thái 'cho_kham' và cấp STT mới.
    3. Trả về thông tin đầy đủ để in 'Phiếu Hướng Dẫn Điều Phối Bệnh Nhân' (khổ giấy A5).
    """
    cur_lich = db.query(models.LichKham).filter(models.LichKham.id == data.lich_kham_hien_tai_id).first()
    if not cur_lich:
        raise HTTPException(status_code=404, detail="Không tìm thấy lượt khám hiện tại!")

    bn = cur_lich.benh_nhan
    if not bn:
        raise HTTPException(status_code=400, detail="Bệnh nhân không hợp lệ!")

    doc_current = db.query(models.BacSi).filter(models.BacSi.user_id == current_user.id).first()
    phong_hien_tai = doc_current.phong_kham if (doc_current and doc_current.phong_kham) else "Phòng khám lâm sàng"
    bac_si_chi_dinh = f"{doc_current.hoc_vi or 'BS.'} {doc_current.ho_ten}" if doc_current else current_user.username

    target_room = data.phong_kham_dich.strip()
    target_user_id = data.bac_si_dich_id
    target_spec_id = data.chuyen_khoa_dich_id

    if not target_user_id:
        doc_target = db.query(models.BacSi).filter(models.BacSi.phong_kham.ilike(f"%{target_room.split(' - ')[0]}%")).first()
        if doc_target:
            target_user_id = doc_target.user_id
            if not target_spec_id and doc_target.chuyen_khoa:
                ck_target = db.query(models.ChuyenKhoa).filter(models.ChuyenKhoa.ten_chuyen_khoa == doc_target.chuyen_khoa).first()
                if ck_target:
                    target_spec_id = ck_target.id

    today_date = date.today()
    max_stt_today = db.query(func.max(models.LichKham.stt)).filter(
        func.date(models.LichKham.thoi_gian) == today_date
    ).scalar() or 0
    new_stt = max_stt_today + 1

    new_lich = models.LichKham(
        benh_nhan_id=bn.id,
        bac_si_id=target_user_id,
        chuyen_khoa_id=target_spec_id,
        thoi_gian=datetime.now(),
        stt=new_stt,
        trang_thai="cho_kham",
        ly_do_kham=f"[CLS_GOC:#{cur_lich.id}] Điều phối từ {phong_hien_tai}: {data.chi_dinh_dich_vu}"
    )
    db.add(new_lich)

    # Đổi trạng thái ca khám ban đầu sang 'cho_ket_qua_cls' (không xóa/hoàn tất)
    cur_lich.trang_thai = "cho_ket_qua_cls"
    db.commit()
    db.refresh(new_lich)

    vi_tri_phong = "Tầng 2 - Khu Cận Lâm Sàng & Kỹ Thuật Cao" if any(k in target_room for k in ["201", "202", "203", "204", "205", "206", "X-Quang", "Nội soi"]) else "Tầng 1 - Khu Khám Lâm Sàng & Xét Nghiệm"

    dob_str = bn.ngay_sinh.strftime("%d/%m/%Y") if bn.ngay_sinh else ""
    nam_sinh = bn.ngay_sinh.year if bn.ngay_sinh else None

    audit = models.AuditLog(
        user_id=current_user.id,
        action="CREATE",
        target_table="lich_khams",
        target_id=new_lich.id,
        mo_ta=f"Bác sĩ {current_user.username} điều phối BN {bn.ho_ten} từ {phong_hien_tai} sang {target_room} (Chỉ định: {data.chi_dinh_dich_vu})"
    )
    db.add(audit)
    db.commit()

    return {
        "message": f"Chuyển phòng thành công! Bệnh nhân đã được đưa vào hàng chờ {target_room}",
        "phieu_dieu_phoi": {
            "ma_phieu": f"DP{new_lich.id:04d}",
            "lich_kham_moi_id": new_lich.id,
            "stt_moi": new_lich.stt,
            "thoi_gian_tao": datetime.now().strftime("%H:%M ngày %d/%m/%Y"),
            "benh_nhan": {
                "id": bn.id,
                "ho_ten": bn.ho_ten,
                "ngay_sinh": dob_str,
                "nam_sinh": nam_sinh,
                "gioi_tinh": bn.gio_tinh or "Khác",
                "so_dien_thoai": bn.so_dien_thoai or "",
                "ma_bhyt": bn.ma_bhyt or "Không"
            },
            "phong_hien_tai": phong_hien_tai,
            "bac_si_chi_dinh": bac_si_chi_dinh,
            "phong_dich": target_room,
            "vi_tri_phong": vi_tri_phong,
            "chi_dinh_dich_vu": data.chi_dinh_dich_vu,
            "ghi_chu": data.ghi_chu or "Mang theo phiếu này đến thẳng phòng chỉ định để được gọi theo STT."
        }
    }


@router.post("/tra-ket-qua-cls")
def tra_ket_qua_cls(
    data: TraKetQuaCLSInput,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["bac_si", "admin"]))
):
    """
    POST /tra-ket-qua-cls
    Kỹ thuật viên / Bác sĩ phòng Cận lâm sàng hoàn tất chụp chiếu/xét nghiệm
    và gửi kết quả ngược về Bác sĩ phòng khám ban đầu:
    1. Hoàn tất lượt khám tại phòng CLS ('hoan_thanh').
    2. Cập nhật lượt khám gốc ở phòng ban đầu sang 'da_co_ket_qua'.
    3. Cấp Số Thứ Tự (STT) MỚI tại phòng ban đầu để xếp lại vào hàng chờ và đẩy lên ƯU TIÊN số 1.
    4. Lưu kết quả CLS gắn liền với lượt khám ban đầu để bác sĩ xem được ngay.
    """
    cls_lich = db.query(models.LichKham).filter(models.LichKham.id == data.lich_kham_cls_id).first()
    if not cls_lich:
        raise HTTPException(status_code=404, detail="Không tìm thấy lượt khám cận lâm sàng!")

    bn = cls_lich.benh_nhan
    if not bn:
        raise HTTPException(status_code=400, detail="Bệnh nhân không hợp lệ!")

    # Tìm lượt khám gốc ở phòng ban đầu
    goc_lich = None
    if cls_lich.ly_do_kham and "[CLS_GOC:#" in cls_lich.ly_do_kham:
        try:
            start_idx = cls_lich.ly_do_kham.find("[CLS_GOC:#") + len("[CLS_GOC:#")
            end_idx = cls_lich.ly_do_kham.find("]", start_idx)
            goc_id = int(cls_lich.ly_do_kham[start_idx:end_idx])
            goc_lich = db.query(models.LichKham).filter(models.LichKham.id == goc_id).first()
        except Exception:
            pass

    # Nếu không tìm thấy qua tag, tìm ca 'cho_ket_qua_cls' gần nhất của bệnh nhân
    if not goc_lich:
        goc_lich = db.query(models.LichKham).filter(
            models.LichKham.benh_nhan_id == bn.id,
            models.LichKham.id != cls_lich.id,
            models.LichKham.trang_thai == "cho_ket_qua_cls"
        ).order_by(models.LichKham.id.desc()).first()

    if not goc_lich:
        # Dự phòng: tìm bất kỳ ca nào gần nhất chưa hoàn thành
        goc_lich = db.query(models.LichKham).filter(
            models.LichKham.benh_nhan_id == bn.id,
            models.LichKham.id != cls_lich.id
        ).order_by(models.LichKham.id.desc()).first()

    # Xác định phòng thực hiện CLS
    doc_cls = db.query(models.BacSi).filter(models.BacSi.user_id == current_user.id).first()
    ten_phong_cls = doc_cls.phong_kham if (doc_cls and doc_cls.phong_kham) else "Phòng Cận lâm sàng"
    ten_bs_cls = f"{doc_cls.hoc_vi or 'BS.'} {doc_cls.ho_ten}" if doc_cls else current_user.username

    # 1. Đóng ca CLS
    cls_lich.trang_thai = "hoan_thanh"

    # 2. Cấp STT mới lượt 2 cho ca khám gốc tại phòng ban đầu
    today_date = date.today()
    max_stt_today = db.query(func.max(models.LichKham.stt)).filter(
        func.date(models.LichKham.thoi_gian) == today_date
    ).scalar() or 0
    new_stt_goc = max_stt_today + 1

    formatted_cls_result = (
        f"\n[KẾT QUẢ CLS TỪ {ten_phong_cls} ({ten_bs_cls})]: "
        f"{data.ket_luan} | Chi tiết: {data.ket_qua_chi_tiet}"
    )

    if goc_lich:
        goc_lich.stt = new_stt_goc
        goc_lich.trang_thai = "da_co_ket_qua"
        goc_lich.ly_do_kham = (goc_lich.ly_do_kham or "") + formatted_cls_result

    db.commit()

    # Ghi audit log
    audit = models.AuditLog(
        user_id=current_user.id,
        action="UPDATE",
        target_table="lich_khams",
        target_id=cls_lich.id,
        mo_ta=f"Bác sĩ {current_user.username} ({ten_phong_cls}) trả kết quả CLS cho BN {bn.ho_ten}. STT mới phòng ban đầu: #{new_stt_goc}"
    )
    db.add(audit)
    db.commit()

    return {
        "success": True,
        "message": f"Đã gửi trả kết quả cận lâm sàng về phòng khám ban đầu thành công! Bệnh nhân được cấp STT #{new_stt_goc} (Ưu tiên).",
        "lich_kham_goc_id": goc_lich.id if goc_lich else None,
        "stt_moi": new_stt_goc,
        "benh_nhan": {
            "id": bn.id,
            "ho_ten": bn.ho_ten,
        },
        "phong_cls": ten_phong_cls,
        "ket_luan": data.ket_luan,
        "ket_qua_chi_tiet": data.ket_qua_chi_tiet
    }

