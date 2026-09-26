# BẢN THẢO THIẾT KẾ & KẾ HOẠCH TRIỂN KHAI: ĐỒNG BỘ DỮ LIỆU LỄ TÂN - BÁC SĨ & VÒNG LẶP KHÁM LÂM SÀNG - CẬN LÂM SÀNG (CLOSED-LOOP CLINICAL ROUTING)

**Branch:** `feat/man-hinh-kham-va-chatbot`  
**Người phụ trách:** BẠN (Tech Lead)  
**Ngày cập nhật:** 21/09/2026  
**Trạng thái:** ⏳ ĐANG CHỜ XÁC NHẬN TRƯỚC KHI CODE  

---

## 🎯 I. MỤC TIÊU NGHIỆP VỤ

1. **Đồng bộ hóa dữ liệu toàn diện giữa Lễ tân và Bác sĩ:**
   - Dữ liệu do Lễ tân tiếp nhận (hoặc bệnh nhân đặt online được duyệt) phải được truyền tải đầy đủ tới Màn hình Bác sĩ (`lap_phieu_kham.html`).
   - Bác sĩ khi xem danh sách và chọn bệnh nhân sẽ thấy **Card Tổng Quan Lâm Sàng** chi tiết:
     + Họ tên, Tuổi, Năm sinh, Giới tính, SĐT, Mã BHYT, CCCD, Địa chỉ.
     + **Tiền sử bệnh lý & Dị ứng** (Cảnh báo an toàn điều trị).
     + **Lý do đến khám & Triệu chứng ban đầu** do Lễ tân ghi nhận.
     + **Phòng khám & Bác sĩ phụ trách**, Giờ tiếp nhận, Mã lịch khám.

2. **Closed-Loop Clinical Routing (Vòng lặp Cận lâm sàng khép kín):**
   - **Giai đoạn 1:** Bác sĩ phòng khám ban đầu (Phòng 101) chỉ định Cận lâm sàng $\rightarrow$ Ca tại Phòng 101 chuyển `cho_ket_qua_cls` (không xóa/hoàn thành) $\rightarrow$ Tự động tạo lượt khám mới tại Phòng CLS (Phòng 202 X-Quang) với **STT mới tại Phòng 202** $\rightarrow$ In Phiếu Điều Phối A5.
   - **Giai đoạn 2:** Phòng CLS gọi BN, chụp chiếu/xét nghiệm, nhập kết quả và bấm **"📤 Trả Kết Quả Về Bác Sĩ Phòng Khám Ban Đầu"** $\rightarrow$ Ca CLS hoàn tất.
   - **Giai đoạn 3:** Ca gốc tại Phòng 101 tự động chuyển trạng thái `da_co_ket_qua`, **cấp Số Thứ Tự (STT) MỚI tại Phòng 101** để xếp lại vào hàng chờ và đẩy lên **Ưu tiên số 1** $\rightarrow$ Kiosk và Màn hình Bác sĩ hiển thị badge ⭐ **[ƯU TIÊN: ĐÃ CÓ KẾT QUẢ CLS]** $\rightarrow$ Bác sĩ gọi vào, màn hình hiển thị ngay kết quả CLS gửi về để bác sĩ chẩn đoán xác định, kê đơn và bấm "Hoàn Tất Khám & In Đơn Thuốc (A5)".

---

## 📁 II. DANH SÁCH FILE THAY ĐỔI & LÝ DO

| File | Thao tác | Lý do |
|---|:---:|---|
| `routers/lich_khams.py` | [SỬA] | Đồng bộ trả về toàn diện thông tin bệnh nhân trong `GET /`. Bổ sung endpoint `POST /api/v1/lich-khams/tra-ket-qua-cls` (cấp STT mới lượt 2, lưu kết quả CLS). Cập nhật `dieu-phoi-chuyen-phong` giữ trạng thái `cho_ket_qua_cls`. |
| `templates/lap_phieu_kham.html` | [SỬA] | Thiết kế Card Tổng Quan Lâm Sàng hiển thị đầy đủ thông tin từ Lễ tân. Thêm badge ưu tiên `[⭐ ĐÃ CÓ KẾT QUẢ CLS]` và `[⏳ ĐANG CHỜ KẾT QUẢ CLS]` trong hàng chờ. Thêm Khung Kết Quả CLS gửi về và Tab Trả kết quả CLS. |
| `templates/man_hinh_phong_kham.html` | [SỬA] | Hiển thị ưu tiên hàng đầu và phát loa gọi số cho ca đã có kết quả CLS. |

---

## 📋 III. THỨ TỰ THỰC HIỆN CÁC BƯỚC

1. **Commit 1 (Backend):**
   - Nâng cấp `GET /api/v1/lich-khams/` trả về thông tin lâm sàng chi tiết + phòng khám.
   - Bổ sung `POST /api/v1/lich-khams/tra-ket-qua-cls` và hoàn thiện `dieu-phoi-chuyen-phong`.
   - *Message:* `feat(api): dong bo du lieu benh nhan va them endpoint tra ket qua cls closed-loop`

2. **Commit 2 (Frontend Doctor Dashboard):**
   - Thiết kế Card Tổng Quan Lâm Sàng bệnh nhân trên `templates/lap_phieu_kham.html`.
   - Bổ sung badge phân loại hàng chờ và khối xem kết quả CLS gửi về.
   - Bổ sung form và nút trả kết quả CLS cho các phòng cận lâm sàng.
   - *Message:* `feat(ui): tich hop card tong quan lam sang va giao dien closed-loop cls`

3. **Commit 3 (Frontend Kiosk Display):**
   - Cập nhật hiển thị ưu tiên và giọng đọc loa gọi số cho ca đã có kết quả CLS trên `templates/man_hinh_phong_kham.html`.
   - *Message:* `feat(ui): hien thi uu tien tren kiosk man hinh phong kham`

4. **Kiểm thử tự động & Self-Test:**
   - Kiểm tra syntax Python, test toàn bộ chu trình từ Tiếp nhận Lễ tân -> Bác sĩ phòng 101 -> Chuyển phòng 202 -> Trả kết quả -> Bác sĩ phòng 101 kết luận & kê đơn.
