# Kế Hoạch Thực Hiện: Hoàn Thiện Phân Công Bác Sĩ & Liên Kết Mã Số Gọi Khám Giữa Lễ Tân - Bác Sĩ - Phòng Khám

> **Nhánh làm việc:** `feat/dieu-phoi-goi-kham-va-phan-cong-bs`  
> **Người thực hiện:** Antigravity AI Agent & Nhóm 03  
> **Tài liệu tham chiếu:** `AGENTS.md`, `SRS NHÓM_03.docx`, `FR-04` (Điều phối lịch khám), `FR-05` (Tiếp nhận & Hàng đợi)

---

## 1. Mục Tiêu & Vấn Đề Cần Giải Quyết

1. **Khắc phục lỗi dropdown Bác sĩ bị rỗng khi Tạo lịch khám:**
   - Chuẩn hóa hàm tìm kiếm/lọc chuyên khoa trong `templates/lich_kham.html` (chuyển sang fuzzy match / case-insensitive), đảm bảo chọn bất kỳ chuyên khoa nào cũng hiển thị danh sách bác sĩ trực thuộc khoa đó.
2. **Bổ sung tính năng Phân công / Đổi Bác sĩ cho Lễ tân:**
   - Thêm API Backend: `PUT /api/v1/lich-khams/{lich_kham_id}/phan-cong-bac-si` để cập nhật bác sĩ phụ trách cho lịch hẹn đã tồn tại (đặc biệt là các ca đang "Chưa phân công").
   - Thêm giao diện modal & nút **[Phân công BS]** trực tiếp ngay tại bảng Lịch khám của Lễ tân.
3. **Thiết lập chuỗi liên kết Mã số gọi khám (STT) $\longleftrightarrow$ Phòng khám $\longleftrightarrow$ Bác sĩ:**
   - **Lễ tân (`lich_kham.html`):** Hiển thị rõ ràng Cột Phòng Khám và Bác Sĩ phụ trách tương ứng với từng Mã số gọi khám (STT); hỗ trợ xem/in "Phiếu Tiếp Nhận Số Khám" mini với thông tin STT, Phòng khám, Bác sĩ để bệnh nhân biết di chuyển tới đúng phòng.
   - **Bác sĩ (`lap_phieu_kham.html`):** Bác sĩ mở giao diện phòng của mình sẽ thấy ngay bệnh nhân có STT được phân về phòng; bấm "Mời vào khám" sẽ phát loa và đồng bộ dữ liệu.
   - **Màn hình Kiosk TV phòng (`man_hinh_phong_kham.html`):** Hiển thị đúng STT đang khám và danh sách STT chuẩn bị vào của phòng đó.

---

## 2. Danh Sách File Sẽ Thay Đổi & Lý Do

| STT | File | Hành động | Lý do |
|:---:|:---|:---:|:---|
| 1 | `routers/lich_khams.py` | Chỉnh sửa | Thêm endpoint `PUT /{lich_kham_id}/phan-cong-bac-si` và tối ưu truy vấn phòng khám theo bác sĩ. |
| 2 | `templates/lich_kham.html` | Chỉnh sửa | 1) Sửa hàm lọc bác sĩ linh hoạt không lỗi so sánh.<br>2) Thêm nút/modal [Phân công BS] cho lịch chưa có bác sĩ.<br>3) Hiển thị thông tin Phòng khám và popup Phiếu tiếp nhận STT khám. |
| 3 | `templates/lap_phieu_kham.html` | Chỉnh sửa | Tự động nhận diện phòng khám/bác sĩ đăng nhập, đảm bảo hiển thị đúng hàng chờ STT mà Lễ tân đã điều phối. |
| 4 | `docs/plans/feat-dieu-phoi-goi-kham-va-phan-cong-bs.md` | Tạo mới | Tài liệu kế hoạch thực thi theo quy định AGENTS.md. |

---

## 3. Thứ Tự Các Bước Thực Hiện

### Bước 1: Backend - API Phân công Bác sĩ & Thông tin Phòng
- Tạo schema `LichKhamAssignDoctorInput(bac_si_id: int)`.
- Viết endpoint `PUT /api/v1/lich-khams/{lich_kham_id}/phan-cong-bac-si`:
  - Kiểm tra tồn tại của lịch khám và bác sĩ.
  - Gán `lich_kham.bac_si_id = data.bac_si_id`.
  - Tự động gán `lich_kham.chuyen_khoa_id` theo chuyên khoa của bác sĩ nếu chưa có.
  - Ghi AuditLog để lưu vết phân công.
- *Commit:* `feat(api): them endpoint phan cong bac si cho lich kham`

### Bước 2: Frontend Lễ Tân - Sửa Lọc Bác Sĩ & Thêm Phân Công Nhanh
- Viết hàm normalize tiếng Việt và so khớp linh hoạt cho dropdown chuyên khoa $\rightarrow$ bác sĩ trong form Đặt Lịch Mới.
- Thêm cột **Phòng khám** trong bảng Lịch khám Lễ tân.
- Bổ sung nút **[Phân công BS]** với icon điều phối cạnh chữ "Chưa phân công" để Lễ tân gán bác sĩ ngay tại chỗ.
- Bổ sung modal In/Xem "Phiếu Tiếp Nhận STT Khám" để cung cấp cho người bệnh khi Lễ tân bấm [Tiếp nhận (Cấp STT)].
- *Commit:* `feat(ui): sua loc bac si va them tinh nang phan cong phong kham`

### Bước 3: Đồng Bộ Bác Sĩ & Màn Hình Gọi Khám Kiosk
- Kiểm tra tính liên kết giữa STT cấp ở Lễ tân với hàng chờ ở màn hình Bác sĩ (`lap_phieu_kham.html`) và màn hình Smart TV gọi số (`man_hinh_phong_kham.html`).
- Đảm bảo khi Bác sĩ ở Phòng A bấm "Mời vào khám", số STT của bệnh nhân hiển thị đúng tại Phòng A trên TV và loa đọc đúng tên phòng.
- *Commit:* `feat(ui): dong bo ma so goi kham giua le tan bac si va kiosk tv`

---

## 4. Kế Hoạch Kiểm Thử (Test Cases)

1. **Test Lọc Bác Sĩ:** Vào Tạo Lịch Mới $\rightarrow$ Chọn chuyên khoa `Dị ứng - Miễn dịch` $\rightarrow$ Dropdown "Bác sĩ phụ trách" phải hiển thị đầy đủ danh sách bác sĩ chuyên khoa này (kèm phòng khám của họ).
2. **Test Phân Công Lịch Cũ:** Tại lịch `#LK-31` (Trần Văn Minh - Chưa phân công) $\rightarrow$ Bấm nút `[Phân công BS]` $\rightarrow$ Chọn BS $\rightarrow$ Lưu thành công, bảng cập nhật tên BS và Phòng khám ngay lập tức.
3. **Test Tiếp Nhận Cấp STT & Phòng Khám:** Bấm Tiếp nhận $\rightarrow$ Nhận STT `#04` $\rightarrow$ Hiển thị rõ số phòng (VD: Phòng 101).
4. **Test Màn Hình Bác Sĩ & Gọi Số:** Bác sĩ tại Phòng 101 mở màn hình khám $\rightarrow$ Thấy bệnh nhân STT `#04` trong hàng chờ $\rightarrow$ Bấm "Mời vào khám" $\rightarrow$ Loa phát đọc số và Kiosk TV hiển thị đúng STT `#04`.
