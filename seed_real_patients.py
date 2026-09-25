"""
seed_real_patients.py — Tạo 20 hồ sơ bệnh nhân thực tế với thông tin tiếng Việt chuẩn
Dự án: Hospital-AI Management System / Clinova Clinic
"""

import sys
from datetime import datetime, date, timedelta
import random

# Đảm bảo in tiếng Việt trên console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from database import SessionLocal
import models

REAL_PATIENTS_DATA = [
    {
        "ho_ten": "Nguyễn Văn Hùng",
        "ngay_sinh": date(1982, 5, 14),
        "gio_tinh": "Nam",
        "so_dien_thoai": "0912345678",
        "cccd": "001082009123",
        "dia_chi": "Số 45 Nguyễn Huệ, Quận 1, TP. Hồ Chí Minh",
        "ma_bhyt": "DN4790123456789",
        "tien_su_benh": "Tăng huyết áp vô căn (5 năm), dị ứng kháng sinh Penicillin",
        "ly_do_kham": "Đau tức ngực trái khi gắng sức, hồi hộp trống ngực",
        "chuyen_khoa_ten": "Tim Mạch"
    },
    {
        "ho_ten": "Trần Thị Mai",
        "ngay_sinh": date(1990, 8, 22),
        "gio_tinh": "Nữ",
        "so_dien_thoai": "0987654321",
        "cccd": "079190001234",
        "dia_chi": "128 Lê Văn Sỹ, Phường 10, Quận Phú Nhuận, TP.HCM",
        "ma_bhyt": "GD4790876543210",
        "tien_su_benh": "Viêm xoang mạn tính, hen suyễn nhẹ từ nhỏ",
        "ly_do_kham": "Khó thở về đêm, ho có đờm trắng đục kéo dài 1 tuần",
        "chuyen_khoa_ten": "Hô Hấp - Phổi"
    },
    {
        "ho_ten": "Lê Hoàng Nam",
        "ngay_sinh": date(1975, 11, 3),
        "gio_tinh": "Nam",
        "so_dien_thoai": "0903112233",
        "cccd": "001075003344",
        "dia_chi": "72 Trần Hưng Đạo, Hoàn Kiếm, Hà Nội",
        "ma_bhyt": "DN4010311223344",
        "tien_su_benh": "Viêm loét dạ dày tá tràng HP dương tính (2022), gan nhiễm mỡ độ 1",
        "ly_do_kham": "Đau rát vùng thượng vị sau khi ăn, ợ chua, buồn nôn",
        "chuyen_khoa_ten": "Tiêu Hóa - Gan Mật"
    },
    {
        "ho_ten": "Phạm Thu Hà",
        "ngay_sinh": date(1995, 3, 18),
        "gio_tinh": "Nữ",
        "so_dien_thoai": "0938445566",
        "cccd": "079195005566",
        "dia_chi": "215 Võ Văn Tần, Quận 3, TP. Hồ Chí Minh",
        "ma_bhyt": "GD4790384455667",
        "tien_su_benh": "Không có tiền sử bệnh mạn tính, có thai 16 tuần",
        "ly_do_kham": "Khám thai định kỳ 16 tuần, siêu âm tầm soát hình thái",
        "chuyen_khoa_ten": "Sản Phụ Khoa"
    },
    {
        "ho_ten": "Hoàng Minh Tuấn",
        "ngay_sinh": date(2018, 9, 10),
        "gio_tinh": "Nam",
        "so_dien_thoai": "0977889900",
        "cccd": "079218009988",
        "dia_chi": "56 Đường số 7, KDC An Phú, TP. Thủ Đức, TP.HCM",
        "ma_bhyt": "TE4790778899001",
        "tien_su_benh": "Viêm phế quản co thắt tái phát nhiều lần",
        "ly_do_kham": "Sốt cao 38.5 độ, sổ mũi, ho húng hắng, biếng ăn",
        "chuyen_khoa_ten": "Nhi Khoa"
    },
    {
        "ho_ten": "Vũ Thị Lan",
        "ngay_sinh": date(1968, 12, 5),
        "gio_tinh": "Nữ",
        "so_dien_thoai": "0918223344",
        "cccd": "031168004455",
        "dia_chi": "104 Lạch Tray, Ngô Quyền, TP. Hải Phòng",
        "ma_bhyt": "HT4310182233445",
        "tien_su_benh": "Thoái hóa khớp gối hai bên, loãng xương mức độ trung bình",
        "ly_do_kham": "Đau nhức hai khớp gối khi leo cầu thang, cứng khớp buổi sáng",
        "chuyen_khoa_ten": "Cơ Xương Khớp"
    },
    {
        "ho_ten": "Đặng Quốc Bảo",
        "ngay_sinh": date(1988, 7, 29),
        "gio_tinh": "Nam",
        "so_dien_thoai": "0909556677",
        "cccd": "079188007788",
        "dia_chi": "334 Nguyễn Trãi, Quận 5, TP. Hồ Chí Minh",
        "ma_bhyt": "DN4790909556677",
        "tien_su_benh": "Rối loạn tiền đình, đau nửa đầu Migraine",
        "ly_do_kham": "Chóng mặt quay cuồng khi thay đổi tư thế, hoa mắt, ù tai",
        "chuyen_khoa_ten": "Thần Kinh"
    },
    {
        "ho_ten": "Bùi Thị Bích Ngọc",
        "ngay_sinh": date(2001, 4, 15),
        "gio_tinh": "Nữ",
        "so_dien_thoai": "0944112233",
        "cccd": "079201002233",
        "dia_chi": "89 Cách Mạng Tháng 8, Quận 10, TP.HCM",
        "ma_bhyt": "SV4790441122334",
        "tien_su_benh": "Viêm da cơ địa, dị ứng mỹ phẩm",
        "ly_do_kham": "Nổi mẩn đỏ ngứa rát vùng mặt và hai cánh tay",
        "chuyen_khoa_ten": "Da Liễu - Thẩm Mỹ Da"
    },
    {
        "ho_ten": "Đỗ Đức Thắng",
        "ngay_sinh": date(1980, 1, 20),
        "gio_tinh": "Nam",
        "so_dien_thoai": "0932887766",
        "cccd": "001080007766",
        "dia_chi": "15 Đội Cấn, Ba Đình, Hà Nội",
        "ma_bhyt": "DN4010328877665",
        "tien_su_benh": "Viêm tai giữa mạn tính tai phải",
        "ly_do_kham": "Đau nhức tai phải, chảy dịch vàng, nghe kém",
        "chuyen_khoa_ten": "Tai Mũi Họng"
    },
    {
        "ho_ten": "Ngô Thị Phương Thảo",
        "ngay_sinh": date(1993, 6, 8),
        "gio_tinh": "Nữ",
        "so_dien_thoai": "0966334455",
        "cccd": "079193004455",
        "dia_chi": "520 Điện Biên Phủ, Phường 21, Quận Bình Thạnh, TP.HCM",
        "ma_bhyt": "DN4790663344556",
        "tien_su_benh": "Khô mắt do làm việc máy tính nhiều, cận thị 3 độ",
        "ly_do_kham": "Mắt cộm rát, mờ mắt, nhìn lóa khi xem màn hình",
        "chuyen_khoa_ten": "Mắt (Nhãn Khoa)"
    },
    {
        "ho_ten": "Trịnh Văn Long",
        "ngay_sinh": date(1972, 10, 12),
        "gio_tinh": "Nam",
        "so_dien_thoai": "0913998877",
        "cccd": "001072008877",
        "dia_chi": "42 Quang Trung, TP. Nam Định",
        "ma_bhyt": "HT4360139988776",
        "tien_su_benh": "Đái tháo đường type 2 (8 năm), HbA1c 7.8%",
        "ly_do_kham": "Tái khám đường huyết định kỳ, tê bì đầu các ngón chân",
        "chuyen_khoa_ten": "Nội Tiết - Đái Tháo Đường"
    },
    {
        "ho_ten": "Dương Thùy Linh",
        "ngay_sinh": date(1998, 2, 25),
        "gio_tinh": "Nữ",
        "so_dien_thoai": "0982554433",
        "cccd": "079198004433",
        "dia_chi": "18 Phan Đăng Lưu, Phường 6, Quận Bình Thạnh, TP.HCM",
        "ma_bhyt": "DN4790825544332",
        "tien_su_benh": "Sâu răng hàm số 6 dưới, ê buốt khi ăn đồ lạnh",
        "ly_do_kham": "Đau nhức răng dữ dội lan lên thái dương, sưng nướu",
        "chuyen_khoa_ten": "Răng Hàm Mặt"
    },
    {
        "ho_ten": "Phan Thanh Tùng",
        "ngay_sinh": date(1985, 8, 30),
        "gio_tinh": "Nam",
        "so_dien_thoai": "0908776655",
        "cccd": "079185006655",
        "dia_chi": "95 Hùng Vương, Phường 4, Quận 5, TP.HCM",
        "ma_bhyt": "DN4790087766554",
        "tien_su_benh": "Sỏi thận trái 6mm (2023), tiểu buốt từng đợt",
        "ly_do_kham": "Đau quặn thắt hông lưng bên trái, nước tiểu đục",
        "chuyen_khoa_ten": "Thận - Tiết Niệu"
    },
    {
        "ho_ten": "Lý Mỹ Duyên",
        "ngay_sinh": date(1996, 11, 19),
        "gio_tinh": "Nữ",
        "so_dien_thoai": "0933221100",
        "cccd": "079196001100",
        "dia_chi": "68 Pasteur, Bến Nghé, Quận 1, TP.HCM",
        "ma_bhyt": "GD4790332211009",
        "tien_su_benh": "Dị ứng phấn hoa, mày đay mạn tính",
        "ly_do_kham": "Hắt hơi liên tục, ngứa mũi mắt, nghẹt mũi kéo dài",
        "chuyen_khoa_ten": "Dị Ứng - Miễn Dịch Lâm Sàng"
    },
    {
        "ho_ten": "Đinh Quang Khải",
        "ngay_sinh": date(1978, 4, 5),
        "gio_tinh": "Nam",
        "so_dien_thoai": "0915667788",
        "cccd": "001078007788",
        "dia_chi": "88 Phố Huế, Hai Bà Trưng, Hà Nội",
        "ma_bhyt": "DN4010156677889",
        "tien_su_benh": "Gout mạn tính (4 năm), Acid Uric máu 520 umol/L",
        "ly_do_kham": "Sưng nóng đỏ đau khớp ngón chân cái bàn chân phải",
        "chuyen_khoa_ten": "Cơ Xương Khớp"
    },
    {
        "ho_ten": "Đoàn Thị Kim Oanh",
        "ngay_sinh": date(1965, 7, 14),
        "gio_tinh": "Nữ",
        "so_dien_thoai": "0902334455",
        "cccd": "079165004455",
        "dia_chi": "142 Hai Bà Trưng, Phường Đa Kao, Quận 1, TP.HCM",
        "ma_bhyt": "HT4790023344556",
        "tien_su_benh": "Rối loạn lipid máu, tăng men gan nhẹ",
        "ly_do_kham": "Kiểm tra sức khỏe tổng quát định kỳ người cao tuổi",
        "chuyen_khoa_ten": "Nội Tổng Quát"
    },
    {
        "ho_ten": "Mai Xuân Trường",
        "ngay_sinh": date(1992, 9, 27),
        "gio_tinh": "Nam",
        "so_dien_thoai": "0971223344",
        "cccd": "038192003344",
        "dia_chi": "79 Lê Duẩn, TP. Thanh Hóa",
        "ma_bhyt": "DN4380712233445",
        "tien_su_benh": "Chấn thương phần mềm cổ chân trái sau đá bóng",
        "ly_do_kham": "Cổ chân trái sưng to bầm tím, đi lại đau nhói",
        "chuyen_khoa_ten": "Ngoại Chấn Thương Chỉnh Hình"
    },
    {
        "ho_ten": "Tạ Hồng Hạnh",
        "ngay_sinh": date(1987, 1, 16),
        "gio_tinh": "Nữ",
        "so_dien_thoai": "0945889900",
        "cccd": "079187009900",
        "dia_chi": "310 Nguyễn Đình Chiểu, Quận 3, TP.HCM",
        "ma_bhyt": "DN4790458899001",
        "tien_su_benh": "Mất ngủ kéo dài, suy nhược thần kinh",
        "ly_do_kham": "Khó vào giấc ngủ, ngủ chập chờn hay giật mình, đau đầu",
        "chuyen_khoa_ten": "Tâm Thần - Tâm Lý Lâm Sàng"
    },
    {
        "ho_ten": "Chu Đình Trọng",
        "ngay_sinh": date(1997, 5, 2),
        "gio_tinh": "Nam",
        "so_dien_thoai": "0968990011",
        "cccd": "001197000011",
        "dia_chi": "12 Cầu Giấy, Quận Cầu Giấy, Hà Nội",
        "ma_bhyt": "DN4010689900112",
        "tien_su_benh": "Dạ dày trào ngược độ A",
        "ly_do_kham": "Khám sức khỏe tổng quát cấp giấy phép lao động",
        "chuyen_khoa_ten": "Kiểm Tra Sức Khỏe Tổng Quát"
    },
    {
        "ho_ten": "Võ Hải Yến",
        "ngay_sinh": date(1989, 10, 8),
        "gio_tinh": "Nữ",
        "so_dien_thoai": "0937112299",
        "cccd": "079189002299",
        "dia_chi": "260 Trường Chinh, Quận Tân Bình, TP.HCM",
        "ma_bhyt": "GD4790371122998",
        "tien_su_benh": "Bướu nhân tuyến giáp lành tính TIRADS 2",
        "ly_do_kham": "Nuốt vướng cổ họng, sụt cân nhẹ, run tay khi xúc động",
        "chuyen_khoa_ten": "Nội Tiết - Đái Tháo Đường"
    }
]

def seed_real_patients():
    db = SessionLocal()
    print("=" * 75)
    print("🏥 BẮT ĐẦU TẠO 20 HỒ SƠ BỆNH NHÂN THỰC TẾ & LẬP LỊCH KHÁM CHUẨN")
    print("=" * 75)

    try:
        base_time = datetime.now()
        created_patients = 0
        created_appointments = 0

        for idx, p_data in enumerate(REAL_PATIENTS_DATA, start=1):
            # 1. Tìm hoặc tạo Hồ sơ bệnh nhân
            bn = models.BenhNhan(
                ho_ten=p_data["ho_ten"],
                ngay_sinh=p_data["ngay_sinh"],
                gio_tinh=p_data["gio_tinh"],
                so_dien_thoai=p_data["so_dien_thoai"],
                cccd=p_data["cccd"],
                dia_chi=p_data["dia_chi"],
                ma_bhyt=p_data["ma_bhyt"],
                tien_su_benh=p_data["tien_su_benh"]
            )
            db.add(bn)
            db.flush() # Lấy bn.id
            created_patients += 1

            # 2. Tìm chuyên khoa phù hợp
            spec = db.query(models.ChuyenKhoa).filter(models.ChuyenKhoa.ten_chuyen_khoa == p_data["chuyen_khoa_ten"]).first()
            if not spec:
                spec = db.query(models.ChuyenKhoa).first()

            # 3. Tìm bác sĩ thuộc chuyên khoa đó
            doctor = None
            if spec:
                doctor = db.query(models.BacSi).filter(models.BacSi.chuyen_khoa == spec.ten_chuyen_khoa).first()
            if not doctor:
                doctor = db.query(models.BacSi).first()

            # 4. Lập lịch khám trong ngày hôm nay (khung giờ từ 08:00 - 16:30)
            app_time = base_time.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(minutes=20 * (idx - 1))
            
            # Phân bổ trạng thái thực tế: 6 bệnh nhân đầu là 'cho_kham' để bác sĩ khám ngay, các bệnh nhân sau là 'cho_xac_nhan' hoặc 'da_dat_lich'
            if idx <= 6:
                status_kham = "cho_kham"
            elif idx <= 12:
                status_kham = "da_dat_lich"
            else:
                status_kham = "cho_xac_nhan"

            lich = models.LichKham(
                benh_nhan_id=bn.id,
                bac_si_id=doctor.user_id if doctor else None,
                chuyen_khoa_id=spec.id if spec else None,
                stt=idx,
                thoi_gian=app_time,
                trang_thai=status_kham,
                ly_do_kham=p_data["ly_do_kham"]
            )
            db.add(lich)
            created_appointments += 1

            print(f"[{idx:02d}] ✅ {bn.ho_ten} ({bn.gio_tinh}, {bn.ngay_sinh.year}) | SĐT: {bn.so_dien_thoai} | Khám: {spec.ten_chuyen_khoa} -> STT: #{idx} ({status_kham})")

        db.commit()
        print("=" * 75)
        print(f"🎉 HOÀN THÀNH TẠO:")
        print(f"   👥 {created_patients} Hồ sơ Bệnh nhân với thông tin thật đầy đủ (CCCD, BHYT, Địa chỉ, Tiền sử bệnh).")
        print(f"   📅 {created_appointments} Lịch khám bệnh phân bổ đều cho các Bác sĩ chuyên khoa.")
        print(f"   🏥 6 Bệnh nhân đầu tiên đã được xếp hàng ở trạng thái 'Chờ khám' để Bác sĩ vào khám & kê đơn ngay!")
        print("=" * 75)
        return True

    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi khi tạo dữ liệu bệnh nhân: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    seed_real_patients()
