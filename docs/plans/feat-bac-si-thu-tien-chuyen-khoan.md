# Kế hoạch: Phân quyền Bác sĩ thu tiền CHỈ qua chuyển khoản ngân hàng bệnh viện (FR-07)

## 1. Mục tiêu & Nghiệp vụ
- **Mục tiêu:** Cho phép Bác sĩ (`bac_si`) có quyền thực hiện thu tiền viện phí/thuốc trực tiếp từ bệnh nhân tại phòng khám để giảm thiểu thời gian chờ đợi cho bệnh nhân không phải di chuyển qua lại quầy thu ngân.
- **Ràng buộc an toàn tài chính (BẮT BUỘC):**
  - Bác sĩ **CHỈ ĐƯỢC THU QUA CHUYỂN KHOẢN** (`chuyen_khoan` hoặc `qr`) trực tiếp về tài khoản ngân hàng chính thức của bệnh viện (Clinova).
  - Bác sĩ **TUYỆT ĐỐI KHÔNG ĐƯỢC THU TIỀN MẶT** (`tien_mat`). Mọi giao dịch tiền mặt bắt buộc thực hiện tại Quầy Kế toán / Thu ngân.
  - Backend phải kiểm soát chặt chẽ: nếu Bác sĩ gửi yêu cầu thanh toán với hình thức `tien_mat`, hệ thống phải từ chối ngay với mã lỗi `403 Forbidden`.

---

## 2. Danh sách file thay đổi & Lý do

| File | Thay đổi chính | Lý do |
|------|----------------|-------|
| `routers/hoa_dons.py` | - Thêm `current_user` vào endpoint xác nhận hóa đơn `POST /api/v1/hoa-dons/`<br>- Bổ sung RBAC: Bác sĩ được phép thanh toán nếu `hinh_thuc_tt in ["chuyen_khoan", "qr"]`<br>- Chặn Bác sĩ thu tiền mặt `tien_mat` (HTTP 403 Forbidden)<br>- Ghi audit log chi tiết | Đảm bảo tính toàn vẹn dữ liệu, kiểm soát gian lận tiền mặt ở tầng Backend |
| `templates/thanh_toan.html` | - Kiểm tra role `bac_si` khi vào trang thanh toán<br>- Khóa/ẩn lựa chọn "Tiền mặt", cố định chọn "Chuyển khoản VietQR"<br>- Hiển thị banner cảnh báo quy định thu tiền cho bác sĩ<br>- Hiển thị mã VietQR bệnh viện với đúng số tiền và nội dung | Đảm bảo UI phản ánh đúng quyền hạn của bác sĩ khi vào trang thanh toán |
| `templates/lap_phieu_kham.html` | - Tích hợp nút và modal **"Thu Tiền Chuyển Khoản (VietQR)"** ngay tại bàn khám<br>- Tự động tính tổng viện phí (tiền khám + tiền thuốc)<br>- Hiển thị mã VietQR ngân hàng bệnh viện để bệnh nhân quét mã ngay tại phòng khám<br>- Nút "Xác nhận đã nhận chuyển khoản" gọi API thanh toán `chuyen_khoan` | Tiện lợi tối đa cho bác sĩ và bệnh nhân, không cần chuyển tab hay đi sang quầy khác |

---

## 3. Thứ tự thực hiện các bước

1. **Bước 1 — Backend:** Cập nhật `routers/hoa_dons.py`:
   - Thêm dependency xác thực người dùng `get_current_user`.
   - Kiểm tra: Nếu user có `role == "bac_si"` và yêu cầu `hinh_thuc_tt == "tien_mat"`:
     Trả về lỗi `HTTP 403`: `"Bác sĩ chỉ có quyền thu viện phí qua chuyển khoản ngân hàng bệnh viện, không được thu tiền mặt. Vui lòng hướng dẫn bệnh nhân nộp tiền mặt tại quầy thu ngân!"`.
   - Commit: `feat(api): phan quyen bac si chi thu tien chuyen khoan ve ngan hang benh vien`

2. **Bước 2 — Frontend Thanh toán:** Cập nhật `templates/thanh_toan.html`:
   - Khi `role === "bac_si"`: Disable option tiền mặt, tự động chọn `chuyen_khoan`.
   - Hiển thị badge / alert thông báo quy định.

3. **Bước 3 — Frontend Phòng khám:** Cập nhật `templates/lap_phieu_kham.html`:
   - Thêm nút **"Thu tiền chuyển khoản (VietQR)"** tại Tab 2.
   - Modal hiển thị mã VietQR của Bệnh viện Clinova (ngân hàng MB / Techcombank / Vietinbank) kèm số tiền, nội dung thanh toán `TT PK{id} {ho_ten}`.
   - Nút xác nhận thanh toán chuyển khoản gửi `hinh_thuc_tt: "chuyen_khoan"` lên API.
   - Commit: `feat(ui): tich hop thu tien chuyen khoan vietqr tai phong kham cho bac si`

4. **Bước 4 — Kiểm thử:**
   - Viết test tự động:
     * Bác sĩ gửi `tien_mat` -> Bị chặn 403 Forbidden.
     * Bác sĩ gửi `chuyen_khoan` -> Thành công 201 Created.
     * Thu ngân/kế toán gửi `tien_mat` -> Thành công 201 Created.
   - Chạy Playwright kiểm thử giao diện thực tế và chụp ảnh minh chứng.

5. **Bước 5 — Dừng lại & Báo cáo:**
   - Báo cáo kết quả kiểm tra cho người dùng.
   - Tuyệt đối KHÔNG push Git remote khi chưa có sự đồng ý.

---

## 4. Rủi ro & Lưu ý
- **Không làm gián đoạn luồng thu ngân truyền thống:** Quầy thu ngân và quầy dược vẫn phải nhận được thông tin phiếu khám và hóa đơn bình thường dù do bác sĩ hay thu ngân xác nhận.
- **Tính toán tiền thuốc:** Tổng tiền phải đồng bộ chính xác giữa phí khám và danh mục thuốc thực tế bác sĩ kê.
