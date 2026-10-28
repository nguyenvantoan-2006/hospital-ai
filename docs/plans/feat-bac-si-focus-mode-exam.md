# Kế hoạch phát triển: Chế độ Khám bệnh Toàn màn hình (Tự động Ẩn Hàng chờ khi Gọi Bệnh nhân)

- **Branch:** `feat/bac-si-focus-mode-exam`
- **Mục tiêu:**
  1. Khi Bác sĩ bấm **"Mời vào khám"**, **"Mời vào kết luận"** hoặc chọn một bệnh nhân trong danh sách:
     - Tự động ẩn cột **"Hàng Chờ Khám Hôm Nay"** bên trái.
     - Cột **"Form Khám bệnh & Kê đơn & AI"** tự động mở rộng sang toàn màn hình (`col-12` full-width) giúp giao diện rộng rãi, dễ đọc kết quả CLS, kê đơn thuốc và ghi chép lâm sàng.
  2. Bổ sung nút điều hướng quay lại linh hoạt:
     - Thêm nút **`← Quay lại Hàng chờ (N ca)`** trên đầu form khám bệnh để Bác sĩ có thể quay lại danh sách hàng chờ bất cứ lúc nào chỉ với 1 click.
     - Thêm nút Toggle **`≡ Ẩn / Hiện Hàng chờ`** trên thanh công cụ để bác sĩ chủ động bật/tắt theo ý muốn.
  3. Khi lưu phiếu khám xong hoặc khi hoàn tất ca khám:
     - Tự động hiển thị lại Hàng chờ để Bác sĩ đón bệnh nhân tiếp theo.

---

## 1. Danh sách file thay đổi

| STT | File | Lý do thay đổi |
|---|---|---|
| 1 | `templates/lap_phieu_kham.html` | - Thêm ID `#colQueue` (`col-lg-4`) và `#colExam` (`col-lg-8`)<br>- Thêm nút `← Quay lại Hàng chờ` vào Card Tổng quan Bệnh nhân<br>- Thêm nút `≡ Ẩn/Hiện Hàng chờ` trên header công cụ<br>- Cập nhật hàm `goiVaoKham()`, `selectPatientForExam()` để kích hoạt chế độ toàn màn hình (`enableExamFocusMode(true)`)<br>- Viết hàm `toggleQueuePanel()` và `enableExamFocusMode(enabled)` mượt mà |

---

## 2. Thứ tự thực hiện các bước

### Bước 1: Điều chỉnh cấu trúc HTML layout
- Gán ID `#colQueue` cho cột hàng chờ và `#colExam` cho cột form khám bệnh.
- Thêm nút:
  ```html
  <button id="btnBackToQueue" class="btn btn-outline-primary btn-sm rounded-pill fw-bold d-none" onclick="enableExamFocusMode(false)">
    <i class="fa-solid fa-arrow-left me-1"></i> Quay lại Hàng chờ (<span id="backQueueCount">0</span>)
  </button>
  ```
- Thêm nút Toggle cạnh nút Làm mới:
  ```html
  <button id="btnToggleQueue" class="btn btn-outline-secondary btn-sm rounded-3 px-3 fw-semibold" onclick="toggleQueuePanel()">
    <i class="fa-solid fa-table-columns me-1"></i> Ẩn/Hiện Hàng chờ
  </button>
  ```

### Bước 2: Viết logic chuyển đổi giao diện (JavaScript)
- Hàm `enableExamFocusMode(isFocus)`:
  + Nếu `isFocus = true`:
    * `#colQueue`: thêm class `d-none`.
    * `#colExam`: đổi từ `col-lg-8` sang `col-12`.
    * `#btnBackToQueue`: bỏ class `d-none`.
  + Nếu `isFocus = false`:
    * `#colQueue`: bỏ class `d-none`.
    * `#colExam`: đổi từ `col-12` sang `col-lg-8`.
    * `#btnBackToQueue`: thêm class `d-none`.
- Trong `selectPatientForExam(item)`: tự động gọi `enableExamFocusMode(true)`.
- Trong sự kiện lưu phiếu khám / hoàn tất khám thành công: gọi `enableExamFocusMode(false)` để trở về hàng chờ.

### Bước 3: Đồng bộ vào Docker & Kiểm thử tự động bằng Playwright
- Đồng bộ file vào container `clinova_fastapi_app`.
- Viết test mô phỏng Bác sĩ click gọi số, kiểm tra cột hàng chờ ẩn đi và form khám mở rộng `col-12`, sau đó bấm nút quay lại hàng chờ.
- Chụp ảnh màn hình minh chứng.

---

## 3. Rủi ro & Lưu ý
- Đảm bảo khi mở rộng `col-12`, các bảng thuốc, bảng dịch vụ cận lâm sàng và khung AI thích ứng tốt với độ rộng mới (responsive).
