# Kế hoạch phát triển: Bảo vệ Phiên làm việc & Tối ưu hóa Điều hướng Nội bộ (Internal Navigation & Session Guard)

- **Mã tính năng:** `feat/internal-navigation-and-session-guard`
- **Mục tiêu:**
  1. Nút "Trang chủ" trên Sidebar nội bộ dẫn về "Bàn làm việc chính" của từng vai trò (Bác sĩ -> `lap_phieu_kham.html`, Lễ tân -> `lich_kham.html`, Kế toán -> `ke_toan.html`, Admin -> `admin_dashboard.html`).
  2. Nút xem website Bệnh nhân bên ngoài được tách thành liên kết mở Tab mới riêng biệt (`target="_blank"`), không bao giờ làm mất tab làm việc chuyên môn.
  3. Trên Cổng Bệnh nhân (`index.html`): Tự động phát hiện phiên đăng nhập của nhân viên, hiển thị nút thông minh "Quay lại Bàn làm việc" (1-click trở lại đúng phòng ban mà không cần đăng nhập lại).
  4. Cảnh báo an toàn khi đang khám bệnh / nhập dữ liệu dở dang mà chuyển trang (`beforeunload`).

---

## 1. Danh sách file sẽ thay đổi

1. `templates/lap_phieu_kham.html`:
   - Nút "Trang chủ" trên sidebar đổi `href="lap_phieu_kham.html"`.
   - Nút logo navbar đổi `href="lap_phieu_kham.html"`.
   - Thêm nút xem cổng bệnh nhân: `<a href="index.html" target="_blank" class="nav-item-custom"><i class="fa-solid fa-globe"></i> Cổng Bệnh nhân <i class="fa-solid fa-arrow-up-right-from-square small ms-1 opacity-50"></i></a>`.
   - Thêm cảnh báo khi đang có nội dung khám chưa lưu.
2. `templates/lich_kham.html`:
   - Nút Trang chủ đổi `href="lich_kham.html"`.
   - Logo đổi `href="lich_kham.html"`.
3. `templates/thanh_toan.html`, `templates/quay_thuoc.html`, `templates/ke_toan.html`:
   - Logo navbar đổi `href="ke_toan.html"`.
4. `templates/admin_dashboard.html`:
   - Logo navbar đổi `href="admin_dashboard.html"`.
   - Nút xem trang chính mở `target="_blank"`.
5. `templates/index.html`:
   - Thêm script kiểm tra `localStorage.getItem("access_token")` và `localStorage.getItem("role")`.
   - Nếu đã đăng nhập -> Hiển thị nút: `[BS/LT/KT/AD] Quay lại Bàn làm việc` kèm link về đúng `DEFAULT_HOME_PAGE[role]`.
