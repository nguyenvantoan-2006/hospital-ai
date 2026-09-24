# Kế hoạch Thực hiện: Phân Hệ Quầy Thuốc, Thanh Toán Tiền Thuốc & Quản Lý Cấp Phát Thuốc

- **Branch:** `feat/quay-thuoc-thanh-toan`
- **Người thực hiện:** Antigravity AI Agent & Nhóm 03
- **Yêu cầu liên quan:** FR-06 (Kê đơn thuốc), FR-07 (Thanh toán viện phí & tiền thuốc), Quản lý Quầy Dược
- **Trạng thái:** ⏳ Chờ người dùng duyệt kế hoạch

---

## 1. Phân tích yêu cầu & Mục tiêu nghiệp vụ

### 🏥 Bối cảnh thực tế tại phòng khám:
1. **Sau khi Bác sĩ khám và kê đơn:** Bác sĩ chẩn đoán bệnh và kê đơn thuốc cho bệnh nhân trên trang khám bệnh (`lap_phieu_kham.html`).
2. **Bệnh nhân di chuyển sang Quầy Thuốc / Thu ngân:**
   - Dược sĩ / Thu ngân tra cứu đơn thuốc của bệnh nhân theo Mã Phiếu Khám (#PK) hoặc Tên / Mã BHYT.
   - Giao diện hiển thị chi tiết: Bác sĩ điều trị, Chẩn đoán, Bảng kê chi tiết từng loại thuốc (Tên thuốc, Đơn vị tính, Số lượng kê, Đơn giá, Thành tiền, Liều dùng chi tiết).
3. **Thanh toán tiền thuốc:**
   - Thu ngân / Dược sĩ chọn hình thức thanh toán (Tiền mặt, Quét mã QR chuyển khoản, Khấu trừ BHYT).
   - Xác nhận thanh toán hóa đơn tiền thuốc.
4. **Sau khi bệnh nhân lấy thuốc (Cấp phát thuốc):**
   - Dược sĩ đóng gói đúng các loại thuốc theo đơn, hướng dẫn bệnh nhân cách dùng.
   - Bấm nút **"Xác nhận đã phát thuốc & Xuất kho"**.
   - Hệ thống tự động:
     * Cập nhật trạng thái sang `da_lay_thuoc` (Đã nhận thuốc).
     * Tự động khấu trừ số lượng tồn kho `so_luong_ton` trong kho dược phẩm (`thuocs`).
     * Ghi nhận ngày giờ phát thuốc và tên người phụ trách.
5. **In Đơn thuốc & Hướng dẫn sử dụng:**
   - Cung cấp tính năng in phiếu thu tiền thuốc & Hướng dẫn uống thuốc chuẩn phòng khám để gửi cho bệnh nhân.

---

## 2. Danh sách file sẽ thay đổi & Tạo mới

| File | Loại | Mục đích & Chi tiết |
|---|:---:|---|
| `models.py` | Sửa | Bổ sung cột `trang_thai_phat_thuoc`, `thoi_gian_phat_thuoc` vào bảng `hoa_dons` (hoặc `phieu_khams`) để theo dõi trạng thái phát thuốc |
| `schemas.py` | Sửa | Bổ sung schema Pydantic cho dữ liệu đơn thuốc, phát thuốc, cập nhật trạng thái lấy thuốc |
| `routers/hoa_dons.py` | Sửa | Bổ sung API chuyên sâu cho Quầy thuốc: `GET /api/v1/hoa-dons/don-thuoc-cho-phat`, `POST /api/v1/hoa-dons/xac-nhan-phat-thuoc` (tự động trừ kho `thuocs`) |
| `templates/quay_thuoc.html` | Tạo mới | Giao diện chuyên nghiệp Quầy Dược & Cấp Phát Thuốc: Danh sách đơn chờ, Chi tiết đơn, Nút thanh toán tiền thuốc, Nút xác nhận phát thuốc, Modal in đơn thuốc |
| `templates/thanh_toan.html` | Sửa | Nâng cấp hiển thị chi tiết từng loại thuốc (tên, số lượng, đơn giá, thành tiền) khi thu tiền tại quầy thu ngân |
| `templates/index.html` | Sửa | Bổ sung menu và thẻ Card Quầy Dược & Cấp Phát Thuốc vào trang chủ |
| `main.py` | Sửa | Khai báo route nếu cần (đã có dynamic template routing) |

---

## 3. Thứ tự thực hiện các bước

- **Bước 1:** Bổ sung trường dữ liệu trạng thái phát thuốc trong Database MySQL & `models.py`, `schemas.py`.
- **Bước 2:** Xây dựng các API backend cho Quầy thuốc (`routers/hoa_dons.py`):
  * Lấy danh sách đơn thuốc đã kê (kèm lọc theo trạng thái: Chờ thanh toán, Chờ lấy thuốc, Đã phát thuốc).
  * API thanh toán tiền thuốc riêng hoặc gộp viện phí.
  * API xác nhận đã phát thuốc (tự động kiểm tra và trừ tồn kho `so_luong_ton` trong bảng `thuocs`).
- **Bước 3:** Thiết kế giao diện `templates/quay_thuoc.html` hiện đại, chuẩn thẩm mỹ Clinova:
  * Thẻ KPI: Đơn thuốc hôm nay, Đơn chờ lấy thuốc, Đã phát thành công, Doanh thu thuốc.
  * Bảng danh sách đơn thuốc trực quan có bộ lọc tìm kiếm bệnh nhân nhanh.
  * Khung chi tiết đơn thuốc: Hiển thị rõ tên thuốc, số lượng, cách dùng, giá tiền.
  * Nút hành động: "Xác nhận thu tiền thuốc", "Xác nhận đã phát thuốc cho bệnh nhân", "In đơn thuốc & Hướng dẫn".
- **Bước 4:** Nâng cấp đồng bộ `templates/thanh_toan.html` và gắn liên kết chuyển hướng trên Navbar / Sidebar.
- **Bước 5:** Kiểm thử luồng khép kín:
  * Bác sĩ kê đơn tại `lap_phieu_kham.html` -> Xuất hiện ngay tại Quầy thuốc.
  * Quầy thuốc thu tiền & bấm phát thuốc -> Kho dược tự động trừ tồn kho.
  * Trạng thái cập nhật thành `Đã phát thuốc`.

---

## 4. Rủi ro & Điểm cần lưu ý

1. **Rủi ro âm tồn kho thuốc:** Khi bệnh nhân lấy số lượng thuốc vượt quá tồn kho thực tế -> API sẽ kiểm tra trước, nếu không đủ thuốc sẽ cảnh báo và thông báo dược sĩ.
2. **Không phá vỡ dữ liệu cũ:** Bệnh nhân khám không kê thuốc (như #PK-16 trong ảnh) vẫn thanh toán viện phí bình thường mà không bị lỗi.
