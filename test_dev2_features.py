# test_dev2_features.py
# Kịch bản kiểm thử toàn diện các module của DEV 2

import os
import sys
import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Thiết lập SQLite in-memory cho test
from database import Base
import models
import schemas

class TestDev2Backend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.db = self.Session()

    def tearDown(self):
        self.db.close()

    def test_01_models_ailog_and_huong_dan(self):
        """Kiểm tra model AILog và huong_dan_sau_kham trong PhieuKham."""
        # Tạo bệnh nhân và lịch khám
        bn = models.BenhNhan(ho_ten="Nguyễn Văn Test", so_dien_thoai="0987654321")
        self.db.add(bn)
        self.db.commit()

        lk = models.LichKham(benh_nhan_id=bn.id, thoi_gian=datetime.now(), trang_thai="cho_kham")
        self.db.add(lk)
        self.db.commit()

        # Tạo phiếu khám với huong_dan_sau_kham
        pk = models.PhieuKham(
            lich_kham_id=lk.id,
            trieu_chung="Ho khan",
            chan_doan="Viêm họng nhẹ",
            huong_dan_sau_kham="Uống nhiều nước ấm, nghỉ ngơi 2 ngày."
        )
        self.db.add(pk)
        self.db.commit()

        self.assertIsNotNone(pk.id)
        self.assertEqual(pk.huong_dan_sau_kham, "Uống nhiều nước ấm, nghỉ ngơi 2 ngày.")

        # Tạo bản ghi AILog
        ai_log = models.AILog(
            user_id=1,
            chuc_nang="ai_summary",
            prompt_masked="Tóm tắt bệnh nhân N*** A",
            response_text="Bệnh nhân có tiền sử viêm họng",
            model_name="gemini-1.5-flash",
            response_time_ms=1200,
            trang_thai="success"
        )
        self.db.add(ai_log)
        self.db.commit()

        self.assertIsNotNone(ai_log.id)
        self.assertEqual(ai_log.chuc_nang, "ai_summary")
        self.assertEqual(ai_log.response_time_ms, 1200)

    def test_02_thuoc_crud_and_stock(self):
        """Kiểm tra CRUD thuốc và quản lý số lượng tồn kho."""
        thuoc = models.Thuoc(
            ten_thuoc="Amoxicillin 500mg",
            don_vi_tinh="Viên",
            gia_nhap=1500.0,
            don_gia=3000.0,
            so_luong_ton=50
        )
        self.db.add(thuoc)
        self.db.commit()

        self.assertIsNotNone(thuoc.id)
        self.assertEqual(thuoc.so_luong_ton, 50)

        # Kiểm tra lọc cảnh báo tồn kho thấp
        thuoc_het = models.Thuoc(
            ten_thuoc="Vitamin C 1000mg",
            don_vi_tinh="Ống",
            gia_nhap=5000.0,
            don_gia=8000.0,
            so_luong_ton=4
        )
        self.db.add(thuoc_het)
        self.db.commit()

        low_stocks = self.db.query(models.Thuoc).filter(models.Thuoc.so_luong_ton < 10).all()
        self.assertEqual(len(low_stocks), 1)
        self.assertEqual(low_stocks[0].ten_thuoc, "Vitamin C 1000mg")

    def test_03_prescription_and_stock_deduction(self):
        """Kiểm tra kê đơn và trừ tồn kho an toàn."""
        # 1. Tạo thuốc
        t1 = models.Thuoc(ten_thuoc="Paracetamol 500mg", don_vi_tinh="Viên", don_gia=2000.0, so_luong_ton=100)
        self.db.add(t1)
        self.db.commit()

        # 2. Tạo bệnh nhân, lịch khám
        bn = models.BenhNhan(ho_ten="Trần Thị B", so_dien_thoai="0911223344")
        self.db.add(bn)
        self.db.commit()

        lk = models.LichKham(benh_nhan_id=bn.id, thoi_gian=datetime.now(), trang_thai="cho_kham")
        self.db.add(lk)
        self.db.commit()

        # 3. Kê đơn
        pk = models.PhieuKham(
            lich_kham_id=lk.id,
            trieu_chung="Sốt",
            chan_doan="Cảm cúm",
            huong_dan_sau_kham="Uống thuốc sau ăn"
        )
        self.db.add(pk)
        self.db.commit()

        dt = models.DonThuoc(phieu_kham_id=pk.id, thuoc_id=t1.id, so_luong=10, lieu_dung="2 viên/ngày")
        self.db.add(dt)
        self.db.commit()

        # 4. Trừ kho khi phát thuốc
        self.assertEqual(t1.so_luong_ton, 100)
        t1.so_luong_ton -= dt.so_luong
        self.db.commit()

        # Kiểm tra số lượng tồn sau khi trừ
        t1_reload = self.db.query(models.Thuoc).filter(models.Thuoc.id == t1.id).first()
        self.assertEqual(t1_reload.so_luong_ton, 90)

if __name__ == "__main__":
    unittest.main()
