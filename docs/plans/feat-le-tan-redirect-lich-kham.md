# Kế hoạch: Đồng bộ trang đích sau khi đăng nhập cho Lễ tân về Lịch hẹn & Tiếp nhận (FR-01, FR-03)

## 1. Mục tiêu & Nghiệp vụ
- **Mục tiêu:** Khi người dùng có vai trò Lễ tân (`le_tan`, ví dụ tài khoản `letan`) đăng nhập thành công vào hệ thống Clinova, trình duyệt phải tự động chuyển hướng vào đúng trang **Lịch hẹn & Tiếp nhận bệnh nhân (`lich_kham.html`)**.
- **Giải quyết lỗi:** Hiện tại đang bị chuyển nhầm sang trang cũ `patient_management.html` (giao diện 2 cột cũ, thiếu thanh điều hướng Sidebar Clinova chuẩn).

## 2. Danh sách file sẽ thay đổi
1. `static/js/auth.js`:
   - Cập nhật `DEFAULT_HOME_PAGE.le_tan = "lich_kham.html"` (thay vì `"patient_management.html"`).
   - Đảm bảo khi lễ tân đăng nhập hoặc truy cập các trang không có quyền, hệ thống sẽ fallback về `lich_kham.html`.
2. `templates/dashboard.html` (nếu có liên kết đến `patient_management.html`):
   - Đổi liên kết Quản lý bệnh nhân sang `danh_sach_benh_nhan.html` để đồng bộ hoàn toàn.

## 3. Thứ tự thực hiện các bước
1. **Bước 1:** Cập nhật `static/js/auth.js`.
2. **Bước 2:** Cập nhật các liên kết tồn đọng trong `templates/dashboard.html`.
3. **Bước 3:** Chạy kiểm thử tự động với Playwright:
   - Mô phỏng đăng nhập tài khoản `letan`.
   - Xác minh URL sau đăng nhập là `http://127.0.0.1:8000/lich_kham.html`.
   - Chụp ảnh màn hình giao diện tiếp nhận bệnh nhân.
4. **Bước 4:** Commit từng nhóm file theo chuẩn `AGENTS.md`.

## 4. Rủi ro & Lưu ý
- Không ảnh hưởng đến các vai trò khác (`admin`, `bac_si`, `ke_toan`).
- TUYỆT ĐỐI KHÔNG push code lên remote Git khi chưa có lệnh từ người dùng.
