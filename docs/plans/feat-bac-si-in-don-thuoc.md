# Kế hoạch Thực hiện: Tính Năng In Đơn Thuốc Trực Tiếp Cho Bác Sĩ (Hướng 1)
- **Branch:** `feat/bac-si-in-don-thuoc`
- **Người thực hiện:** User 1 (Frontend & Workflow)
- **Yêu cầu / FR liên quan:** FR-05 (Lập phiếu khám), FR-06 (Kê đơn thuốc điện tử), FR-AI-03 (Hướng dẫn sau khám)
- **Trạng thái:** ⏳ Chờ xác nhận từ người dùng

---

## 1. Phân tích yêu cầu & Mục tiêu
- **Mục tiêu chức năng:**
  * Cho phép Bác sĩ xem trước (Print Preview) và in ngay Đơn thuốc điện tử (khổ A5) trực tiếp trên trang khám bệnh `lap_phieu_kham.html`.
  * Không bắt buộc Bác sĩ phải chuyển đổi thủ công giữa các Tab nhánh Closed-loop (tự động kích hoạt Tab Kê đơn khi có thuốc).
  * Hỗ trợ 2 chế độ in:
    1. **Xem trước & In nháp:** Bác sĩ có thể bấm xem mẫu đơn thuốc bất kỳ lúc nào ngay khi đang nhập thuốc trên bảng để đối chiếu.
    2. **Lưu & In 1-Click:** Lưu phiếu khám vào CSDL ➔ Tự động mở hộp thoại in trình duyệt (`window.print()`).
- **Luồng người dùng (User Flow):**
  1. Bác sĩ chọn bệnh nhân từ hàng chờ ➔ Nhập triệu chứng, chẩn đoán.
  2. Tại bảng **Kê Đơn Thuốc Điện Tử (FR-06)**, Bác sĩ chọn thuốc và nhập liều dùng.
  3. Bác sĩ có thể bấm nút **"Xem Trước Đơn Thuốc (A5)"** ngay cạnh nút `+ Thêm thuốc` để xem trước mẫu in.
  4. Bác sĩ bấm **"Lưu & In Đơn Thuốc Ngay"**: Hệ thống lưu phiếu khám ➔ Đẩy đơn sang Quầy Dược & Kế toán ➔ Mở ngay bản in A5 cho Bác sĩ in ra máy in.

---

## 2. Danh sách File cần thay đổi
| File | Loại thay đổi | Mục đích / Lý do |
| :--- | :--- | :--- |
| `templates/lap_phieu_kham.html` | Sửa | - Bổ sung nút "Xem trước Đơn Thuốc (A5)" tại header bảng kê đơn.<br>- Tự động active Tab 2 khi bác sĩ thêm thuốc.<br>- Bổ sung nút 1-Click "Lưu & In Đơn Thuốc Ngay".<br>- Cập nhật hàm `previewDonThuocLive()` lấy dữ liệu trực tiếp từ form.<br>- Tinh chỉnh CSS `@media print` cho khổ A5 chuẩn y tế. |
| `docs/plans/feat-bac-si-in-don-thuoc.md` | Thêm mới | File kế hoạch theo quy định AGENTS.md. |

---

## 3. Kế hoạch Tách Commit
- [ ] **Commit 1 (Docs & Plan):** `docs(plan): them ke hoach feat-bac-si-in-don-thuoc`
- [ ] **Commit 2 (Frontend Template):** `feat(ui): them nut xem truoc va in don thuoc truc tiep cho bac si tren lap_phieu_kham`

---

## 4. Kế hoạch Tự Kiểm tra & Test (Self-Verification)
- [ ] Kiểm tra cú pháp Javascript / HTML không bị lỗi cú pháp.
- [ ] Kiểm tra hiển thị bảng in: Đầy đủ tên bệnh nhân, tuổi, giới tính, mã BHYT, chẩn đoán, danh mục thuốc (tên thuốc, số lượng, liều dùng), lời dặn dò, chữ ký bác sĩ.
- [ ] Kiểm tra luồng lưu phiếu: Bấm "Lưu & In" tạo bản ghi thành công trong CSDL (`phieu_khams`, `don_thuocs`).
- [ ] Kiểm thử với tài khoản Bác sĩ: `bacsi` / `BacSi@2024!`.

---

> ⚠️ **CHỐT CHẶN (HUMAN GATE):** AI Agent phải dừng tại đây và chờ người dùng gõ xác nhận duyệt kế hoạch trước khi bắt đầu viết code!
