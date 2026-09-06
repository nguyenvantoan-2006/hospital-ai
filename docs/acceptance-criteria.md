# Acceptance Criteria — Hệ Thống Quản Lý Phòng Khám có Tích Hợp AI

**Nguồn:** Dựa trên docs/user-stories.md và NHÓM_03.docx  
**Ngày:** 2026-08-30

---

## AC-01: Đăng nhập hệ thống (US-01)

**AC-01-01: Đăng nhập thành công**
```
Given: Người dùng có tài khoản hợp lệ đang hoạt động
When:  Nhập đúng username/email và mật khẩu
Then:  - Hệ thống trả về JWT access token
        - Người dùng được chuyển đến dashboard phù hợp với role
        - Phiên làm việc được khởi tạo
```

**AC-01-02: Đăng nhập sai mật khẩu**
```
Given: Người dùng tồn tại trong hệ thống
When:  Nhập sai mật khẩu
Then:  - HTTP 401 Unauthorized
        - Thông báo lỗi "Tên đăng nhập hoặc mật khẩu không đúng"
        - Không tiết lộ tài khoản có tồn tại hay không
```

**AC-01-03: Tài khoản bị khóa**
```
Given: Tài khoản is_active = false
When:  Cố đăng nhập
Then:  - Từ chối đăng nhập
        - Thông báo yêu cầu liên hệ Admin
```

**AC-01-04: Phân quyền RBAC**
```
Given: Người dùng role "doctor" đã đăng nhập
When:  Truy cập API /admin/users
Then:  - HTTP 403 Forbidden
        - Không hiển thị dữ liệu admin
```

**AC-01-05: Bảo mật mật khẩu**
```
Given: Admin tạo tài khoản mới với mật khẩu "Admin@123"
When:  Xem database bảng users
Then:  - password_hash bắt đầu bằng "$2b$" (bcrypt format)
        - Không có chuỗi plain text "Admin@123" trong database
```

---

## AC-02: Quản lý bệnh nhân (US-03, US-04)

**AC-02-01: Tạo bệnh nhân mới**
```
Given: Lễ tân đã đăng nhập
When:  Nhập đầy đủ thông tin bệnh nhân (họ tên, ngày sinh, SĐT)
Then:  - Hồ sơ được tạo trong database
        - Trả về patient_id
        - Thông báo thành công
```

**AC-02-02: Ngăn trùng hồ sơ**
```
Given: Đã có bệnh nhân với SĐT "0912345678"
When:  Tạo bệnh nhân mới với SĐT "0912345678"
Then:  - Cảnh báo "Số điện thoại đã tồn tại"
        - Hiển thị hồ sơ có thể trùng để lễ tân kiểm tra
        - Không tạo hồ sơ trùng
```

**AC-02-03: Tìm kiếm bệnh nhân**
```
Given: Có bệnh nhân tên "Nguyễn Văn A"
When:  Tìm kiếm với từ khóa "Nguyễn Văn A"
Then:  - Danh sách kết quả hiển thị trong ≤ 2 giây
        - Kết quả chứa thông tin đúng bệnh nhân
```

---

## AC-04: Quản lý lịch khám (US-06, US-07)

**AC-04-01: Đặt lịch thành công**
```
Given: Bác sĩ có lịch trống ngày 2026-09-01 lúc 09:00
When:  Lễ tân đặt lịch cho bệnh nhân vào khung giờ đó
Then:  - Lịch khám được tạo, status = "da_xac_nhan"
        - Hiển thị trong danh sách lịch của bác sĩ đó ngày đó
```

**AC-04-02: Kiểm tra xung đột lịch**
```
Given: Bác sĩ đã có lịch ngày 2026-09-01 lúc 09:00
When:  Lễ tân cố đặt lịch khác cho bác sĩ đó cùng giờ
Then:  - Hệ thống từ chối
        - Thông báo "Bác sĩ đã có lịch vào khung giờ này"
        - Gợi ý khung giờ khác
```

---

## AC-09: Đặt lịch trực tuyến (US-08, US-09)

**AC-09-01: Gửi OTP**
```
Given: Bệnh nhân nhập email hợp lệ, reCAPTCHA pass
When:  Yêu cầu gửi OTP
Then:  - OTP 6 số được gửi đến email trong ≤ 30 giây
        - OTP có hạn sử dụng ≤ 10 phút
        - Rate limit: tối đa 3 OTP/email/giờ
```

**AC-09-02: Đặt lịch thành công qua online**
```
Given: OTP đã xác minh thành công, khung giờ còn trống
When:  Hệ thống xử lý yêu cầu đặt lịch
Then:  - Lịch được tạo với status = "cho_xac_nhan"
        - Mã lịch hẹn (booking_code) được sinh và hiển thị
        - Lễ tân thấy lịch mới trong danh sách cần xác nhận
```

**AC-09-03: OTP hết hạn**
```
Given: OTP đã quá 10 phút
When:  Bệnh nhân nhập OTP đó
Then:  - Thông báo "Mã OTP đã hết hạn"
        - Cho phép yêu cầu gửi OTP mới
```

---

## AC-AI-01: AI Summary (US-13)

**AC-AI-01-01: Data Masking bắt buộc**
```
Given: Bác sĩ mở hồ sơ bệnh nhân "Nguyễn Văn A", SĐT "0912345678"
When:  Hệ thống chuẩn bị gửi dữ liệu cho LLM
Then:  - Dữ liệu gửi LLM KHÔNG chứa "Nguyễn Văn A"
        - Dữ liệu gửi LLM KHÔNG chứa "0912345678"
        - Các trường PII được thay bằng "***" hoặc "BỆNH NHÂN"
```

**AC-AI-01-02: Kết quả là bản nháp**
```
Given: AI trả về bản tóm tắt
When:  Bác sĩ xem kết quả
Then:  - Hiển thị rõ ràng "Bản nháp — chỉ dành cho tham khảo"
        - Không tự động lưu vào hồ sơ bệnh án
        - Bác sĩ có thể xem hồ sơ gốc để đối chiếu
```

**AC-AI-01-03: Fallback khi AI lỗi**
```
Given: LLM API không phản hồi (timeout)
When:  Bác sĩ yêu cầu AI Summary
Then:  - Thông báo "Chức năng AI tạm thời không khả dụng"
        - Bác sĩ vẫn có thể xem hồ sơ bệnh nhân bình thường
        - AI Log ghi nhận status = "fallback"
```

**AC-AI-01-04: AI Log ghi nhận**
```
Given: AI Summary được gọi thành công
When:  Kiểm tra bảng ai_logs
Then:  - Có record với function_name = "ai_summary"
        - input_masked không chứa PII
        - status = "success"
        - duration_ms được ghi nhận
```

---

## AC-AI-02: AI Chatbot (US-14)

**AC-AI-02-01: Trả lời câu hỏi hành chính**
```
Given: Bệnh nhân hỏi "Phòng khám mở cửa lúc mấy giờ?"
When:  Chatbot xử lý câu hỏi
Then:  - Chatbot trả lời về giờ làm việc của phòng khám
        - Câu trả lời lịch sự, dễ hiểu
```

**AC-AI-02-02: Từ chối câu hỏi y tế**
```
Given: Bệnh nhân hỏi "Tôi bị ho, có phải bệnh gì không?"
When:  Chatbot nhận câu hỏi
Then:  - Chatbot TỪ CHỐI lịch sự
        - Giải thích "Tôi chỉ hỗ trợ thông tin hành chính"
        - Hướng dẫn đặt lịch khám bác sĩ
        - KHÔNG đưa ra bất kỳ thông tin y tế nào
```

---

## AC-AI-03: AI Post-exam Guide (US-15)

**AC-AI-03-01: Nội dung bắt buộc phê duyệt**
```
Given: Bác sĩ sử dụng AI sinh hướng dẫn sau khám
When:  AI tạo nội dung hướng dẫn
Then:  - Nội dung hiển thị với trạng thái "BẢN NHÁP — Chờ phê duyệt"
        - Không thể gửi bệnh nhân khi chưa bác sĩ Approve
        - Bác sĩ có thể chỉnh sửa trước khi phê duyệt
```

**AC-AI-03-02: Không thêm thông tin không có trong ghi chú**
```
Given: Bác sĩ ghi chú "uống nhiều nước, nghỉ ngơi 3 ngày"
When:  AI sinh hướng dẫn
Then:  - Nội dung chỉ liên quan đến "uống nước" và "nghỉ ngơi 3 ngày"
        - KHÔNG có thuốc, điều trị hay khuyến nghị thêm không có trong ghi chú
```
