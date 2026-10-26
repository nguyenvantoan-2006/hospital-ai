# Architecture Decision Records (ADR) — Hospital-AI

**Dự án:** Hospital-AI Management System  
**Nhóm:** 03 — KTPM K23C | GVHD: TS. Nguyễn Đình Dũng  
**Định dạng:** MADR (Markdown Architectural Decision Records)

> ADR là tài liệu ghi lại **tại sao** chúng ta chọn một giải pháp kỹ thuật cụ thể.  
> Mỗi quyết định được đánh số, có trạng thái và không bị xóa khi thay đổi (chỉ được "deprecated").

---

## ADR-001: Chọn FastAPI làm Web Framework

**Ngày:** 2026-08-15  
**Trạng thái:** ✅ Accepted

### Bối cảnh
Cần chọn Python web framework cho hệ thống quản lý phòng khám có tích hợp AI.

### Các lựa chọn đã xem xét
| Option | Ưu điểm | Nhược điểm |
|--------|---------|-----------|
| Django | Đầy đủ tính năng, ORM tốt | Nặng, khó tùy chỉnh AI endpoints |
| Flask | Nhẹ, linh hoạt | Thiếu async, phải tự cấu hình nhiều |
| **FastAPI** | Async native, OpenAPI tự động, Pydantic V2 | Ít template sẵn hơn Django |

### Quyết định
Chọn **FastAPI** vì:
- Hỗ trợ `async/await` native → phù hợp với các lượt gọi AI API (latency cao)
- Tự động sinh **OpenAPI docs** tại `/docs` → tiện test
- Tích hợp tốt với **Pydantic V2** cho validation
- Performance cao hơn Django/Flask trong các benchmark

### Hệ quả
- Cần hiểu rõ Dependency Injection của FastAPI
- Template rendering dùng Jinja2 riêng (không có built-in như Django)

---

## ADR-002: Chọn PostgreSQL làm Database

**Ngày:** 2026-08-15  
**Trạng thái:** ✅ Accepted

### Bối cảnh
Cần CSDL quan hệ lưu trữ hồ sơ bệnh nhân, lịch khám, hóa đơn với tính toàn vẹn cao.

### Các lựa chọn đã xem xét
| Option | Ghi chú |
|--------|---------|
| SQLite | Chỉ dùng cho dev/test, không production |
| MySQL | Phổ biến nhưng kém hơn PostgreSQL về ACID |
| **PostgreSQL** | ACID mạnh, hỗ trợ JSON, Railway support tốt |
| MongoDB | NoSQL không phù hợp với dữ liệu quan hệ phòng khám |

### Quyết định
Chọn **PostgreSQL** vì:
- ACID compliance cực kỳ quan trọng cho dữ liệu y tế (hóa đơn, lịch khám)
- Hỗ trợ deploy trên Railway (managed PostgreSQL)
- SQLAlchemy hỗ trợ hoàn hảo
- Hỗ trợ `TEXT` type cho AI output (ai_summary, huong_dan_sau_kham)

### Hệ quả
- Dev local dùng SQLite (qua `DATABASE_URL` trong `.env`)
- Production dùng Railway PostgreSQL

---

## ADR-003: Chọn Google Gemini làm AI Model

**Ngày:** 2026-08-20  
**Trạng thái:** ✅ Accepted

### Bối cảnh
Cần AI model để: tóm tắt hồ sơ bệnh nhân, sinh hướng dẫn sau khám, và chatbot hỏi đáp.

### Các lựa chọn đã xem xét
| Option | Ưu điểm | Nhược điểm |
|--------|---------|-----------|
| OpenAI GPT-4 | Mạnh nhất | Đắt tiền, không free tier |
| **Gemini 1.5 Flash** | Free tier, nhanh, đủ chất lượng | Đôi khi chậm hơn GPT |
| Llama (local) | Không cần API key | Cần GPU, phức tạp deploy |

### Quyết định
Chọn **Google Gemini 1.5 Flash** vì:
- **Free tier** phù hợp cho dự án học thuật
- Tốc độ nhanh, đủ chất lượng cho tóm tắt y tế đơn giản
- SDK Python (`google-generativeai`) dễ dùng
- Nhóm đã có tài khoản Google AI Studio

### Hệ quả
- Phụ thuộc vào Google AI API (rate limit, availability)
- Cần exponential backoff khi gặp rate limit
- Cần Data Masking để không gửi PII lên cloud

---

## ADR-004: Áp dụng Data Masking cho AI Calls

**Ngày:** 2026-08-25  
**Trạng thái:** ✅ Accepted

### Bối cảnh
Dữ liệu bệnh nhân là PII (Personally Identifiable Information) — không được gửi thẳng lên AI API.

### Quyết định
Trước khi gửi prompt lên Gemini API, **bắt buộc** thay thế:
- Tên bệnh nhân → `[BN_001]`
- Số điện thoại → `[SDT_MASKED]`
- CCCD → `[CCCD_MASKED]`
- Địa chỉ → `[DIA_CHI_MASKED]`

### Implementation
```python
# routers/ai.py — hàm mask_pii()
def mask_pii(text: str, benh_nhan_id: int) -> str:
    # Replace tên, SĐT, CCCD với placeholder
    ...
```

### Hệ quả
- AI response chỉ dựa trên triệu chứng + chẩn đoán (không có PII)
- Ghi `prompt_masked` vào bảng `ai_logs` (không ghi thông tin thật)
- Đảm bảo tuân thủ quy định bảo mật dữ liệu y tế

---

## ADR-005: Sử dụng JWT cho Authentication

**Ngày:** 2026-08-20  
**Trạng thái:** ✅ Accepted

### Bối cảnh
Hệ thống cần xác thực người dùng (Admin, Lễ tân, Bác sĩ, Kế toán) và phân quyền theo role.

### Quyết định
Dùng **JWT (JSON Web Token)** với:
- Library: `python-jose[cryptography]`
- Algorithm: HS256
- Expiry: 8 giờ (phù hợp ca làm việc)
- Payload: `user_id`, `role`, `exp`

### Lý do không dùng Session-based auth
- JWT stateless → không cần lưu session trên server
- Phù hợp với FastAPI Dependency Injection pattern
- Dễ mở rộng nếu sau này thêm mobile app

### Hệ quả
- Không thể revoke token trước khi hết hạn (trừ khi thêm blacklist)
- Bệnh nhân không có JWT — dùng **Guest mode** (không token)

---

## ADR-006: Server-side Rendering với Jinja2 (không dùng SPA)

**Ngày:** 2026-08-18  
**Trạng thái:** ✅ Accepted

### Bối cảnh
Cần chọn cách render giao diện: Server-side (SSR) hay Single Page App (React/Vue).

### Quyết định
Chọn **Jinja2 Server-side Rendering** vì:
- Đơn giản hơn cho nhóm (không cần học thêm React/Vue)
- SEO friendly
- Phù hợp timeline dự án học thuật
- FastAPI hỗ trợ Jinja2 tích hợp tốt

### Hệ quả
- Mỗi page reload sẽ gọi server
- Dynamic interactions (dropdown, AJAX) vẫn dùng Vanilla JS
- Không có state management phức tạp

---

## ADR-007: Quản lý số thứ tự (STT) theo Bác sĩ + Ngày

**Ngày:** 2026-09-10  
**Trạng thái:** ✅ Accepted

### Bối cảnh
Hệ thống cần cấp số thứ tự xếp hàng khám bệnh. Cần xác định phạm vi STT.

### Quyết định
STT được tính **theo bác sĩ + theo ngày**:
- Mỗi bác sĩ có STT riêng, reset về 1 mỗi ngày mới
- Giới hạn: `BacSi.so_benh_nhan_toi_da_ngay` (default 200/ngày)
- Giới hạn khung giờ: `BacSi.so_benh_nhan_toi_da_khung_gio` (default 20/khung giờ)

### Lý do
- Mỗi bác sĩ có tốc độ khám khác nhau → cần giới hạn riêng
- Tránh quá tải một bác sĩ cụ thể

### Hệ quả
- Query phức tạp hơn khi tính STT (cần GROUP BY bac_si_id + DATE)
- Cần sync STT khi lịch hủy (recalculate STT remaining)

---

## ADR-008: Feature Branch Workflow + Squash Merge

**Ngày:** 2026-08-15  
**Trạng thái:** ✅ Accepted

### Bối cảnh
Nhóm 2 người làm song song trên nhiều tính năng — cần chiến lược Git tránh conflict.

### Quyết định
- **Feature Branch**: mỗi tính năng = 1 branch `feat/<name>`
- **Squash Merge**: khi hoàn thành, squash tất cả commits thành 1 commit rõ ràng vào `main`
- **main protected**: không commit/push trực tiếp lên `main`

### Lý do
- Squash merge giữ history `main` sạch và dễ đọc
- Feature branch cho phép 2 người làm song song không conflict

### Hệ quả
- Mất chi tiết commit history khi squash (nhưng feature branch vẫn còn)
- Cần rebase thường xuyên để tránh conflict lớn

---

*Mọi quyết định kiến trúc mới cần được thêm vào file này.*  
*Format: ADR-XXX, ngày, trạng thái (Proposed / Accepted / Deprecated / Superseded).*
