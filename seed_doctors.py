"""
seed_doctors.py — Cập nhật danh sách 5 Bác sĩ tên thật cho mỗi Chuyên khoa (Hospital-AI / Clinova)
"""

import os
import sys
import io
import re
import unicodedata
import bcrypt
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from database import SessionLocal
import models

load_dotenv()

# Danh sách 155 tên thật do người dùng cung cấp
RAW_DOCTOR_NAMES = """
Hoàng Hải	Anh
Nguyễn Quốc	Anh
Nguyễn Quốc	Bảo
Bùi Ngọc	Bình
Hà Thị Mỹ	Bình
Phạm Thanh	Bình
Cao Xuân	Chiến
Nguyễn Duy	Chiến
Dương Văn	Chuẩn
Nguyễn Hải	Đăng
Cao Tiến	Đạt
Hoàng Đình Gia	Đạt
Hoàng Tiến	Đạt
Mai Văn	Đạt
Nguyễn Thành	Đạt
Nông Tiến	Đạt
Nguyễn Việt	Đức
Dương Hải	Dương
Nguyễn Thị	Giang
Trương Đình	Giang
Ngọ Quang	Hải
Nguyễn Hồng	Hải
Nguyễn Văn	Hải
Diệp Đình	Hân
Bùi Ngọc	Huân
Hoàng Thanh	Hùng
Dương Minh	Hưng
Nguyễn Thành	Hưng
Phạm Hải	Hướng
Ngô Hoàng	Lan
Trần Khánh	Liêm
Nguyễn Tuấn	Lực
Nguyễn Ngọc	Lương
Đinh Khôi	Nguyên
Đinh Hữu	Phúc
Trần Khả	Quân
Vi Hoàng	Quân
Hứa Quốc	Thắng
Nguyễn Ngọc	Thắng
Lý Văn	Thuận
Trần Minh	Thuận
Bùi Phương	Thúy
Nguyễn Thị Thu	Trà
Nguyễn Thị Huyền	Trang
Đỗ Kiên	Trung
Tô Quang	Tú
La Văn	Tuấn
Lường Thanh	Tùng
Đồng Văn	Tuyên
Nguyễn Thị Hồng	Vân
Nguyễn Quốc	Việt
Nguyễn Văn	Vũ
Lê Tâm	An
Nguyễn Tuấn	Anh
Phạm Công	Anh
Dương Triệu	Bách
Dương Thời	Bằng
Lò Văn	Bình
Tô Văn Tiến	Đạt
Hà Văn	Đức
Trần Danh	Đức
Dương Tiến	Dũng
Vũ Hồng	Dũng
Hoàng Thái	Dương
Phạm Hoàng	Dương
Nguyễn Văn	Hảo
Vi Thị	Hậu
Nguyễn Văn	Hiếu
Tạ Quang	Hiếu
Dương Đình	Hoàng
Nguyễn Trung	Học
Lê Quang	Hưng
Lý Văn	Hưng
La Hoàng	Huy
Trần Quốc	Huy
Vũ Quang	Huy
Ngô Đức	Khải
Hoàng Minh	Khánh
Triệu Quốc	Khánh
Hoàng Văn	Khuyến
Nguyễn Minh	Lượng
Đào Đức	Mạnh
Đoàn Ngọc	Mạnh
Đỗ Quang	Minh
Vũ Thị Thanh	Ngân
Hà Sỹ	Nguyên
Vũ Hồng	Nhung
Nguyễn Ngọc	Phúc
Hoàng Thanh	Phương
Nguyễn Thị Hà	Phương
Phạm Đình	Sơn
Nguyễn Văn	Thái
Hà Văn	Thăng
Hoàng Văn	Thoại
Lê Thị Minh	Thư
Long Hoàng	Tiến
Nông Minh	Trí
Trần Xuân	Trí
Hà Đức	Trung
Lê Đăng	Tuân
Quách Anh	Tuấn
Phạm Đức	Việt
Nguyễn Quang	Vinh
Phan Thái	An
Nguyễn Thị	Ánh
Bùi Thanh	Bình
Ngô Tiến	Đạt
Trần Tiến	Đạt
Lã Quý	Doanh
Nguyễn Hữu	Đức
Lê Chí	Dũng
Hà Thái	Dương
Hà Thành	Duy
Bùi Đức	Hà
Nguyễn Thị Thu	Hà
Đào Ngọc	Hiệp
Trần Trung	Hiếu
Nguyễn Thái	Hoàng
Nguyễn Xuân	Hồng
Vũ Bá	Hùng
Nguyễn Xuân	Hưởng
Trần Ngọc	Huy
Vi Văn	Huy
Nguyễn Văn	Khải
Lê Quang	Khánh
Trần Khánh	Lâm
Trần Thị	Loan
Lê Đắc	Lộc
Hứa Hiền	Lương
Ngô Phương	Mai
Nguyễn Văn	Minh
Trần Vũ	Minh
Ngô Thị Ánh	Ngọc
Lưu Thanh	Nguyên
Nguyễn Duy	Niên
Lê Hồng	Phong
Vũ Ngọc	Phong
Trần Văn	Phúc
Nguyễn Minh	Quang
Dương Hữu	Thắng
Ngô Xuân	Thủy
Nguyễn Việt	Tiến
Nguyễn Văn	Toàn
Tạ Khánh	Toàn
Nguyễn Thị	Trang
Dương Quang	Trung
Bùi Văn	Trường
Phùng Xuân	Trường
Ngô Thanh	Tú
Dương Văn	Tuấn
Nông Quốc	Tuấn
Ma Khánh	Tùng
Đinh Trọng	Việt
Nguyễn Hồng	Vinh
Nguyễn Thành	Vũ
"""

def clean_vietnamese_accent(text: str) -> str:
    """Chuyển tiếng Việt có dấu thành không dấu để tạo username đẹp."""
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = text.replace('đ', 'd').replace('Đ', 'D')
    return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

TITLES = ["TS. BS", "BS. CK2", "ThS. BS", "BS. CK1", "BS."]
SHIFTS = [
    "Thứ 2 - Thứ 6 (07:30 - 11:30)",
    "Thứ 2 - Thứ 6 (13:30 - 17:00)",
    "Thứ 2 - Thứ 7 (08:00 - 16:30)",
    "Thứ 3 - Chủ nhật (07:30 - 16:30)",
    "Thứ 2, 4, 6 (08:00 - 17:00)",
]

def main():
    names = [' '.join(line.split()) for line in RAW_DOCTOR_NAMES.strip().split('\n') if line.strip()]
    print(f"Loaded {len(names)} doctor names.")

    db = SessionLocal()
    specialties = db.query(models.ChuyenKhoa).filter(models.ChuyenKhoa.trang_thai == True).all()
    print(f"Found {len(specialties)} active specialties in database.")

    # Tạo password hash chung cho toàn bộ bác sĩ mới (BacSi@2024!)
    common_password = "BacSi@2024!"
    salt = bcrypt.gensalt(rounds=12)
    pwd_hash = bcrypt.hashpw(common_password.encode("utf-8"), salt).decode("utf-8")

    # Xóa các bác sĩ test cũ trong bảng bac_si
    old_docs = db.query(models.BacSi).all()
    print(f"Deleting {len(old_docs)} old doctors from bac_si table...")
    for d in old_docs:
        db.delete(d)
    db.commit()

    created_count = 0
    name_idx = 0

    for spec_idx, spec in enumerate(specialties):
        print(f"\n--- Chuyên khoa [{spec_idx + 1}/{len(specialties)}]: {spec.ten_chuyen_khoa} ---")
        for doc_num in range(5):
            name = names[name_idx % len(names)]
            name_idx += 1

            code = f"BS{created_count + 101:03d}"
            slug = clean_vietnamese_accent(name)
            username = f"bs_{slug}_{created_count + 101}"

            # Tìm hoặc tạo User
            user = db.query(models.User).filter(models.User.username == username).first()
            if not user:
                user = models.User(
                    username=username,
                    password_hash=pwd_hash,
                    role="bac_si",
                    email=f"{slug}{created_count + 101}@clinova.vn",
                    trang_thai=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)

            title = TITLES[doc_num % len(TITLES)]
            shift = SHIFTS[doc_num % len(SHIFTS)]
            room_num = 100 + (spec_idx % 10) * 10 + (doc_num + 1)
            room = f"Phòng {room_num}"
            phone = f"09{((created_count * 7 + 1234567) % 90000000 + 10000000)}"

            bac_si = models.BacSi(
                user_id=user.id,
                ma_bac_si=code,
                ho_ten=name,
                hoc_vi=title,
                chuyen_khoa=spec.ten_chuyen_khoa,
                so_dien_thoai=phone,
                phong_kham=room,
                lich_truc=shift,
                trang_thai=True
            )
            db.add(bac_si)
            created_count += 1
            print(f"  + {code}: {title} {name} | {room} | User: {username}")

    db.commit()
    print(f"\n{'='*60}")
    print(f"HOÀN THÀNH:")
    print(f"Đã tạo {created_count} bác sĩ cho {len(specialties)} chuyên khoa (mỗi chuyên khoa đúng 5 bác sĩ).")
    print(f"Mật khẩu chung cho tất cả tài khoản bác sĩ: {common_password}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
