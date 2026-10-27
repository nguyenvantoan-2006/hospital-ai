# database.py
# Thiết lập kết nối CSDL MySQL bằng SQLAlchemy

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Tải biến môi trường từ file .env
load_dotenv()

# ─── CẤU HÌNH KẾT NỐI CƠ SỞ DỮ LIỆU ──────────────────────────────────────────
# Ưu tiên đọc từ biến môi trường DATABASE_URL; nếu không có sẽ dùng SQLite nội bộ an toàn
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL or DATABASE_URL.strip() == "":
    DATABASE_URL = "sqlite:///./clinic.db"
    print("ℹ️ DATABASE_URL chưa được cung cấp trong .env, sử dụng SQLite nội bộ an toàn: clinic.db")


# ─── ENGINE ──────────────────────────────────────────────────────────────────
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine_kwargs = {
    "echo": False,
    "connect_args": connect_args
}
if not DATABASE_URL.startswith("sqlite"):
    engine_kwargs["pool_pre_ping"] = True

engine = create_engine(DATABASE_URL, **engine_kwargs)

# ─── SESSION FACTORY ─────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ─── BASE CLASS ──────────────────────────────────────────────────────────────
Base = declarative_base()


# ─── DEPENDENCY INJECTION (dùng trong FastAPI Router) ────────────────────────
def get_db():
    """
    Generator function cung cấp DB Session cho mỗi request.
    Đảm bảo session luôn được đóng sau khi request hoàn tất.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
