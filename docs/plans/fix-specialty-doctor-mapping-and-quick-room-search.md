# KẾ HOẠCH: Khắc phục Lỗi Chuyên Khoa - Bác Sĩ & Thêm Ô Tìm Kiếm Nhanh Số Phòng

## 1. Mục tiêu & FR liên quan
- **FR-04 / UC-04 (Đặt lịch khám & Tiếp đón bệnh nhân):**
  - Khắc phục lỗi chọn một số chuyên khoa (ví dụ "Mắt", "Da liễu", "Hô hấp"...) nhưng danh sách Bác Sĩ bị trống không hiển thị.
  - Khắc phục lỗi nghiệp vụ nghiêm trọng: Bệnh nhân đăng ký/tiếp đón khám Mắt nhưng hệ thống tự động gán nhầm sang Bác Sĩ chuyên khoa Tiêu Hóa - Gan Mật (do cơ chế so khớp `ilike` của MySQL với collation `utf8mb4_general_ci` coi `Mắt` == `Mật` == `Mặt`).
  - **Chuẩn hóa phân quyền Lễ tân (RBAC):** Lễ tân chỉ được xác nhận đặt lịch (`da_dat_lich`), tiếp nhận cấp STT (`cho_kham`) và bấm "Vào khám" (`dang_kham`) để bác sĩ nhận được thông tin bệnh nhân có mặt. Tuyệt đối KHÔNG hiển thị nút "Lập phiếu khám" trên màn hình Lễ tân (nghiệp vụ lập phiếu khám, chẩn đoán, kê đơn thuộc thẩm quyền của Bác sĩ).
- **FR-03 (Bác sĩ Dashboard & Hàng chờ khám):**
  - Thêm ô tìm kiếm nhanh số phòng trực quan ngay tại thanh công cụ (chỉ cần gõ số phòng "101", "202", "107"... là lọc và hiển thị ngay danh sách chờ của phòng đó, không cần cuộn tìm thủ công).

---

## 2. Nguyên nhân kỹ thuật cụ thể đã xác minh
1. **Lỗi không hiện Bác sĩ khi chọn chuyên khoa:**
   - Trong bảng `chuyen_khoa` tồn tại các bản ghi cũ từ đợt seed đầu (ID 1-37 cũ như ID 8 "Mắt", ID 7 "Da liễu", ID 12 "Hô hấp"...) song song với 37 chuyên khoa chuẩn (ID 38-63 như ID 41 "Mắt (Nhãn Khoa)", ID 42 "Da Liễu - Thẩm Mỹ Da"...).
   - API `/api/v1/admin/specialties` trả về toàn bộ 63 chuyên khoa.
   - Khi người dùng chọn "Mắt" (ID 8), frontend gọi `/api/v1/lich-khams/public/doctors?chuyen_khoa=Mắt`. Backend dùng `BacSi.chuyen_khoa == 'Mắt'`, trong khi 5 bác sĩ mắt đều có tên khoa là `Mắt (Nhãn Khoa)` $\implies$ Trả về 0 bác sĩ.
2. **Lỗi khám Mắt bị phân sang Bác sĩ Gan Mật:**
   - Tại API tiếp đón tại quầy (`tiep_don_tai_quay`), khi tự động tìm bác sĩ cho chuyên khoa ID 8 ("Mắt"), backend chạy:
     `db.query(models.BacSi).filter(models.BacSi.chuyen_khoa.ilike("%Mắt%")).first()`
   - Do collation MySQL mặc định không phân biệt dấu mũ/dấu á tiếng Việt trong `LIKE`, chuỗi `'%Mắt%'` khớp cả `'Tiêu Hóa - Gan Mật'` (bác sĩ đầu tiên là Lê Đức Long ID 227) và `'Răng Hàm Mặt'` trước khi đến `'Mắt (Nhãn Khoa)'`.
   - Kết quả: Bệnh nhân khám mắt bị gán nhầm sang bác sĩ Gan Mật!
3. **Thiếu ô tìm kiếm nhanh phòng khám:**
   - Bộ lọc phòng trên `lap_phieu_kham.html` hiện tại chỉ là thẻ `<select>` thông thường với danh sách dài hơn 40 phòng, gây khó khăn cho bác sĩ khi muốn chuyển nhanh về phòng mình trực.

---

## 3. Danh sách File sẽ thay đổi & Lý do

| STT | File | Mục đích thay đổi |
| :---: | :--- | :--- |
| **1** | `routers/lich_khams.py` | 1. Sửa `get_public_doctors`: so khớp chuyên khoa thông minh và phân biệt chính xác dấu tiếng Việt bằng Python.<br>2. Sửa `tiep_don_tai_quay` & `verify_otp_and_book`: gán đúng bác sĩ chuyên khoa, ngăn chặn tuyệt đối lỗi nhầm `Mắt` sang `Gan Mật`. |
| **2** | `routers/admin.py` | Cập nhật API `GET /api/v1/admin/specialties` chỉ trả về danh mục chuyên khoa chuẩn hoạt động có bác sĩ, hoặc lọc `trang_thai == True`. |
| **3** | `templates/dat_lich_online.html` | Đảm bảo nạp đúng danh sách 37 chuyên khoa chuẩn, tự động chọn bác sĩ mượt mà khi chọn "Mắt (Nhãn Khoa)" hoặc "Mắt". |
| **4** | `templates/lich_kham.html` | Cập nhật hàm `onSpecialtyChange()` để lọc bác sĩ linh hoạt, chuẩn hóa mapping chuyên khoa và phòng khám. |
| **5** | `templates/lap_phieu_kham.html` | Thêm ô Input Tìm kiếm nhanh số phòng trực tiếp trên thanh công cụ (gõ số phòng 101, 107, 202... lọc hàng chờ tức thì) kèm Datalist gợi ý và nút Clear. |
| **6** | `scripts/fix_specialties_and_appointments.py` | Script one-off: Đồng bộ `trang_thai` của các chuyên khoa dư thừa, di chuyển lịch khám cũ về đúng chuyên khoa chuẩn (ID 8 $\to$ ID 41), và sửa lại lịch khám #59 sang đúng bác sĩ Mắt. |

---

## 4. Thứ tự thực hiện các bước
1. **Bước 1:** Viết và chạy script di chuyển dữ liệu & sửa lịch khám #59 về bác sĩ Mắt, tắt các bản ghi chuyên khoa dư thừa.
2. **Bước 2:** Cập nhật backend `routers/lich_khams.py` và `routers/admin.py` với logic so khớp tiếng Việt chính xác.
3. **Bước 3:** Cập nhật giao diện `lap_phieu_kham.html` bổ sung ô tìm kiếm nhanh số phòng.
4. **Bước 4:** Cập nhật frontend `dat_lich_online.html` và `lich_kham.html`.
5. **Bước 5:** Chạy kiểm thử tự động toàn bộ hệ thống (`pytest`) và kiểm tra trên giao diện thực tế.

---

## 5. Rủi ro & Điểm cần chú ý
- Đảm bảo các lịch khám và phiếu khám đã tạo trước đây không bị mất liên kết foreign key khi cập nhật trạng thái chuyên khoa.
- Đảm bảo tìm kiếm phòng theo chuỗi con (ví dụ gõ "101" thì khớp "Phòng 101 (Khu A)", gõ "Mắt" thì khớp phòng Mắt).
