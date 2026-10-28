# 🔑 TÀI KHOẢN VÀ MẬT KHẨU CÁC VAI TRÒ (HOSPITAL-AI)

> Chi tiết đầy đủ xem tại file: [docs/tai-khoan-actors.md](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/docs/tai-khoan-actors.md)  
> Trang đăng nhập: `http://127.0.0.1:8000/login.html` (hoặc cổng `8001`)

---

### 📌 BẢNG ĐĂNG NHẬP NHANH

| Vai trò (Actor) | Tên đăng nhập (`username`) | Mật khẩu (`password`) | Link Dashboard |
| :--- | :--- | :--- | :--- |
| 🛡️ **Quản trị viên (Admin)** | `admin` | `Admin@2024!` | [/admin_dashboard.html](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/templates/admin_dashboard.html) |
| 👩‍💼 **Lễ tân (Receptionist)** | `letan` | `LeTan@2024!` | [/lich_kham.html](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/templates/lich_kham.html) |
| 👨‍⚕️ **Bác sĩ (Doctor)** | `bacsi` *(hoặc `bs_BS001`)* | `BacSi@2024!` | [/bac_si_dashboard.html](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/templates/bac_si_dashboard.html) |
| 💰 **Kế toán (Accountant)** | `ketoan` | `KeToan@2024!` | [/hoa_don.html](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/templates/hoa_don.html) |
| 🧑‍🦽 **Bệnh nhân (Patient)** | *(Không cần tài khoản)* | *(Xác thực OTP)* | [/dat_lich_online.html](file:///e:/BAI_TAP/HOC-KY-7/project_AI/hospital-ai/templates/dat_lich_online.html) |

---

### 👨‍⚕️ Bác sĩ theo các chuyên khoa khác:
- Tất cả các bác sĩ trong hệ thống (từ `bs_BS001` đến `bs_BS393`) đều có mật khẩu chung là: **`BacSi@2024!`**
- Ví dụ:
  * Tim mạch: `bs_BS002` / `BacSi@2024!`
  * Hô hấp: `bs_BS003` / `BacSi@2024!`
  * Nhi khoa: `bs_BS005` / `BacSi@2024!`
