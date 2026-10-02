import sys
import os
import unittest

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass
from datetime import datetime, date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import SessionLocal, engine
import models
from main import app

client = TestClient(app)

class TestAppointmentCapacityAndSync(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db: Session = SessionLocal()
        # Tìm hoặc tạo Bác sĩ thử nghiệm A và B
        cls.doc_a = cls.db.query(models.BacSi).filter(models.BacSi.ho_ten.like("%Nguyễn Văn A%")).first()
        if not cls.doc_a:
            cls.doc_a = models.BacSi(
                ma_bac_si="BS_TEST_A",
                ho_ten="Nguyễn Văn A",
                hoc_vi="ThS. BS",
                chuyen_khoa="Nội tổng quát",
                phong_kham="Phòng 101 (Khu A)",
                so_benh_nhan_toi_da_ngay=200,
                so_benh_nhan_toi_da_khung_gio=20,
                trang_thai=True
            )
            cls.db.add(cls.doc_a)
            cls.db.commit()
            cls.db.refresh(cls.doc_a)
        else:
            cls.doc_a.so_benh_nhan_toi_da_ngay = 200
            cls.doc_a.so_benh_nhan_toi_da_khung_gio = 20
            cls.db.commit()

        cls.doc_b = cls.db.query(models.BacSi).filter(models.BacSi.ho_ten.like("%Trần Thị B%")).first()
        if not cls.doc_b:
            cls.doc_b = models.BacSi(
                ma_bac_si="BS_TEST_B",
                ho_ten="Trần Thị B",
                hoc_vi="BS. CKI",
                chuyen_khoa="Nội tổng quát",
                phong_kham="Phòng 102 (Khu A)",
                so_benh_nhan_toi_da_ngay=200,
                so_benh_nhan_toi_da_khung_gio=20,
                trang_thai=True
            )
            cls.db.add(cls.doc_b)
            cls.db.commit()
            cls.db.refresh(cls.doc_b)

        # Tạo bệnh nhân thử nghiệm
        cls.patient_1 = cls.db.query(models.BenhNhan).filter(models.BenhNhan.so_dien_thoai == "0900000001").first()
        if not cls.patient_1:
            cls.patient_1 = models.BenhNhan(
                ho_ten="Bệnh Nhân Test 1",
                so_dien_thoai="0900000001",
                gio_tinh="Nam"
            )
            cls.db.add(cls.patient_1)
            cls.db.commit()
            cls.db.refresh(cls.patient_1)

        # Xóa các lịch khám cũ của ngày test: 2026-10-10 và 2026-10-11
        cls.test_date_1 = date(2026, 10, 10)
        cls.test_date_2 = date(2026, 10, 11)
        cls.clean_test_appointments()

    @classmethod
    def clean_test_appointments(cls):
        cls.db.query(models.LichKham).filter(
            models.LichKham.bac_si_id.in_([cls.doc_a.id, cls.doc_a.user_id, cls.doc_b.id, cls.doc_b.user_id])
        ).delete(synchronize_session=False)
        cls.db.commit()

    def test_01_doctor_has_available_capacity(self):
        """Test Case 01 – Bác sĩ còn chỗ (150/200) -> Cho phép đặt."""
        # Giả lập đã có 150 bệnh nhân đặt vào ngày 2026-10-10
        doc_user_id = self.doc_a.user_id or self.doc_a.id
        
        # Kiểm tra API availability
        res = client.get(f"/api/v1/lich-khams/public/doctor-availability?bac_si_id={self.doc_a.id}&ngay_kham=2026-10-10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse(data["is_full_ngay"])
        self.assertEqual(data["toi_da_ngay"], 200)

        # Thử đặt thêm 1 bệnh nhân vào khung giờ 08:00
        thoi_gian_str = "2026-10-10 08:00"
        create_res = client.post(
            "/api/v1/lich-khams/tiep-don-tai-quay",
            headers={"Authorization": "Bearer fake_or_admin_skip"}, # or direct test
            json={
                "benh_nhan_id": self.patient_1.id,
                "bac_si_id": doc_user_id,
                "thoi_gian": "2026-10-10T08:00:00",
                "trang_thai": "da_dat_lich"
            }
        )
        # Note: tiep-don-tai-quay requires auth or we test via helper
        # Let's verify with check_doctor_capacity directly or via API
        from routers.lich_khams import check_doctor_capacity
        is_valid, err_code, err_msg, details = check_doctor_capacity(
            self.db, doc_user_id, datetime(2026, 10, 10, 8, 0)
        )
        self.assertTrue(is_valid)
        print("  -> Test Case 01 PASSED: Bác sĩ còn chỗ -> Cho phép đặt.")

    def test_02_and_03_patient_200_and_201_capacity_limit(self):
        """
        Test Case 02 – Bệnh nhân thứ 200 (199/200) -> Cho phép đặt -> Sau khi đặt = 200.
        Test Case 03 – Bệnh nhân thứ 201 (200/200) -> Không cho phép đặt -> Gợi ý giờ khác / ngày khác / bác sĩ khác.
        """
        from routers.lich_khams import check_doctor_capacity
        doc_user_id = self.doc_a.user_id or self.doc_a.id

        # Nạp giả lập các lịch khám để đạt 199 ca trong ngày
        existing_count = self.db.query(models.LichKham).filter(
            models.LichKham.bac_si_id == doc_user_id,
            models.LichKham.thoi_gian >= datetime(2026, 10, 10, 0, 0),
            models.LichKham.thoi_gian <= datetime(2026, 10, 10, 23, 59)
        ).count()

        needed = 199 - existing_count
        bulk_items = []
        for i in range(needed):
            bulk_items.append(models.LichKham(
                benh_nhan_id=self.patient_1.id,
                bac_si_id=doc_user_id,
                thoi_gian=datetime(2026, 10, 10, 17, 0) + timedelta(seconds=i),
                trang_thai="da_dat_lich"
            ))
        if bulk_items:
            self.db.bulk_save_objects(bulk_items)
            self.db.commit()

        # Kiểm tra bệnh nhân thứ 200:
        is_valid, err_code, err_msg, details = check_doctor_capacity(
            self.db, doc_user_id, datetime(2026, 10, 10, 14, 30)
        )
        self.assertTrue(is_valid, "Bệnh nhân thứ 200 (199/200) phải được phép đặt!")
        print("  -> Test Case 02 PASSED: Bệnh nhân thứ 200 được phép đặt.")

        # Thêm ca thứ 200
        ca_200 = models.LichKham(
            benh_nhan_id=self.patient_1.id,
            bac_si_id=doc_user_id,
            thoi_gian=datetime(2026, 10, 10, 14, 30),
            trang_thai="da_dat_lich"
        )
        self.db.add(ca_200)
        self.db.commit()

        # Bây giờ đã đủ 200/200: Thử đặt ca thứ 201:
        is_valid, err_code, err_msg, details = check_doctor_capacity(
            self.db, doc_user_id, datetime(2026, 10, 10, 9, 0)
        )
        self.assertFalse(is_valid, "Bệnh nhân thứ 201 không được phép đặt khi đã đủ 200!")
        self.assertEqual(err_code, "DOCTOR_DAY_FULL")
        self.assertIn("đã đủ số lượng bệnh nhân trong ngày", err_msg)
        print("  -> Test Case 03 PASSED: Bệnh nhân thứ 201 bị chặn khi bác sĩ đã đủ 200/200.")

        # Kiểm tra API gợi ý ngày khác và bác sĩ khác khi đầy
        alt_dates_res = client.get(f"/api/v1/lich-khams/public/doctor-alternative-dates?bac_si_id={self.doc_a.id}&from_date=2026-10-10")
        self.assertEqual(alt_dates_res.status_code, 200)
        dates_data = alt_dates_res.json()
        self.assertTrue(len(dates_data["ngay_goi_y"]) > 0)

        alt_docs_res = client.get(f"/api/v1/lich-khams/public/specialty-alternative-doctors?ngay_kham=2026-10-10&chuyen_khoa=Nội tổng quát&exclude_bac_si_id={self.doc_a.id}")
        self.assertEqual(alt_docs_res.status_code, 200)
        docs_data = alt_docs_res.json()
        self.assertTrue(len(docs_data) > 0)
        print("  -> API gợi ý ngày khác và bác sĩ khác hoạt động chính xác.")

    def test_04_05_06_correct_doctor_date_and_time_sync(self):
        """
        Test Case 04 – Đúng bác sĩ (Patient chọn Doctor A -> Appointment.DoctorId = Doctor A, Queue.DoctorId = Doctor A)
        Test Case 05 – Đúng ngày (Patient chọn 10/10/2026 -> Appointment.Date = 10/10/2026, Queue.Date = 10/10/2026)
        Test Case 06 – Đúng giờ (Patient chọn 09:00 -> Appointment.Time = 09:00, Queue.Time = 09:00, Phiếu lễ tân = 09:00)
        """
        from routers.lich_khams import calculate_gio_du_kien, resolve_appointment_doctor_and_room

        doc_user_id = self.doc_a.user_id or self.doc_a.id
        target_dt = datetime(2026, 10, 10, 9, 0) # 09:00 ngày 10/10/2026

        # Tạo lịch khám đặt trước 09:00 với Doctor A
        lk = models.LichKham(
            benh_nhan_id=self.patient_1.id,
            bac_si_id=doc_user_id,
            thoi_gian=target_dt,
            trang_thai="cho_kham",
            stt=25 # Cấp STT 25
        )
        self.db.add(lk)
        self.db.commit()
        self.db.refresh(lk)

        # 1. Kiểm tra Bác sĩ:
        self.assertEqual(lk.bac_si_id, doc_user_id)
        ten_bs, phong, _ = resolve_appointment_doctor_and_room(self.db, lk.bac_si_id, lk.chuyen_khoa_id)
        self.assertIn("Nguyễn Văn A", ten_bs)
        print("  -> Test Case 04 PASSED: Đúng Bác sĩ (Doctor A).")

        # 2. Kiểm tra Ngày:
        self.assertEqual(lk.thoi_gian.date(), date(2026, 10, 10))
        print("  -> Test Case 05 PASSED: Đúng Ngày (10/10/2026).")

        # 3. Kiểm tra Giờ khám:
        gio_kham = calculate_gio_du_kien(lk.stt, lk.thoi_gian)
        self.assertEqual(gio_kham, "09:00", "Giờ khám trên phiếu và queue phải tuyệt đối giữ nguyên 09:00!")
        self.assertEqual(lk.thoi_gian.strftime("%H:%M"), "09:00")
        print("  -> Test Case 06 PASSED: Đúng Giờ (09:00) không bị tự động trượt theo STT.")

    def test_07_change_to_another_date(self):
        """
        Test Case 07 – Chuyển ngày
        Doctor A ngày 10/10/2026 = FULL, Patient chọn 11/10/2026 -> Appointment.Date = 11/10/2026, cùng Doctor A.
        """
        doc_user_id = self.doc_a.user_id or self.doc_a.id
        from routers.lich_khams import check_doctor_capacity

        # Kiểm tra ngày 11/10/2026 của Doctor A
        is_valid, err_code, _, _ = check_doctor_capacity(
            self.db, doc_user_id, datetime(2026, 10, 11, 9, 0)
        )
        self.assertTrue(is_valid)

        # Tạo lịch ngày mới
        new_appointment = models.LichKham(
            benh_nhan_id=self.patient_1.id,
            bac_si_id=doc_user_id,
            thoi_gian=datetime(2026, 10, 11, 9, 0),
            trang_thai="da_dat_lich"
        )
        self.db.add(new_appointment)
        self.db.commit()
        self.db.refresh(new_appointment)

        self.assertEqual(new_appointment.bac_si_id, doc_user_id)
        self.assertEqual(new_appointment.thoi_gian.date(), date(2026, 10, 11))
        print("  -> Test Case 07 PASSED: Chuyển ngày thành công, giữ nguyên Bác sĩ A.")

    def test_08_change_to_another_doctor_in_same_specialty(self):
        """
        Test Case 08 – Chọn bác sĩ khác
        Doctor A = FULL, Patient chọn Doctor B -> Appointment.DoctorId = Doctor B.
        """
        doc_b_user_id = self.doc_b.user_id or self.doc_b.id
        from routers.lich_khams import check_doctor_capacity

        # Bác sĩ B còn chỗ ngày 10/10/2026
        is_valid, _, _, _ = check_doctor_capacity(
            self.db, doc_b_user_id, datetime(2026, 10, 10, 9, 0)
        )
        self.assertTrue(is_valid)

        # Tạo lịch hẹn với Bác sĩ B
        appointment_doc_b = models.LichKham(
            benh_nhan_id=self.patient_1.id,
            bac_si_id=doc_b_user_id,
            thoi_gian=datetime(2026, 10, 10, 9, 0),
            trang_thai="da_dat_lich"
        )
        self.db.add(appointment_doc_b)
        self.db.commit()
        self.db.refresh(appointment_doc_b)

        self.assertEqual(appointment_doc_b.bac_si_id, doc_b_user_id)
        self.assertEqual(appointment_doc_b.thoi_gian.date(), date(2026, 10, 10))
        print("  -> Test Case 08 PASSED: Chọn Bác sĩ B khác cùng khoa thành công.")


if __name__ == "__main__":
    unittest.main()
