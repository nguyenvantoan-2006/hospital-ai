# Kế hoạch phát triển: Chuẩn hóa Lịch trực Đặt lịch & Đồng bộ Màn hình Gọi số Kiosk

- **Branch:** `feat/kiosk-sync-and-schedule-validation`
- **Các vấn đề cần xử lý:**
  1. **Lịch trực Bác sĩ khi Đặt lịch Online:** Bác sĩ không có ca trực trong ngày (ví dụ chỉ trực Thứ 3, 5, 7 ca chiều nhưng hôm nay Thứ 4) vẫn mở slot cho bệnh nhân đặt. Cần chặn triệt để và hiển thị đúng lịch trực.
  2. **Giao diện Màn hình Kiosk (`man_hinh_phong_kham.html`):** Thanh chọn phòng bị đè lên tiêu đề phòng khám. Cần thiết kế lại gọn gàng, thêm nút Ẩn/Hiện thanh chọn phòng cho chế độ Kiosk TV và thêm ô Tìm kiếm / Tra cứu nhanh số thứ tự.
  3. **Đồng bộ Gọi số Bác sĩ - Kiosk:** Bác sĩ bấm "Mời vào khám" / "Mời vào kết luận" trên Bàn làm việc phải cập nhật chuẩn xác 100% dữ liệu số thứ tự, tên bệnh nhân, phòng khám lên Màn hình Kiosk và phát loa.

---

## 1. Danh sách file sẽ thay đổi

| STT | File | Lý do thay đổi |
|---|---|---|
| 1 | `routers/lich_khams.py` | - Xây dựng hàm parser lịch trực `is_doctor_working_on(lich_truc, target_date)`<br>- Cập nhật endpoint `/public/available-slots`: Chặn đặt lịch ngày bác sĩ không trực, chỉ mở slot đúng ca trực (sáng/chiều)<br>- Nâng cấp `/public/queue-display`: Đồng bộ chuẩn theo phòng khám, bác sĩ và trạng thái ưu tiên kết luận CLS |
| 2 | `templates/dat_lich_online.html` | - Hiển thị cảnh báo rõ ràng khi bác sĩ không trực ngày đã chọn<br>- Tự động vô hiệu hóa các slot ngoài ca trực, hiển thị nhãn "Ngoài ca trực" |
| 3 | `templates/man_hinh_phong_kham.html` | - Sửa lỗi layout bị chồng đè giữa dropdown phòng và tiêu đề phòng khám<br>- Thêm nút bật/tắt (Ẩn / Hiện) thanh chọn phòng cho chế độ TV toàn màn hình<br>- Thêm modal / thanh tìm kiếm tra cứu nhanh STT, mã lịch hẹn, tên bệnh nhân<br>- Cập nhật hiển thị ưu tiên khi bệnh nhân có kết quả cận lâm sàng vào kết luận |
| 4 | `templates/lap_phieu_kham.html` | - Thêm nút "📺 Màn hình Gọi số phòng này" để Bác sĩ mở nhanh Kiosk chuẩn phòng của mình<br>- Đảm bảo khi bấm "Mời vào khám" / "Mời vào kết luận", dữ liệu đồng bộ tức thì với Kiosk |

---

## 2. Thứ tự thực hiện các bước

### Bước 1: Xử lý logic Lịch trực Bác sĩ (Backend & Frontend Đặt lịch)
- Phân tích cú pháp các mẫu lịch trực: `Thứ 3, 5, 7 (Ca chiều: 13:00 - 18:00)`, `Thứ 2, 4, 6 (Ca sáng: 07:00 - 12:00)`, `Thứ 2 - Thứ 6`, `Cả ngày Thứ 7 & Chủ Nhật`.
- Khi gọi `/api/v1/lich-khams/public/available-slots`:
  + Kiểm tra ngày khám đối chiếu với lịch trực bác sĩ.
  + Nếu không trực ngày này: Trả về `is_working_day: false`, `ly_do: "Bác sĩ không có lịch trực vào..."`.
  + Nếu chỉ trực chiều: Vô hiệu hóa ca sáng (`available: false`, lý do: `Ngoài ca trực`).
  + Nếu chỉ trực sáng: Vô hiệu hóa ca chiều.
- Cập nhật UI `dat_lich_online.html` thông báo trực quan và chặn chọn slot không hợp lệ.

### Bước 2: Tinh chỉnh Giao diện Kiosk Gọi số (`man_hinh_phong_kham.html`)
- Chuyển dropdown chọn phòng thành thanh công cụ trên góc phải, không dùng vị trí fixed đè lên tiêu đề.
- Thêm nút Toggle **"👁️ Ẩn thanh chọn phòng"** (thu gọn thành nút icon nhỏ ở góc hoặc bật toàn màn hình).
- Thêm nút **"🔍 Tra cứu STT"**: Người dùng nhập số thứ tự hoặc họ tên để tra cứu nhanh vị trí trong hàng đợi.

### Bước 3: Đồng bộ Gọi số Bác sĩ - Kiosk
- Kiểm tra việc liên kết giữa Bác sĩ và Phòng khám để Kiosk luôn nhận đúng ca `dang_kham`.
- Bổ sung nút liên kết Kiosk ngay trên Bàn làm việc Bác sĩ (`lap_phieu_kham.html`).
- Kiểm thử luồng gọi số từ Bác sĩ -> Màn hình Kiosk phát loa và hiển thị chuẩn xác.

---

## 3. Rủi ro & Điểm cần chú ý
- Lịch trực trong CSDL có nhiều định dạng tiếng Việt tự do (có dấu, không dấu, khoảng trắng, viết tắt). Parser cần viết bằng Regex linh hoạt để nhận diện chính xác các thứ trong tuần và ca sáng/chiều.
- Khi người dùng chọn phòng trên Kiosk, cần tự động lưu lại vào `localStorage` để khi refresh trang không bị nhảy về phòng mặc định khác.
