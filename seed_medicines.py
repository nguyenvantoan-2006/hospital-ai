"""
seed_medicines.py — Nạp thêm danh mục Thuốc tân dược và Vật tư y tế vào kho thuốc (Hospital-AI / Clinova)
"""

import sys
import io
import os
from dotenv import load_dotenv

# Đảm bảo in tiếng Việt trên console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from database import SessionLocal
import models

load_dotenv()

# Danh mục thuốc và vật tư y tế bổ sung
NEW_MEDICINES_AND_SUPPLIES = [
    # ─── 1. VẬT TƯ Y TẾ TIÊU CHUẨN ──────────────────────────────────────────
    {
        "ten_thuoc": "Nước muối sinh lý NaCl 0.9% (Chai 500ml)",
        "don_vi_tinh": "Chai",
        "gia_nhap": 10000.0,
        "don_gia": 18000.0,
        "so_luong_ton": 300
    },
    {
        "ten_thuoc": "Bơm tiêm vô trùng 5ml (Kim tiêm y tế)",
        "don_vi_tinh": "Cái",
        "gia_nhap": 1500.0,
        "don_gia": 3000.0,
        "so_luong_ton": 1000
    },
    {
        "ten_thuoc": "Bơm tiêm vô trùng 10ml",
        "don_vi_tinh": "Cái",
        "gia_nhap": 2000.0,
        "don_gia": 4000.0,
        "so_luong_ton": 800
    },
    {
        "ten_thuoc": "Băng gạc y tế tiệt trùng 10x10cm",
        "don_vi_tinh": "Gói",
        "gia_nhap": 5000.0,
        "don_gia": 9000.0,
        "so_luong_ton": 500
    },
    {
        "ten_thuoc": "Cồn y tế 70 độ sát khuẩn (Chai 500ml)",
        "don_vi_tinh": "Chai",
        "gia_nhap": 15000.0,
        "don_gia": 25000.0,
        "so_luong_ton": 200
    },
    {
        "ten_thuoc": "Dung dịch sát trùng Povidone Iodine 10% (100ml)",
        "don_vi_tinh": "Chai",
        "gia_nhap": 20000.0,
        "don_gia": 32000.0,
        "so_luong_ton": 150
    },
    {
        "ten_thuoc": "Khẩu trang y tế 4 lớp kháng khuẩn N95",
        "don_vi_tinh": "Hộp 20 chiếc",
        "gia_nhap": 50000.0,
        "don_gia": 85000.0,
        "so_luong_ton": 100
    },
    {
        "ten_thuoc": "Găng tay y tế cao su có bột",
        "don_vi_tinh": "Hộp 100 chiếc",
        "gia_nhap": 75000.0,
        "don_gia": 120000.0,
        "so_luong_ton": 80
    },
    {
        "ten_thuoc": "Cuộn băng dính lụa y tế Urgo",
        "don_vi_tinh": "Cuộn",
        "gia_nhap": 12000.0,
        "don_gia": 20000.0,
        "so_luong_ton": 350
    },
    {
        "ten_thuoc": "Dây truyền dịch y tế vô trùng có kim bướm",
        "don_vi_tinh": "Bộ",
        "gia_nhap": 8000.0,
        "don_gia": 15000.0,
        "so_luong_ton": 400
    },

    # ─── 2. THUỐC TÂN DƯỢC & ĐẶC TRỊ CHUYÊN KHOA ─────────────────────────────
    {
        "ten_thuoc": "Ibuprofen 400mg (Kháng viêm, giảm đau hạ sốt)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 1500.0,
        "don_gia": 3000.0,
        "so_luong_ton": 600
    },
    {
        "ten_thuoc": "Augmentin 1g (Kháng sinh phối hợp)",
        "don_vi_tinh": "Hộp 14 viên",
        "gia_nhap": 180000.0,
        "don_gia": 240000.0,
        "so_luong_ton": 90
    },
    {
        "ten_thuoc": "Telfast HD 180mg (Thuốc chống dị ứng)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 7000.0,
        "don_gia": 12000.0,
        "so_luong_ton": 300
    },
    {
        "ten_thuoc": "Tobradex nhỏ mắt (Kháng sinh/kháng viêm)",
        "don_vi_tinh": "Lọ 5ml",
        "gia_nhap": 48000.0,
        "don_gia": 68000.0,
        "so_luong_ton": 110
    },
    {
        "ten_thuoc": "Smecta 3g (Bột pha trị tiêu chảy)",
        "don_vi_tinh": "Gói",
        "gia_nhap": 3500.0,
        "don_gia": 6000.0,
        "so_luong_ton": 500
    },
    {
        "ten_thuoc": "Salbutamol 2mg (Giãn phế quản trị hen suyễn)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 800.0,
        "don_gia": 1500.0,
        "so_luong_ton": 400
    },
    {
        "ten_thuoc": "Amlodipin 5mg (Thuốc điều trị tăng huyết áp)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 1200.0,
        "don_gia": 2500.0,
        "so_luong_ton": 550
    },
    {
        "ten_thuoc": "Metformin 850mg (Thuốc điều trị đái tháo đường)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 1800.0,
        "don_gia": 3200.0,
        "so_luong_ton": 600
    },
    {
        "ten_thuoc": "Voltaren Emulgel 20g (Gel bôi giảm đau khớp)",
        "don_vi_tinh": "Tuýp",
        "gia_nhap": 65000.0,
        "don_gia": 92000.0,
        "so_luong_ton": 85
    },
]

def seed_medicines():
    db = SessionLocal()
    try:
        added_count = 0
        updated_count = 0

        print(f"Bắt đầu nạp dữ liệu Thuốc & Vật tư y tế vào kho...")
        for item in NEW_MEDICINES_AND_SUPPLIES:
            existing = db.query(models.Thuoc).filter(models.Thuoc.ten_thuoc == item["ten_thuoc"]).first()
            if existing:
                existing.don_vi_tinh = item["don_vi_tinh"]
                existing.gia_nhap = item["gia_nhap"]
                existing.don_gia = item["don_gia"]
                existing.so_luong_ton = item["so_luong_ton"]
                updated_count += 1
                print(f" [CẬP NHẬT] {item['ten_thuoc']} | Tồn: {item['so_luong_ton']} | Giá: {item['don_gia']:,.0f}đ")
            else:
                new_thuoc = models.Thuoc(
                    ten_thuoc=item["ten_thuoc"],
                    don_vi_tinh=item["don_vi_tinh"],
                    gia_nhap=item["gia_nhap"],
                    don_gia=item["don_gia"],
                    so_luong_ton=item["so_luong_ton"]
                )
                db.add(new_thuoc)
                added_count += 1
                print(f" [THÊM MỚI] {item['ten_thuoc']} | ĐVT: {item['don_vi_tinh']} | Tồn: {item['so_luong_ton']} | Giá: {item['don_gia']:,.0f}đ")

        db.commit()

        total = db.query(models.Thuoc).count()
        print(f"\n========================================================")
        print(f"HOÀN THÀNH NẠP DỮ LIỆU KHO THUỐC:")
        print(f" - Thêm mới: {added_count} mục")
        print(f" - Cập nhật: {updated_count} mục")
        print(f" - Tổng số thuốc & vật tư hiện có trong DB: {total} mục")
        print(f"========================================================")
    except Exception as e:
        db.rollback()
        print(f"Lỗi khi nạp dữ liệu: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_medicines()
