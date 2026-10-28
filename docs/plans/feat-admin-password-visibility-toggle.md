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
   - Thêm nút `<button class="btn btn-outline-secondary" type="button" onclick="togglePasswordVisibility('inputId', this)">` với icon `<i class="fa-solid fa-eye" style="pointer-events: none;"></i>`.
   - Thêm `autocomplete="new-password"`.
   - Nhúng trực tiếp hàm `togglePasswordVisibility` vào inline `<script>` để chống cache trình duyệt 100%.
   - Thêm query version `admin.js?v=20261028_1001` vào thẻ nạp script.
2. `static/js/admin.js`:
   - Viết hàm dùng chung `togglePasswordVisibility(inputId, btnEl)` với xử lý icon và class trực tiếp, an toàn tuyệt đối.
   - Khi mở modal Thêm Bác sĩ, tự động đặt mật khẩu khởi tạo mẫu `BacSi@2024!` để Admin tiện quản lý.

## 2. Khắc phục sự cố "mắt ko dùng dc" (Browser Cache & Event Binding)
- **Nguyên nhân:** File `admin.js` bị lưu cache trên trình duyệt người dùng nên hàm `togglePasswordVisibility` chưa được nạp khi click.
- **Biện pháp khắc phục triệt để:**
  1. Định nghĩa `togglePasswordVisibility` ngay trong HTML inline script của `admin_dashboard.html`.
  2. Thêm `pointer-events: none;` cho icon `<i>` bên trong button.
  3. Cập nhật `admin.js?v=20261028_1001`.
  4. Thêm listener `DOMContentLoaded` tự động gán click handler cho các nút con mắt.
  5. Đồng bộ vào Docker container `clinova_fastapi_app`.

