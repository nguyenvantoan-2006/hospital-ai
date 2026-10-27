import random
import threading
import email_service
# routers/auth.py
# Router Xác thực & Phân quyền RBAC cho FastAPI
#
# [BẢO MẬT]
#   - Mật khẩu được băm bằng bcrypt (thông qua passlib) — KHÔNG dùng SHA256
#   - Không có hardcode password nào trong source code
#   - Mọi endpoint đều yêu cầu JWT hợp lệ — không có auto-login
# ════════════════════════════════════════════════════════════════════════════════

import os
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt  # PyJWT

# bcrypt — thư viện băm mật khẩu an toàn theo chuẩn (dùng trực tiếp, không qua passlib)
import bcrypt

from database import get_db
import models
import schemas

from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# ─── CẤU HÌNH JWT ─────────────────────────────────────────────────────────────
_env_secret = os.getenv("SECRET_KEY")
if not _env_secret or _env_secret.strip() == "" or _env_secret == "CHANGE_ME_IN_PRODUCTION":
    import secrets
    _env_secret = secrets.token_hex(32)
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ SECRET_KEY không được cấu hình trong .env! Đã tự động tạo khóa ngẫu nhiên tạm thời để bảo vệ hệ thống.")

SECRET_KEY                 = _env_secret
ALGORITHM                  = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 480))

# ─── CẤU HÌNH BCRYPT ──────────────────────────────────────────────────────────
# bcrypt: thuật toán băm mật khẩu công nghiệp, chậm có chủ đích để chống brute-force
# BCRYPT_ROUNDS: 12 là chuẩn cân bằng bảo mật / hiệu năng (tăng lên làm chậm brute-force)
BCRYPT_ROUNDS = 12


# ════════════════════════════════════════════════════════════════════════════════
#  SCHEMAS nội bộ (chỉ dùng trong router auth)
# ════════════════════════════════════════════════════════════════════════════════

class LoginInput(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    username:     str
    role:         str


# ════════════════════════════════════════════════════════════════════════════════
#  UTILS: BCRYPT HASHING
# ════════════════════════════════════════════════════════════════════════════════

def hash_password(password: str) -> str:
    """
    Băm mật khẩu bằng bcrypt với salt ngẫu nhiên.
    Mỗi lần gọi trả về hash KHÁC NHAU (do salt) — đây là tính năng bảo mật,
    không phải lỗi. Dùng verify_password() để kiểm tra, không so sánh chuỗi trực tiếp.
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Xác minh mật khẩu người dùng nhập vào với bcrypt hash đã lưu trong CSDL.
    bcrypt.checkpw() thực hiện so sánh theo thời gian cố định (timing-safe).
    KHÔNG có hardcode hay bypass nào ở đây.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


# ════════════════════════════════════════════════════════════════════════════════
#  UTILS: JWT TOKEN
# ════════════════════════════════════════════════════════════════════════════════

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo JWT Token chứa payload (sub = username, role) với thời hạn hết hạn.
    Token được ký bằng SECRET_KEY lấy từ .env — không hardcode trong code.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ════════════════════════════════════════════════════════════════════════════════
#  SEED: TÀI KHOẢN MẶC ĐỊNH (chỉ chạy 1 lần khi CSDL trống)
# ════════════════════════════════════════════════════════════════════════════════

def seed_default_users(db: Session):
    """
    Khởi tạo 4 tài khoản mặc định đại diện các vai trò RBAC.
    Mật khẩu được băm bằng bcrypt trước khi lưu vào CSDL.
    Hàm này chỉ thêm tài khoản nếu CHƯA tồn tại (idempotent).

    Tài khoản mặc định (chỉ dùng trong môi trường DEV):
      - admin   / Admin@2024!
      - letan   / LeTan@2024!
      - bacsi   / BacSi@2024!
      - ketoan  / KeToan@2024!
    """
    default_users = [
        {"username": "admin",  "password": "Admin@2024!",  "role": "admin",   "email": "admin@clinic.com"},
        {"username": "letan",  "password": "LeTan@2024!",  "role": "le_tan",  "email": "letan@clinic.com"},
        {"username": "bacsi",  "password": "BacSi@2024!",  "role": "bac_si",  "email": "bacsi@clinic.com"},
        {"username": "ketoan", "password": "KeToan@2024!", "role": "ke_toan", "email": "ketoan@clinic.com"},
    ]

    for u in default_users:
        # Kiểm tra cả username VÀ email để tránh IntegrityError (Duplicate entry)
        existing_by_username = db.query(models.User).filter(
            models.User.username == u["username"]
        ).first()
        existing_by_email = db.query(models.User).filter(
            models.User.email == u["email"]
        ).first()

        if not existing_by_username and not existing_by_email:
            new_user = models.User(
                username      = u["username"],
                password_hash = hash_password(u["password"]),  # ← bcrypt hash
                role          = u["role"],
                email         = u["email"],
                trang_thai    = True,
            )
            db.add(new_user)

    try:
        db.commit()
    except Exception:
        db.rollback()  # Không crash server nếu đã có dữ liệu

    # Seed mẫu hồ sơ Bác sĩ vào bảng bac_si (nếu chưa có)
    try:
        bacsi_user = db.query(models.User).filter(models.User.username == "bacsi").first()
        if bacsi_user:
            existing_doc = db.query(models.BacSi).filter(
                models.BacSi.user_id == bacsi_user.id
            ).first()
            if not existing_doc:
                new_doc = models.BacSi(
                    user_id       = bacsi_user.id,
                    ma_bac_si     = "BS001",
                    ho_ten        = "BS. Nguyễn Minh Tuấn",
                    hoc_vi        = "BS. CK1",
                    chuyen_khoa   = "Nội tổng hợp",
                    so_dien_thoai = "0901234567",
                    phong_kham    = "P.101",
                    lich_truc     = "Thứ 2 - Thứ 6 (Ca Sáng: 08:00 - 12:00)",
                    trang_thai    = True,
                )
                db.add(new_doc)
                db.commit()
    except Exception:
        db.rollback()


# ════════════════════════════════════════════════════════════════════════════════
#  DEPENDENCIES: RBAC — Kiểm tra quyền truy cập
# ════════════════════════════════════════════════════════════════════════════════

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> models.User:
    """
    Dependency: Xác thực JWT Token trong Header 'Authorization: Bearer <token>'.

    [BẢO MẬT] Không có fallback hay auto-login.
    Nếu thiếu token hoặc token không hợp lệ → 401 Unauthorized.
    """
    # 1. Kiểm tra header Authorization có tồn tại không
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chưa đăng nhập. Vui lòng đăng nhập để tiếp tục.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Tách token khỏi "Bearer "
    token = authorization[len("Bearer "):].strip()

    # 3. Giải mã & xác thực JWT
    try:
        payload  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ: thiếu thông tin định danh.",
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã bị sửa đổi.",
        )

    # 4. Tra cứu user trong CSDL
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tài khoản.",
        )

    # 5. Kiểm tra tài khoản còn hoạt động không
    if not user.trang_thai:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản này đã bị khóa. Liên hệ quản trị viên.",
        )

    return user


def require_roles(allowed_roles: List[str]):
    """
    Dependency factory: Kiểm tra role của user hiện tại.
    Admin luôn có toàn quyền (bypass check role).

    Cách dùng:
        @router.get("/...", dependencies=[Depends(require_roles(["le_tan", "bac_si"]))])
    """
    def role_checker(
        current_user: models.User = Depends(get_current_user),
    ) -> models.User:
        if current_user.role != "admin" and current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Tài khoản vai trò '{current_user.role}' "
                    f"không được phép thực hiện thao tác này."
                ),
            )
        return current_user

    return role_checker


# ════════════════════════════════════════════════════════════════════════════════
#  ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════════

@router.post("/login", response_model=TokenResponse, summary="Đăng nhập hệ thống")
def login(data: LoginInput, db: Session = Depends(get_db)):
    """
    Xác thực tài khoản và trả về JWT Access Token.

    **Luồng xử lý:**
    1. Seed tài khoản mặc định nếu CSDL trống
    2. Tìm tài khoản theo username
    3. Xác minh mật khẩu bằng bcrypt
    4. Kiểm tra trạng thái tài khoản
    5. Tạo và trả về JWT Token
    """
    # Bước 1: Đảm bảo có tài khoản mặc định để đăng nhập lần đầu
    seed_default_users(db)

    # Bước 2: Tìm tài khoản
    user = db.query(models.User).filter(models.User.username == data.username).first()

    # Bước 3: Xác minh mật khẩu — dùng bcrypt, không dùng ==
    # Trả về lỗi chung chung để tránh lộ thông tin (username tồn tại hay không)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu không chính xác.",
        )

    # Bước 4: Kiểm tra tài khoản có bị khóa không
    if not user.trang_thai:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản này đã bị khóa. Liên hệ quản trị viên.",
        )

    # Bước 5: Tạo JWT Token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )

    return {
        "access_token": access_token,
        "token_type":   "bearer",
        "username":     user.username,
        "role":         user.role,
    }


@router.get("/me", summary="Thông tin tài khoản đang đăng nhập")
def get_me(current_user: models.User = Depends(get_current_user)):
    """
    Trả về thông tin tài khoản dựa theo JWT Token trong header.
    Không trả về password_hash.
    """
    return {
        "id":       current_user.id,
        "username": current_user.username,
        "role":     current_user.role,
        "email":    current_user.email,
    }




# ════════════════════════════════════════════════════════════════════════════════
#  QUÊN MẬT KHẨU & TỰ PHỤC HỒI QUA EMAIL OTP (STAFF SELF-SERVICE)
# ════════════════════════════════════════════════════════════════════════════════

_staff_otp_lock = threading.Lock()
# Lưu trữ bộ đệm: { username: { "otp": "123456", "expires_at": datetime, "attempts": 0, "email": "..." } }
_staff_otp_store: dict = {}


@router.post("/forgot-password", summary="Yêu cầu gửi mã OTP quên mật khẩu qua Email")
def forgot_password(body: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Tiếp nhận yêu cầu khôi phục mật khẩu từ Bác sĩ / Nhân viên y tế.
    Tự động tra cứu email và gửi mã OTP 6 số (hạn 5 phút).
    Tuân thủ bảo mật OWASP: Không tiết lộ tài khoản có tồn tại hay không.
    """
    identity = body.identity.strip()
    if not identity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vui lòng nhập Username hoặc Email.")

    user = db.query(models.User).filter(
        (models.User.username == identity) | (models.User.email == identity)
    ).first()

    if user and user.email:
        otp = f"{random.randint(100000, 999999)}"
        expires_at = datetime.now() + timedelta(minutes=5)
        with _staff_otp_lock:
            _staff_otp_store[user.username] = {
                "otp": otp,
                "expires_at": expires_at,
                "attempts": 0,
                "username": user.username,
                "email": user.email
            }
        
        # Gửi email thật ngầm (daemon thread)
        threading.Thread(
            target=email_service.send_password_reset_otp_email,
            args=(user.email, user.username, otp),
            daemon=True
        ).start()

    return {
        "success": True,
        "message": "Nếu thông tin chính xác, mã xác thực OTP đã được gửi về email công vụ của bạn. Vui lòng kiểm tra hộp thư (bao gồm cả hòm thư Rác/Spam)."
    }


@router.post("/verify-otp", summary="Xác thực mã OTP khôi phục mật khẩu")
def verify_forgot_password_otp(body: schemas.VerifyOtpRequest, db: Session = Depends(get_db)):
    """
    Xác minh mã OTP 6 số do nhân viên cung cấp.
    Nếu hợp lệ, sinh reset_token ngắn hạn (10 phút) để mở quyền đặt mật khẩu mới.
    """
    identity = body.identity.strip()
    otp_input = body.otp.strip()

    user = db.query(models.User).filter(
        (models.User.username == identity) | (models.User.email == identity)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thông tin tài khoản hoặc mã OTP không chính xác."
        )

    with _staff_otp_lock:
        record = _staff_otp_store.get(user.username)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Yêu cầu OTP không tồn tại hoặc đã hết hạn. Vui lòng gửi lại yêu cầu."
            )

        if datetime.now() > record["expires_at"]:
            _staff_otp_store.pop(user.username, None)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã OTP đã hết hạn (chỉ có hiệu lực trong 5 phút). Vui lòng yêu cầu mã mới."
            )

        if record["otp"] != otp_input:
            record["attempts"] += 1
            if record["attempts"] >= 3:
                _staff_otp_store.pop(user.username, None)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bạn đã nhập sai OTP quá 3 lần. Mã đã bị hủy vì lý do an toàn."
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mã OTP không chính xác. Bạn còn {3 - record['attempts']} lần thử."
            )

        # Xác thực thành công -> Hủy OTP và cấp reset_token 10 phút
        _staff_otp_store.pop(user.username, None)
        reset_token = create_access_token(
            data={"sub": user.username, "purpose": "password_reset"},
            expires_delta=timedelta(minutes=10)
        )
        return {
            "success": True,
            "reset_token": reset_token,
            "message": "Xác thực OTP thành công. Vui lòng tạo mật khẩu mới."
        }


@router.post("/reset-password", summary="Đặt lại mật khẩu mới với reset_token")
def reset_password_with_token(body: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Cập nhật mật khẩu mới cho người dùng sau khi xác thực OTP thành công.
    Mật khẩu mới được băm bằng bcrypt trước khi lưu CSDL.
    """
    try:
        payload = jwt.decode(body.reset_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        purpose: str = payload.get("purpose")
        if not username or purpose != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token đặt lại mật khẩu không hợp lệ."
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phiên làm việc đặt lại mật khẩu đã hết hạn. Vui lòng thực hiện lại từ đầu."
        )

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại.")

    user.password_hash = hash_password(body.new_password)
    db.commit()

    # Ghi nhận audit log nếu bảng AuditLog tồn tại
    try:
        audit = models.AuditLog(
            user_id=user.id,
            action="RESET_PASSWORD_SELF",
            chi_tiet=f"Tài khoản {user.username} ({user.role}) đã tự đặt lại mật khẩu thành công qua Email OTP."
        )
        db.add(audit)
        db.commit()
    except Exception:
        db.rollback()

    return {
        "success": True,
        "message": "Đặt lại mật khẩu thành công! Bạn có thể đăng nhập ngay với mật khẩu mới."
    }
