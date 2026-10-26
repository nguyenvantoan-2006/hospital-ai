# Kế Hoạch Triển Khai: Hệ Thống Đặt Lịch Khám & Cấp Số Thứ Tự Chuẩn Hóa
## Đồng bộ Bác sĩ, Ngày, Giờ, Giới Hạn Tiếp Nhận & Chống Lệch Số Thứ Tự

- **Mã tính năng:** `feat/dat-lich-sync-stt-limits`
- **Mục tiêu:** Đáp ứng đầy đủ 18 yêu cầu nghiêm ngặt về đồng bộ lịch hẹn, giới hạn tải của bác sĩ (cấp ngày & cấp giờ), quyền tự chọn của bệnh nhân và đồng bộ tuyệt đối với phiếu khám lễ tân.
- **Ngày lập kế hoạch:** 02/10/2026

---

## 1. PHÂN TÍCH HIỆN TRẠNG & NGUYÊN NHÂN LỆCH DỮ LIỆU

1. **Lệch giờ khám giữa Lịch hẹn và Phiếu khám lễ tân:**
   - Hiện tại hàm `calculate_gio_du_kien` đang tự động tính giờ bằng công thức: `session_start + (stt - 1) * 15 phút`. Khi bệnh nhân đặt `09:00`, nếu có STT khác nhau thì giờ hiển thị bị nhảy thành `08:45` hoặc `10:15`.
   - **Khắc phục:** Giữ nguyên 100% giờ khám gốc do bệnh nhân đã chọn (`Appointment.Time = Queue.Time = Reception Ticket.Time = 09:00`). Tuyệt đối không tự động trượt giờ.
2. **Thiếu ràng buộc giới hạn tiếp nhận của Bác sĩ:**
   - Bảng `BacSi` chưa lưu hạn mức tiếp nhận trong ngày (`so_benh_nhan_toi_da_ngay`, mặc định: 200) và hạn mức từng khung giờ (`so_benh_nhan_toi_da_khung_gio`, mặc định: 20).
   - Chưa có tầng kiểm tra tổng số lượng đã đặt ở cả 2 cấp độ (Toàn ngày & Khung giờ) trước khi xác nhận lịch.
3. **Thiếu cơ chế điều hướng khi đầy lịch:**
   - Khi bác sĩ đầy lịch trong khung giờ hoặc cả ngày, hệ thống chưa cung cấp danh sách lựa chọn thay thế (Chọn giờ khác / Chọn ngày khác / Chọn bác sĩ khác cùng khoa).
4. **Đồng bộ Bác sĩ:**
   - Khi bệnh nhân đã chỉ định rõ Bác sĩ muốn khám, hệ thống phải bảo toàn chính xác ID bác sĩ đó từ lúc đặt online đến khi lễ tân tiếp nhận và in phiếu STT.

---

## 2. DANH SÁCH FILE SẼ THAY ĐỔI & LÝ DO

| File thay đổi | Loại | Lý do thay đổi |
| :--- | :--- | :--- |
| `models.py` | Model/DB | Bổ sung cột `so_benh_nhan_toi_da_ngay` (default 200) và `so_benh_nhan_toi_da_khung_gio` (default 20) vào model `BacSi`. Tận dụng cấu trúc hiện tại, không tạo bảng mới thừa thãi. |
| `schemas.py` | Schema | Cập nhật schemas cho Bác sĩ, cấu hình giới hạn, request/response đặt lịch, và schema trả về danh sách gợi ý khi đầy lịch. |
| `routers/lich_khams.py` | Backend Router | 1. Thêm API kiểm tra slot còn trống của Bác sĩ: `/public/check-doctor-availability`.<br>2. Thêm API gợi ý giờ khác, ngày khác, bác sĩ khác cùng khoa khi đầy lịch.<br>3. Thêm Transaction an toàn khi đặt lịch: kiểm tra giới hạn toàn ngày + giới hạn khung giờ trước khi lưu.<br>4. Chuẩn hóa đồng bộ tuyệt đối Bác sĩ, Ngày khám, Giờ khám giữa Online -> Tiếp đón tại quầy -> In phiếu tiếp nhận. Loại bỏ logic tự trượt giờ. |
| `templates/dat_lich_online.html` | Frontend Portal | 1. Hiển thị số lượng chỗ còn lại theo thời gian thực khi chọn Bác sĩ, Ngày, Giờ.<br>2. Hiển thị Modal/Giao diện lựa chọn thông minh khi Bác sĩ bị đầy (Giờ khác / Ngày khác / Bác sĩ khác cùng chuyên khoa).<br>3. Đảm bảo giữ nguyên lựa chọn của bệnh nhân. |
| `templates/lich_kham.html` | Frontend Lễ Tân | 1. Đồng bộ phiếu in tiếp nhận: `Ngày khám`, `Giờ khám`, `Bác sĩ`, `STT` khớp chính xác 100% với lịch hẹn.<br>2. Form tiếp nhận tại quầy cũng kiểm tra giới hạn của bác sĩ. |
| `test_appointment_capacity_sync.py` | Unit/Integration Test | Viết kịch bản kiểm thử tự động toàn bộ 8 test case bắt buộc trong tài liệu yêu cầu. |

---

## 3. THIẾT KẾ CHI TIẾT CÁC MODULE

### A. Database Model ([models.py](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/models.py))
Cập nhật class `BacSi`:
```python
so_benh_nhan_toi_da_ngay = Column(Integer, default=200, nullable=False)
so_benh_nhan_toi_da_khung_gio = Column(Integer, default=20, nullable=False)
```

### B. Logic Kiểm Tra Giới Hạn & Transaction ([routers/lich_khams.py](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/routers/lich_khams.py))
Quy trình đặt lịch trong Transaction:
```
BEGIN TRANSACTION
1. Kiểm tra bác sĩ tồn tại và đang hoạt động (trang_thai == True)
2. Xác định ngày khám (Date) và khung giờ khám (Time)
3. Đếm số ca khám hiện tại của bác sĩ trong ngày (ngoại trừ trạng thái 'huy'):
   COUNT(LichKham WHERE bac_si_id == doc.user_id AND date == target_date AND trang_thai != 'huy')
   --> Nếu >= doc.so_benh_nhan_toi_da_ngay (200):
       ROLLBACK & Báo lỗi FULL NGÀY + Trả về danh sách ngày khác còn chỗ và bác sĩ khác cùng khoa còn chỗ.
4. Đếm số ca khám hiện tại của bác sĩ trong khung giờ:
   COUNT(LichKham WHERE bac_si_id == doc.user_id AND thoi_gian == target_datetime AND trang_thai != 'huy')
   --> Nếu >= doc.so_benh_nhan_toi_da_khung_gio (20):
       ROLLBACK & Báo lỗi FULL GIỜ + Trả về danh sách khung giờ khác còn chỗ trong ngày.
5. Kiểm tra bệnh nhân không bị trùng lịch khám trong cùng khung giờ.
6. Tạo LichKham (Lưu chính xác benh_nhan_id, bac_si_id, chuyen_khoa_id, thoi_gian).
7. Commit Transaction.
```

### C. Các API Mới Hỗ Trợ Đặt Lịch & Điều Hướng
1. `GET /api/v1/lich-khams/public/doctor-availability`:
   - Query: `bac_si_id`, `ngay_kham`
   - Response:
     * `tong_ngay`: `{ toi_da: 200, da_dat: 150, con_lai: 50, is_full: false }`
     * `khung_gio`: Danh sách slot (08:00, 09:00, 10:00, 13:30, 14:30, 15:30, 17:00) kèm số lượng chỗ còn lại từng slot (`da_dat`, `toi_da`, `con_lai`, `is_full`).
2. `GET /api/v1/lich-khams/public/doctor-alternative-dates`:
   - Trả về 7 ngày tiếp theo của bác sĩ và tình trạng chỗ trống từng ngày.
3. `GET /api/v1/lich-khams/public/specialty-alternative-doctors`:
   - Trả về các bác sĩ khác cùng chuyên khoa còn chỗ trong ngày khám được chọn.

### D. Đồng Bộ Tuyệt Đối Với Phiếu Khám Lễ Tân
- Bảng hiển thị và Phiếu in của Lễ tân ([templates/lich_kham.html](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/templates/lich_kham.html)) luôn lấy:
  * `Ngày khám`: Format `DD/MM/YYYY` từ `LichKham.thoi_gian.date()`
  * `Giờ khám`: Format `HH:MM` từ `LichKham.thoi_gian.time()` (chính xác giờ bệnh nhân đã đặt)
  * `Bác sĩ`: Lấy đúng Bác sĩ trong `LichKham.bac_si_id`
  * `STT`: Số thứ tự được cấp trong ngày
- Phiếu in hiển thị chuẩn:
  ```text
  PHIẾU KHÁM
  Bệnh nhân: Nguyễn Văn B
  Bác sĩ: Nguyễn Văn A
  Ngày khám: 10/10/2026
  Giờ khám: 09:00
  Số thứ tự: A025
  ```

---

## 4. THỨ TỰ CÁC BƯỚC THỰC HIỆN

- [ ] **Bước 1:** Bổ sung trường `so_benh_nhan_toi_da_ngay` và `so_benh_nhan_toi_da_khung_gio` trong [models.py](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/models.py) và chạy migration bổ sung cột an toàn qua script SQLite/MySQL.
- [ ] **Bước 2:** Cập nhật schemas trong [schemas.py](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/schemas.py).
- [ ] **Bước 3:** Cập nhật [routers/lich_khams.py](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/routers/lich_khams.py):
  * Cài đặt API kiểm tra chỗ trống và API đề xuất thay thế.
  * Tích hợp kiểm tra giới hạn Ngày & Giờ kèm Transaction trong `verify_otp_and_book`, `create_lich_kham`, và `tiep_don_tai_quay`.
  * Chuẩn hóa giữ nguyên giờ khám, bỏ logic trượt giờ trong phiếu tiếp nhận.
- [ ] **Bước 4:** Nâng cấp [templates/dat_lich_online.html](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/templates/dat_lich_online.html):
  * Tự động tải số lượng chỗ trống khi người dùng chọn Bác sĩ, Ngày, Giờ.
  * Hiển thị giao diện 3 lựa chọn (Giờ khác / Ngày khác / Bác sĩ khác) khi bác sĩ đầy lịch.
- [ ] **Bước 5:** Cập nhật [templates/lich_kham.html](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/templates/lich_kham.html):
  * Đồng bộ thông tin phiếu khám và in phiếu khớp 100% (Bác sĩ, Ngày, Giờ, STT).
- [ ] **Bước 6:** Viết kịch bản kiểm thử tự động `test_appointment_capacity_sync.py` kiểm tra đủ 8 Test Case:
  1. Bác sĩ còn chỗ (150/200) -> Cho phép đặt.
  2. Bệnh nhân thứ 200 (199/200) -> Cho phép đặt -> Đạt 200/200.
  3. Bệnh nhân thứ 201 (200/200) -> Chặn, hiển thị giờ khác / ngày khác / bác sĩ khác.
  4. Đúng Bác sĩ (Doctor A -> Appointment.DoctorId = Doctor A).
  5. Đúng Ngày (10/10/2026 -> Appointment.Date = 10/10/2026).
  6. Đúng Giờ (09:00 -> Appointment.Time = 09:00, Phiếu lễ tân = 09:00).
  7. Chuyển ngày khi FULL -> Tạo đúng ngày mới với cùng bác sĩ.
  8. Chọn bác sĩ khác khi FULL -> Tạo đúng bác sĩ khác.

---

## 5. RỦI RO & ĐIỂM CẦN CHÚ Ý
- **Cơ sở dữ liệu đã có dữ liệu mẫu:** Cần chạy migration script thêm cột mà không làm mất hoặc hỏng dữ liệu hiện tại của các bảng.
- **Race Condition khi nhiều người đặt cùng lúc:** Transaction trong SQLAlchemy kết hợp kiểm tra count tại thời điểm commit để ngăn chặn overbooking quá 200 người/ngày hoặc 20 người/giờ.
- **Tính tương thích ngược:** Đảm bảo các API cũ và màn hình phòng khám (`man_hinh_phong_kham.html`), dashboard bác sĩ (`lap_phieu_kham.html`) vẫn hoạt động bình thường, không bị đứt gãy dữ liệu.
