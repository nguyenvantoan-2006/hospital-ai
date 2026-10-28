# 📝 Lịch sử Prompt AI — Hospital-AI Project

**Mục đích:** Ghi lại toàn bộ các prompt đã sử dụng với AI Agent (Antigravity / Gemini)  
**Dự án:** Hospital-AI Management System — Nhóm 03 — KTPM K23C  
**Ý nghĩa:** Bằng chứng ứng dụng AI-Augmented SDLC trong quá trình phát triển phần mềm

> 📌 File này là **kết quả thực hành AI-Augmented SDLC** theo tài liệu `1_Thuc_hanh_AI_Augmented_SDLC.docx`.  
> Mỗi prompt phản ánh một bước trong quy trình SDLC được AI hỗ trợ.

---

## 📊 Thống kê tổng quan

| Chỉ số | Giá trị |
|--------|--------|
| Tổng số prompt | 23+ |
| Thời gian ghi nhận | 2026-08-01 → 2026-10-03 |
| Conversation ID hiện tại | `bdc95597-1949-42a3-9f8f-940cd22062d3` |
| AI Agent sử dụng | Antigravity (Google Gemini / Claude Sonnet) |
| Giai đoạn SDLC được AI hỗ trợ | Requirements → Architecture → DB Design → Implementation → Testing → Docs |

---

## 🗓️ Phiên làm việc: 2026-10-03

### Session bdc95597 — Cấu trúc dự án & Skill Files

| # | Thời gian | Prompt | Giai đoạn SDLC | Output |
|---|-----------|--------|----------------|--------|
| 1 | 15:42 | "bạn kiểm tra lại tất cả dự án của tôi xem đã có cấu trúc như này chưa thiếu file nào báo cáo lại cho tôi vì yêu cầu chuẩn phải có các file này làm skill tiền đề có làm việc sau này" | 🔍 Analysis | Báo cáo gap analysis: thiếu README.md, database/schema.sql, docs/architecture.md, docs/architecture-decisions.md |
| 2 | 15:46 | "tạo các file còn thiếu để hoàn chỉnh skill và cho tôi biết các file hoạt động như nào" | 🏗️ Implementation | Tạo 4 files: README.md, database/schema.sql, docs/architecture.md, docs/architecture-decisions.md. 3 commits riêng biệt |
| 3 | 15:55 | "thứ nhất cho vào skill 1 bảng lịch sử prompt lưu lại toàn bộ các prompt tôi hỏi bạn để làm kết quả tôi ứng dụng AI" | 📋 Documentation | Tạo docs/ai-prompt-history.md + cập nhật testing/SKILL.md |

---

## 🗓️ Các phiên làm việc trước (từ Git history & docs)

> Các prompt dưới đây được tái hiện từ Git commit history, docs/plans/, và docs/requirements-issues.md

---

### 📐 Giai đoạn 1 — Requirements Analysis (BƯỚC 1 SDLC)

| # | Prompt (tóm tắt) | Giai đoạn | Output |
|---|-----------------|-----------|--------|
| R-01 | "Phân tích yêu cầu từ file NHÓM_03.docx và tạo docs/requirements.md" | Requirements | `docs/requirements.md` (FR-01→FR-16) |
| R-02 | "Tạo user stories từ requirements đã có" | Requirements | `docs/user-stories.md` |
| R-03 | "Tạo acceptance criteria chi tiết cho từng FR" | Requirements | `docs/acceptance-criteria.md` |
| R-04 | "Tạo customer-requirement.md từ góc nhìn khách hàng phòng khám" | Requirements | `docs/customer-requirement.md` |
| R-05 | "Ghi lại các vấn đề requirements chưa rõ vào requirements-issues.md" | Requirements | `docs/requirements-issues.md` |

---

### 🏗️ Giai đoạn 2 — Architecture Design (BƯỚC 2 SDLC)

| # | Prompt (tóm tắt) | Giai đoạn | Output |
|---|-----------------|-----------|--------|
| A-01 | "Thiết kế kiến trúc Layered Architecture cho hệ thống phòng khám" | Architecture | `docs/architecture.md` |
| A-02 | "Thiết kế ERD cho 14 bảng database từ requirements đã approve" | Architecture | `docs/ERD.md`, `ERD.png` |
| A-03 | "Tạo database/schema.sql DDL PostgreSQL từ models.py" | Architecture | `database/schema.sql` |
| A-04 | "Ghi lại các quyết định kiến trúc quan trọng (ADR)" | Architecture | `docs/architecture-decisions.md` |

---

### 💻 Giai đoạn 3 — Implementation (BƯỚC 3 SDLC)

| # | Prompt (tóm tắt) | Giai đoạn | Output |
|---|-----------------|-----------|--------|
| I-01 | "Tạo models.py với SQLAlchemy ORM cho tất cả 14 bảng" | Implementation | `models.py` |
| I-02 | "Tạo schemas.py với Pydantic V2 multi-model pattern" | Implementation | `schemas.py` |
| I-03 | "Tạo router đặt lịch trực tuyến với OTP email verification" | Implementation | `routers/lich_khams.py` |
| I-04 | "Tích hợp Gemini AI cho tính năng AI Summary hồ sơ bệnh nhân" | Implementation | `routers/ai.py` |
| I-05 | "Implement Data Masking PII trước khi gửi AI API" | Implementation | `routers/ai.py` — hàm `mask_pii()` |
| I-06 | "Tạo AI Chatbot cho bệnh nhân với guardrails y đức" | Implementation | `routers/ai.py` — endpoint `/chatbot` |
| I-07 | "Tạo trang dashboard lễ tân với quản lý lịch khám theo ngày" | Implementation | `templates/lich_kham.html` |
| I-08 | "Tạo trang lập phiếu khám cho bác sĩ với AI summary integration" | Implementation | `templates/lap_phieu_kham.html` |
| I-09 | "Implement STT (số thứ tự) tự động theo bác sĩ và ngày" | Implementation | `routers/lich_khams.py` — STT logic |
| I-10 | "Tạo seed data cho thuốc, bác sĩ, bệnh nhân thật" | Implementation | `seed_medicines.py`, `seed_doctors.py`, `seed_real_patients.py` |

---

### 🤖 Giai đoạn 4 — AI Features (BƯỚC 4 SDLC — Đặc thù AI SDLC)

| # | Prompt (tóm tắt) | Giai đoạn | Output |
|---|-----------------|-----------|--------|
| AI-01 | "Tối ưu system prompt cho AI Summary để giảm hallucination" | AI Integration | `routers/ai.py` — system prompt |
| AI-02 | "Thêm guardrails từ chối câu hỏi chẩn đoán trong Chatbot" | AI Integration | `routers/ai.py` — guardrails logic |
| AI-03 | "Tạo RAG knowledge base cho quy trình phòng khám" | AI Integration | RAG implementation |
| AI-04 | "Implement exponential backoff khi Gemini API bị rate limit" | AI Integration | `routers/ai.py` — retry logic |
| AI-05 | "Ghi ai_logs cho mọi lượt gọi AI để audit" | AI Integration | `models.py` — AILog model |

---

### 🧪 Giai đoạn 5 — Testing (BƯỚC 5 SDLC)

| # | Prompt (tóm tắt) | Giai đoạn | Output |
|---|-----------------|-----------|--------|
| T-01 | "Chạy test toàn hệ thống và báo cáo kết quả" | Testing | `run_full_system_test.py` |
| T-02 | "Test closed-loop routing: đặt lịch → khám → hóa đơn" | Testing | `test_closed_loop_and_sync.py` |
| T-03 | "Test capacity sync: giới hạn STT/ngày và STT/khung giờ" | Testing | `test_appointment_capacity_sync.py` |

---

### 📋 Giai đoạn 6 — Documentation & DevOps (BƯỚC 6 SDLC)

| # | Prompt (tóm tắt) | Giai đoạn | Output |
|---|-----------------|-----------|--------|
| D-01 | "Deploy lên Railway, tạo hướng dẫn deploy" | DevOps | `docs/deploy-railway.md`, `Procfile`, `railway.toml` |
| D-02 | "Tạo git-workflow.md mô tả Feature Branch + Squash Merge" | Docs | `docs/git-workflow.md` |
| D-03 | "Tạo tai-khoan-actors.md liệt kê tài khoản test cho từng role" | Docs | `docs/tai-khoan-actors.md` |

---

## 🎯 Phân tích ứng dụng AI theo giai đoạn SDLC

```
Requirements Analysis ──── AI hỗ trợ phân tích, tổ chức FR từ tài liệu Word
       ↓
Architecture Design ─────── AI đề xuất kiến trúc, tạo ERD, viết ADR
       ↓
Implementation ──────────── AI sinh code (models, schemas, routers, templates)
       ↓
AI Feature Integration ──── AI tối ưu prompts, guardrails, RAG, logging
       ↓
Testing ─────────────────── AI tạo test cases, chạy integration tests
       ↓
Documentation ───────────── AI sinh toàn bộ technical docs
```

**Nhận xét:** AI Agent được sử dụng xuyên suốt **toàn bộ vòng đời SDLC**,  
không chỉ ở giai đoạn code — đây chính là **AI-Augmented SDLC** theo phương pháp `1_Thuc_hanh_AI_Augmented_SDLC.docx`.

---

## 📌 Hướng dẫn cập nhật file này

Sau mỗi phiên làm việc với AI, thêm dòng mới vào bảng theo format:

```
| [số thứ tự] | [HH:MM] | "[nội dung prompt]" | [Giai đoạn] | [Output tạo ra] |
```

**Giai đoạn hợp lệ:**
- 🔍 Analysis
- 📐 Requirements  
- 🏗️ Architecture
- 💻 Implementation
- 🤖 AI Integration
- 🧪 Testing
- 📋 Documentation
- 🚀 DevOps

---

*File này là bằng chứng thực hành AI-Augmented SDLC — Nhóm 03 KTPM K23C — 2026*
