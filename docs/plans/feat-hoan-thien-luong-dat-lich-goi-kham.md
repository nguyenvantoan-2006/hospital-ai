# KẾ HOẠCH TRIỂN KHAI: HOÀN THIỆN TOÀN DIỆN LUỒNG TIẾP NHẬN - GỌI KHÁM - KÊ ĐƠN - PHÁT THUỐC

**Branch:** `feat/dieu-phoi-goi-kham-va-phan-cong-bs`  
**Người phụ trách:** BẠN (Tech Lead)  
**Ngày lập kế hoạch:** 25/09/2026  
**Trạng thái:** ⏳ ĐANG CHỜ XÁC NHẬN CỦA BẠN TRƯỚC KHI CODE  

---

## 🎯 I. MỤC TIÊU VÀ YÊU CẦU NGHIỆP VỤ (FR)

Hoàn thiện trọn vẹn và khép kín 100% luồng vận hành khám chữa bệnh trong phòng khám:
1. **Lễ tân tiếp nhận (FR-04 & UC-04):**
   - Khi tiếp nhận / xác nhận bệnh nhân, hệ thống **cấp ngay STT hàng đợi**, **gán phòng khám của Bác sĩ** và **tính toán khung giờ dự kiến vào khám cụ thể** (ví dụ: *08:15 - 08:30*).
   - In Phiếu Tiếp Nhận Khám Bệnh A5 / Kiosk Ticket chuẩn đẹp cho bệnh nhân cầm đến phòng khám.
2. **Bác sĩ & Màn hình TV gọi số (FR-05 & UC-05):**
   - Bác sĩ đồng bộ danh sách hàng chờ theo ngày, đúng phòng và chuyên khoa.
   - Bác sĩ bấm "Gọi vào khám", trạng thái chuyển sang `dang_kham`.
   - Màn hình Kiosk phòng khám hiển thị STT to rõ và tự động phát **Loa giọng nói gọi tên** vào phòng khám.
3. **Liên kết luồng liên phòng khép kín:**
   - **Bác sĩ $\leftrightarrow$ Cận lâm sàng:** Chuyển phòng CLS (X-quang) có STT mới $\rightarrow$ Trả kết quả về phòng ban đầu với STT ưu tiên ⭐.
   - **Bác sĩ $\rightarrow$ Kế toán $\rightarrow$ Quầy Dược:** Kê đơn thuốc với gợi ý kho thuốc tự động $\rightarrow$ Lưu đơn thuốc và sinh hóa đơn viện phí $\rightarrow$ Kế toán thu tiền $\rightarrow$ Quầy Dược phát thuốc và trừ tồn kho.

---

## 📁 II. DANH SÁCH FILE SẼ THAY ĐỔI & LÝ DO

| STT | File | Thao tác | Lý do thay đổi |
|---|---|:---:|---|
| 1 | `routers/lich_khams.py` | [SỬA] | Tự động cấp STT ngay khi tạo lịch ở trạng thái `cho_kham`. Bổ sung tính giờ dự kiến khám `gio_du_kien`. Đảm bảo trả về đầy đủ phòng khám và bác sĩ. |
| 2 | `templates/lich_kham.html` | [SỬA] | Nâng cấp Phiếu Tiếp Nhận STT hiển thị STT to, Tên Bác sĩ, Số phòng, Khung giờ dự kiến khám cụ thể, lời dặn di chuyển. Tự động mở popup in phiếu khi tiếp nhận. |
| 3 | `templates/lap_phieu_kham.html` | [SỬA] | Tinh chỉnh bảng kê đơn thuốc kết nối trọn vẹn với backend mới (gửi `don_thuocs` chuẩn định dạng), hỗ trợ in đơn thuốc A5 và mở modal in phiếu điều phối. |
| 4 | `templates/man_hinh_phong_kham.html` | [SỬA] | Đảm bảo hiển thị đúng giờ dự kiến, tự động phát loa gọi số mượt mà, hỗ trợ lọc theo phòng và bác sĩ. |

---

## 📋 III. THỨ TỰ THỰC HIỆN CÁC BƯỚC

### Bước 1: Nâng cấp Backend (`routers/lich_khams.py`)
- Cập nhật hàm `create_lich_kham`: nếu `trang_thai == "cho_kham"` thì tự động tính STT trong ngày.
- Bổ sung trường `gio_du_kien` được tính toán dựa trên STT (mỗi ca khám cách nhau 15 phút từ giờ bắt đầu ca: 08:00 sáng hoặc 13:30 chiều).
- *Commit message:* `feat(api): tu dong cap stt va tinh gio du kien vao kham khi tiep nhan`

### Bước 2: Nâng cấp Giao diện Lễ tân (`templates/lich_kham.html`)
- Bổ sung hiển thị `Giờ dự kiến khám` trên bảng danh sách lịch khám.
- Thiết kế lại mẫu in **Phiếu Tiếp Nhận Khám Bệnh A5 / Thermal Ticket** gồm: STT to nổi bật, Bác sĩ phụ trách, Số phòng khám & Tầng, Giờ vào khám cụ thể.
- Khi Lễ tân bấm nút `"Tiếp nhận (Cấp STT)"`, hệ thống cập nhật xong sẽ tự động hiển thị popup xem và in phiếu ngay.
- *Commit message:* `feat(ui): nang cap phieu tiep nhan stt va gio du kien kham cu the`

### Bước 3: Hoàn thiện liên kết Kê đơn thuốc tại Màn hình Bác sĩ (`templates/lap_phieu_kham.html`)
- Kiểm tra kết nối gửi `don_thuocs` lên `POST /api/v1/phieu-khams/`.
- Kiểm tra tính toán tồn kho, tự động sinh Hóa đơn viện phí sang Thu Ngân và đơn thuốc sang Quầy Dược.
- *Commit message:* `feat(ui): hoan thien ke don thuoc lien ket thu ngan va quay duoc`

### Bước 4: Kiểm thử E2E Toàn trình (Self-Test)
- Viết / chạy kịch bản kiểm thử tự động từ: Tiếp nhận Lễ tân (cấp STT, phòng, giờ) $\rightarrow$ Bác sĩ gọi số $\rightarrow$ Kê đơn $\rightarrow$ Thu ngân thanh toán $\rightarrow$ Quầy Dược phát thuốc & trừ kho.
- Đảm bảo 100% các ca kiểm thử đạt (PASS).

---

## ⚠️ IV. RỦI RO & ĐIỂM CẦN LƯU Ý
- **Tránh conflict với code của Loan:** Các file `routers/hoa_dons.py`, `routers/phieu_khams.py`, `models.py` vừa merge từ Loan không chỉnh sửa cấu trúc cốt lõi, chỉ gọi API theo đúng schema Loan đã định nghĩa.
- **Không push lên remote:** Giữ toàn bộ commit tại local trên branch `feat/dieu-phoi-goi-kham-va-phan-cong-bs`.
