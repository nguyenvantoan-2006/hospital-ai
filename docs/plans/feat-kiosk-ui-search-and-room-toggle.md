# Kế hoạch phát triển: Bổ sung Tìm kiếm & Ẩn/Hiện Thanh Chọn Phòng trên Màn hình Kiosk Gọi số

- **Branch:** `feat/kiosk-ui-search-and-room-toggle`
- **Mục tiêu:**
  1. Loại bỏ hoàn toàn lỗi hiển thị: Thanh chọn phòng khám bị cố định vị trí (`fixed right: 560px`) đè trực tiếp lên banner tiêu đề `PHÒNG 101 - NỘI TỔNG QUÁT`.
  2. Bổ sung tính năng **"Ẩn thanh phòng lên"**:
     - Cho phép thu gọn/ẩn thanh chọn phòng lên trên để màn hình Kiosk TV hiển thị sạch sẽ, trang trọng khi trình chiếu ở sảnh/cửa phòng.
     - Có nút Toggle mở lại thanh chọn phòng khi cần cấu hình đổi phòng.
  3. Bổ sung nút **"🔍 Tra cứu STT / Tìm kiếm phòng & bệnh nhân"**:
     - Cho phép tìm kiếm nhanh phòng khám theo từ khóa.
     - Cho phép bệnh nhân/người nhà tra cứu số thứ tự của mình (đang khám, đang chờ vị trí số mấy, bác sĩ phụ trách).

---

## 1. Danh sách file thay đổi

| STT | File | Lý do thay đổi |
|---|---|---|
| 1 | `templates/man_hinh_phong_kham.html` | - Chuyển thanh chọn phòng thành slidebar thanh lịch có thể ẩn lên trên (`toggleRoomSelector`)<br>- Tích hợp các nút điều khiển (Đổi phòng, Tra cứu, Bật loa) vào header chuẩn flexbox, không đè lên banner phòng<br>- Thêm Modal Tra cứu số thứ tự & Bệnh nhân phục vụ Kiosk |

---

## 2. Thứ tự thực hiện các bước

### Bước 1: Điều chỉnh CSS và HTML Header
- Bỏ CSS `.room-selector-box { position: fixed; right: 560px; }` và `.audio-control-btn { position: fixed; right: 320px; }`.
- Tổ chức lại Header: Bên trái là Brand Logo, Ở giữa là Banner phòng khám (`.room-badge-banner`), Bên phải là Cụm nút điều khiển và Đồng hồ kỹ thuật số.
- Tạo slidebar `.room-selector-slidebar` nằm gọn ngay dưới header, mặc định có nút "Ẩn lên" và lưu trạng thái vào `localStorage`.

### Bước 2: Thêm Modal Tra cứu STT & Lịch khám cho Kiosk
- Nút "🔍 Tra cứu STT": mở modal hiển thị nhanh danh sách hàng đợi hoặc ô tìm kiếm theo STT/Tên.
- Hiển thị rõ: STT hiện tại, số người đang chờ trước bạn, bác sĩ phụ trách và phòng khám.

### Bước 3: Đồng bộ vào Docker & Kiểm thử Playwright
- Đồng bộ `templates/man_hinh_phong_kham.html` vào container `clinova_fastapi_app`.
- Kiểm thử hiển thị không còn đè chữ, test nút ẩn/hiện thanh phòng và nút tìm kiếm.

---

## 3. Kết quả hoàn thành
- [x] Đã khắc phục 100% hiện tượng đè chữ giữa thanh chọn phòng và banner tiêu đề phòng trên màn hình Kiosk TV.
- [x] Đã bổ sung nút "Đổi phòng" dạng toggle cho phép thu gọn/mở rộng thanh chọn phòng mượt mà.
- [x] Đã bổ sung nút "Tìm kiếm" mở modal tra cứu số thứ tự và tình trạng hàng đợi cho bệnh nhân/người nhà.
- [x] Đã kiểm thử hiển thị trên Playwright và kiểm thử trên môi trường Docker container.
- [x] Đã tài liệu hóa chi tiết kèm hình ảnh minh chứng trong báo cáo đồ án `NHOM_03_HOAN_CHINH_.docx`.

