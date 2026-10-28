# Kế hoạch phát triển: Tính năng Quên mật khẩu & Đặt lại mật khẩu (Doctor/Staff Password Recovery & Admin Reset)

- **Mã tính năng:** `feat/auth-forgot-password-and-reset`
- **Phân hệ:** Xác thực & Bảo mật (Auth & Security - FR-AUTH)
- **Nhóm thực hiện:** Nhóm 03 - KTPM K23C
- **Trạng thái:** Chờ phê duyệt kế hoạch

---

## 1. Mục tiêu & Yêu cầu nghiệp vụ (FR)
Giải quyết bài toán thực tế khi Bác sĩ hoặc nhân viên phòng khám quên mật khẩu đăng nhập nội bộ:
1. **Self-Service qua Email OTP (Bác sĩ tự khôi phục):**
   - Cho phép Bác sĩ/Nhân viên yêu cầu mã xác thực OTP 6 số gửi về Email công vụ đã liên kết.
   - Nhập OTP hợp lệ trong vòng 5 phút để tạo Mật khẩu mới an toàn.
   - Bảo mật y tế: Chống dò quét tài khoản (Username Enumeration) bằng thông báo trung lập, giới hạn thử OTP tối đa 3 lần.
2. **Admin/IT Helpdesk Reset (Quản trị viên hỗ trợ khẩn cấp):**
   - Admin có quyền đặt lại mật khẩu trực tiếp cho Bác sĩ từ Admin Dashboard khi Bác sĩ mất quyền truy cập email hoặc cần khám gấp.
   - Ghi nhật ký hệ thống (`audit_logs`) mọi thao tác reset mật khẩu.
3. **Cung cấp thông tin hỗ trợ khẩn cấp:**
   - Trên màn hình Login hiển thị đường dây nóng IT nội bộ để hỗ trợ trực tiếp 24/7.

---

## 2. Danh sách tệp sẽ thay đổi & Lý do

| STT | Đường dẫn tệp | Lý do thay đổi |
| :--- | :--- | :--- |
| 1 | `schemas.py` | Bổ sung Pydantic models: `ForgotPasswordRequest`, `VerifyOtpRequest`, `ResetPasswordRequest`, `AdminResetPasswordRequest`. |
| 2 | `routers/auth.py` | Bổ sung 3 API endpoints: gửi OTP (`/forgot-password`), xác thực OTP (`/verify-otp`), và cập nhật mật khẩu mới (`/reset-password`). |
| 3 | `routers/admin.py` | Bổ sung API Admin reset mật khẩu cho nhân viên (`POST /api/admin/users/{user_id}/reset-password`) kèm ghi Audit Log. |
| 4 | `templates/login.html` | Thêm liên kết "Quên mật khẩu?", Modal popup quy trình 3 bước (Nhập email/user -> Nhập OTP -> Đổi mật khẩu) và hotline IT. |
| 5 | `templates/admin_dashboard.html` & `static/js/admin.js` | Thêm nút icon Chìa khóa trong danh sách Bác sĩ để Admin click reset nhanh mật khẩu khi có yêu cầu. |
| 6 | `run_full_system_test.py` | Bổ sung test cases tự động kiểm tra luồng quên mật khẩu và Admin reset mật khẩu. |

---

## 3. Thứ tự thực hiện các bước

1. **Bước 1 — Định nghĩa Schemas:**
   - Tạo các schema request/response với ràng buộc độ dài mật khẩu tối thiểu 6 ký tự.
2. **Bước 2 — Backend Endpoints (`routers/auth.py` & `routers/admin.py`):**
   - Lưu trữ OTP an toàn trong bộ nhớ kèm thời gian hết hạn (`expire_at = now + 5 phút`).
   - Tích hợp `email_service.send_otp_email` để gửi OTP thật qua Gmail SMTP (fallback in ra console nếu chưa cấu hình SMTP).
   - Xây dựng API Admin reset mật khẩu sinh pass tạm hoặc nhận pass mới, băm bằng `hash_password(new_pass)`.
3. **Bước 3 — Giao diện Modal Quên mật khẩu (`templates/login.html`):**
   - Thiết kế Modal Bootstrap 5 chuyên nghiệp: Chuyển đổi mượt mà giữa các bước (Email -> OTP -> Mật khẩu mới).
   - Thêm đường dây nóng IT hỗ trợ nội bộ.
4. **Bước 4 — Giao diện Admin Reset (`templates/admin_dashboard.html`):**
   - Thêm nút hành động "Reset mật khẩu" và popup xác nhận cho Quản trị viên.
5. **Bước 5 — Kiểm thử & Tự đánh giá:**
   - Chạy test kiểm tra case đúng, case OTP sai, case OTP hết hạn, case Admin reset.
   - Đảm bảo 100% test cases hệ thống vượt qua thành công.

---

## 4. Điểm chú ý về an toàn thông tin y tế
- Không báo lỗi *"Tên đăng nhập không tồn tại"* ở API công khai để tránh hacker liệt kê danh sách bác sĩ.
- Mật khẩu mới bắt buộc phải được băm an toàn qua hàm `bcrypt` / `hash_password`.
- Mọi hành vi reset mật khẩu đều được lưu vết trong bảng `audit_logs` để truy vết trách nhiệm.

