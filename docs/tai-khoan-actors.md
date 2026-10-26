# 📋 DANH SÁCH TÀI KHOẢN VÀ MẬT KHẨU CÁC ACTOR (HOSPITAL-AI)

> **Dự án:** Hệ thống Quản lý Phòng khám Hospital-AI  
> **Phiên bản:** 1.0.0  
> **Cổng truy cập:** `http://127.0.0.1:8000` (hoặc `http://127.0.0.1:8001`)  
> **Trang đăng nhập tập trung:** `/login.html`

---

## 🔑 1. BẢNG TỔNG HỢP TÀI KHOẢN THEO VAI TRÒ (ACTOR)

| Vai trò (Actor) | Tên đăng nhập (`username`) | Mật khẩu (`password`) | Role hệ thống | Trang Dashboard / Giao diện chính |
| :--- | :--- | :--- | :--- | :--- |
| 🛡️ **Quản trị viên (Admin)** | `admin` | `Admin@2024!` | `admin` | [`admin_dashboard.html`](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/templates/admin_dashboard.html) |
| 👩‍💼 **Lễ tân (Receptionist)** | `letan` | `LeTan@2024!` | `le_tan` | [`lich_kham.html`](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/templates/lich_kham.html)<br>[`tiep_don_tai_quay.html`](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/templates/tiep_don_tai_quay.html) |
| 👨‍⚕️ **Bác sĩ (Doctor) Mặc định** | `bacsi`<br>hoặc `bs_BS001` | `BacSi@2024!` | `bac_si` | [`bac_si_dashboard.html`](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/templates/bac_si_dashboard.html)<br>[`lap_phieu_kham.html`](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/templates/lap_phieu_kham.html) |
| 💰 **Kế toán (Accountant)** | `ketoan` | `KeToan@2024!` | `ke_toan` | [`hoa_don.html`](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/templates/hoa_don.html)<br>[`bao_cao_tai_chinh.html`](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/templates/bao_cao_tai_chinh.html) |
| 🧑‍🦽 **Bệnh nhân (Patient)** | *(Không cần đăng nhập)* | *(Xác thực qua OTP)* | Khách vãng lai | [`dat_lich_online.html`](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/templates/dat_lich_online.html)<br>[`index.html`](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/templates/index.html) |

---

## 🏥 2. CHI TIẾT VAI TRÒ VÀ QUYỀN HẠN TỪNG ACTOR

### 1. Quản trị viên (Admin)
- **Tài khoản:** `admin` | **Mật khẩu:** `Admin@2024!`
- **Nhiệm vụ chính:**
  * Quản lý người dùng: thêm, sửa, xóa, khóa/kích hoạt tài khoản và cấp lại mật khẩu.
  * Quản lý chuyên khoa, phòng khám và phân công nhân sự.
  * Cấu hình tham số hệ thống, giới hạn tải của bác sĩ (Daily/Slot capacity limit).
  * Xem nhật ký hoạt động và báo cáo tổng thể phòng khám.

### 2. Nhân viên Lễ tân (Receptionist)
- **Tài khoản chính:** `letan` | **Mật khẩu:** `LeTan@2024!`  
  *(Tài khoản dự phòng: `HoangHanh` | Mật khẩu: `Admin@2024!`)*
- **Nhiệm vụ chính:**
  * Tiếp đón bệnh nhân tại quầy, tra cứu mã hồ sơ / số điện thoại.
  * Phân luồng, chọn bác sĩ và cấp số thứ tự (STT) vào hàng đợi.
  * In phiếu khám bệnh (ghi rõ ngày khám, giờ khám chính xác, phòng khám và STT).
  * Quản lý danh sách lịch hẹn đặt trực tuyến đến check-in.

### 3. Bác sĩ chuyên khoa (Doctor)
- **Tài khoản test nhanh:** `bacsi` hoặc `bs_BS001` | **Mật khẩu:** `BacSi@2024!`
- **Tất cả các bác sĩ trong hệ thống:**  
  * Cú pháp `username`: `bs_BS001` đến `bs_BS393` (hoặc `bacsi_001` đến `bacsi_185`).
  * Mật khẩu chung: **`BacSi@2024!`**
- **Nhiệm vụ chính:**
  * Xem danh sách bệnh nhân đang chờ theo đúng số thứ tự (STT) trong ngày.
  * Gọi khám theo lượt, xem lịch sử tiền sử bệnh án.
  * Tạo phiếu khám bệnh, chẩn đoán, kê đơn thuốc và chỉ định xét nghiệm.
  * Tích hợp trợ lý AI: Tóm tắt bệnh án, gợi ý hướng dẫn sau khám.

### 4. Nhân viên Kế toán / Thu ngân (Accountant)
- **Tài khoản:** `ketoan` | **Mật khẩu:** `KeToan@2024!`
- **Nhiệm vụ chính:**
  * Tiếp nhận phiếu khám và đơn thuốc đã hoàn thành từ Bác sĩ.
  * Tính tổng chi phí khám + thuốc + cận lâm sàng.
  * Xử lý thanh toán (Tiền mặt, Chuyển khoản QR VNPay/VietQR).
  * In hóa đơn viện phí và tổng hợp doanh thu tài chính theo ngày/tháng.

### 5. Bệnh nhân / Thân nhân (Patient)
- **Phương thức truy cập:** Trực tiếp trên cổng web công khai, không bắt buộc tài khoản thành viên.
- **Trang đặt khám:** `http://127.0.0.1:8000/dat_lich_online.html`
- **Cơ chế xác thực:**
  * Đặt lịch online: Nhập thông tin cá nhân -> Hệ thống gửi mã OTP (6 số) qua Email/SMS -> Xác thực thành công sẽ cấp mã đặt lịch và bảo lưu suất khám.
  * Tra cứu tiến trình khám: Nhập Số điện thoại + Mã lịch hẹn tại tab **"Tra Cứu Hồ Sơ & Lịch Khám"** trên trang `dat_lich_online.html`.

---

## 💡 3. DANH SÁCH MẪU MỘT SỐ BÁC SĨ THEO CHUYÊN KHOA ĐỂ TEST

Tất cả các tài khoản dưới đây đều sử dụng mật khẩu: **`BacSi@2024!`**

| Mã BS | Username | Họ và tên bác sĩ | Học vị | Chuyên khoa | Phòng khám |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `BS001` | `bs_BS001` / `bacsi` | Nguyễn Văn An | ThS.BS | Nội tổng quát | Phòng 101 (Khu A) |
| `BS002` | `bs_BS002` | Trần Thị Bích | BSCKI | Tim mạch | Phòng 102 (Khu B) |
| `BS003` | `bs_BS003` | Lê Hoàng Cường | TS.BS | Hô hấp - Phổi | Phòng 103 (Khu C) |
| `BS004` | `bs_BS004` | Phạm Minh Đức | PGS.TS | Tiêu hóa - Gan mật | Phòng 104 (Khu D) |
| `BS005` | `bs_BS005` | Hoàng Thu Hà | BSCKII | Nhi khoa | Phòng 105 (Khu A) |
| `BS006` | `bs_BS006` | Vũ Tuấn Kiệt | BSCKI | Tai Mũi Họng | Phòng 106 (Khu B) |
| `BS007` | `bs_BS007` | Đỗ Thanh Long | ThS.BS | Răng Hàm Mặt | Phòng 107 (Khu C) |
| `BS008` | `bs_BS008` | Bùi Mai Phương | BSCKI | Mắt (Nhãn khoa) | Phòng 108 (Khu D) |
| `BS009` | `bs_BS009` | Ngô Quang Thắng | TS.BS | Da liễu | Phòng 109 (Khu A) |
| `BS010` | `bs_BS010` | Đinh Hồng Vân | ThS.BS | Cơ Xương Khớp | Phòng 110 (Khu B) |

---

## ⚙️ 4. CƠ CHẾ BẢO MẬT & ĐỔI MẬT KHẨU
- Mật khẩu lưu trữ trong CSDL MySQL (`hospital_ai.users`) được mã hóa bảo mật chuẩn **Bcrypt Salted Hash**.
- Khi đăng nhập thành công qua `/api/v1/auth/login`, hệ thống trả về mã **JWT Access Token** (HS256) chứa thông tin `user_id`, `username`, `role` và hạn dùng.
- Quản trị viên (Admin) có thể đổi hoặc reset mật khẩu cho bất kỳ người dùng nào tại giao diện:
  `Quản trị viên -> Quản lý người dùng -> Cấp lại mật khẩu`.
