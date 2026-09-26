"""
scripts/fix_specialties_and_appointments.py
Script chuẩn hóa danh mục chuyên khoa và khắc phục lịch khám bị gán nhầm bác sĩ.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from database import SessionLocal
import models
from seed_specialties_and_doctors import SPECIALTIES_DATA

def run_fix():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("🩺 BẮT ĐẦU CHUẨN HÓA 37 CHUYÊN KHOA & SỬA LỊCH KHÁM")
        print("=" * 60)

        # 1. Danh sách 37 tên chuẩn
        standard_names = [s["ten"] for s in SPECIALTIES_DATA]
        std_dict_lower = {s["ten"].lower(): s for s in SPECIALTIES_DATA}

        # 2. Chuẩn hóa tên và kích hoạt 37 chuyên khoa chuẩn trong DB
        all_specs = db.query(models.ChuyenKhoa).all()
        for s in all_specs:
            s_lower = s.ten_chuyen_khoa.lower().strip()
            if s_lower in std_dict_lower:
                s.ten_chuyen_khoa = std_dict_lower[s_lower]["ten"]
                s.mo_ta = std_dict_lower[s_lower]["mo_ta"]
                s.gia_kham_tieu_chuan = float(std_dict_lower[s_lower]["gia"])
                s.trang_thai = True
            else:
                s.trang_thai = False

        db.commit()

        # Kiểm tra lại số lượng chuyên khoa chuẩn đang active
        active_specs = db.query(models.ChuyenKhoa).filter(models.ChuyenKhoa.trang_thai == True).all()
        std_specs_map = {s.ten_chuyen_khoa: s for s in active_specs}
        print(f"✓ Đã kích hoạt {len(std_specs_map)}/37 chuyên khoa chuẩn: {list(std_specs_map.keys())[:5]}...")

        # 3. Bản đồ chuyển đổi các chuyên khoa cũ sang chuyên khoa chuẩn
        old_to_std_map = {
            "Mắt": "Mắt (Nhãn Khoa)",
            "Da liễu": "Da Liễu - Thẩm Mỹ Da",
            "Nội Tiết": "Nội Tiết - Đái Tháo Đường",
            "Thận – Tiết niệu": "Thận - Tiết Niệu",
            "Hô hấp": "Hô Hấp - Phổi",
            "Tiêu hóa - Gan mật": "Tiêu Hóa - Gan Mật",
            "Nội tổng hợp": "Nội Tổng Quát",
            "Ngoại khoa": "Ngoại Tổng Quát",
            "Huyết học": "Huyết Học - Truyền Máu",
            "Lão khoa": "Lão Khoa (Sức Khỏe Người Cao Tuổi)",
            "Dị ứng - Miễn dịch": "Dị Ứng - Miễn Dịch Lâm Sàng",
            "Sản phụ khoa": "Sản Phụ Khoa",
            "Nhi khoa": "Nhi Khoa",
            "Tim mạch": "Tim Mạch",
            "Cơ xương khớp": "Cơ Xương Khớp",
            "Thần kinh": "Thần Kinh",
            "Ung bướu": "Ung Bướu (Ung Thư)",
            "Tâm thần - Tâm lý": "Tâm Thần - Tâm Lý Lâm Sàng",
            "Y học cổ truyền": "Y Học Cổ Truyền",
            "Phục hồi chức năng": "Phục Hồi Chức Năng - Vật Lý Trị Liệu",
            "Dinh dưỡng": "Dinh Dưỡng Lâm Sàng",
            "Nam khoa": "Nam Khoa - Y Học Giới Tính",
            "Chẩn đoán hình ảnh": "Chẩn Đoán Hình Ảnh",
            "Xét nghiệm - Giải phẫu bệnh": "Xét Nghiệm Y Học",
            "Cấp cứu - Hồi sức": "Cấp Cứu - Hồi Sức Tích Cực",
            "Gây mê hồi sức": "Gây Mê Hồi Sức",
            "Chấn thương chỉnh hình": "Ngoại Chấn Thương Chỉnh Hình",
            "Ngoại tim mạch - Lồng ngực": "Ngoại Lồng Ngực - Mạch Máu",
            "Tiêm chủng - Vắc-xin": "Tiêm Chủng - Phòng Ngừa",
            "Khám sức khỏe tổng quát": "Kiểm Tra Sức Khỏe Tổng Quát",
            "Tạo hình thẩm mỹ": "Thẩm Mỹ - Tạo Hình Y Khoa",
        }

        # 4. Di chuyển các LichKham đang tham chiếu chuyên khoa cũ sang chuyên khoa chuẩn
        old_specs = db.query(models.ChuyenKhoa).filter(models.ChuyenKhoa.trang_thai == False).all()
        remapped_count = 0
        for old_s in old_specs:
            target_name = old_to_std_map.get(old_s.ten_chuyen_khoa)
            if target_name and target_name in std_specs_map:
                target_std = std_specs_map[target_name]
                lks = db.query(models.LichKham).filter(models.LichKham.chuyen_khoa_id == old_s.id).all()
                for lk in lks:
                    lk.chuyen_khoa_id = target_std.id
                    remapped_count += 1

        db.commit()
        print(f"✓ Đã di chuyển {remapped_count} lịch khám cũ về đúng chuyên khoa chuẩn.")

        # 5. Sửa cụ thể lịch khám #59 (khám mắt cắt kính)
        lk59 = db.query(models.LichKham).filter(models.LichKham.id == 59).first()
        if lk59:
            eye_spec = std_specs_map.get("Mắt (Nhãn Khoa)")
            eye_doc = db.query(models.BacSi).filter(
                models.BacSi.chuyen_khoa == "Mắt (Nhãn Khoa)",
                models.BacSi.trang_thai == True
            ).first()
            if eye_spec:
                lk59.chuyen_khoa_id = eye_spec.id
            if eye_doc:
                lk59.bac_si_id = eye_doc.user_id if eye_doc.user_id else eye_doc.id
                print(f"✓ Đã sửa LK #59: Bệnh nhân Hoàng Văn Tùng -> Bác sĩ Mắt: {eye_doc.hoc_vi} {eye_doc.ho_ten} ({eye_doc.phong_kham})")
        # 6. Chuẩn hóa phòng khám có KHU cho 100% bác sĩ
        spec_to_room_map = {}
        for idx, s in enumerate(SPECIALTIES_DATA, start=1):
            room_str = f"Phòng {100 + idx} (Khu {chr(65 + (idx % 4))})"
            spec_to_room_map[s["ten"]] = room_str

        all_active_docs = db.query(models.BacSi).filter(models.BacSi.trang_thai == True).all()
        updated_docs_count = 0
        for doc in all_active_docs:
            current_spec = (doc.chuyen_khoa or "").strip()
            std_spec_name = old_to_std_map.get(current_spec, current_spec)
            if std_spec_name in spec_to_room_map:
                std_room = spec_to_room_map[std_spec_name]
                if doc.phong_kham != std_room or doc.chuyen_khoa != std_spec_name:
                    doc.chuyen_khoa = std_spec_name
                    doc.phong_kham = std_room
                    updated_docs_count += 1
            elif not doc.phong_kham or "Khu" not in doc.phong_kham:
                doc.phong_kham = f"{doc.phong_kham or 'Phòng khám'} (Khu A)"
                updated_docs_count += 1

        db.commit()
        print(f"✓ Đã chuẩn hóa {updated_docs_count} bác sĩ: 100% có số phòng kèm KHU (Khu A, Khu B, Khu C, Khu D).")

        print("=" * 60)
        print("🎉 HOÀN TẤT CHUẨN HÓA DỮ LIỆU CHUYÊN KHOA & BÁC SĨ")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"Lỗi: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run_fix()
