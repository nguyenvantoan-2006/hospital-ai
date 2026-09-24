# Kế hoạch Thực hiện: Xây dựng Phân hệ Kế toán Toàn diện (CLINOVA Finance & Accounting)
- **Branch:** `feat/ke-toan-dashboard`
- **Người thực hiện:** Antigravity AI Agent & Nhóm 03
- **Yêu cầu / FR liên quan:** Mở rộng FR-07 (Thanh toán viện phí), FR-08 (Báo cáo & Thống kê tài chính)
- **Trạng thái:** ⏳ Chờ người dùng duyệt kế hoạch

---

## 1. Phân tích yêu cầu & Mục tiêu

### Mục tiêu chức năng:
1. **Quản lý & Phát lương nhân viên (Payroll):**
   - Lập bảng tính lương theo tháng/năm cho nhân viên và bác sĩ (Lương cơ bản + Phụ cấp + Thưởng - Khấu trừ = Thực lĩnh).
   - Cập nhật trạng thái phát lương (`chua_chi` -> `da_chi`), lưu vết ngày chi và ghi chú.
   - Tính toán tổng chi phí quỹ lương vào báo cáo tài chính.
2. **Quản lý Xuất - Nhập Kho Dược / Hàng hóa:**
   - Quản lý số lượng tồn kho và giá vốn nhập hàng của thuốc/vật tư y tế.
   - Lập phiếu nhập kho từ nhà cung cấp (ghi nhận chi phí mua hàng đầu vào).
   - Báo cáo xuất thuốc theo đơn khám bệnh (ghi nhận doanh thu bán dược phẩm và giá vốn hàng bán).
3. **Quản lý Doanh thu Viện phí theo Bệnh nhân:**
   - Bảng kê chi tiết từng bệnh nhân: Tiền khám + Tiền thuốc + Trạng thái thu tiền + Hình thức thanh toán.
4. **Báo cáo Thống kê Đa chiều (Ngày / Tháng / Quý):**
   - Lọc doanh thu và chi phí linh hoạt:
     * Theo Ngày cụ thể hoặc khoảng ngày.
     * Theo Tháng trong năm.
     * Theo Quý (Quý I: T1-T3, Quý II: T4-T6, Quý III: T7-T9, Quý IV: T10-T12).
   - Báo cáo kết quả hoạt động kinh doanh: `Doanh thu thuần` - `Giá vốn hàng bán` - `Chi phí lương` = `Lợi nhuận ròng`.
5. **Xuất file Báo cáo Thực tế (Excel .xlsx / CSV UTF-8):**
   - Xuất dữ liệu thật dạng file bảng tính (Excel/CSV tiếng Việt có dấu chuẩn UTF-8-BOM) tải trực tiếp về máy tính người dùng.
6. **Giao diện Kế toán Tổng hợp (`templates/ke_toan.html`):**
   - Xây dựng giao diện trực quan, đồng bộ phong cách CLINOVA, phục vụ trực tiếp trang `http://localhost:8000/ke_toan.html` mà người dùng đang mở.

---

## 2. Danh sách File cần thay đổi & Thêm mới

| File | Loại | Mục đích & Chi tiết |
| :--- | :---: | :--- |
| `models.py` | Sửa | Thêm bảng `BangLuong`, `PhieuNhapKho`, `ChiTietNhapKho`; thêm cột `so_luong_ton`, `gia_nhap` vào bảng `Thuoc`. |
| `schemas.py` | Sửa | Thêm Pydantic schemas cho Bảng lương, Phiếu nhập kho, Bộ lọc Ngày/Tháng/Quý. |
| `routers/ke_toan.py` | **Thêm mới** | Toàn bộ API nghiệp vụ Kế toán: Phát lương, Nhập kho, Báo cáo Ngày/Tháng/Quý, Xuất file báo cáo. |
| `main.py` | Sửa | Đăng ký `ke_toan.router` vào `/api/v1/ke-toan`. |
| `templates/ke_toan.html` | **Thêm mới** | Giao diện Dashboard Kế toán Tổng hợp & Tài chính (Dashboard thu chi, Bảng lương, Kho thuốc, Xuất báo cáo). |
| `templates/thanh_toan.html` | Sửa | Thêm nút điều hướng nhanh sang Dashboard Kế toán `ke_toan.html`. |

---

## 3. Kế hoạch Tách Commit theo Quy tắc AGENTS.md

- [ ] **Commit 1 (Model & Schemas):** `feat(model): them bang bang_luong, phieu_nhap_kho va cap nhat model thuoc`
- [ ] **Commit 2 (Backend Router):** `feat(api): them router ke_toan xu ly phat luong, kho duoc, bao cao quy va xuat file`
- [ ] **Commit 3 (Frontend Template):** `feat(ui): them trang ke_toan.html quan ly tai chinh va cap nhat main.py`

---

## 4. Kế hoạch Tự Kiểm tra & Test (Self-Verification)

- [ ] Kiểm tra tính toàn vẹn CSDL (SQLAlchemy tự tạo các bảng mới khi khởi động).
- [ ] Test API: Tạo bảng lương, phát lương, nhập kho thuốc, lọc doanh thu theo Ngày/Tháng/Quý.
- [ ] Test xuất file báo cáo: Tải file về và kiểm tra định dạng dữ liệu không bị lỗi font tiếng Việt.
- [ ] Test giao diện trên trình duyệt: Truy cập `http://localhost:8000/ke_toan.html`, kiểm tra các tab hoạt động mượt mà, trực quan.

---
> ⚠️ **CHỐT CHẶN (HUMAN GATE):** Chờ người dùng xác nhận duyệt kế hoạch trước khi tiến hành code.
