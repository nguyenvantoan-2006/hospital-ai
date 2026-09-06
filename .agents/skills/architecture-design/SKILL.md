---
name: architecture-design
description: Thiết kế kiến trúc phần mềm từ yêu cầu đã phê duyệt cho Hệ thống Quản lý Phòng Khám có tích hợp AI (Layered Architecture + FastAPI + PostgreSQL).
---

# Architecture Design Skill — Hospital AI System

## Objective
Chuyển đổi yêu cầu đã phê duyệt thành kiến trúc phần mềm nhất quán.

## Inputs
Đọc: `docs/requirements.md`, `docs/user-stories.md`, `docs/acceptance-criteria.md`
**Chỉ dùng requirements đã qua Human Gate 1.**

## Architecture (Layered + Client-Server)
```
Presentation Layer  →  FastAPI (Business Logic + AI)  →  PostgreSQL
      Browser              Routers / Services               Data
```

**Công nghệ:** Python + FastAPI + SQLAlchemy + PostgreSQL (SQLite dev) + Jinja2 + JWT + bcrypt

## Major Components

| Component | Trách nhiệm | FR liên quan |
|---|---|---|
| Auth Module | JWT, bcrypt, RBAC | FR-01 |
| Patient Service | CRUD hồ sơ bệnh nhân | FR-02 |
| Doctor Service | Bác sĩ, chuyên khoa, lịch trực | FR-03 |
| Schedule Service | Đặt lịch, kiểm tra xung đột | FR-04 |
| Exam Service | Phiếu khám, chẩn đoán | FR-05 |
| Prescription Service | Kê đơn thuốc điện tử | FR-06 |
| Payment Service | Hóa đơn, xác nhận thanh toán | FR-07 |
| Report Service | Thống kê, báo cáo doanh thu | FR-08 |
| Patient Portal | Đặt lịch trực tuyến, OTP, reCAPTCHA | FR-09 |
| AI Service | Data Masking → LLM → Fallback → AI Logs | FR-AI-01/02/03 |

## AI Data Flow (bắt buộc)
```
Dữ liệu hồ sơ
    → Data Masking (ẩn: họ tên, SĐT, CCCD, địa chỉ)
    → LLM API (Gemini — key từ .env)
    → Kết quả AI (bản nháp)
    → Human-in-the-Loop (bác sĩ phê duyệt)
    → AI Log ghi nhận
```

## Security Boundaries
- JWT bắt buộc cho tất cả API (trừ Patient Portal public).
- Data Masking bắt buộc trước khi gọi LLM.
- API Key trong `.env`, không hard-code.
- RBAC theo role: admin/receptionist/doctor/accountant.

## Architectural Decisions

| Quyết định | Lý do |
|---|---|
| FastAPI | Async, type-safe, tự sinh OpenAPI docs |
| PostgreSQL | Ràng buộc toàn vẹn dữ liệu y tế |
| JWT + bcrypt | Bảo mật chuẩn, stateless |
| Data Masking | Tuân thủ Nghị định 13/2023/NĐ-CP (PDPA) |
| Fallback | Đảm bảo hoạt động khi AI lỗi (NFR-REL-01) |
| AI Logs | Minh bạch, tuân thủ đạo đức AI |

## Rules
- Không implement source code.
- Mọi quyết định phải có lý do.
- Không thay đổi requirements đã phê duyệt.

## Outputs
- `docs/architecture.md`
- `docs/architecture-decisions.md`
