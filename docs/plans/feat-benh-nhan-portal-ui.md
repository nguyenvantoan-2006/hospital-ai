# Kế hoạch Thực hiện: Nâng cấp Toàn diện Giao diện Khách hàng (Bệnh nhân & Khách thăm)
**Branch:** `feat/benh-nhan-portal`  
**Actor:** Bệnh nhân, Khách hàng, Thân nhân  
**Yêu cầu chức năng liên quan:** FR-09 (Đặt lịch khám trực tuyến), FR-10 (Tra cứu thông tin và kết quả khám), FR-AI-01 (Chatbot AI tư vấn y tế)

---

## 1. Mục tiêu & Vấn đề giải quyết

### 1.1 Vấn đề hiện tại:
- **`index.html`**: Đang đóng vai trò như một dashboard nội bộ có gắn `initAuthGuard()`. Khi khách hàng / bệnh nhân truy cập trang chủ (`http://localhost:8000/`), hệ thống ngay lập tức chuyển hướng sang `login.html` bắt đăng nhập, khiến khách hàng không thể tiếp cận thông tin bệnh viện hay đặt lịch trực tuyến.
- **`benh_nhan.html`**: Đã có cấu trúc khung cổng bệnh nhân phong phú nhưng cần được tinh chỉnh thiết kế thẩm mỹ cao cấp (Modern Medical Glassmorphism), tối ưu trải nghiệm Stepper đặt lịch, kết nối dữ liệu động thực tế từ Backend (chuyên khoa, danh sách bác sĩ, giờ khám khả dụng) và hiển thị thẻ phiếu khám điện tử có QR code rõ nét.
- **AI Chatbot**: Cần hoàn thiện cơ chế widget nổi có thể nhúng đồng bộ, trả lời tư vấn dịch vụ, hướng dẫn đặt hẹn và giải đáp quy trình tức thì thông qua endpoint `/api/ai/chat`.

### 1.2 Mục tiêu sau khi hoàn thành:
1. **Trang chủ (`index.html`)** trở thành Cổng thông tin & Giới thiệu Bệnh viện Thông minh (Clinova AI Hospital) đẳng cấp quốc tế:
   - Hero banner trực quan với các chỉ số ấn tượng, hiệu ứng chuyển động mượt mà.
   - Thanh điều hướng (Navbar) thông minh: Khách vãng lai xem được thông tin, đặt khám, tra cứu; đồng thời có nút "Cổng Cán bộ Y tế" để nhân viên đăng nhập vào hệ thống quản lý.
   - Trưng bày các Chuyên khoa thế mạnh, Đội ngũ Bác sĩ chuyên gia đầu ngành (tải động từ CSDL).
   - Quy trình khám khép kín (Closed-loop) 4 bước minh bạch và tiện lợi.
   - Bảng giá dịch vụ khám công khai, rõ ràng.
2. **Cổng Bệnh nhân (`benh_nhan.html`)** chuyên nghiệp, trực quan:
   - **Quy trình Đặt lịch khám 4 bước (Stepper UX)**:
     - Bước 1: Chọn Chuyên khoa & Dịch vụ khám.
     - Bước 2: Chọn Bác sĩ chuyên khoa & Khung giờ khám linh hoạt.
     - Bước 3: Điền thông tin cá nhân (Họ tên, SĐT, CCCD, Mã BHYT, Triệu chứng).
     - Bước 4: Xác nhận đặt hẹn, sinh ngay Phiếu khám điện tử (Appointment Pass) có mã QR Code để quét Check-in nhanh tại Kiosk bệnh viện.
   - **Khu vực Tra cứu Hồ sơ khám bệnh**:
     - Tra cứu theo SĐT / CCCD / Mã lịch hẹn.
     - Hiển thị tình trạng lịch hẹn (Chờ xác nhận, Đã đặt lịch, Chờ khám, Đã khám xong).
     - Xem kết quả khám, đơn thuốc điện tử và hóa đơn viện phí nếu đã hoàn thành khám.
3. **AI Medical Chatbot Assistant**:
   - Widget nổi hiện đại, giao diện trò chuyện tinh tế, tích hợp sẵn các câu hỏi mẫu gợi ý (hướng dẫn đặt hẹn, giờ làm việc, bảo hiểm y tế, hướng dẫn chuẩn bị trước khi khám).

---

## 2. Danh sách file sẽ thay đổi

| STT | File | Hành động | Lý do |
|:---:|------|:---------:|-------|
| 1 | `templates/index.html` | Cập nhật lớn | Tái cấu trúc thành Trang chủ Bệnh viện hiện đại, thân thiện khách hàng, tích hợp tra cứu, đặt khám nhanh và nút vào Cổng cán bộ y tế |
| 2 | `templates/benh_nhan.html` | Nâng cấp | Hoàn thiện giao diện Cổng Bệnh nhân, quy trình stepper đặt khám, sinh QR check-in, tra cứu lịch sử khám |
| 3 | `static/css/chatbot.css` | Tinh chỉnh | Nâng cấp styling cho Chatbot Widget nổi, badge thông báo, hiệu ứng mở/đóng mượt mà |
| 4 | `static/js/chatbot.js` | Tinh chỉnh | Kết nối đồng bộ với API `/api/ai/chat`, tối ưu hiển thị markdown và gợi ý câu hỏi nhanh |
| 5 | `docs/plans/feat-benh-nhan-portal-ui.md` | Tạo mới | File kế hoạch theo quy định AGENTS.md |

---

## 3. Thứ tự thực hiện các bước

### Bước 1: Hoàn thiện Trang chủ Bệnh viện `templates/index.html`
- Thiết kế theo chuẩn giao diện hiện đại (Modern Medical Web Design):
  - Topbar & Navigation thông minh (Logo Clinova, Menu điều hướng, Hotline cấp cứu 24/7, Nút Đăng nhập Cán bộ y tế).
  - Hero Section với tiêu đề ấn tượng, nút kêu gọi hành động (CTA) "Đặt Lịch Khám Ngay" & "Tra Cứu Hồ Sơ".
  - Thẻ tính năng nổi bật: Đặt khám thông minh, AI Trợ lý chẩn đoán, BHYT & Thanh toán linh hoạt, Quy trình không chờ đợi.
  - Danh mục Chuyên khoa & Dịch vụ y tế (kèm icon và mô tả súc tích).
  - Đội ngũ Bác sĩ tiêu biểu (lấy từ dữ liệu hệ thống).
  - Khu vực Tra cứu nhanh lịch hẹn ngay trên trang chủ.
  - Footer chuyên nghiệp với đầy đủ thông tin pháp lý, địa chỉ, giấy phép y tế.

### Bước 2: Nâng cấp Cổng Bệnh nhân `templates/benh_nhan.html`
- Hoàn thiện luồng Đặt lịch khám trực tuyến (Online Booking Wizard):
  - Load danh sách Chuyên khoa thực tế từ `/api/v1/lich-khams/specialties` hoặc `/api/v1/admin/chuyen-khoa`.
  - Tải động danh sách Bác sĩ tương ứng với chuyên khoa đã chọn.
  - Hiển thị lưới chọn khung giờ khám theo ca (Sáng: 07:30 - 11:30 | Chiều: 13:30 - 17:00).
  - Thu thập thông tin bệnh nhân chuẩn xác (Họ tên, SĐT, Ngày sinh, Giới tính, CCCD, Mã BHYT, Tiền sử dị ứng/bệnh lý).
  - Gửi request tạo lịch hẹn vào backend (`/api/v1/lich-khams/`).
  - Hiển thị Thẻ Phiếu Khám Điện Tử (Appointment Card) với Mã vạch / QR Code để bệnh nhân có thể lưu lại hoặc quét tại quầy.
- Tối ưu màn hình Tra cứu Lịch hẹn & Hồ sơ khám:
  - Cho phép tra cứu bằng Số điện thoại hoặc Mã CCCD.
  - Hiển thị danh sách lịch khám sắp tới và các lần khám đã hoàn thành.

### Bước 3: Nâng cấp Widget Trợ lý Ảo AI Chatbot (`static/js/chatbot.js` & `chatbot.css`)
- Nút nổi (Floating Action Button) có hiệu ứng pulse lôi cuốn ở góc phải màn hình.
- Cửa sổ trò chuyện bo góc sang trọng, hỗ trợ các câu hỏi mẫu gợi ý (Quick Prompts).
- Xử lý tương tác thông minh với endpoint `/api/ai/chat`, hiển thị chỉ báo typing và hỗ trợ định dạng trả lời rõ ràng.

### Bước 4: Kiểm tra và Tự rà soát
- Kiểm tra tính tương thích trên mọi kích thước màn hình (Desktop, Tablet, Mobile).
- Kiểm tra không còn lỗi chuyển hướng sai từ `index.html` sang `login.html` đối với khách vãng lai.
- Kiểm tra chức năng đặt lịch tạo bản ghi hợp lệ trong CSDL.
- Kiểm tra không có lỗi console JavaScript.

---

## 4. Điểm cần lưu ý & Quản trị rủi ro
- **Phân tách rõ vai trò Khách hàng vs Nhân viên nội bộ**: Trang chủ `index.html` tuyệt đối không được ép gọi `initAuthGuard()` khiến khách hàng bị chặn truy cập. Cán bộ y tế sẽ có nút bấm riêng để vào `login.html`.
- **Dữ liệu thật (No Dummy Placeholders)**: Kết nối dữ liệu chuyên khoa và bác sĩ trực tiếp từ cơ sở dữ liệu để đồng bộ 100% với hệ thống lễ tân và bác sĩ.
- **Tuân thủ quy tắc commit**: Thực hiện commit tách biệt theo nhóm file (Frontend HTML -> Static assets -> Docs).
