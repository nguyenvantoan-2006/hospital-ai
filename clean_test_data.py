"""
clean_test_data.py — Dọn dẹp toàn bộ dữ liệu Bệnh nhân test, Lịch khám test, Phiếu khám & Hóa đơn test.
Giữ nguyên:
- Danh mục 37 Chuyên khoa y tế tiêu chuẩn
- Danh sách 185 Bác sĩ chuyên khoa chính thức
- 110 Mặt hàng thuốc & vật tư y tế trong kho dược
- Tài khoản quản trị & nhân viên (admin, letan, ketoan, các bác sĩ)
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from database import SessionLocal
import models

def clean_database():
    db = SessionLocal()
    print("=" * 70)
    print("🧹 BẮT ĐẦU DỌN DẸP DỮ LIỆU BỆNH NHÂN VÀ LỊCH KHÁM TEST")
    print("=" * 70)

    try:
        # 1. Xóa chi tiết đơn thuốc
        deleted_don_thuoc = db.query(models.DonThuoc).delete()
        print(f"🗑️ Đã xóa {deleted_don_thuoc} bản ghi Đơn thuốc test.")

        # 2. Xóa hóa đơn viện phí
        deleted_hoa_don = db.query(models.HoaDon).delete()
        print(f"🗑️ Đã xóa {deleted_hoa_don} bản ghi Hóa đơn viện phí test.")

        # 3. Xóa phiếu khám bệnh
        deleted_phieu_kham = db.query(models.PhieuKham).delete()
        print(f"🗑️ Đã xóa {deleted_phieu_kham} bản ghi Phiếu khám test.")

        # 4. Xóa lịch khám bệnh
        deleted_lich_kham = db.query(models.LichKham).delete()
        print(f"🗑️ Đã xóa {deleted_lich_kham} bản ghi Lịch khám test.")

        # 5. Xóa danh sách bệnh nhân test
        deleted_benh_nhan = db.query(models.BenhNhan).delete()
        print(f"🗑️ Đã xóa {deleted_benh_nhan} bản ghi Bệnh nhân test.")

        # 6. Xóa các tài khoản user có role patient (nếu có)
        deleted_patient_users = db.query(models.User).filter(models.User.role == "patient").delete()
        print(f"🗑️ Đã xóa {deleted_patient_users} tài khoản Bệnh nhân login test.")

        # 7. Xóa vết AI logs test
        deleted_ai_logs = db.query(models.AILog).delete()
        print(f"🗑️ Đã xóa {deleted_ai_logs} bản ghi AI Logs test.")

        db.commit()

        # Kiểm tra lại số lượng sau dọn dẹp
        print("-" * 70)
        print(f"🏥 Số lượng Bệnh nhân hiện tại: {db.query(models.BenhNhan).count()}")
        print(f"📅 Số lượng Lịch khám hiện tại: {db.query(models.LichKham).count()}")
        print(f"📋 Số lượng Phiếu khám hiện tại: {db.query(models.PhieuKham).count()}")
        print(f"💳 Số lượng Hóa đơn hiện tại: {db.query(models.HoaDon).count()}")
        print(f"👨‍⚕️ Số lượng Bác sĩ chính thức: {db.query(models.BacSi).count()}")
        print(f"🩺 Số lượng Chuyên khoa y tế: {db.query(models.ChuyenKhoa).count()}")
        print(f"💊 Số lượng Thuốc & Vật tư y tế: {db.query(models.Thuoc).count()}")
        print("=" * 70)
        print("🎉 DỌN DẸP DỮ LIỆU TEST HOÀN TẤT! CƠ SỞ DỮ LIỆU SẴN SÀNG VẬN HÀNH THỰC TẾ.")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi khi dọn dẹp CSDL: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    clean_database()
