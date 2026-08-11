# database.py
# Thiết lập kết nối CSDL MySQL bằng SQLAlchemy

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Tải biến môi trường từ file .env
load_dotenv()

# ─── CẤU HÌNH KẾT NỐI MYSQL ──────────────────────────────────────────────────
# Cú pháp: mysql+pymysql://<user>:<password>@<host>:<port>/<dbname>
DEFAULT_DB_URL = "mysql+pymysql://root:password@localhost:3306/hospital_ai"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)


# ─── ENGINE ──────────────────────────────────────────────────────────────────
engine = create_engine(
    DATABASE_URL,
    echo=True,          # Log câu lệnh SQL ra console
    pool_pre_ping=True, # Tự động kiểm tra và phục hồi kết nối MySQL bị timeout
)

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
