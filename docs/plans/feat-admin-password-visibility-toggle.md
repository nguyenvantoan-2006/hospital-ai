# Kế hoạch phát triển: Bổ sung Con mắt Ẩn/Hiện Mật khẩu khởi tạo Bác sĩ & Tài khoản (Admin Dashboard)

- **Mã tính năng:** `feat/admin-password-visibility-toggle`
- **Mục tiêu:**
  1. Thêm nút con mắt (Eye Toggle) cạnh ô "Mật khẩu khởi tạo" trong modal Thêm Bác sĩ (`#mAddDoc`).
  2. Ngăn trình duyệt tự động điền (autofill) mật khẩu của Admin vào form tạo bác sĩ bằng `autocomplete="new-password"`.
  3. Mặc định gợi ý mật khẩu khởi tạo chuẩn: `BacSi@2024!` (có thể bấm con mắt để xem rõ hoặc sửa lại).
  4. Đồng bộ thêm icon con mắt cho cả modal Sửa Bác sĩ (`#mEditDoc`), Thêm Tài khoản (`#mAddUser`), và Đặt lại mật khẩu (`#mResetPwd`).

---

## 1. Danh sách file thay đổi

1. `templates/admin_dashboard.html`:
   - Bọc các ô input password (`#dPassword`, `#ePassword`, `#uPass`, `#rPwd`) trong `.input-group`.
   - Thêm nút `<button class="btn btn-outline-secondary" type="button" onclick="togglePasswordVisibility('inputId', this)">` với icon `<i class="fa-solid fa-eye"></i>`.
   - Thêm `autocomplete="new-password"`.
2. `static/js/admin.js`:
   - Viết hàm dùng chung `togglePasswordVisibility(inputId, btnEl)`.
   - Khi mở modal Thêm Bác sĩ, tự động đặt mật khẩu khởi tạo mẫu `BacSi@2024!` để Admin tiện quản lý.
