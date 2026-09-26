#!/usr/bin/env python3
"""
startup.py - Script khởi tạo môi trường production cho Hospital-AI
Chạy tự động trên Railway trước khi uvicorn start.
Thực hiện:
  1. Tạo tables nếu chưa có
  2. Seed chuyên khoa + bác sĩ nếu DB trống
  3. Seed thuốc nếu chưa có
"""
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

print("=" * 60)
print("CLINOVA Hospital-AI — Startup Initialization")
print("=" * 60)

try:
    from database import engine, Base, SessionLocal
    import models

    # 1. Tạo bảng
    print("[1/3] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("  ✓ Tables ready")

    db = SessionLocal()

    # 2. Seed chuyên khoa + bác sĩ nếu chưa có
    spec_count = db.query(models.ChuyenKhoa).count()
    if spec_count == 0:
        print("[2/3] Seeding specialties and doctors (first time)...")
        try:
            import seed_specialties_and_doctors
            seed_specialties_and_doctors.run_seed(db)
            print("  ✓ Specialties and doctors seeded")
        except Exception as e:
            print(f"  ! Seed specialties error: {e}")
    else:
        print(f"[2/3] Specialties already exist ({spec_count} records) — skip seed")

    # 3. Seed thuốc nếu chưa có
    thuoc_count = db.query(models.Thuoc).count()
    if thuoc_count == 0:
        print("[3/3] Seeding medicines...")
        try:
            import seed_medicines
            seed_medicines.run_seed(db)
            print("  ✓ Medicines seeded")
        except Exception as e:
            print(f"  ! Seed medicines error: {e}")
    else:
        print(f"[3/3] Medicines already exist ({thuoc_count} records) — skip seed")

    db.close()
    print("=" * 60)
    print("Startup complete! Starting uvicorn server...")
    print("=" * 60)

except Exception as e:
    print(f"STARTUP ERROR: {e}")
    # Không exit — để uvicorn vẫn chạy dù seed fail
