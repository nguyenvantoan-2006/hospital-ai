# seed_specialties_and_doctors.py
# Kịch bản Seed dữ liệu: 37 Chuyên khoa y tế tiêu chuẩn và 185 Bác sĩ (5 bác sĩ / chuyên khoa)
# Mỗi bác sĩ được gán tài khoản User (role=bac_si, password=BacSi@2024!) và hồ sơ BacSi chi tiết
# ════════════════════════════════════════════════════════════════════════════════

import os
import sys

# Đảm bảo in tiếng Việt và ký tự đặc biệt không bị lỗi trên Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import bcrypt
from datetime import datetime
from database import SessionLocal, engine, Base
import models

# ─── DANH SÁCH 37 CHUYÊN KHOA Y TẾ TIÊU CHUẨN ─────────────────────────────────
SPECIALTIES_DATA = [
    {"ten": "Nội Tổng Quát", "mo_ta": "Khám và điều trị các bệnh nội khoa tổng quát người lớn", "gia": 150000},
    {"ten": "Ngoại Tổng Quát", "mo_ta": "Phẫu thuật chẩn đoán và điều trị bệnh ngoại khoa thông thường", "gia": 180000},
    {"ten": "Nhi Khoa", "mo_ta": "Chăm sóc sức khỏe, điều trị bệnh và tiêm chủng cho trẻ sơ sinh và trẻ nhỏ", "gia": 160000},
    {"ten": "Sản Phụ Khoa", "mo_ta": "Khám thai, theo dõi thai kỳ, sàng lọc dị tật và điều trị bệnh phụ khoa", "gia": 200000},
    {"ten": "Tim Mạch", "mo_ta": "Khám bệnh lý tăng huyết áp, suy tim, mạch vành, siêu âm tim mạch", "gia": 220000},
    {"ten": "Hô Hấp - Phổi", "mo_ta": "Điều trị hen suyễn, viêm phế quản, viêm phổi, đo chức năng hô hấp", "gia": 180000},
    {"ten": "Tiêu Hóa - Gan Mật", "mo_ta": "Khám dạ dày, đại tràng, viêm gan virus, xơ gan, nội soi tiêu hóa", "gia": 200000},
    {"ten": "Cơ Xương Khớp", "mo_ta": "Khám thoái hóa khớp, thoát vị đĩa đệm, viêm khớp dạng thấp, gout", "gia": 190000},
    {"ten": "Thần Kinh", "mo_ta": "Khám đau đầu, mất ngủ, rối loạn tiền đình, đột quỵ và động kinh", "gia": 210000},
    {"ten": "Tai Mũi Họng", "mo_ta": "Nội soi và điều trị viêm xoang, viêm tai giữa, viêm amidan họng", "gia": 170000},
    {"ten": "Răng Hàm Mặt", "mo_ta": "Nhổ răng, hàn răng, cạo vôi, thẩm mỹ nụ cười và chỉnh nha", "gia": 160000},
    {"ten": "Mắt (Nhãn Khoa)", "mo_ta": "Đo tật khúc xạ, khám đục thủy tinh thể, glocom và điều trị mắt", "gia": 170000},
    {"ten": "Da Liễu - Thẩm Mỹ Da", "mo_ta": "Điều trị mụn trứng cá, chàm, vảy nến, viêm da cơ địa và laser da", "gia": 180000},
    {"ten": "Nội Tiết - Đái Tháo Đường", "mo_ta": "Khám tiểu đường, bướu cổ, suy giáp, cường giáp, hội chứng chuyển hóa", "gia": 200000},
    {"ten": "Thận - Tiết Niệu", "mo_ta": "Khám sỏi thận, nhiễm trùng đường tiểu, suy thận, tuyến tiền liệt", "gia": 190000},
    {"ten": "Ung Bướu (Ung Thư)", "mo_ta": "Tầm soát ung thư sớm, tư vấn phác đồ hóa trị, xạ trị và miễn dịch", "gia": 250000},
    {"ten": "Huyết Học - Truyền Máu", "mo_ta": "Khám thiếu máu, rối loạn đông máu, bệnh lý tủy xương và máu", "gia": 200000},
    {"ten": "Dị Ứng - Miễn Dịch Lâm Sàng", "mo_ta": "Khám dị ứng thời tiết, thức ăn, thuốc, viêm mũi dị ứng và lupus", "gia": 190000},
    {"ten": "Truyền Nhiễm (Bệnh Nhiệt Đới)", "mo_ta": "Khám sốt xuất huyết, cúm, sốt rét, tay chân miệng, thủy đậu", "gia": 160000},
    {"ten": "Y Học Cổ Truyền", "mo_ta": "Bắt mạch, kê đơn thuốc thang đông y, châm cứu, bấm huyệt trị liệu", "gia": 150000},
    {"ten": "Phục Hồi Chức Năng - Vật Lý Trị Liệu", "mo_ta": "Tập vật lý trị liệu sau tai biến, sau phẫu thuật chấn thương", "gia": 170000},
    {"ten": "Dinh Dưỡng Lâm Sàng", "mo_ta": "Tư vấn chế độ dinh dưỡng cho người béo phì, suy dinh dưỡng, đái tháo đường", "gia": 150000},
    {"ten": "Tâm Thần - Tâm Lý Lâm Sàng", "mo_ta": "Trị liệu tâm lý, trầm cảm, âu lo, rối loạn cảm xúc và mất ngủ kéo dài", "gia": 220000},
    {"ten": "Cấp Cứu - Hồi Sức Tích Cực", "mo_ta": "Tiếp nhận cấp cứu 24/7, xử lý tai nạn, shock và ngộ độc cấp tính", "gia": 250000},
    {"ten": "Chẩn Đoán Hình Ảnh", "mo_ta": "Chụp X-quang kỹ thuật số, CT-Scanner, MRI, siêu âm màu Doppler", "gia": 200000},
    {"ten": "Xét Nghiệm Y Học", "mo_ta": "Xét nghiệm huyết học, sinh hóa, miễn dịch, sinh học phân tử PCR", "gia": 150000},
    {"ten": "Gây Mê Hồi Sức", "mo_ta": "Khám tiền mê, giảm đau sau mổ, gây tê vùng và hồi sức ngoại khoa", "gia": 200000},
    {"ten": "Ngoại Thần Kinh (Sọ Não - Cột Sống)", "mo_ta": "Phẫu thuật chấn thương sọ não, u não, thoái hóa thoát vị cột sống", "gia": 250000},
    {"ten": "Ngoại Chấn Thương Chỉnh Hình", "mo_ta": "Nắn bó bột, phẫu thuật kết hợp xương gãy, thay khớp gối khớp háng", "gia": 220000},
    {"ten": "Ngoại Lồng Ngực - Mạch Máu", "mo_ta": "Phẫu thuật bệnh lý lồng ngực, suy giãn tĩnh mạch chi dưới, u phổi", "gia": 240000},
    {"ten": "Nam Khoa - Y Học Giới Tính", "mo_ta": "Khám vô sinh nam, rối loạn cương dương, xuất tinh sớm, bệnh nam khoa", "gia": 200000},
    {"ten": "Lão Khoa (Sức Khỏe Người Cao Tuổi)", "mo_ta": "Khám đa bệnh lý mạn tính, sa sút trí tuệ, suy kiệt ở người già", "gia": 180000},
    {"ten": "Giải Phẫu Bệnh - Tế Bào Học", "mo_ta": "Sinh thiết giải phẫu tế bào, chẩn đoán bản chất lành tính/ác tính khối u", "gia": 220000},
    {"ten": "Nội Soi Tiêu Hóa Can Thiệp", "mo_ta": "Nội soi dạ dày tiền mê, nội soi đại tràng không đau, cắt polyp", "gia": 250000},
    {"ten": "Tiêm Chủng - Phòng Ngừa", "mo_ta": "Tư vấn và tiêm chủng vắc-xin cho trẻ em, người lớn và phụ nữ trước mang thai", "gia": 120000},
    {"ten": "Kiểm Tra Sức Khỏe Tổng Quát", "mo_ta": "Gói tầm soát sức khỏe định kỳ cho cá nhân, doanh nghiệp và hồ sơ xin việc", "gia": 250000},
    {"ten": "Thẩm Mỹ - Tạo Hình Y Khoa", "mo_ta": "Tạo hình thẩm mỹ, sửa sẹo xấu, phẫu thuật phục hồi đường nét khuôn mặt", "gia": 300000},
]

# Danh sách Họ, Tên Đệm và Tên tiếng Việt phong phú để tạo 185 bác sĩ khác nhau
HO_LIST = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
DEM_LIST = ["Văn", "Thị", "Đức", "Thanh", "Hoàng", "Minh", "Quốc", "Hồng", "Anh", "Đình", "Xuân", "Ngọc", "Gia", "Bảo"]
TEN_LIST = [
    "An", "Bình", "Cường", "Dũng", "Đạt", "Giang", "Hải", "Hiếu", "Hoàng", "Huy",
    "Khoa", "Khánh", "Long", "Minh", "Nam", "Nghĩa", "Phong", "Phúc", "Quân", "Quang",
    "Sơn", "Thắng", "Thành", "Thịnh", "Tiến", "Toàn", "Trung", "Tuấn", "Tùng", "Việt",
    "Vinh", "Vũ", "Hương", "Hà", "Hạnh", "Hoa", "Linh", "Lan", "Mai", "Nga", "Phương",
    "Quỳnh", "Thảo", "Trang", "Tuyết", "Yến", "Thư", "Ngân", "Loan", "Thu"
]

HOC_VI_LIST = ["BS. CKI", "BS. CKII", "ThS. BS.", "TS. BS.", "PGS.TS. BS."]
CA_TRUC_LIST = [
    "Thứ 2 - Thứ 6 (07:30 - 16:30)",
    "Thứ 2, 4, 6 (Ca sáng: 07:00 - 12:00)",
    "Thứ 3, 5, 7 (Ca chiều: 13:00 - 18:00)",
    "Cả ngày Thứ 7 & Chủ Nhật (08:00 - 17:00)",
    "Thứ 2 - Thứ 7 (Ca linh hoạt)"
]


def hash_default_password() -> str:
    """Băm mật khẩu mặc định BacSi@2024! bằng bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(b"BacSi@2024!", salt).decode("utf-8")


def seed_database():
    db = SessionLocal()
    try:
        print("=" * 70)
        print("🌱 BẮT ĐẦU SEED 37 CHUYÊN KHOA VÀ 185 BÁC SĨ (5 BÁC SĨ / KHOA)")
        print("=" * 70)

        # 1. Tạo bảng nếu chưa có
        Base.metadata.create_all(bind=engine)

        default_password_hash = hash_default_password()

        created_specs = 0
        created_docs = 0
        doctor_global_idx = 1

        for spec_idx, spec_info in enumerate(SPECIALTIES_DATA, start=1):
            ten_khoa = spec_info["ten"]
            # Kiểm tra hoặc tạo chuyên khoa
            spec = db.query(models.ChuyenKhoa).filter(
                models.ChuyenKhoa.ten_chuyen_khoa == ten_khoa
            ).first()

            if not spec:
                spec = models.ChuyenKhoa(
                    ten_chuyen_khoa=ten_khoa,
                    mo_ta=spec_info["mo_ta"],
                    gia_kham_tieu_chuan=float(spec_info["gia"]),
                    trang_thai=True
                )
                db.add(spec)
                db.commit()
                db.refresh(spec)
                created_specs += 1
            else:
                # Cập nhật thông tin mô tả và giá chuẩn nếu cần
                spec.mo_ta = spec_info["mo_ta"]
                spec.gia_kham_tieu_chuan = float(spec_info["gia"])
                spec.trang_thai = True
                db.commit()

            print(f"\n📂 [{spec_idx:02d}/37] Chuyên khoa: {ten_khoa} (ID: {spec.id})")

            # 2. Tạo 5 bác sĩ cho chuyên khoa này
            for doc_num in range(1, 6):
                ma_bs = f"BS{doctor_global_idx:03d}"
                username = f"bacsi_{doctor_global_idx:03d}"
                email = f"bs{doctor_global_idx:03d}@clinic.com"

                # Lựa chọn tên sinh ngẫu nhiên nhưng cố định theo index
                ho = HO_LIST[(doctor_global_idx * 3 + doc_num) % len(HO_LIST)]
                dem = DEM_LIST[(doctor_global_idx * 7 + doc_num) % len(DEM_LIST)]
                ten = TEN_LIST[(doctor_global_idx * 5 + doc_num) % len(TEN_LIST)]
                ho_ten = f"{ho} {dem} {ten}"

                hoc_vi = HOC_VI_LIST[(doctor_global_idx + doc_num) % len(HOC_VI_LIST)]
                sdt = f"09{doctor_global_idx:03d}{doc_num:02d}{spec_idx:02d}"[:10]
                phong_kham = f"Phòng {100 + spec_idx} (Khu {chr(65 + (spec_idx % 4))})"
                lich_truc = CA_TRUC_LIST[(doctor_global_idx + doc_num) % len(CA_TRUC_LIST)]

                # Kiểm tra tài khoản User
                user = db.query(models.User).filter(models.User.username == username).first()
                if not user:
                    user = models.User(
                        username=username,
                        password_hash=default_password_hash,
                        role="bac_si",
                        email=email,
                        trang_thai=True
                    )
                    db.add(user)
                    db.commit()
                    db.refresh(user)

                # Kiểm tra hồ sơ BacSi
                doc = db.query(models.BacSi).filter(
                    (models.BacSi.ma_bac_si == ma_bs) | (models.BacSi.user_id == user.id)
                ).first()

                if not doc:
                    doc = models.BacSi(
                        user_id=user.id,
                        ma_bac_si=ma_bs,
                        ho_ten=ho_ten,
                        hoc_vi=hoc_vi,
                        chuyen_khoa=ten_khoa,
                        so_dien_thoai=sdt,
                        phong_kham=phong_kham,
                        lich_truc=lich_truc,
                        trang_thai=True
                    )
                    db.add(doc)
                    db.commit()
                    db.refresh(doc)
                    created_docs += 1
                    status_flag = "MỚI"
                else:
                    # Đồng bộ thông tin chuyên khoa
                    doc.chuyen_khoa = ten_khoa
                    doc.ho_ten = ho_ten
                    doc.hoc_vi = hoc_vi
                    doc.phong_kham = phong_kham
                    doc.lich_truc = lich_truc
                    doc.trang_thai = True
                    db.commit()
                    status_flag = "CẬP NHẬT"

                print(f"   └─ [{status_flag}] #{doctor_global_idx:03d} {hoc_vi} {ho_ten} ({ma_bs}) | User: {username}")
                doctor_global_idx += 1

        print("\n" + "=" * 70)
        total_specs_db = db.query(models.ChuyenKhoa).count()
        total_docs_db = db.query(models.BacSi).count()
        print(f"🎉 HOÀN TẤT THÀNH CÔNG!")
        print(f"   • Tổng số chuyên khoa hiện có trong DB: {total_specs_db}/37")
        print(f"   • Tổng số bác sĩ hiện có trong DB: {total_docs_db}/185")
        print(f"   • Mật khẩu đăng nhập mặc định cho toàn bộ bác sĩ: BacSi@2024!")
        print("=" * 70)

    except Exception as e:
        db.rollback()
        print(f"❌ LỖI KHI SEED DỮ LIỆU: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
