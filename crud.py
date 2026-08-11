# crud.py
from sqlalchemy.orm import Session
import models
import schemas

def get_benh_nhan(db: Session, benh_nhan_id: int):
    """Lấy thông tin chi tiết 1 bệnh nhân theo ID."""
    return db.query(models.BenhNhan).filter(models.BenhNhan.id == benh_nhan_id).first()

def get_benh_nhans(db: Session, skip: int = 0, limit: int = 100):
    """Lấy danh sách bệnh nhân hỗ trợ phân trang (skip, limit)."""
    return db.query(models.BenhNhan).offset(skip).limit(limit).all()

def create_benh_nhan(db: Session, benh_nhan: schemas.BenhNhanCreate):
    """Thêm một bệnh nhân mới vào CSDL."""
    db_benh_nhan = models.BenhNhan(**benh_nhan.model_dump())
    db.add(db_benh_nhan)
    db.commit()
    db.refresh(db_benh_nhan)
    return db_benh_nhan
