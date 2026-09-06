---
name: security-review
description: Rà soát bảo mật toàn diện Hệ thống Quản lý Phòng Khám có tích hợp AI — kiểm tra OWASP Top 10, bảo mật dữ liệu y tế, AI guardrails và tuân thủ pháp lý. Không sửa code.
---

# Security Review Skill — Hospital AI System

## Objective
Rà soát bảo mật toàn hệ thống, đặc biệt chú ý dữ liệu y tế nhạy cảm và phân hệ AI.

## Inputs
Đọc toàn bộ mã nguồn + `docs/requirements.md` + `docs/architecture.md`

## Security Checklist

### 1. Authentication & Authorization
- [ ] Mật khẩu hash bằng **bcrypt** (passlib) — KHÔNG SHA256
- [ ] JWT secret đủ mạnh (≥32 ký tự, từ env var)
- [ ] JWT có thời hạn hợp lý (ACCESS_TOKEN_EXPIRE_MINUTES)
- [ ] RBAC đúng: admin/receptionist/doctor/accountant
- [ ] Tất cả protected endpoints có `Depends(get_current_user)`
- [ ] Không có "backdoor" (tài khoản hardcode, bypass auth)
- [ ] Tài khoản bị khóa không thể đăng nhập

### 2. SQL Injection
- [ ] Sử dụng SQLAlchemy ORM (parameterized)
- [ ] Không có raw SQL string concatenation: `f"WHERE name='{name}'"` → CRITICAL
- [ ] Tìm kiếm an toàn: `db.query(Patient).filter(Patient.phone == phone)`

### 3. XSS (Cross-Site Scripting)
- [ ] Jinja2 auto-escape HTML output
- [ ] Không render user input raw vào template
- [ ] Content-Security-Policy header được set

### 4. CSRF
- [ ] API endpoint JSON (không dùng form-based POST) → ít rủi ro
- [ ] Kiểm tra nếu dùng cookie-based auth thêm CSRF token

### 5. Data Privacy (Dữ liệu y tế — ưu tiên cao)
- [ ] **Data Masking** hoạt động: ẩn họ tên, SĐT, CCCD, địa chỉ trước LLM
- [ ] `ai_logs.input_masked` không chứa PII
- [ ] Dữ liệu bệnh nhân không lộ ra ngoài phạm vi quyền
- [ ] Tuân thủ Nghị định 13/2023/NĐ-CP (PDPA Việt Nam)

### 6. Secrets Management
- [ ] `GEMINI_API_KEY` từ env var, không hard-code trong source
- [ ] `SECRET_KEY` (JWT) từ env var
- [ ] `DATABASE_URL` từ env var
- [ ] `.env` trong `.gitignore`
- [ ] `.env.example` tồn tại (không chứa giá trị thật)
- [ ] Git history không chứa secrets

### 7. AI-Specific Security (SEC-AI)
- [ ] SEC-AI-01: Data Masking bắt buộc trước mọi LLM call
- [ ] SEC-AI-02: Prompt prohibits: chẩn đoán, kê đơn, phác đồ điều trị
- [ ] SEC-AI-03: Fallback khi LLM lỗi — nghiệp vụ không gián đoạn
- [ ] SEC-AI-04: AI Logs ghi đầy đủ (function, status, duration, user)
- [ ] Chatbot từ chối câu hỏi y tế ngoài phạm vi hành chính

### 8. Input Validation
- [ ] Pydantic v2 validate tất cả request body
- [ ] Validate email format cho đặt lịch online
- [ ] Validate ngày giờ (không đặt lịch quá khứ)
- [ ] Rate Limiting trên OTP endpoint (IP-based)

### 9. OTP Security (FR-09)
- [ ] OTP có thời hạn ≤10 phút
- [ ] OTP tối đa 3-5 lần nhập sai → block
- [ ] Rate Limiting: max 3 OTP/email/giờ
- [ ] OTP không lộ ra response (chỉ gửi qua email)
- [ ] reCAPTCHA v3 kiểm tra trước gửi OTP

### 10. Dependency Vulnerabilities
- [ ] Chạy `pip audit` hoặc `safety check`
- [ ] Không dùng thư viện deprecated/unmaintained
- [ ] `requirements.txt` pin version cụ thể

### 11. Information Leakage
- [ ] Lỗi 500 không trả stack trace cho client
- [ ] Error response chỉ chứa thông điệp thân thiện
- [ ] Server version không lộ trong headers

### 12. Audit Logs
- [ ] `audit_logs` ghi: đăng nhập, thay đổi hồ sơ bệnh nhân, xác nhận thanh toán
- [ ] Log không thể bị xóa bởi user thường

## Severity Classification
| Mức | Ví dụ |
|---|---|
| **CRITICAL** | Hard-code API key, không Data Masking, không bcrypt |
| **HIGH** | Không RBAC, SQL injection khả năng, JWT không expire |
| **MEDIUM** | Missing Rate Limiting, lỗi không log |
| **LOW** | Thiếu CSP header, verbose error message |

## Rules
- **Không** sửa code.
- Tham chiếu file và line number cụ thể.
- Ưu tiên issues liên quan đến dữ liệu y tế và AI.

## Outputs
- `docs/security-review.md`
