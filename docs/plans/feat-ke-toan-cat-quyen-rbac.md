# Kế hoạch: Cắt quyền truy cập Quầy Thuốc, Bệnh Nhân và Admin của tác nhân Kế toán (RBAC Hardening)

## 1. Mục tiêu & Nghiệp vụ
- **Mục tiêu:** Đảm bảo nguyên tắc đặc quyền tối thiểu (Least Privilege) và phân tách trách nhiệm (Separation of Duties) trong hệ thống bệnh viện Clinova đối với vai trò **Kế toán (`ke_toan`)**:
  - Kế toán chỉ tập trung vào nghiệp vụ tài chính, báo cáo thu chi, công nợ và quầy thu ngân (`thanh_toan.html`).
  - **Cắt quyền truy cập:** Kế toán **KHÔNG** được truy cập vào:
    1. **Quầy Thuốc (`quay_thuoc.html`)**: Nghiệp vụ của Dược sĩ / Bác sĩ.
    2. **Hồ sơ Bệnh nhân (`danh_sach_benh_nhan.html`)**: Nghiệp vụ của Lễ tân / Bác sĩ.
    3. **Admin Dashboard (`admin_dashboard.html`)**: Nghiệp vụ quản trị tối cao của Admin.

## 2. Danh sách file sẽ thay đổi
1. `templates/ke_toan.html`:
   - Gỡ bỏ 3 nút liên kết trên thanh Navbar:
     - Nút `Quầy Thuốc` (`quay_thuoc.html`)
     - Nút `Bệnh Nhân` (`danh_sach_benh_nhan.html`)
     - Nút `Admin` (`admin_dashboard.html`)
   - Chỉ giữ lại nút cần thiết: `Quầy Thu Ngân` (`thanh_toan.html`) và nút `Đăng xuất`.
2. `templates/quay_thuoc.html`:
   - Cập nhật hàm bảo vệ `initAuthGuard(["admin", "le_tan", "bac_si"])` — **loại bỏ vai trò `ke_toan`** khỏi danh sách cho phép vào trang Quầy Dược.
3. `templates/danh_sach_benh_nhan.html` & `templates/admin_dashboard.html`:
   - Xác nhận rằng các trang này đã chặn vai trò `ke_toan` (hiển thị thông báo không có quyền và tự động quay về `ke_toan.html` nếu cố tình nhập URL).

## 3. Thứ tự thực hiện các bước
1. **Bước 1:** Chỉnh sửa thanh Navbar trong `templates/ke_toan.html`.
2. **Bước 2:** Cập nhật `initAuthGuard` trong `templates/quay_thuoc.html`.
3. **Bước 3:** Viết script kiểm thử Playwright tự động:
   - Đăng nhập với tài khoản `ketoan`.
   - Kiểm tra Navbar trang `ke_toan.html`: Không còn nút `Quầy Thuốc`, `Bệnh Nhân`, `Admin`.
   - Thử truy cập trực tiếp URL `quay_thuoc.html`, `danh_sach_benh_nhan.html`, `admin_dashboard.html`: Hệ thống chặn lại và cảnh báo không có quyền truy cập.
   - Chụp ảnh màn hình làm bằng chứng kiểm thử.
4. **Bước 4:** Commit từng nhóm file theo chuẩn `AGENTS.md`.

## 4. Rủi ro & Lưu ý
- Đảm bảo Kế toán vẫn giữ nguyên quyền vào `thanh_toan.html` (Quầy thu ngân / hóa đơn).
- TUYỆT ĐỐI KHÔNG push code lên remote Git khi chưa có sự xác nhận của người dùng.
