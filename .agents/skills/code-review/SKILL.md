---
name: code-review
description: Review toàn bộ implementation của Hệ thống Quản lý Phòng Khám — kiểm tra correctness, requirements compliance, architecture compliance, security, performance và test quality. Không sửa code.
---

# Code Review Skill — Hospital AI System

## Objective
Review code theo các tiêu chí chất lượng, phân loại vấn đề và tạo báo cáo. Không sửa code trong bước này.

## Inputs
Đọc toàn bộ mã nguồn hiện tại cùng với:
- `docs/requirements.md`
- `docs/architecture.md`
- `docs/database-design.md`

## Review Checklist

### 1. Correctness (Tính đúng đắn)
- [ ] Logic nghiệp vụ đúng với requirements
- [ ] Conflict detection lịch khám hoạt động đúng
- [ ] Tổng tiền hóa đơn tính đúng
- [ ] Trạng thái phiếu khám, lịch khám, hóa đơn chuyển đúng

### 2. Requirements Compliance (Tuân thủ yêu cầu)
- [ ] FR-01: RBAC đúng với từng role
- [ ] FR-04: Kiểm tra xung đột lịch trước khi tạo
- [ ] FR-05: Chỉ bác sĩ tạo phiếu khám
- [ ] FR-07: Chỉ kế toán xác nhận thanh toán
- [ ] FR-AI: Data Masking bắt buộc trước LLM call
- [ ] SEC-AI-02: AI không chẩn đoán, không kê đơn

### 3. Architecture Compliance (Tuân thủ kiến trúc)
- [ ] Code tổ chức theo Layered Architecture (router → service → model)
- [ ] Không có business logic trong router trực tiếp
- [ ] AI Service tách biệt hoàn toàn với Database access
- [ ] Không có raw SQL string concatenation

### 4. Security (Bảo mật — ưu tiên cao)
- [ ] Password hash bằng **bcrypt** (không SHA256, không plain text)
- [ ] JWT secret từ env var, không hard-code
- [ ] GEMINI_API_KEY từ env var, không trong source code
- [ ] Data Masking ẩn đúng: họ tên, SĐT, CCCD, địa chỉ
- [ ] Không có SQL injection (dùng SQLAlchemy ORM)
- [ ] Không lộ stack trace ra response trả về client
- [ ] `.env` trong `.gitignore`

### 5. Performance (Hiệu năng)
- [ ] Query bệnh nhân có index (phone, full_name)
- [ ] Query lịch khám có index (doctor_id, scheduled_at)
- [ ] Không có N+1 query problem

### 6. Code Quality (Chất lượng code)
- [ ] Không có duplicate code
- [ ] Error handling đầy đủ (try/except với logging)
- [ ] Type hints đầy đủ (Pydantic v2)
- [ ] Không có dead code
- [ ] Tên biến/hàm rõ nghĩa (tiếng Anh hoặc tiếng Việt nhất quán)

### 7. AI-Specific Review
- [ ] `ai_service.py` không truy cập Database trực tiếp
- [ ] Fallback hoạt động khi LLM lỗi
- [ ] AI Log ghi đầy đủ (function_name, status, duration_ms)
- [ ] Kết quả AI trả về dạng "bản nháp", cần bác sĩ phê duyệt
- [ ] Chatbot từ chối câu hỏi về chẩn đoán/điều trị

### 8. Test Quality (Chất lượng kiểm thử)
- [ ] Test coverage ≥70% cho module nghiệp vụ cốt lõi
- [ ] Test AI Guardrails tồn tại
- [ ] Test Data Masking tồn tại
- [ ] Test RBAC phân quyền tồn tại

## Severity Classification
| Mức | Ý nghĩa |
|---|---|
| **CRITICAL** | Lỗi bảo mật, data loss, vi phạm y đức AI — phải sửa ngay |
| **HIGH** | Vấn đề lớn ảnh hưởng chức năng nghiệp vụ cốt lõi |
| **MEDIUM** | Cần cải thiện, ảnh hưởng đến chất lượng |
| **LOW** | Góp ý nhỏ, refactoring, style |

## Ví dụ CRITICAL Issues
- `password_hash = hashlib.sha256(password).hexdigest()` → CRITICAL (phải dùng bcrypt)
- `GEMINI_API_KEY = "AIza..."` hard-coded → CRITICAL
- AI endpoint trực tiếp query database → CRITICAL
- Không có Data Masking trước LLM call → CRITICAL

## Rules
- **Không** sửa code trong bước review.
- Phân loại từng issue với severity.
- Ghi rõ file, line number và giải thích.

## Outputs
- `docs/code-review.md` (bao gồm tất cả findings với severity)
