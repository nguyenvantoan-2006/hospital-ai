---
name: documentation
description: Tạo và cập nhật tài liệu kỹ thuật đầy đủ cho Hệ thống Quản lý Phòng Khám có tích hợp AI — phản ánh đúng implementation hiện tại, không mô tả chức năng chưa triển khai.
---

# Documentation Skill — Hospital AI System

## Objective
Tạo tài liệu kỹ thuật phản ánh đúng trạng thái hiện tại của hệ thống.

## Inputs
Đọc toàn bộ project (source code, docs, schema, tests).

## Process
```
Read codebase → Understand current state → Generate/Update docs
→ Cross-check với requirements → Verify accuracy → Finalize
```

## Rules
- Chỉ mô tả chức năng đã được **triển khai và kiểm thử**.
- KHÔNG mô tả chức năng chưa hoàn thành.
- Ghi rõ trạng thái từng tính năng (Implemented/In Progress/Planned).
- Tài liệu phải nhất quán với mã nguồn thực tế.

## Outputs cần tạo/cập nhật

### README.md
```markdown
# Hệ Thống Quản Lý Phòng Khám có Tích Hợp AI
Nhóm 03 - KTPM K23C | GVHD: TS. Nguyễn Đình Dũng

## Giới thiệu
[Mô tả ngắn gọn hệ thống]

## Tech Stack
- Python 3.11+ / FastAPI
- SQLAlchemy + PostgreSQL (SQLite dev)
- JWT + bcrypt
- Gemini API (AI features)
- Jinja2 (HTML templates)

## Cài đặt
[Hướng dẫn từng bước]

## Cấu hình
[Mô tả các biến .env]

## Chạy hệ thống
[Lệnh chạy development server]

## API Documentation
Truy cập: http://localhost:8000/docs

## Tính năng đã triển khai
[Danh sách FR đã hoàn thành]

## Đạo đức AI
[Mô tả ngắn gọn Guardrails, không chẩn đoán, Data Masking]
```

### docs/api.md
Mô tả tất cả API endpoints:
- Method, Path, Auth required, Request body, Response
- Ví dụ request/response cho từng endpoint chính

### docs/architecture.md
- Sơ đồ kiến trúc (ASCII hoặc mô tả)
- Mô tả các tầng (Presentation, Business, Data)
- Luồng xử lý chính

### docs/database-design.md
- ERD mô tả bằng văn bản
- Danh sách bảng với mục đích
- Các ràng buộc quan trọng

### docs/deployment.md
- Yêu cầu hệ thống
- Các bước cài đặt môi trường
- Cấu hình biến môi trường
- Chạy migrations
- Khởi động server

### docs/user-guide.md
- Hướng dẫn từng role:
  - Admin: quản lý tài khoản, phân quyền
  - Lễ tân: tiếp nhận, đặt lịch
  - Bác sĩ: khám bệnh, sử dụng AI
  - Kế toán: thanh toán, báo cáo
  - Bệnh nhân: đặt lịch online

### docs/ai-ethics.md
```markdown
# Đạo Đức AI trong Hệ Thống

## Nguyên tắc cốt lõi
- AI CHỈ hỗ trợ hành chính, KHÔNG thay thế bác sĩ.
- AI KHÔNG chẩn đoán bệnh, KHÔNG kê đơn thuốc.
- Mọi output AI cần bác sĩ phê duyệt (Human-in-the-Loop).

## Data Masking
[Giải thích cơ chế ẩn PII trước khi gửi LLM]

## AI Logs
[Giải thích cơ chế ghi nhật ký AI để minh bạch và kiểm soát]

## Fallback
[Giải thích hệ thống vẫn hoạt động khi AI lỗi]

## Tuân thủ pháp lý
- Nghị định 13/2023/NĐ-CP (PDPA)
- Luật 15/2023/QH15 (Khám chữa bệnh)
- Thông tư 46/2017/TT-BYT (Hồ sơ bệnh án điện tử)
```
