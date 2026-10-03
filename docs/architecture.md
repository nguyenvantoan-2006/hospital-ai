# Kiến trúc Hệ thống — Hospital-AI Management System

**Dự án:** Hospital-AI Management System  
**Nhóm:** 03 — KTPM K23C | GVHD: TS. Nguyễn Đình Dũng  
**Ngày:** 2026-10-03  
**Trạng thái:** ✅ APPROVED

---

## 1. Tổng quan kiến trúc

Hệ thống áp dụng **Layered Architecture (Kiến trúc phân lớp)** kết hợp với **FastAPI** làm web framework và **PostgreSQL** làm cơ sở dữ liệu quan hệ.

```
┌──────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                     │
│  Jinja2 HTML Templates + Vanilla JS + Vanilla CSS        │
│  (templates/, static/)                                   │
└─────────────────────────┬────────────────────────────────┘
                          │ HTTP Request/Response
┌─────────────────────────▼────────────────────────────────┐
│                      API LAYER                            │
│  FastAPI Routers (routers/*.py)                          │
│  JWT Auth Middleware | RBAC Dependency                   │
└─────────────────────────┬────────────────────────────────┘
                          │ Python function calls
┌─────────────────────────▼────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                    │
│  Validation (Pydantic V2 schemas.py)                     │
│  Business rules, STT management, AI orchestration        │
└──────────────┬──────────────────────────┬────────────────┘
               │ SQLAlchemy queries        │ HTTP API call
┌──────────────▼───────────┐  ┌──────────▼────────────────┐
│      DATA LAYER          │  │       AI LAYER             │
│  SQLAlchemy ORM          │  │  Google Gemini API         │
│  models.py               │  │  gemini-1.5-flash          │
│  PostgreSQL Database     │  │  Data Masking (PII)        │
└──────────────────────────┘  └───────────────────────────┘
```

---

## 2. Các thành phần chính

### 2.1 FastAPI Application (`main.py`)
- Khởi tạo FastAPI app, mount static files
- Đăng ký tất cả routers
- Cấu hình Jinja2 templates
- CORS middleware
- Startup event: khởi tạo DB tables

### 2.2 Database Layer (`database.py`, `models.py`)
- **`database.py`**: Tạo SQLAlchemy engine, SessionLocal, Base
- **`models.py`**: 14 ORM models ánh xạ trực tiếp đến PostgreSQL tables
- Kết nối qua `DATABASE_URL` trong `.env`
- Hỗ trợ cả PostgreSQL (production) và SQLite (dev/test)

### 2.3 API Routers (`routers/`)

| Router | Prefix | Chức năng |
|--------|--------|-----------|
| `auth.py` | `/auth` | Đăng nhập, JWT token |
| `benh_nhans.py` | `/benh-nhans` | CRUD hồ sơ bệnh nhân |
| `lich_khams.py` | `/lich-khams` | Đặt lịch, STT, sync |
| `phieu_khams.py` | `/phieu-khams` | Phiếu khám, AI summary |
| `hoa_dons.py` | `/hoa-dons` | Hóa đơn, phát thuốc |
| `thuocs.py` | `/thuocs` | Danh mục thuốc, tồn kho |
| `ai.py` | `/ai` | AI Summary, Chatbot, Post-exam |
| `admin.py` | `/admin` | Quản lý tài khoản, bác sĩ |
| `bac_si.py` | `/bac-si` | Danh mục bác sĩ |
| `chuyen_khoa.py` | `/chuyen-khoa` | Danh mục chuyên khoa |
| `ke_toan.py` | `/ke-toan` | Báo cáo, lương, nhập kho |

### 2.4 Schemas (`schemas.py`)
- Pydantic V2 models theo **multi-model pattern**:
  - `XxxCreate` — dữ liệu đầu vào khi tạo mới
  - `XxxUpdate` — dữ liệu đầu vào khi cập nhật (Optional fields)
  - `XxxResponse` — dữ liệu trả về client (loại bỏ sensitive fields)

### 2.5 AI Layer (`routers/ai.py`)
- **AI Summary**: Tóm tắt hồ sơ bệnh nhân + lịch sử khám cho bác sĩ
- **AI Post-exam Guide**: Sinh hướng dẫn chăm sóc sau khám
- **AI Chatbot**: Hỏi đáp quy trình phòng khám cho bệnh nhân (Guest mode)
- **Data Masking**: Thay thế tên, SĐT, CCCD bằng mã giả trước khi gửi AI
- **AI Logging**: Ghi nhật ký mọi lượt gọi AI vào bảng `ai_logs`

### 2.6 Templates & Static (`templates/`, `static/`)
- Server-side rendering với **Jinja2**
- Mỗi role có dashboard riêng biệt
- Vanilla JS cho dynamic interactions (AJAX calls)
- Vanilla CSS cho styling

---

## 3. Authentication & Authorization

```
Client → POST /auth/login (username + password)
       ← JWT Token (Bearer)

Client → GET /any-protected-route
         Header: Authorization: Bearer <token>
       → FastAPI dependency: get_current_user()
       → Decode JWT → lấy user_id + role
       → Check role permission → Allow/Deny
```

**RBAC Roles:**
| Role | Quyền truy cập |
|------|---------------|
| `admin` | Toàn bộ hệ thống |
| `le_tan` | Bệnh nhân, Lịch khám |
| `bac_si` | Phiếu khám, AI features |
| `ke_toan` | Hóa đơn, Báo cáo, Kho thuốc |
| Guest (no token) | AI Chatbot only |

---

## 4. Database Schema (ERD tổng quan)

```
users ──────────────── benh_nhans
  │                         │
  │ (bac_si_id)             │ (benh_nhan_id)
  │                    lich_khams ─────────── chuyen_khoa
  │                         │
  │                    phieu_khams
  │                    ├── don_thuocs ──── thuocs ──── chi_tiet_nhap_kho
  │                    └── hoa_dons                         │
  │                                                    phieu_nhap_kho
  ├── bac_si (danh mục)
  ├── audit_logs
  ├── ai_logs
  └── bang_luong
```

Xem chi tiết: [database/schema.sql](../database/schema.sql) | [ERD.png](../ERD.png)

---

## 5. Technology Stack

| Thành phần | Technology | Phiên bản |
|-----------|-----------|----------|
| Web Framework | FastAPI | 0.111+ |
| ORM | SQLAlchemy | 2.0 |
| Schema Validation | Pydantic | V2 |
| Database | PostgreSQL | 14+ |
| Template Engine | Jinja2 | 3.x |
| Authentication | JWT (python-jose) | — |
| Password Hashing | bcrypt (passlib) | — |
| AI Model | Google Gemini | 1.5-flash |
| AI SDK | google-generativeai | — |
| Python Version | Python | 3.11+ |
| Deployment | Railway | — |

---

## 6. Luồng xử lý chính

### Luồng đặt lịch khám (FR-04)
```
Bệnh nhân → POST /lich-khams/dat-lich
  → Validate form (Pydantic)
  → Kiểm tra giới hạn STT/ngày + STT/khung giờ (BacSi model)
  → Tạo LichKham với STT auto-increment
  → Gửi email xác nhận (email_service.py)
  → Response: thông tin lịch + STT
```

### Luồng khám bệnh + AI (FR-08, FR-10)
```
Bác sĩ → POST /phieu-khams/ (tạo phiếu khám)
  → Lưu triệu chứng, chẩn đoán
  → POST /ai/summary (AI tóm tắt)
    → Data Masking PII
    → Call Gemini API
    → Lưu kết quả vào phieu_kham.ai_summary
    → Ghi ai_logs
  → Bác sĩ duyệt + thêm huong_dan_sau_kham
  → Tạo HoaDon tự động
```

---

## 7. Non-Functional Requirements (Kiến trúc)

| NFR | Giải pháp |
|-----|----------|
| **NFR-PERF-01**: Response < 2s | Async FastAPI, indexed queries |
| **NFR-SEC-01**: No data leak | JWT + RBAC + AI Data Masking |
| **NFR-SEC-02**: Password security | bcrypt hashing |
| **NFR-AVAIL-01**: Uptime | Railway deploy + health check |
| **NFR-AUDIT-01**: Traceability | audit_logs + ai_logs tables |

---

*Tài liệu này phản ánh kiến trúc hiện tại của implementation.*  
*Cập nhật khi có thay đổi kiến trúc đáng kể.*
