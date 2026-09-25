# 🚀 Hướng dẫn Deploy Hospital-AI lên Railway.app

## Yêu cầu
- Tài khoản [Railway.app](https://railway.app) (đăng nhập bằng GitHub)
- Code đã được push lên GitHub repo

---

## BƯỚC 1 — Push code lên GitHub

```bash
# Đảm bảo code mới nhất được commit
git add seed_specialties_and_doctors.py seed_medicines.py railway.toml requirements.txt
git commit -m "chore(deploy): add run_seed wrappers + update railway config"
git push origin feat/dieu-phoi-goi-kham-va-phan-cong-bs
```

> **Lưu ý:** Railway có thể deploy từ bất kỳ branch nào, không nhất thiết phải là `main`.

---

## BƯỚC 2 — Tạo Project trên Railway

1. Vào [railway.app](https://railway.app) → **New Project**
2. Chọn **"Deploy from GitHub repo"**
3. Chọn repo `hospital-ai`
4. Chọn branch cần deploy
5. Railway sẽ tự detect `railway.toml` và bắt đầu build

---

## BƯỚC 3 — Thêm MySQL Database

1. Trong project Railway, click **"+ New"** → **"Database"** → **"MySQL"**
2. Đợi MySQL khởi động (30-60 giây)
3. Click vào service MySQL → tab **"Variables"**
4. Copy giá trị `MYSQL_URL` (dạng: `mysql://user:pass@host:port/railway`)

---

## BƯỚC 4 — Cài biến môi trường cho App

Click vào service **App** (FastAPI) → tab **"Variables"** → thêm từng biến:

| Biến | Giá trị |
|------|---------|
| `DATABASE_URL` | Paste `MYSQL_URL` từ bước 3 (đổi `mysql://` → `mysql+pymysql://`) |
| `GEMINI_API_KEY` | API key Gemini của bạn |
| `SECRET_KEY` | Chuỗi bí mật JWT (copy từ `.env` local) |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `480` |
| `GMAIL_USER` | Email gửi OTP |
| `GMAIL_APP_PASSWORD` | App password Gmail (16 ký tự) |
| `SMTP_SERVER` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `EMAIL_SENDER_NAME` | `CLINOVA Smart Clinic` |

### ⚠️ Quan trọng về DATABASE_URL
Railway cung cấp URL dạng:
```
mysql://root:password@host.railway.internal:3306/railway
```
Phải đổi thành:
```
mysql+pymysql://root:password@host.railway.internal:3306/railway
```

---

## BƯỚC 5 — Deploy và kiểm tra Logs

Sau khi set biến → Railway tự động redeploy.
Xem **logs** trong tab "Deployments":
```
[1/3] Creating database tables... ✓
[2/3] Seeding specialties and doctors (first time)...
    37 chuyên khoa + 185 bác sĩ đang được seed...
    ✓ Specialties and doctors seeded
[3/3] Seeding medicines... ✓
Startup complete! Starting uvicorn server...
```

---

## BƯỚC 6 — Lấy URL Public

1. Tab **"Settings"** → **"Generate Domain"**
2. URL: `https://hospital-ai-production.up.railway.app`
3. Chia sẻ URL này cho khách hàng truy cập

---

## Kiểm tra sau deploy

| Endpoint | Mô tả |
|----------|-------|
| `/` | Trang chủ CLINOVA |
| `/health` | Health check → `{"status":"healthy"}` |
| `/docs` | Swagger API |
| `/dat_lich_online.html` | Cổng đặt lịch online cho khách hàng |
| `/login.html` | Đăng nhập nội bộ |

---

## Tài khoản sau seed

| Role | Username | Password |
|------|----------|----------|
| Bác sĩ (1-185) | `bacsi_001` → `bacsi_185` | `BacSi@2024!` |
| Admin | Tạo thủ công qua `/docs` | — |

---

## Xử lý sự cố

| Lỗi | Nguyên nhân | Giải pháp |
|-----|-------------|-----------|
| `Can't connect to MySQL` | DATABASE_URL sai | Đổi `mysql://` → `mysql+pymysql://` |
| `Module not found` | requirements.txt chưa push | Push lại code |
| Seed bị skip | DB đã có dữ liệu | Bình thường — seed chỉ chạy 1 lần |
| Build timeout | Seed chậm | `healthcheckTimeout=120` đã được set |
