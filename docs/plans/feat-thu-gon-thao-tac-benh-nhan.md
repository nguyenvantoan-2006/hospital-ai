# Kế hoạch: Thu gọn cột "THAO TÁC" thành Menu 3 chấm (Dropdown ⋮) bảng Hồ sơ Bệnh nhân

## 1. Mục tiêu & Nghiệp vụ
- **Mục tiêu:** Tối ưu hóa tối đa không gian hiển thị bảng danh sách hồ sơ bệnh nhân (`danh_sach_benh_nhan.html`).
- **Yêu cầu cụ thể:**
  - Chuyển đổi cột "THAO TÁC" từ 2 nút riêng biệt sang **Menu 3 chấm thả xuống (Dropdown ⋮)**.
  - Cột thao tác thu nhỏ về chỉ khoảng 45px - 50px, nút 3 chấm dạng icon tròn tối giản, thanh lịch (`.btn-action-dropdown`).
  - Khi click vào nút 3 chấm sẽ mở menu xổ xuống (Dropdown Menu) với các lựa chọn:
    - `Cập nhật hồ sơ` (icon bút xanh `fa-pen-to-square`)
    - `Xóa hồ sơ bệnh nhân` (icon thùng rác đỏ `fa-trash`)
  - Đảm bảo Dropdown không bị che khuất bởi thuộc tính overflow của `.table-responsive` nhờ cấu hình Popper fixed / boundary viewport.

## 2. Danh sách file thay đổi
- `templates/danh_sach_benh_nhan.html`:
  - Điều chỉnh `<th>`: `<th class="text-center" style="width: 50px;">Thao tác</th>`.
  - Bổ sung CSS cho nút 3 chấm (`.btn-action-dropdown`), hover effect và style cho dropdown menu.
  - Cập nhật hàm `fetchPatients()`: Render nút dropdown Bootstrap 5 kèm menu hành động.

## 3. Thứ tự thực hiện
1. **Bước 1:** Cập nhật CSS và cấu trúc dropdown trong `templates/danh_sach_benh_nhan.html`.
2. **Bước 2:** Kiểm thử giao diện bằng Playwright, chụp ảnh trạng thái bình thường và trạng thái khi mở menu 3 chấm.
3. **Bước 3:** Commit theo quy tắc `AGENTS.md`.

## 4. Rủi ro & Lưu ý
- Không bị che khuất khi mở dropdown ở các dòng cuối bảng.
- Tuyệt đối KHÔNG thực hiện `git push` hoặc merge lên `main` khi chưa có sự đồng ý của người dùng.
