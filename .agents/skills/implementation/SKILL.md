---
name: implementation
description: Triển khai mã nguồn Hệ thống Quản lý Phòng Khám có tích hợp AI — đọc specification, hiểu kiến trúc và database, lập trình, chạy lint và tests, báo cáo diff. Không tự suy đoán khi specification không đủ.
---

# Implementation Skill — Hospital AI System

## Objective
Triển khai mã nguồn theo đúng specification đã phê duyệt, kiến trúc FastAPI + SQLAlchemy + PostgreSQL.

## Inputs
Đọc:
- `docs/requirements.md`
- `docs/architecture.md`
- `docs/database-design.md`
- `database/schema.sql`

## Process
```
Read Specification
    → Understand Architecture (FastAPI Layered)
    → Understand Database (schema.sql)
    → Implement (router → service → model)
    → Run Linter (flake8 / ruff)
    → Run Tests (pytest)
    → Review Diff
    → Report Changed Files
```

## Tech Stack
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.x + Alembic (migrations)
- **Database:** PostgreSQL (SQLite for dev/testing)
- **Auth:** JWT (python-jose) + bcrypt (passlib)
- **Validation:** Pydantic v2
- **Templates:** Jinja2 (HTML server-side rendering)
- **Testing:** pytest + httpx (TestClient)

## Project Structure
```
hospital-ai/
├── main.py              ← FastAPI app entry point
├── database.py          ← DB connection, SessionLocal
├── models.py            ← SQLAlchemy models (tất cả entities)
├── schemas.py           ← Pydantic schemas (request/response)
├── crud.py              ← Generic CRUD helpers
├── routers/
│   ├── auth.py          ← FR-01: đăng nhập, JWT
│   ├── benh_nhans.py    ← FR-02: quản lý bệnh nhân
│   ├── bac_si.py        ← FR-03: bác sĩ, chuyên khoa
│   ├── lich_kham.py     ← FR-04: lịch khám, xung đột
│   ├── phieu_kham.py    ← FR-05: khám bệnh, phiếu khám
│   ├── don_thuoc.py     ← FR-06: kê đơn thuốc
│   ├── thanh_toan.py    ← FR-07: hóa đơn, thanh toán
│   ├── bao_cao.py       ← FR-08: báo cáo, thống kê
│   ├── dat_lich.py      ← FR-09: đặt lịch trực tuyến
│   ├── ai.py            ← FR-AI-01/02/03: AI services
│   └── admin.py         ← Admin management
├── services/
│   ├── ai_service.py    ← Data Masking + LLM calls
│   ├── otp_service.py   ← OTP generation & email
│   └── auth_service.py  ← Token management
├── templates/           ← Jinja2 HTML templates
├── static/              ← CSS, JS assets
├── tests/               ← pytest test files
├── .env                 ← API keys, DB URL (KHÔNG commit)
├── .env.example         ← Template (commit)
└── requirements.txt
```

## Implementation Rules

### Security (bắt buộc)
- Password: **bcrypt** via `passlib` — KHÔNG SHA256.
- JWT: secret từ `SECRET_KEY` env var.
- GEMINI_API_KEY: từ env var, không hard-code.
- Parameterized queries: dùng SQLAlchemy ORM, không raw SQL string concat.
- Data Masking: ẩn họ tên, SĐT, CCCD trước khi gửi LLM.

### AI Service Rules (SEC-AI)
```python
# services/ai_service.py — bắt buộc theo flow:
def ai_summary(patient_data):
    masked = data_masking(patient_data)   # SEC-AI-01
    try:
        result = call_llm(masked)          # gọi Gemini API
        log_ai_usage(function='ai_summary', status='success')  # SEC-AI-04
        return result
    except Exception:
        log_ai_usage(function='ai_summary', status='fallback')  # SEC-AI-03
        return None  # Fallback: trả None, hệ thống vẫn chạy
```

### Business Rules (bắt buộc)
- Kiểm tra xung đột lịch: `UNIQUE(doctor_id, scheduled_at)` + validation.
- Chỉ role `doctor` được tạo phiếu khám và kê đơn.
- Chỉ role `accountant` được xác nhận thanh toán.
- Một bệnh nhân = một hồ sơ (kiểm tra trùng SĐT).
- AI output phải có trạng thái "bản nháp", bác sĩ phải phê duyệt.

## Giai Đoạn Triển Khai

### Phase 1 — Core Business (không có AI)
1. Database connection + models
2. Auth: đăng nhập, JWT, RBAC middleware
3. Patient CRUD (FR-02)
4. Doctor + Specialty management (FR-03)
5. Schedule management + conflict check (FR-04)
6. Exam records (FR-05)
7. Prescriptions (FR-06)
8. Payments (FR-07)
9. Reports (FR-08)

### Phase 2 — AI Integration
1. `services/ai_service.py` với Data Masking
2. AI Summary endpoint (FR-AI-01)
3. AI Chatbot endpoint (FR-AI-02)
4. Post-exam guide (FR-AI-03)
5. AI Logs ghi nhận

### Phase 3 — Patient Portal
1. Đặt lịch trực tuyến + OTP + reCAPTCHA (FR-09)
2. Tra cứu thông tin cá nhân (FR-10)

## After Implementation
- Chạy: `flake8 .` hoặc `ruff check .`
- Chạy: `pytest tests/ -v`
- Kiểm tra lỗi và báo cáo các file đã thay đổi.
- Không thay đổi requirements hoặc architecture.

## Stop Condition
Nếu specification không đủ để triển khai → **DỪNG và báo cáo**, không tự suy đoán.

> Agent tốt biết khi nào cần dừng và yêu cầu con người quyết định.
