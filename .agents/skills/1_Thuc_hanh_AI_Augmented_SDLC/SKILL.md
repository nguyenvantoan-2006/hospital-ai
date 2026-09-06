---
name: 1_Thuc_hanh_AI_Augmented_SDLC
description: AI-Augmented SDLC toàn diện cho dự án Hospital-AI (Nhóm 03 - KTPM K23C). Áp dụng quy trình phát triển phần mềm có trợ giúp AI theo đúng tài liệu SRS NHÓM_03.docx và phương pháp 1_Thuc_hanh_AI_Augmented_SDLC.docx.
---

# AI-Augmented SDLC — Hospital AI Management System

> **Nhóm 03 — KTPM K23C | GVHD: TS. Nguyễn Đình Dũng**  
> **Đề tài:** Hệ thống quản lý phòng khám có tích hợp AI (Trợ lý hành chính)

---

## 1. Tổng Quan Phương Pháp Luận

Phương pháp AI-Augmented SDLC kết hợp kỹ năng của AI với kinh nghiệm của con người qua các Human Gates có kiểm soát, đảm bảo chất lượng production-grade cho hệ thống y tế có dữ liệu nhạy cảm.

```
Requirements → Architecture → Database → Implementation → Testing → Review → Security → Docs
       │               │              │              │              │          │          │
  [Gate 1]       [Gate 2]       [Gate 2]         [Gate 3]     [Gate 3]  [Gate 4]  [Gate 5]
  Con người       Con người       Con người       Con người     Con người  Con người  Approval
  Review          Approve         Approve         Code Review   Test OK    Security   Final
```

---

## 2. Actors của Hệ Thống (NHÓM_03.docx)

| Actor | Vai trò | Quyền AI |
|---|---|---|
| Quản trị viên | Quản lý hệ thống, phân quyền, AI Logs | Xem AI Logs |
| Lễ tân | Tiếp nhận, đặt lịch, hồ sơ bệnh nhân | Hướng dẫn Chatbot |
| Bác sĩ | Khám bệnh, kê đơn | AI Summary + AI Post-exam |
| Kế toán | Thanh toán, báo cáo tài chính | Không dùng AI |
| Bệnh nhân | Đặt lịch online, tra cứu cá nhân | AI Chatbot (Guest) |

---

## 3. Yêu Cầu Hệ Thống — Mapping từ SRS

### 3.1. Functional Requirements
| Mã | Tên | Actor |
|---|---|---|
| FR-01 | Đăng nhập và phân quyền (RBAC) | Admin, Lễ tân, Bác sĩ, Kế toán |
| FR-02 | Quản lý bệnh nhân | Lễ tân |
| FR-03 | Quản lý bác sĩ và chuyên khoa | Admin |
| FR-04 | Quản lý lịch khám | Lễ tân |
| FR-05 | Khám bệnh và lập phiếu khám | Bác sĩ |
| FR-06 | Kê đơn thuốc điện tử | Bác sĩ |
| FR-07 | Quản lý thanh toán viện phí | Kế toán |
| FR-08 | Báo cáo và thống kê | Admin, Kế toán |
| FR-09 | Đặt lịch khám trực tuyến (OTP + reCAPTCHA) | Bệnh nhân |
| FR-10 | Tra cứu thông tin cá nhân | Bệnh nhân |
| FR-AI-01 | AI tóm tắt hồ sơ bệnh án | Bác sĩ |
| FR-AI-02 | AI Chatbot hỏi đáp quy trình | Bệnh nhân, Lễ tân |
| FR-AI-03 | AI sinh hướng dẫn sau khám | Bác sĩ |

### 3.2. AI Security Mechanisms (SEC-AI)
| Mã | Cơ chế |
|---|---|
| SEC-AI-01 | Data Masking: ẩn PII trước khi gửi LLM |
| SEC-AI-02 | AI Guardrails: không chẩn đoán, không kê đơn |
| SEC-AI-03 | Fallback: AI lỗi → hệ thống vẫn chạy bình thường |
| SEC-AI-04 | AI Logs: ghi nhật ký đầy đủ mọi lần gọi AI |

---

## 4. SDLC Phases với AI Skills

### Phase 1: Requirements Analysis
**Skill:** `.agents/skills/requirements-analysis/SKILL.md`  
**AI làm:**
- Đọc `docs/customer-requirement.md`
- Phân loại FR, NFR, Business Rules, Assumptions
- Tạo User Stories với Acceptance Criteria
- Ghi rõ Ambiguities

**Outputs:**
- `docs/requirements.md` ✅
- `docs/user-stories.md` ✅
- `docs/acceptance-criteria.md` ✅
- `docs/requirements-issues.md` ✅

---

> ### 🚧 HUMAN GATE 1: Requirements Review
> **Người thực hiện:** Nhóm 03 (tất cả thành viên)  
> **Checklist:**
> - [ ] Tất cả FR từ SRS (FR-01 đến FR-AI-03) đã được capture
> - [ ] Không có AI hallucination (đảm bảo không tự thêm thắt yêu cầu ngoài tài liệu gốc)
> - [ ] Acceptance Criteria có thể kiểm thử được
> - [ ] Ambiguities đã được ghi rõ
> - [ ] Guardrails AI được phản ánh đúng (SEC-AI-01 đến SEC-AI-04)
>
> **Phê duyệt:** ✅ APPROVED ngày: ___________  
> **Chữ ký:** ___________

---

### Phase 2: Architecture & Database Design
**Skill:** `.agents/skills/architecture-design/SKILL.md`  
**Skill:** `.agents/skills/database-design/SKILL.md`  
**AI làm:**
- Định nghĩa kiến trúc Layered + FastAPI + PostgreSQL
- Thiết kế schema đầy đủ
- Xác định Security Boundaries
- Ghi Architecture Decision Records

**Outputs:**
- `docs/architecture.md`
- `docs/architecture-decisions.md`
- `docs/database-design.md`
- `database/schema.sql`

---

> ### 🚧 HUMAN GATE 2: Architecture Review
> **Checklist:**
> - [ ] Kiến trúc đáp ứng đủ 13 FR + 3 FR-AI
> - [ ] Data Masking có trong luồng AI
> - [ ] Fallback Mechanism được thiết kế
> - [ ] RBAC được thể hiện trong kiến trúc
> - [ ] Schema đủ tables (users, doctors, patients, schedules, exams, invoices, ai_logs...)
> - [ ] bcrypt được chỉ định (không SHA256)
>
> **Phê duyệt:** ✅ APPROVED ngày: ___________

---

### Phase 3: Implementation
**Skill:** `.agents/skills/implementation/SKILL.md`  
**AI làm:**
- Tạo project FastAPI chuẩn cấu trúc
- Implement từng router theo FR
- Implement AI Service (Data Masking + LLM + Fallback + Logs)
- Chạy linter (`ruff check .`)

**Tech Stack:**
- Python 3.11+ / FastAPI / SQLAlchemy 2.x / PostgreSQL
- JWT (python-jose) / bcrypt (passlib) / Pydantic v2 / Jinja2

**Outputs:**
- Source code đầy đủ
- `.env.example` (không commit giá trị thật)
- `requirements.txt`

---

> ### 🚧 HUMAN GATE 3: Code Review
> **Checklist:**
> - [ ] bcrypt — không SHA256
> - [ ] API Keys từ env, không hard-code
> - [ ] Data Masking tồn tại trước mọi LLM call
> - [ ] Chatbot từ chối câu hỏi y tế
> - [ ] AI output là bản nháp, bác sĩ phải approve
> - [ ] RBAC đúng cho từng endpoint
>
> **Phê duyệt:** ✅ APPROVED ngày: ___________

---

### Phase 4: Testing
**Skill:** `.agents/skills/testing/SKILL.md`  
**AI làm:**
- Tạo test cases từ Acceptance Criteria
- Viết pytest tests cho tất cả FR
- Ưu tiên: Auth, AI Guardrails, Data Masking
- Chạy `pytest -v` và báo cáo coverage

**Outputs:**
- `tests/test_auth.py`
- `tests/test_patients.py`
- `tests/test_schedules.py`
- `tests/test_ai_service.py`
- `docs/test-report.md`

---

> ### 🚧 HUMAN GATE 4: Test Results Review
> **Checklist:**
> - [ ] Tất cả TC-01 đến TC-AI-03 pass
> - [ ] Test Data Masking pass
> - [ ] Test AI Fallback pass
> - [ ] Test RBAC pass
> - [ ] Coverage ≥70%
>
> **Phê duyệt:** ✅ APPROVED ngày: ___________

---

### Phase 5: Code Review & Security Review
**Skill:** `.agents/skills/code-review/SKILL.md`  
**Skill:** `.agents/skills/security-review/SKILL.md`  
**AI làm:**
- Review code theo checklist
- Phân loại issues: CRITICAL/HIGH/MEDIUM/LOW
- Security review: OWASP Top 10 + AI-specific

**Outputs:**
- `docs/code-review.md`
- `docs/security-review.md`

---

> ### 🚧 HUMAN GATE 5: Security Approval
> **Checklist:**
> - [ ] Không có issue CRITICAL nào chưa xử lý
> - [ ] Tất cả HIGH issues đã resolve
> - [ ] `.env` trong `.gitignore`
> - [ ] Secrets không lộ trong git history
>
> **Phê duyệt:** ✅ APPROVED ngày: ___________

---

### Phase 6: Documentation
**Skill:** `.agents/skills/documentation/SKILL.md`  
**AI làm:**
- Cập nhật README.md
- Tạo API docs
- Tạo User Guide
- Tạo AI Ethics doc

**Outputs:**
- `README.md` (updated)
- `docs/api.md`
- `docs/user-guide.md`
- `docs/ai-ethics.md`
- `docs/deployment.md`

---

## 5. AI Prompts Design (từ SRS 3.4.6)

### AI Summary — System Prompt
```
Bạn là một trợ lý y tế hành chính thông minh. Nhiệm vụ của bạn là tóm tắt
ngắn gọn lịch sử khám bệnh, các triệu chứng cũ và đơn thuốc của bệnh nhân
để bác sĩ xem nhanh. TUYỆT ĐỐI KHÔNG đưa ra chẩn đoán y khoa, KHÔNG đề
xuất phác đồ điều trị hay thay đổi đơn thuốc.
```

### AI Chatbot — System Prompt
```
Bạn là nhân viên lễ tân ảo của phòng khám. Bạn CHỈ ĐƯỢC PHÉP trả lời các
câu hỏi về: Giờ làm việc, Quy trình đặt lịch, Bảng giá dịch vụ và Thủ tục
hành chính. Nếu người dùng hỏi về triệu chứng bệnh hoặc xin tư vấn điều
trị, từ chối lịch sự và hướng dẫn đặt lịch khám bác sĩ.
```

### AI Post-exam Guide — System Prompt
```
Bạn là trợ lý soạn thảo văn bản y tế cho bác sĩ. Dựa trên các từ khóa và
ghi chú ngắn gọn của bác sĩ, soạn thảo hướng dẫn chăm sóc sức khỏe sau
khám. TUYỆT ĐỐI KHÔNG tự sáng tạo, KHÔNG thêm bớt phương pháp điều trị
hay các loại thuốc không có trong ghi chú.
```

---

## 6. Sub-skills Available
Tất cả sub-skills được lưu trong `.agents/skills/`:

| Skill | Mục đích |
|---|---|
| **A. NHÓM QUẢN TRỊ QUY TRÌNH (SDLC)** | |
| `requirements-analysis` | Phân tích yêu cầu (Phase 1) |
| `architecture-design` | Thiết kế kiến trúc (Phase 2) |
| `database-design` | Thiết kế CSDL (Phase 2) |
| `implementation` | Triển khai dự án (Phase 3) |
| `testing` | Viết & chạy Test (Phase 4) |
| `code-review` | Đánh giá Code (Phase 5) |
| `security-review` | Đánh giá Bảo mật (Phase 5) |
| `ai-rag-consultant` | Tư vấn Guardrails & Tích hợp AI |
| `documentation` | Viết tài liệu (Phase 6) |
| **B. NHÓM KỸ THUẬT CODE (TECHNICAL)** | |
| `fastapi-pro` | Hướng dẫn code backend FastAPI chuẩn |
| `pydantic-models-py` | Cách viết schema/validate dữ liệu bằng Pydantic |
| `gemini-api-integration`| Hướng dẫn gọi API Gemini & xử lý lỗi |
| `llm-prompt-optimize` | Hướng dẫn viết Prompt cho AI hiệu quả |
| `rag-implementation` | Hướng dẫn làm RAG (Truy xuất dữ liệu) |

---

## 7. Quy Tắc Bất Biến (Không Thay Đổi)

```
🔒 GUARDRAILS — HOSPITAL AI SYSTEM

1. DATA MASKING: Bắt buộc ẩn PII trước mọi lần gọi LLM
2. AI ETHICS:    AI không chẩn đoán, không kê đơn, không thay bác sĩ
3. HUMAN-IN-THE-LOOP: Mọi output AI phải bác sĩ phê duyệt trước khi dùng
4. FALLBACK:     AI lỗi → hệ thống vẫn hoạt động bình thường
5. BCRYPT:       Mật khẩu phải hash bằng bcrypt (không SHA256)
6. SECRETS:      API keys từ env var (không hard-code, không commit)
7. RBAC:         Mỗi endpoint phải kiểm tra role người dùng
8. AUDIT LOGS:   Ghi nhật ký đầy đủ mọi thao tác quan trọng
```

---

## 8. Tuân Thủ Pháp Lý
- Luật Khám bệnh, chữa bệnh (Luật số 15/2023/QH15)
- Nghị định 13/2023/NĐ-CP (Bảo vệ dữ liệu cá nhân — PDPA)
- Thông tư 46/2017/TT-BYT (Hồ sơ bệnh án điện tử)
