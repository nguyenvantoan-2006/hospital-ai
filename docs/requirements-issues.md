# Requirements Issues — Hệ Thống Quản Lý Phòng Khám có Tích Hợp AI

**Ngày phân tích:** 2026-08-30  
**Người phân tích:** AI Agent + Human Review (Nhóm 03)

---

## Danh sách vấn đề cần làm rõ

### ISSUE-01: Thông tin chính xác về giờ làm việc cho Chatbot
**Loại:** Thiếu thông tin  
**Liên quan:** FR-AI-02  
**Mô tả:** Knowledge base cho AI Chatbot cần được cung cấp thông tin cụ thể về giờ làm việc, bảng giá dịch vụ, quy trình cụ thể của phòng khám. Tài liệu SRS chưa định nghĩa cách nạp Knowledge Base này.  
**Đề xuất:** Admin nhập thông tin Knowledge Base vào cấu hình hệ thống; hoặc dùng file `clinic_info.json`.  
**Trạng thái:** ⏳ Cần làm rõ

---

### ISSUE-02: Giới hạn số lần đăng nhập sai
**Loại:** Thiếu thông tin  
**Liên quan:** FR-01, NFR-SEC-01  
**Mô tả:** SRS đề cập "tài khoản bị khóa" nhưng không xác định sau bao nhiêu lần đăng nhập sai thì tài khoản bị khóa tự động.  
**Đề xuất:** Mặc định sau 5 lần sai liên tiếp trong 15 phút → khóa 30 phút.  
**Trạng thái:** ⏳ Cần làm rõ

---

### ISSUE-03: Thời gian hết hạn JWT Token
**Loại:** Thiếu thông tin  
**Liên quan:** FR-01, NFR-SEC-01  
**Mô tả:** SRS không xác định thời hạn token. Cần xác định ACCESS_TOKEN_EXPIRE_MINUTES.  
**Đề xuất:** Access token: 30 phút; Refresh token: 7 ngày (nếu dùng).  
**Trạng thái:** ⏳ Cần làm rõ

---

### ISSUE-04: Định nghĩa "lịch trực" bác sĩ
**Loại:** Thiếu thông tin  
**Liên quan:** FR-03, FR-04  
**Mô tả:** Chưa rõ cấu trúc lịch trực: theo ca (sáng/chiều/tối), theo slot (mỗi 30 phút), hay theo ngày?  
**Đề xuất:** Lịch theo slot 30 phút, từ 07:00 đến 17:00, có thể cấu hình.  
**Trạng thái:** ⏳ Cần làm rõ

---

### ISSUE-05: Quản lý tồn kho thuốc
**Loại:** Thiếu thông tin  
**Liên quan:** FR-06  
**Mô tả:** SRS đề cập "không kê vượt số lượng thuốc hiện có" nhưng không mô tả chức năng nhập kho thuốc (ai nhập, quy trình?).  
**Đề xuất:** Admin/Kế toán nhập kho thuốc; hệ thống trừ tồn kho khi đơn thuốc xác nhận.  
**Trạng thái:** ⏳ Cần làm rõ

---

### ISSUE-06: Giao diện Patient Portal
**Loại:** Chưa rõ phạm vi  
**Liên quan:** FR-09, FR-10  
**Mô tả:** SRS đề cập "Cổng thông tin bệnh nhân" nhưng không mô tả đủ UI/UX. Cần xác định: có phải tạo domain riêng không, hay chỉ là route `/patient` trên cùng domain?  
**Đề xuất:** Route `/patient/*` trên cùng FastAPI app, không cần login nội bộ.  
**Trạng thái:** ⏳ Cần làm rõ

---

### ISSUE-07: Chính sách bảo mật AI Logs
**Loại:** Thiếu thông tin  
**Liên quan:** SEC-AI-04  
**Mô tả:** AI Logs cần lưu bao lâu? Ai được xem? Có cần mã hóa không?  
**Đề xuất:** Lưu 12 tháng; chỉ Admin xem; không cần mã hóa thêm (đã masked PII).  
**Trạng thái:** ⏳ Cần làm rõ

---

### ISSUE-08: Định dạng export báo cáo
**Loại:** Thiếu thông tin  
**Liên quan:** FR-08  
**Mô tả:** SRS đề cập "xuất PDF hoặc Excel" nhưng không xác định rõ định dạng nào là ưu tiên.  
**Đề xuất:** Giai đoạn 1: chỉ cần hiển thị trên web; Giai đoạn 2: xuất CSV/Excel.  
**Trạng thái:** ⏳ Cần làm rõ

---

## Confirmed Assumptions (Giả thiết đã sử dụng)

| # | Giả thiết | Lý do |
|---|---|---|
| A-01 | Bcrypt sử dụng cost factor 12 | Cân bằng bảo mật và hiệu năng |
| A-02 | Data Masking ẩn: họ tên, SĐT, CCCD, địa chỉ, số BHYT | Dựa trên Nghị định 13/2023 |
| A-03 | LLM mặc định là Gemini API | Phù hợp với dự án Python |
| A-04 | SQLite cho môi trường dev, PostgreSQL cho production | Dễ setup ban đầu |
| A-05 | JWT không dùng refresh token (đơn giản hóa) | Phạm vi đồ án |

---

## No Hallucination Check ✅
Các yêu cầu sau **KHÔNG** có trong SRS và **KHÔNG** được thêm vào:
- ❌ "Bệnh nhân có thể xem kết quả xét nghiệm online" (không có trong SRS)
- ❌ "Tích hợp với bảo hiểm y tế quốc gia" (SRS nói rõ ngoài phạm vi)
- ❌ "AI chẩn đoán tự động" (vi phạm y đức — cấm tuyệt đối)
- ❌ "Thanh toán online qua MoMo/VNPay" (không đề cập trong SRS)
