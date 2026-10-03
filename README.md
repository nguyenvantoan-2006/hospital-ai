# 🏥 Hospital-AI Management System

> **Hệ thống Quản lý Phòng Khám có Tích hợp AI**  
> Nhóm 03 — KTPM K23C | GVHD: TS. Nguyễn Đình Dũng

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://postgresql.org)
[![Gemini AI](https://img.shields.io/badge/Gemini-1.5--flash-orange)](https://ai.google.dev)

---

## 📋 Tổng quan dự án

Hospital-AI là hệ thống quản lý phòng khám đa năng, tích hợp AI (Google Gemini) để hỗ trợ:
- Đặt lịch khám trực tuyến và quản lý số thứ tự
- AI tóm tắt hồ sơ bệnh nhân (AI Summary)
- AI hướng dẫn sau khám (AI Post-exam Guide)
- AI Chatbot hỏi đáp quy trình (cho bệnh nhân)
- Quản lý bác sĩ, chuyên khoa, thuốc, hóa đơn, lương nhân viên

---

## 👥 Actors (Tác nhân)

| Actor | Vai trò |
|-------|---------|
| **Admin** | Quản lý toàn hệ thống, tài khoản, phân quyền |
| **Lễ tân** | Tiếp nhận, đặt lịch, quản lý hồ sơ bệnh nhân |
| **Bác sĩ** | Khám bệnh, lập phiếu khám, sử dụng AI hỗ trợ |
| **Kế toán** | Thanh toán, báo cáo tài chính, quản lý kho thuốc |
| **Bệnh nhân** | Đặt lịch trực tuyến, tra cứu, dùng AI Chatbot (Guest) |

---

## 🏗️ Kiến trúc hệ thống

```
hospital-ai/
├── main.py               # FastAPI app entrypoint, routes mount
├── database.py           # SQLAlchemy engine, session, Base
├── models.py             # 14 ORM models (tables)
├── schemas.py            # Pydantic V2 schemas (Create/Update/Response)
├── routers/              # API routers phân theo domain
│   ├── auth.py           # JWT login/logout
│   ├── benh_nhans.py     # Bệnh nhân CRUD
│   ├── lich_khams.py     # Lịch khám + số thứ tự
│   ├── phieu_khams.py    # Phiếu khám + AI summary
│   ├── hoa_dons.py       # Hóa đơn + phát thuốc
│   ├── ai.py             # AI endpoints (summary, chatbot, post-exam)
│   ├── admin.py          # Admin management
│   └── ...
├── templates/            # Jinja2 HTML templates (server-side render)
├── static/               # CSS, JS, images
├── database/
│   └── schema.sql        # DDL schema PostgreSQL (tham khảo)
├── docs/                 # Tài liệu dự án
└── .agents/skills/       # AI Agent skills (9 skills tiền đề)
```

**Kiến trúc phân lớp (Layered Architecture):**
```
[Browser / Client]
      ↓ HTTP
[FastAPI Routers]  ← JWT Auth Middleware
      ↓
[Business Logic / CRUD]
      ↓
[SQLAlchemy ORM]
      ↓
[PostgreSQL Database]
      ↑ (song song)
[Google Gemini AI API]  ← AI Endpoints
```

---

## 🚀 Cài đặt & Chạy

### Yêu cầu môi trường
- Python 3.11+
- PostgreSQL 14+
- Google Gemini API key

### Cài đặt

```bash
# 1. Clone repo
git clone <repo-url>
cd hospital-ai

# 2. Tạo môi trường ảo
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Cài dependencies
pip install -r requirements.txt

# 4. Cấu hình môi trường
cp .env.example .env
# Sửa .env: DATABASE_URL, GEMINI_API_KEY, SECRET_KEY

# 5. Chạy server
uvicorn main:app --reload
```

### Truy cập
- **App:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🤖 AI Features

| Tính năng | Endpoint | Mô tả |
|-----------|----------|-------|
| AI Summary | `POST /ai/summary` | Tóm tắt hồ sơ bệnh nhân cho bác sĩ |
| AI Post-exam | `POST /ai/post-exam-guide` | Hướng dẫn chăm sóc sau khám |
| AI Chatbot | `POST /ai/chatbot` | Hỏi đáp quy trình phòng khám (Guest) |

> ⚠️ **Data Masking:** Tất cả dữ liệu PII được che giấu trước khi gửi đến AI API.

---

## 📊 Database — 14 Tables

| Table | Mô tả |
|-------|-------|
| `users` | Tài khoản hệ thống (RBAC) |
| `benh_nhans` | Hồ sơ bệnh nhân |
| `lich_khams` | Lịch khám + số thứ tự |
| `phieu_khams` | Phiếu khám + AI summary |
| `thuocs` | Danh mục thuốc |
| `don_thuocs` | Chi tiết đơn thuốc |
| `hoa_dons` | Hóa đơn thanh toán |
| `bac_si` | Danh mục bác sĩ |
| `chuyen_khoa` | Danh mục chuyên khoa |
| `audit_logs` | Nhật ký hoạt động |
| `phieu_nhap_kho` | Phiếu nhập kho thuốc |
| `chi_tiet_nhap_kho` | Chi tiết nhập kho |
| `bang_luong` | Bảng lương nhân viên |
| `ai_logs` | Nhật ký kiểm toán AI |

---

## 📁 Tài liệu

| File | Nội dung |
|------|---------|
| [docs/requirements.md](docs/requirements.md) | Yêu cầu chức năng (FR-01 → FR-16) |
| [docs/architecture.md](docs/architecture.md) | Kiến trúc hệ thống chi tiết |
| [docs/architecture-decisions.md](docs/architecture-decisions.md) | Các quyết định thiết kế (ADR) |
| [docs/user-stories.md](docs/user-stories.md) | User stories & acceptance criteria |
| [docs/acceptance-criteria.md](docs/acceptance-criteria.md) | Tiêu chí chấp nhận |
| [database/schema.sql](database/schema.sql) | DDL schema PostgreSQL |

---

## 🔄 Git Workflow

Dự án dùng **Feature Branch + Squash Merge**:
```
main (protected)
  ├── feat/benh-nhan-portal
  ├── feat/bac-si-dashboard
  ├── feat/le-tan-dashboard
  └── feat/dat-lich-sync-stt-limits
```

Xem chi tiết: [AGENTS.md](AGENTS.md) | [docs/git-workflow.md](docs/git-workflow.md)

---

## 🔐 Bảo mật

- JWT Bearer Token authentication
- RBAC (Role-Based Access Control)
- bcrypt password hashing
- AI Data Masking (PII protection)
- Audit logging cho mọi hành động quan trọng

---

*Nhóm 03 — KTPM K23C — 2026*
