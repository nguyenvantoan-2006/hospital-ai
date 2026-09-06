# Yêu Cầu Phần Mềm — Hệ Thống Quản Lý Phòng Khám có Tích Hợp AI

**Dự án:** Hospital-AI Management System  
**Nhóm:** 03 — KTPM K23C | GVHD: TS. Nguyễn Đình Dũng  
**Nguồn SRS:** NHÓM_03.docx  
**Ngày:** 2026-08-30  
**Trạng thái:** ✅ APPROVED (Human Gate 1)

---

## 1. Actors (Tác nhân)

| Actor | Mô tả |
|---|---|
| Quản trị viên (Admin) | Quản lý toàn hệ thống, tài khoản, phân quyền |
| Lễ tân (Receptionist) | Tiếp nhận, đặt lịch, hồ sơ bệnh nhân |
| Bác sĩ (Doctor) | Khám bệnh, kê đơn, sử dụng AI hỗ trợ |
| Kế toán (Accountant) | Thanh toán, báo cáo tài chính |
| Bệnh nhân (Patient) | Đặt lịch trực tuyến, AI Chatbot (Guest) |

---

## 2. Functional Requirements (Yêu cầu chức năng)

### FR-01: Đăng nhập và phân quyền
- **Actor:** Admin, Lễ tân, Bác sĩ, Kế toán
- **Mô tả:** Xác thực người dùng bằng username/email + password, phân quyền theo vai trò (RBAC).
- **Ràng buộc:** Mật khẩu hash bcrypt; JWT token; Bệnh nhân dùng Guest mode.

### FR-02: Quản lý bệnh nhân
- **Actor:** Lễ tân, Bác sĩ
- **Mô tả:** CRUD hồ sơ bệnh nhân, tìm kiếm theo tên/SĐT/mã, xem lịch sử khám.
- **Ràng buộc:** Một bệnh nhân chỉ có một hồ sơ (kiểm tra trùng SĐT).

### FR-03: Quản lý bác sĩ và chuyên khoa
- **Actor:** Admin
- **Mô tả:** Thêm/sửa/khóa bác sĩ, quản lý chuyên khoa, phân công lịch trực.
- **Ràng buộc:** Một bác sĩ không được phân công nhiều ca trực cùng thời điểm.

### FR-04: Quản lý lịch khám
- **Actor:** Lễ tân
- **Mô tả:** Đặt lịch, thay đổi, hủy lịch khám; tự động kiểm tra xung đột lịch bác sĩ.
- **Ràng buộc:** UNIQUE(doctor_id, scheduled_at) — không trùng lịch.

### FR-05: Khám bệnh và lập phiếu khám
- **Actor:** Bác sĩ
- **Mô tả:** Ghi nhận triệu chứng, chẩn đoán, kết luận, chỉ định điều trị vào phiếu khám điện tử.
- **Ràng buộc:** Chỉ bác sĩ được lập phiếu khám.

### FR-06: Kê đơn thuốc điện tử
- **Actor:** Bác sĩ
- **Mô tả:** Chọn thuốc từ danh mục, nhập liều dùng, số lượng, hướng dẫn sử dụng.
- **Ràng buộc:** Không được kê vượt số lượng thuốc hiện có; chỉ bác sĩ kê đơn.

### FR-07: Quản lý thanh toán viện phí
- **Actor:** Kế toán
- **Mô tả:** Tổng hợp chi phí (khám + dịch vụ + thuốc), xác nhận thanh toán, in hóa đơn.
- **Ràng buộc:** Chỉ kế toán xác nhận thanh toán; tổng tiền phải khớp với tính toán hệ thống.

### FR-08: Báo cáo và thống kê
- **Actor:** Admin, Kế toán
- **Mô tả:** Thống kê số lượt khám, doanh thu, hiệu suất bác sĩ theo ngày/tháng/năm.
- **Ràng buộc:** Chỉ người có quyền được xem báo cáo; dữ liệu doanh thu bảo mật.

### FR-09: Đặt lịch khám trực tuyến
- **Actor:** Bệnh nhân (Guest)
- **Mô tả:** Bệnh nhân chọn chuyên khoa, bác sĩ, khung giờ, xác minh OTP email, tạo lịch "Chờ xác nhận".
- **Ràng buộc:** reCAPTCHA v3; OTP 6 số, hết hạn sau ≤10 phút; Rate Limiting; kiểm tra lại xung đột trước khi tạo.

### FR-10: Tra cứu thông tin cá nhân
- **Actor:** Bệnh nhân (Guest)
- **Mô tả:** Tra cứu lịch hẹn bằng SĐT + mã lịch hẹn.

### FR-AI-01: AI tóm tắt hồ sơ bệnh án
- **Actor:** Bác sĩ
- **Mô tả:** Tóm tắt lịch sử khám bệnh để bác sĩ xem nhanh.
- **Ràng buộc:** Data Masking bắt buộc; chỉ tham khảo, không thay thế hồ sơ gốc.

### FR-AI-02: AI Chatbot
- **Actor:** Bệnh nhân, Lễ tân
- **Mô tả:** Trả lời câu hỏi về quy trình, thủ tục, giờ làm việc, giá dịch vụ.
- **Ràng buộc:** KHÔNG chẩn đoán, KHÔNG kê đơn, KHÔNG tư vấn điều trị.

### FR-AI-03: AI hướng dẫn sau khám
- **Actor:** Bác sĩ
- **Mô tả:** Sinh nội dung hướng dẫn từ ghi chú bác sĩ.
- **Ràng buộc:** Bắt buộc bác sĩ phê duyệt trước khi lưu và gửi bệnh nhân.

---

## 3. Non-Functional Requirements (Yêu cầu phi chức năng)

### NFR-PER-01: Hiệu năng
- Đăng nhập, tìm kiếm, mở hồ sơ: ≤ 2 giây
- Chức năng AI: ≤ 5 giây (điều kiện bình thường)
- Hỗ trợ nhiều người dùng đồng thời

### NFR-SEC-01: Bảo mật
- Xác thực bắt buộc trước truy cập nghiệp vụ
- Mật khẩu: **bcrypt** (không SHA256, không plain text)
- RBAC theo 4 vai trò nội bộ + Guest cho bệnh nhân
- Data Masking: ẩn PII trước khi gửi LLM
- Audit Logs + AI Logs đầy đủ

### NFR-REL-01: Độ tin cậy
- Dữ liệu lưu chính xác, không mất
- Khi AI lỗi → Fallback, nghiệp vụ vẫn chạy bình thường
- Thông báo lỗi rõ ràng cho người dùng

### NFR-USM-01: Khả năng sử dụng & bảo trì
- Giao diện trực quan, responsive (Chrome/Edge/Firefox)
- Code tổ chức rõ ràng, có tài liệu kỹ thuật

### NFR-SCA-01: Khả năng mở rộng
- Thêm module mới không phá vỡ hệ thống hiện có
- Thay đổi LLM provider không cần refactor toàn bộ

### SEC-AI-01: Data Masking
Ẩn: họ tên, SĐT, CCCD, địa chỉ, số bảo hiểm trước khi gửi LLM.

### SEC-AI-02: AI Guardrails
AI không chẩn đoán, không kê đơn, không thay thế bác sĩ. Mọi output AI cần phê duyệt.

### SEC-AI-03: Fallback Mechanism
AI lỗi → hệ thống thông báo và tiếp tục xử lý thông thường.

### SEC-AI-04: AI Logs
Ghi: thời gian, người dùng, chức năng AI, input_masked, trạng thái.

---

## 4. Business Rules (Quy tắc nghiệp vụ)

| BR# | Quy tắc |
|---|---|
| BR-01 | Một bác sĩ không có 2 lịch khám cùng thời điểm |
| BR-02 | Phiếu khám chỉ tạo sau khi bệnh nhân được tiếp nhận |
| BR-03 | Chỉ bác sĩ lập phiếu khám và kê đơn thuốc |
| BR-04 | Chỉ kế toán xác nhận thanh toán |
| BR-05 | AI chỉ hỗ trợ hành chính, không thay thế bác sĩ |
| BR-06 | Nội dung AI phải được bác sĩ phê duyệt trước khi dùng |
| BR-07 | Một bệnh nhân = một hồ sơ duy nhất (kiểm tra trùng SĐT) |
| BR-08 | Lịch trực tuyến có trạng thái "Chờ xác nhận" cho đến khi lễ tân duyệt |

---

## 5. Assumptions (Giả thiết)

- Phòng khám có kết nối Internet ổn định.
- Thiết bị đầu cuối hỗ trợ trình duyệt hiện đại.
- Admin đã nhập dữ liệu danh mục (bác sĩ, chuyên khoa, dịch vụ) trước khi vận hành.
- LLM API (Gemini) hoạt động bình thường trong điều kiện sử dụng thông thường.

---

## 6. Requirement Traceability Matrix

| Mã YC | Chức năng | Use Case | Test Case |
|---|---|---|---|
| FR-01 | Đăng nhập/RBAC | UC-01 | TC-01 |
| FR-02 | Quản lý bệnh nhân | UC-02 | TC-02 |
| FR-03 | Bác sĩ/Chuyên khoa | UC-12 | TC-03 |
| FR-04 | Lịch khám | UC-04 | TC-04 |
| FR-05 | Phiếu khám | UC-05 | TC-05 |
| FR-06 | Kê đơn thuốc | UC-06 | TC-06 |
| FR-07 | Thanh toán | UC-07 | TC-07 |
| FR-08 | Báo cáo | UC-13 | TC-08 |
| FR-09 | Đặt lịch online | UC-03 | TC-09 |
| FR-10 | Tra cứu cá nhân | UC-11 | TC-10 |
| FR-AI-01 | AI Summary | UC-08 | TC-AI-01 |
| FR-AI-02 | AI Chatbot | UC-09 | TC-AI-02 |
| FR-AI-03 | AI Post-exam | UC-10 | TC-AI-03 |
