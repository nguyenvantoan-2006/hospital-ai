# Kế hoạch phát triển: Phân quyền Menu động (Dynamic Role-based Sidebar Navigation)

- **Mã tính năng:** `feat/dynamic-rbac-sidebar-navigation`
- **Mục tiêu:** 
  1. Đồng bộ hóa phân quyền hiển thị thanh điều hướng (Sidebar/Navbar) theo từng Tác nhân (Bác sĩ, Lễ tân, Kế toán, Admin).
  2. Bác sĩ KHÔNG hiển thị menu Hóa đơn & Quầy thuốc (tập trung 100% vào khám bệnh).
  3. Kế toán đảm nhiệm 2 phân hệ rõ rệt: Thu ngân & Cấp phát thuốc tại quầy (`thanh_toan.html`, `quay_thuoc.html`) và Kế toán Tổng hợp & Lương (`ke_toan.html`).
  4. Lễ tân chỉ hiển thị menu Tiếp đón, Cấp STT và Tra cứu bệnh nhân.
  5. Đảm bảo Route Guard chặn truy cập trái phép nếu gõ URL trực tiếp.

---

## 1. Phân quyền hiển thị Menu chi tiết

| Trang giao diện | Bác sĩ (`bac_si`) | Lễ tân (`le_tan`) | Kế toán (`ke_toan`) | Quản trị (`admin`) |
| :--- | :---: | :---: | :---: | :---: |
| **Trang chủ** (`index.html` / `dashboard.html`) | ✅ Hiện | ✅ Hiện | ✅ Hiện | ✅ Hiện |
| **Quản lý Bệnh nhân** (`danh_sach_benh_nhan.html`) | ✅ Hiện | ✅ Hiện | ✅ Hiện | ✅ Hiện |
| **Lịch hẹn & Tiếp nhận** (`lich_kham.html`) | ✅ Hiện (xem hàng chờ) | ✅ Hiện (tiếp đón & cấp STT) | ❌ Ẩn | ✅ Hiện |
| **Khám bệnh (Bác sĩ)** (`lap_phieu_kham.html`) | ✅ Hiện | ❌ Ẩn | ❌ Ẩn | ✅ Hiện |
| **Hóa đơn & Thanh toán** (`thanh_toan.html`) | ❌ Ẩn | ❌ Ẩn | ✅ Hiện | ✅ Hiện |
| **Quầy Dược & Cấp phát** (`quay_thuoc.html`) | ❌ Ẩn | ❌ Ẩn | ✅ Hiện | ✅ Hiện |
| **Kế toán & Tài chính / Lương** (`ke_toan.html`) | ❌ Ẩn | ❌ Ẩn | ✅ Hiện | ✅ Hiện |
| **Admin Dashboard** (`admin_dashboard.html`) | ❌ Ẩn | ❌ Ẩn | ❌ Ẩn | ✅ Hiện |

---

## 2. Danh sách tệp thay đổi

1. `static/js/auth.js`:
   - Bổ sung hàm `applyDynamicSidebarNav()` tự động chạy khi trang load.
   - Quét tất cả các liên kết `a.nav-item-custom`, `a.nav-link`, `.sidebar a` và ẩn các mục không có quyền truy cập.
   - Cập nhật hàm `initAuthGuard(allowedRoles)` chặt chẽ.
2. `templates/lap_phieu_kham.html`:
   - Gắn class/data-roles chuẩn trên sidebar.
   - Tích hợp khối Viện phí tạm tính ngay dưới Đơn thuốc.
3. `templates/lich_kham.html`, `templates/thanh_toan.html`, `templates/quay_thuoc.html`, `templates/ke_toan.html`:
   - Đồng bộ gọi `applyDynamicSidebarNav()` và chuẩn hóa Route Guard.

