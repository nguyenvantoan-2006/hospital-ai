# Yêu Cầu Khách Hàng — Hệ Thống Quản Lý Phòng Khám có Tích Hợp AI

**Nguồn:** NHÓM_03.docx — Khảo sát hiện trạng và phân tích yêu cầu  
**Ngày:** 2026-08-30  
**Nhóm:** 03 — KTPM K23C | GVHD: TS. Nguyễn Đình Dũng

---

## 1. Bối cảnh

Phòng khám tư nhân hiện đang quản lý bằng sổ sách thủ công và Excel, dẫn đến:
- Trùng lịch khám bác sĩ
- Tra cứu hồ sơ lịch sử khám chậm
- Áp lực hành chính lớn cho lễ tân (trả lời lặp câu hỏi quy trình)
- Tổng hợp báo cáo doanh thu tốn nhiều thời gian
- Thiếu phân quyền và ghi nhật ký truy cập dữ liệu bệnh nhân

---

## 2. Yêu Cầu Hệ Thống Mới

### 2.1. Người dùng và vai trò
Hệ thống phục vụ 5 nhóm người dùng:

**Quản trị viên (Admin):**
- Đăng nhập hệ thống
- Quản lý tài khoản người dùng và phân quyền
- Quản lý bác sĩ và chuyên khoa
- Phân công lịch trực, ca làm việc
- Theo dõi nhật ký truy cập (Audit Logs) và nhật ký AI (AI Logs)
- Xem báo cáo thống kê

**Lễ tân (Receptionist):**
- Tiếp nhận bệnh nhân, tạo/cập nhật hồ sơ hành chính
- Đặt lịch khám, thay đổi/hủy lịch
- Kiểm tra xung đột lịch tự động
- Lập hóa đơn và cập nhật thanh toán

**Bác sĩ (Doctor):**
- Tra cứu lịch khám được phân công
- Xem hồ sơ bệnh nhân, lập phiếu khám
- Kê đơn thuốc điện tử
- Sử dụng AI tóm tắt hồ sơ bệnh án (chỉ tham khảo)
- Sử dụng AI sinh hướng dẫn sau khám (phải phê duyệt trước khi dùng)

**Kế toán (Accountant):**
- Quản lý danh mục dịch vụ và biểu giá
- Xác nhận thanh toán viện phí
- Xuất báo cáo thống kê doanh thu

**Bệnh nhân (Patient — Guest/Public):**
- Đặt lịch khám trực tuyến qua cổng thông tin
- Xác minh OTP qua email
- Tra cứu thông tin lịch hẹn cá nhân
- Sử dụng AI Chatbot hỏi về quy trình, thủ tục, giá dịch vụ

### 2.2. Chức năng nghiệp vụ cốt lõi
1. **Đăng nhập và phân quyền** theo vai trò (RBAC)
2. **Quản lý bệnh nhân**: tạo, cập nhật, tìm kiếm, tra cứu lịch sử
3. **Quản lý bác sĩ và chuyên khoa**: thêm, sửa, phân công lịch
4. **Quản lý lịch khám**: đặt, thay đổi, hủy, kiểm tra xung đột
5. **Khám bệnh và lập phiếu khám**: ghi triệu chứng, chẩn đoán, kết luận
6. **Kê đơn thuốc điện tử**: chọn thuốc, liều dùng, kiểm tra tồn kho
7. **Quản lý thanh toán viện phí**: hóa đơn, xác nhận, in biên lai
8. **Báo cáo và thống kê**: số lượt khám, doanh thu, hiệu suất bác sĩ
9. **Đặt lịch khám trực tuyến**: OTP email + reCAPTCHA + Rate Limiting

### 2.3. Chức năng AI tích hợp
Hệ thống cần chatbot AI và trợ lý hành chính thông minh:

**AI tóm tắt hồ sơ bệnh án:**
- Tóm tắt lịch sử khám để bác sĩ xem nhanh trước khi khám
- CHỈ hỗ trợ hành chính, không thay thế hồ sơ gốc

**AI Chatbot:**
- Trả lời câu hỏi về quy trình khám, thủ tục, giờ làm việc, giá dịch vụ
- KHÔNG chẩn đoán bệnh, KHÔNG tư vấn điều trị

**AI sinh hướng dẫn sau khám:**
- Sinh nội dung từ ghi chú của bác sĩ
- Bắt buộc bác sĩ phê duyệt trước khi gửi bệnh nhân

### 2.4. Yêu cầu kỹ thuật
- Ngôn ngữ: Python, Framework: FastAPI
- Cơ sở dữ liệu: PostgreSQL (SQLite cho môi trường dev/test)
- Bảo mật: bcrypt, JWT, RBAC, Data Masking, Audit Logs
- AI: tích hợp qua API LLM (Gemini) — key từ environment variable

### 2.5. Giới hạn hệ thống (điều bắt buộc)
- AI KHÔNG được chẩn đoán bệnh tự động
- AI KHÔNG được kê đơn thuốc hoặc đề xuất phác đồ điều trị
- AI KHÔNG được thay thế quyết định chuyên môn của bác sĩ
- Dữ liệu PII phải được ẩn danh trước khi gửi tới LLM
- Mọi nội dung AI phải được bác sĩ kiểm tra và phê duyệt

---

## 3. Ràng buộc pháp lý
- Luật Khám bệnh, chữa bệnh (Luật số 15/2023/QH15)
- Nghị định 13/2023/NĐ-CP (Bảo vệ dữ liệu cá nhân)
- Thông tư 46/2017/TT-BYT (Hồ sơ bệnh án điện tử)
