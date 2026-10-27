# Kế Hoạch Sửa Quyền Bác Sĩ: Chỉ Tiếp Nhận Bệnh Nhân Vào Khám, Không Cấp STT

## 1. Mục tiêu & Ràng buộc nghiệp vụ (FR-01, FR-04, FR-05)
- **Vấn đề thực tế:** Hiện tại trên trang `lich_kham.html`, tài khoản `bacsi` vẫn nhìn thấy và bấm được các nút `Tiếp nhận (Cấp STT)`, `Tiếp nhận tại quầy (Cấp STT)`, và `Cấp STT` tại cột STT Khám.
- **Ràng buộc nghiệp vụ (RBAC):**
  - **Lễ tân (Receptionist):** Là người tiếp đón bệnh nhân tại sảnh/quầy, thực hiện xác nhận bệnh nhân có mặt và **Cấp số thứ tự (STT)** (`da_dat_lich` -> `cho_kham`).
  - **Bác sĩ (Doctor):** Ngồi tại phòng khám chuyên khoa, chỉ có quyền **Tiếp nhận bệnh nhân vào phòng khám** (`cho_kham` -> `dang_kham`) và thực hiện khám bệnh/lập phiếu khám. **Bác sĩ tuyệt đối không có quyền cấp số STT tại quầy.**

## 2. Danh sách file sẽ thay đổi
1. `templates/lich_kham.html`:
   - Lấy vai trò người dùng từ `localStorage.getItem("role")`.
   - Phân biệt giao diện bảng lịch khám theo vai trò:
     * **Nếu là `bac_si`:**
       - Đổi tiêu đề cột từ "HÀNH ĐỘNG LỄ TÂN" thành "HÀNH ĐỘNG BÁC SĨ".
       - Ở trạng thái `da_dat_lich`: Ẩn toàn bộ nút "Cấp STT", "Tiếp nhận (Cấp STT)". Thay bằng badge `Chờ lễ tân cấp STT`.
       - Ở trạng thái `cho_kham` (đã có STT từ lễ tân): Bác sĩ có nút `Tiếp nhận vào khám` (chuyển sang `dang_kham`) và nút liên kết sang `lap_phieu_kham.html`.
       - Ẩn nút "+ Đặt Lịch Khám Mới (Tại Quầy)" trên top navbar đối với vai trò `bac_si`.
     * **Nếu là `le_tan` / `admin`:** Giữ nguyên toàn bộ nghiệp vụ tiếp đón và cấp STT tại quầy.
2. `routers/lich_khams.py`:
   - Endpoint `PUT /api/v1/lich-khams/{lich_kham_id}/trang-thai`:
     * Chặn quyền cấp STT (`new_status == "cho_kham"`): Nếu `current_user.role == "bac_si"` -> trả về HTTP 403 Forbidden: `"Bác sĩ không có quyền cấp số thứ tự (STT). Nghiệp vụ này thuộc về Lễ tân tại quầy!"`.
     * Bác sĩ được phép chuyển trạng thái `cho_kham` -> `dang_kham` ("Tiếp nhận vào phòng khám") và `dang_kham` -> `hoan_thanh`.
3. `templates/dat_lich_online.html`:
   - Đồng bộ hiển thị bác sĩ đã chọn và node xanh capacity (hủy race condition request cũ).

## 3. Thứ tự thực hiện các bước
1. Cập nhật backend `routers/lich_khams.py`: Bổ sung kiểm tra RBAC cho hành động chuyển trạng thái `cho_kham`.
2. Cập nhật frontend `templates/lich_kham.html`: Điều chỉnh hiển thị nút theo `role` (Lễ tân vs Bác sĩ).
3. Cập nhật `templates/dat_lich_online.html`: Đảm bảo chọn bác sĩ nào hiển thị đúng thông tin và sức chứa của bác sĩ đó.
4. Kiểm thử tự động & kiểm thử giao diện qua Browser Subagent cho cả 2 vai trò `bacsi` và `letan`.

## 4. Rủi ro & Lưu ý
- Không ảnh hưởng đến luồng tiếp đón tại quầy của Lễ tân (`letan`).
- Bác sĩ vẫn tiếp nhận được bệnh nhân đã có số thứ tự từ hàng chờ (`cho_kham` -> `dang_kham`).
