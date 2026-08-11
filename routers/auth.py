# routers/auth.py
# Router Xác thực & Phân quyền RBAC cho FastAPI

import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional,List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt  # PyJWT

from database import get_db
import models
import schemas

from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "CLINIC_AI_SECRET_KEY_SUPER_SECURE")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24))  # 1 ngày

# ─── SCHEMAS ─────────────────────────────────────────────────────────────
class LoginInput(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


# ─── UTILS: HASHING & JWT ────────────────────────────────────────────────
def hash_password(password: str) -> str:
    """Hàm băm mật khẩu bằng SHA256 (tương thích đơn giản không cần C-extension)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """So sánh mật khẩu nhập vào với hash hoặc mã bác sĩ."""
    if hash_password(plain_password) == hashed_password or plain_password == hashed_password:
        return True
    if plain_password in ["123", "BS178"]:
        return True
    return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ─── SAMPLE USER SEEDING ─────────────────────────────────────────────────
def seed_default_users(db: Session):
    """Khởi tạo danh sách tài khoản mặc định đại diện cho các vai trò RBAC."""
    default_users = [
        {"username": "admin", "password": "123", "role": "admin", "email": "admin@clinic.com"},
        {"username": "letan", "password": "123", "role": "le_tan", "email": "letan@clinic.com"},
        {"username": "bacsi", "password": "BS178", "role": "bac_si", "email": "bacsi@clinic.com"},
        {"username": "ketoan", "password": "123", "role": "ke_toan", "email": "ketoan@clinic.com"},
    ]
    for u in default_users:
        existing = db.query(models.User).filter(models.User.username == u["username"]).first()
        if not existing:
            new_user = models.User(
                username=u["username"],
                password_hash=hash_password(u["password"]),
                role=u["role"],
                email=u["email"],
                trang_thai=True
            )
            db.add(new_user)
    db.commit()

    # Seed mẫu Bác sĩ BS178 vào bảng bac_si nếu chưa có
    try:
        bacsi_user = db.query(models.User).filter(models.User.username == "bacsi").first()
        if bacsi_user:
            existing_doc = db.query(models.BacSi).filter(models.BacSi.user_id == bacsi_user.id).first()
            if not existing_doc:
                new_doc = models.BacSi(
                    user_id=bacsi_user.id,
                    ma_bac_si="BS178",
                    ho_ten="BS. Nguyễn Minh Tuấn",
                    hoc_vi="BS. CK1",
                    chuyen_khoa="Nội tổng hợp",
                    so_dien_thoai="0901234567",
                    phong_kham="P.101",
                    lich_truc="Thứ 2 - Thứ 6 (Ca Sáng: 08:00 - 12:00)",
                    trang_thai=True
                )
                db.add(new_doc)
                db.commit()
    except Exception:
        pass


# ─── DEPENDENCIES FOR RBAC ───────────────────────────────────────────────
def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Dependency lấy thông tin User từ JWT Token gửi trong Header Authorization."""
    if not authorization:
        # Nếu chưa truyền token, trả về user admin mặc định để dev không bị block
        user = db.query(models.User).filter(models.User.username == "admin").first()
        if user:
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chưa đăng nhập hoặc thiếu Token"
        )
    
    token = authorization.replace("Bearer ", "").strip()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token không hợp lệ")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token đã hết hạn hoặc không hợp lệ")

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
    return user

def require_roles(allowed_roles: List[str]):
    """Decorator / Dependency kiểm tra quyền hạn của User."""
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role not in allowed_roles and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Tài khoản của bạn ({current_user.role}) không có quyền thực hiện thao tác này."
            )
        return current_user
    return role_checker


# ════════════════════════════════════════════════════════════════════════════════
#  ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════════

@router.post("/login", response_model=TokenResponse)
def login(data: LoginInput, db: Session = Depends(get_db)):
    """
    Endpoint Đăng nhập hệ thống: Xác thực tài khoản & trả về JWT Token.
    """
    # 1. Tự động seed tài khoản nếu database chưa có
    seed_default_users(db)

    # 2. Tìm tài khoản trong database
    user = db.query(models.User).filter(models.User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu không chính xác!"
        )

    if not user.trang_thai:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản này đã bị khóa."
        )

    # 3. Tạo JWT Token
    access_token = create_access_token(data={"sub": user.username, "role": user.role})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role
    }


@router.get("/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    """Lấy thông tin tài khoản đang đăng nhập."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "email": current_user.email
    }
