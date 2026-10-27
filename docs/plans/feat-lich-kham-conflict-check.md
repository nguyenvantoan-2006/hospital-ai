# Kế hoạch phát triển: Đặt lịch theo khung giờ (Time-Slot) & Chống trùng lịch Bác sĩ (Chuẩn App Bệnh viện Bạch Mai)

- **Mã tính năng:** `feat/lich-kham-conflict-check`
- **Yêu cầu chức năng liên quan:** FR-03 (Đặt lịch khám trực tuyến), FR-04 (Điều phối & Tiếp nhận bệnh nhân)
- **Tham chiếu thực tế:** Ứng dụng Bệnh viện Bạch Mai (BV Bạch Mai Mobile App)

---

## 1. Phân tích bài toán & Mô hình giải pháp

### 🔴 Vấn đề hiện tại:
- Hiện tại hệ thống đang cho phép đặt lịch theo khung giờ rộng (08:00, 09:00, 10:00...) và cho phép tối đa 20 người/giờ.
- Dẫn đến tình huống: 2 bệnh nhân cùng đặt đúng **08:00** của cùng một Bác sĩ, gây trùng lặp thời gian khám, bệnh nhân phải chờ đợi và bác sĩ không thể tiếp 2 người cùng 1 phút.

### 🟢 Giải pháp chuẩn hóa theo App Bệnh viện Bạch Mai:
1. **Chia nhỏ khung giờ (Time-Slot 15 phút):**
   - **Buổi sáng (07:00 - 11:45):**
     `07:00`, `07:15`, `07:30`, `07:45`, `08:00`, `08:15`, `08:30`, `08:45`, `09:00`, `09:15`, `09:30`, `09:45`, `10:00`, `10:15`, `10:30`, `10:45`, `11:00`, `11:15`, `11:30`, `11:45`.
   - **Buổi chiều (13:30 - 16:30):**
     `13:30`, `13:45`, `14:00`, `14:15`, `14:30`, `14:45`, `15:00`, `15:15`, `15:30`, `15:45`, `16:00`, `16:15`, `16:30`.
2. **Quy tắc Chống trùng lịch (Exclusive 1-to-1 Slot Lock):**
   - Mỗi Slot (ví dụ: `08:00 - 08:15`) của một Bác sĩ tại một ngày cụ thể **chỉ phục vụ tối đa 01 bệnh nhân**.
   - Nếu bệnh nhân A đã đặt `08:00` ngày 28/10 với Bác sĩ Oanh -> Slot `08:00` chuyển sang trạng thái **"ĐÃ KÍN" (Disabled / Đã đặt)**.
   - Bệnh nhân B khi vào đặt lịch cùng ngày sẽ thấy nút `08:00` bị mờ/khóa, hệ thống gợi ý chọn các slot liền kề còn trống: `08:15`, `08:30`...
3. **Kiểm tra trùng lặp đa lớp (Double-Check Backend):**
   - Ngay cả khi 2 người cùng bấm nút "Đặt lịch" tại cùng 1 giây, Transaction Backend sẽ khóa và người đến sau sẽ nhận thông báo: *"Khung giờ 08:00 của Bác sĩ vừa có người đặt. Vui lòng chọn khung giờ trống tiếp theo!"*

---

## 2. Danh sách tệp sẽ thay đổi & Lý do

| STT | File thay đổi | Mục đích & Thay đổi |
| :---: | :--- | :--- |
| 1 | `routers/lich_khams.py` | - Thêm endpoint `GET /api/v1/lich-khams/available-slots`: Nhận `bac_si_id` + `ngay`, trả về danh sách các slot 15 phút kèm trạng thái `available: true/false`.<br>- Bổ sung hàm kiểm tra trùng lặp tuyệt đối (Slot conflict lock) khi tạo mới lịch khám. |
| 2 | `templates/dat_lich_online.html` | Cải tiến giao diện chọn giờ khám thành **Lưới khung giờ Slot 15 phút** giống 100% giao diện App Bệnh viện Bạch Mai (chia Buổi sáng / Buổi chiều, slot kín hiển thị mờ). |
| 3 | `templates/index.html` | Cập nhật modal đặt lịch online đồng bộ lưới Slot. |
| 4 | `templates/lich_kham.html` | Tiếp nhận tại quầy của Lễ tân cũng hiển thị lưới Slot trống tương tự để điều phối chuẩn xác. |

---

## 3. Thứ tự thực hiện các bước

- **Bước 1:** Viết API `available-slots` và logic chống trùng 1:1 trong `routers/lich_khams.py`.
- **Bước 2:** Thiết kế UI Lưới chọn giờ (Time Slot Grid) chuẩn Bạch Mai (thẻ bấm tròn, chia ca Sáng/Chiều, đổi màu khi chọn, disabled khi kín).
- **Bước 3:** Tích hợp gọi API động: Khi người dùng đổi ngày hoặc đổi bác sĩ -> Lưới giờ tự động tải lại trạng thái trống/kín tức thì.
- **Bước 4:** Tự kiểm tra (Unit test backend & Playwright UI walkthrough).

---

## 4. Điểm chú ý & Rủi ro
- Các lịch khám cũ đã tạo trước đây vẫn giữ nguyên không bị ảnh hưởng.
- Không phát sinh thay đổi cấu trúc bảng cơ sở dữ liệu (tận dụng trường `thoi_gian` sẵn có).

