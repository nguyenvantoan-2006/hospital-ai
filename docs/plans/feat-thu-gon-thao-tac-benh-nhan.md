# Kế hoạch: Thu gọn các nút trong cột "THAO TÁC" bảng Hồ sơ Bệnh nhân (UI Enhancement)

## 1. Mục tiêu & Nghiệp vụ
- **Mục tiêu:** Tối ưu hóa không gian hiển thị bảng danh sách hồ sơ bệnh nhân (`danh_sach_benh_nhan.html`).
- **Yêu cầu cụ thể:**
  - Thu gọn các nút trong cột "THAO TÁC" thành nhóm nút icon siêu nhỏ (compact `btn-group`).
  - Nút được thiết kế tinh tế (kích thước nhỏ gọn, padding vừa phải, viền bo nhẹ, icon sắc nét, có tooltip hướng dẫn).
  - Giảm chiều rộng của cột Thao tác (`style="width: 90px;"`), giúp bảng không bị tràn ngang hoặc che khuất các thông tin quan trọng khác như Tiền sử bệnh, Mã BHYT, Số CCCD.

## 2. Danh sách file thay đổi
- `templates/danh_sach_benh_nhan.html`:
  - Cập nhật định dạng cột header: Giới hạn độ rộng hợp lý (`<th class="text-center" style="width: 90px;">Thao tác</th>`).
  - Thêm CSS cho lớp `.btn-action-compact`: Kích thước khoảng 28x28px, border mềm, hiệu ứng hover nhẹ nhàng.
  - Cập nhật hàm render dòng bệnh nhân trong JavaScript (`fetchPatients()`): Gom nút Sửa (`fa-pen-to-square`) và nút Xóa (`fa-trash`) vào thẻ `<div class="btn-group btn-group-sm">` siêu nhỏ gọn kèm tooltip Bootstrap.

## 3. Thứ tự thực hiện
1. **Bước 1:** Bổ sung CSS `.btn-compact-group` và `.btn-compact-action` trong `<style>` của `danh_sach_benh_nhan.html`.
2. **Bước 2:** Cập nhật cột tiêu đề `<th>Thao tác</th>` và hàm render table row trong `danh_sach_benh_nhan.html`.
3. **Bước 3:** Kiểm tra giao diện trực tiếp trên trình duyệt, chụp ảnh kiểm thử để đối chiếu với ảnh yêu cầu của người dùng.
4. **Bước 4:** Commit theo quy chuẩn `AGENTS.md`.

## 4. Rủi ro & Lưu ý
- Đảm bảo các hàm gọi sự kiện `onclick="editPatient(...)"` và `onclick="deletePatient(...)"` hoạt động bình thường, không bị ảnh hưởng logic.
- Không tự ý `git push` hoặc squash merge lên `main` khi chưa có lệnh từ người dùng.
