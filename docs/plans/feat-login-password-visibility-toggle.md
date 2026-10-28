# Kế hoạch phát triển: Bổ sung Con mắt Ẩn/Hiện Mật khẩu trong Modal Khôi Phục Mật Khẩu (Login)

- **Mã tính năng / Branch:** `feat/login-password-visibility-toggle`
- **Mục tiêu:**
  1. Thêm nút con mắt (Eye Toggle) cho ô "Mật khẩu mới" (`#fpNewPass`) trong Modal Khôi Phục Mật Khẩu Nhân Viên.
  2. Thêm nút con mắt (Eye Toggle) cho ô "Xác nhận mật khẩu mới" (`#fpConfirmPass`).
  3. Sử dụng `.input-group` Bootstrap 5 chuẩn giao diện y tế, icon FontAwesome (`fa-eye` / `fa-eye-slash`).
  4. Nhúng hàm xử lý trực tiếp vào inline `<script>` của `templates/login.html` để chống cache trình duyệt 100%.

---

## 1. Danh sách file thay đổi

| STT | File | Nội dung thay đổi |
|---|---|---|
| 1 | `templates/login.html` | - Bọc `#fpNewPass` và `#fpConfirmPass` trong `.input-group`<br>- Thêm button toggle với icon `<i class="fa-solid fa-eye" style="pointer-events: none;"></i>`<br>- Viết hàm `togglePasswordVisibility` an toàn trong inline script |

---

## 2. Thứ tự thực hiện các bước

1. Cập nhật HTML trong `templates/login.html`:
   - Cấu trúc `.input-group` cho cả 2 ô input mật khẩu.
   - Gắn `onclick="togglePasswordVisibility('fpNewPass', this)"` và `onclick="togglePasswordVisibility('fpConfirmPass', this)"`.
2. Bổ sung script nội tuyến xử lý toggle.
3. Đồng bộ vào container `clinova_fastapi_app`.
4. Viết kịch bản Playwright mở modal khôi phục mật khẩu, nhập mật khẩu và test click con mắt (chụp ảnh kết quả).

---

## 3. Rủi ro & Lưu ý
- Modal Khôi phục mật khẩu có 3 bước (Bước 1: Nhập email/username -> Bước 2: Nhập OTP -> Bước 3: Đặt mật khẩu mới). Cần đảm bảo khi chuyển bước sang Bước 3, các nút con mắt hoạt động mượt mà, không bị che khuất hoặc lỗi form submit.
