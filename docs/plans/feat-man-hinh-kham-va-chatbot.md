# BẢN THẢO THIẾT KẾ & KẾ HOẠCH TRIỂN KHAI: MÀN HÌNH KHÁM & CHATBOT BỆNH NHÂN

**Branch:** `feat/man-hinh-kham-va-chatbot`  
**Người phụ trách:** BẠN (Tech Lead)  
**Nguồn thiết kế gốc:** `NHÓM_03.docx` & `1_Thuc_hanh_AI_Augmented_SDLC.docx`  
**Ngày lập:** 21/09/2026  
**Trạng thái:** ⏳ ĐANG CHỜ LEAD PHÊ DUYỆT TRƯỚC KHI CODE  

---

## 🎯 I. MỤC TIÊU & CÁC YÊU CẦU NGHIỆP VỤ (FR / NFR LIÊN QUAN)

1. **Màn hình Kiosk gọi số từng phòng khám (Room Queue Display):**
   - Nâng cấp trải nghiệm phòng khám thông minh: Màn hình treo trước cửa phòng khám hiển thị số thứ tự đang khám, danh sách bệnh nhân chuẩn bị vào và tự động phát loa gọi số bằng Web Speech API tiếng Việt.
   - Bám sát quy trình tiếp nhận & cấp số thứ tự tại `BR-02` và `FR-04` (Lễ tân duyệt `cho_kham` -> Bác sĩ gọi `dang_kham`).
2. **AI Chatbot tư vấn hành chính y tế (FR-AI-02 & UC-09):**
   - Xây dựng Chatbot tư vấn 24/7 giải đáp thắc mắc của bệnh nhân về quy trình khám, chi phí khám, giờ làm việc, chuyên khoa.
   - Tuân thủ nghiêm ngặt Guardrails y đức (`SEC-AI-02`): **Tuyệt đối KHÔNG chẩn đoán bệnh, KHÔNG kê đơn thuốc**, chỉ trả lời hành chính.
3. **Cổng Tra cứu thông tin lịch hẹn cá nhân (FR-10 & UC-11):**
   - Bệnh nhân dùng Số điện thoại + Mã lịch hẹn để tra cứu trạng thái lịch khám trực tuyến.
4. **Rate Limiting bảo mật gửi OTP email (FR-09 & AC-09-01):**
   - Khống chế tối đa **3 lượt OTP / email / 1 giờ** để bảo vệ hệ thống khỏi spam bot.

---

## 🎨 II. BẢN THẢO THIẾT KẾ CHI TIẾT GIAO DIỆN (UI/UX MOCKUP)

### 1. Màn hình Kiosk phòng khám (`templates/man_hinh_phong_kham.html`)
* **Mục đích sử dụng:** Trình chiếu Full màn hình trên Smart TV hoặc iPad/Tablet gắn tại cửa mỗi phòng khám.
* **Yêu cầu hiển thị (Theo chỉ đạo của Lead):**
  - **Hiển thị đầy đủ Họ tên và Ngày tháng năm sinh** của bệnh nhân (Ví dụ: `NGUYỄN VĂN BÌNH - 15/08/1990` hoặc `(Năm sinh: 1990)`) để bệnh nhân đang ngồi chờ nhận diện chính xác lượt của mình, tránh bị nhầm lẫn giữa các bệnh nhân trùng tên.
* **Bố cục (Layout 1920x1080 Full HD, Dark/Medical Blue hiện đại):**
  ```
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │ 🏥 CLINIC CLINOVA AI   │  PHÒNG 101 - CHUYÊN KHOA TIM MẠCH   │  🕒 09:45:10 - 21/09/2026│
  │ Bác sĩ trực: PGS.TS.BS Trần Quang Vinh                       │  Phòng khám Đạt chuẩn  │
  ├────────────────────────────────────────┬───────────────────────────────────────────────┤
  │                                        │             DANH SÁCH CHUẨN BỊ                │
  │          🟢 ĐANG KHÁM                  │       (Vui lòng chuẩn bị sẵn sổ/BHYT)         │
  │                                        ├───────────────────────────────────────────────┤
  │     ┌────────────────────────────┐     │  STT 06  •  Trần Thị Hoa     (1985)   (09:50) │
  │     │                            │     │  STT 07  •  Lê Văn Kiên      (1992)   (10:00) │
  │     │          STT 05            │     │  STT 08  •  Phạm Minh Tuấn   (1978)   (10:10) │
  │     │                            │     │  STT 09  •  Đỗ Hoàng Anh     (2001)   (10:20) │
  │     └────────────────────────────┘     ├───────────────────────────────────────────────┤
  │   Bệnh nhân: NGUYỄN VĂN BÌNH           │               THỐNG KÊ CA KHÁM                │
  │   Ngày sinh: 15/08/1990                │  • Đã hoàn tất: 14 bệnh nhân                  │
  │   Mã lịch:   LK0012                    │  • Đang chờ khám: 04 bệnh nhân                │
  ├────────────────────────────────────────┴───────────────────────────────────────────────┤
  │ 📢 THÔNG BÁO: Bệnh nhân đến lượt vui lòng kiểm tra khẩu trang và bước vào phòng khám.  │
  └────────────────────────────────────────────────────────────────────────────────────────┘
  ```
* **Cơ chế âm thanh gọi số (Voice Audio Call):**
  - Sử dụng **Web Speech API (`speechSynthesis`)** tích hợp sẵn của trình duyệt.
  - Khi phát hiện số thứ tự mới chuyển sang `dang_kham`, tự động phát giọng đọc tiếng Việt chuẩn:  
    🔊 *"Xin mời bệnh nhân số 05, Nguyễn Văn Bình, sinh năm 1990, vào phòng khám 101"*.
  - Có nút bật/tắt âm thanh (Mute/Unmute toggle) để linh hoạt tại môi trường bệnh viện.

---

### 2. Floating AI Chatbot Widget (Vị trí: Ngoài Cổng Bệnh nhân — Patient Portal)
* **Vị trí hiển thị:** Đặt ngoài **Cổng Bệnh nhân** dành cho khách vãng lai và bệnh nhân đặt lịch:
  - Trang chủ phòng khám (`templates/index.html`)
  - Cổng đặt lịch khám trực tuyến (`templates/dat_lich_online.html`)
* **Nút bấm (Floating Action Button - FAB):**
  - Đặt cố định ở góc phải dưới màn hình (`bottom: 24px; right: 24px; z-index: 1050;`).
  - Biểu tượng AI Bot màu xanh y tế Gradient, có hiệu ứng đập nhẹ (pulse ring).
* **Cửa sổ Chat (Popup Card):**
  - Thiết kế Glassmorphism bo tròn hiện đại, kích thước chuẩn 380px x 520px.
  - Header: Logo Clinova AI, Avatar bác sĩ trợ lý, nút Thu nhỏ/Đóng.
  - Thân Chat:
    - Tin nhắn chào mừng tự động: *"Chào bạn! Tôi là Trợ lý AI của Clinova. Tôi có thể hỗ trợ bạn tìm hiểu giờ khám, bảng giá dịch vụ và thủ tục đăng ký khám bệnh!"*
    - **4 Câu hỏi gợi ý nhanh (Quick Prompts):**
      + 🕒 *Giờ làm việc của phòng khám?*
      + 💰 *Chi phí khám các chuyên khoa bao nhiêu?*
      + 📝 *Quy trình khám bệnh gồm những bước nào?*
      + 📅 *Làm sao để đặt lịch khám trước?*
    - Ô gõ tin nhắn + nút gửi + hiệu ứng gõ chữ (typing indicator).

---

### 3. Tab Tra cứu lịch hẹn (`templates/dat_lich_online.html`)
* Thêm nút chuyển đổi Tab ngay đầu trang: **[ 📅 Đặt Lịch Khám Mới ]** | **[ 🔍 Tra Cứu Lịch Hẹn ]**.
* Form nhập: **Số điện thoại** + **Mã lịch hẹn** (ví dụ: `LK0005`).
* Thẻ kết quả (Result Card):
  - Mã phiếu, Tên bệnh nhân, Chuyên khoa, Bác sĩ phụ trách, Phòng khám.
  - Trạng thái trực quan: Badge màu (Vàng: Chờ duyệt | Xanh dương: Đã tiếp nhận STT #05 | Xanh lá: Đang khám | Xám: Hoàn thành).
  - Lời dặn sau khám (nếu bác sĩ đã khám xong).

---

## 🔌 III. THIẾT KẾ BACKEND API & DATA CONTRACTS

### 1. API Hàng đợi phòng khám (Dành cho Màn hình Kiosk)
* **Endpoint:** `GET /api/v1/lich-khams/public/queue-display`
* **Query Params:**
  - `phong_kham` *(Optional - string, VD: "Phòng 101")*
  - `chuyen_khoa_id` *(Optional - int)*
* **Response (JSON):**
  ```json
  {
    "phong_kham": "Phòng 101",
    "chuyen_khoa": "Tim mạch",
    "bac_si": "PGS.TS.BS Trần Quang Vinh",
    "dang_kham": {
      "id": 12,
      "stt": 5,
      "ho_ten_masked": "Nguyễn Văn B***",
      "thoi_gian_bat_dau": "09:30"
    },
    "danh_sach_cho": [
      { "stt": 6, "ho_ten_masked": "Trần Thị H***", "thoi_gian_du_kien": "09:50" },
      { "stt": 7, "ho_ten_masked": "Lê Văn K***", "thoi_gian_du_kien": "10:00" },
      { "stt": 8, "ho_ten_masked": "Phạm Minh T***", "thoi_gian_du_kien": "10:10" }
    ],
    "thong_ke": {
      "da_kham": 14,
      "dang_cho": 4
    }
  }
  ```

### 2. API Tra cứu lịch hẹn
* **Endpoint:** `GET /api/v1/lich-khams/public/tra-cuu`
* **Query Params:** `sdt` *(string, bắt buộc)*, `ma_lich` *(Optional - string, VD: "LK0005" hoặc số ID 5)*
* **Response (JSON):** Trả về danh sách các lịch hẹn của số điện thoại đó kèm thông tin phòng khám, bác sĩ, STT và trạng thái.

### 3. API AI Chatbot
* **Endpoint:** `POST /api/ai/chatbot`
* **Payload:**
  ```json
  {
    "message": "Phòng khám mở cửa mấy giờ vậy?",
    "session_id": "optional-uuid"
  }
  ```
* **System Prompt Knowledge Base & Guardrails:**
  ```text
  Bạn là Trợ lý AI Hành chính của Hệ thống Phòng khám Clinova AI Hospital.
  Nhiệm vụ: Giải đáp thân thiện, ngắn gọn và chính xác các thông tin hành chính của phòng khám.

  THÔNG TIN CHÍNH THỨC CỦA PHÒNG KHÁM:
  - Thời gian làm việc: Thứ Hai đến Thứ Bảy (Sáng: 07:30 - 11:30, Chiều: 13:30 - 17:00). Chủ Nhật: Nghỉ.
  - Bảng giá khám: Khám chuyên khoa tiêu chuẩn: 100.000 VNĐ / lượt khám.
  - Quy trình khám: 1. Đặt lịch online hoặc tại quầy lễ tân -> 2. Tiếp nhận & nhận số thứ tự STT -> 3. Vào phòng khám với bác sĩ -> 4. Thanh toán viện phí & nhận thuốc tại quầy dược.
  - Địa chỉ: 123 Đường Sức Khỏe, Quận 1, TP.HCM. Hotline: 1900 6868.

  QUY TẮC Y ĐỨC & BẢO MẬT (SEC-AI-02 - TUYỆT ĐỐI TUÂN THỦ):
  1. TUYỆT ĐỐI KHÔNG đưa ra chẩn đoán bệnh. Nếu người dùng mô tả triệu chứng, hãy khuyên họ đặt lịch khám bác sĩ chuyên khoa hoặc gọi cấp cứu 115 nếu khẩn cấp.
  2. TUYỆT ĐỐI KHÔNG kê đơn hoặc khuyên dùng bất kỳ loại thuốc nào.
  3. Trả lời bằng tiếng Việt lịch sự, súc tích dưới 120 từ.
  ```

### 4. Rate Limiting OTP Email trong `email_service.py`
* Cấu trúc lưu trữ trong bộ nhớ: `OTP_ATTEMPTS = { "email@example.com": [timestamp1, timestamp2, ...] }`
* Logic: Nếu trong vòng 60 phút qua, email này đã yêu cầu gửi 3 lần -> Từ chối và báo lỗi HTTP 429: *"Bạn đã gửi quá 3 mã OTP trong vòng 1 giờ. Vui lòng thử lại sau!"*

---

## 📁 IV. DANH SÁCH CÁC FILE SẼ THAY ĐỔI & LÝ DO

> ⚠️ **Cam kết:** Không chỉnh sửa bất kỳ file nào của Dev 2 (`models.py`, `schemas.py`, `routers/phieu_khams.py`, `routers/hoa_dons.py`, `routers/ke_toan.py`).

| Thao tác | Tên File | Lý do thay đổi |
|:---:|---|---|
| **[MỚI]** | `templates/man_hinh_phong_kham.html` | Tạo giao diện Kiosk Full HD hiển thị số thứ tự phòng khám và loa gọi số. |
| **[SỬA]** | `routers/lich_khams.py` | Bổ sung 2 endpoint công khai: `queue-display` và `tra-cuu`. |
| **[SỬA]** | `routers/ai.py` | Bổ sung endpoint `POST /api/ai/chatbot` với Guardrails y tế. |
| **[SỬA]** | `email_service.py` | Bổ sung Rate Limiting khống chế tối đa 3 OTP/email/giờ. |
| **[SỬA]** | `templates/dat_lich_online.html` | Bổ sung Tab Tra cứu lịch hẹn + nhúng Widget Chatbot AI. |
| **[SỬA]** | `templates/index.html` | Nhúng Widget Chatbot AI + thêm nút mở nhanh Màn hình phòng khám. |
| **[SỬA]** | `main.py` | Cập nhật route nếu cần (hệ thống đã có `/{page_name}.html` tự động load template). |

---

## 📋 V. THỨ TỰ CÁC BƯỚC THỰC HIỆN & COMMIT CONVENTION

Theo đúng quy chuẩn phân tách commit trong `AGENTS.md`:

* **Bước 1 (Backend APIs):**  
  - Sửa `routers/lich_khams.py`: Thêm API hàng đợi Kiosk và API tra cứu lịch hẹn.
  - Sửa `email_service.py`: Thêm Rate Limiting.
  - *Commit 1:* `feat(api): them endpoints queue-display, tra cuu lich hen va rate limit otp`

* **Bước 2 (AI Chatbot Backend):**  
  - Sửa `routers/ai.py`: Thêm endpoint `POST /api/ai/chatbot` và prompt guardrails.
  - *Commit 2:* `feat(ai): them endpoint chatbot tu van quy trinh hanh chinh voi guardrails`

* **Bước 3 (Giao diện Màn hình Kiosk):**  
  - Tạo `templates/man_hinh_phong_kham.html` với âm thanh Web Speech API tiếng Việt.
  - *Commit 3:* `feat(ui): them giao dien man hinh kiosk phong kham va loa goi so tu dong`

* **Bước 4 (Giao diện Cổng bệnh nhân & Chatbot Widget):**  
  - Cập nhật `templates/dat_lich_online.html` và `templates/index.html` với Widget Chatbot và Tab Tra cứu.
  - *Commit 4:* `feat(ui): them widget ai chatbot va tab tra cuu lich hen benh nhan`

* **Bước 5 (Tự kiểm thử toàn diện & Báo cáo Lead):**  
  - Chạy test thực tế: Mở màn hình Kiosk, gọi API chatbot, test loa phát tiếng Việt, test tra cứu lịch hẹn, test chặn spam OTP.

---

## ⚠️ VI. RỦI RO & ĐIỂM CẦN LƯU Ý

1. **Trình duyệt chặn âm thanh tự động (Autoplay Policy):**  
   - Các trình duyệt hiện đại (Chrome/Edge) chặn phát âm thanh nếu người dùng chưa tương tác lần đầu với trang.
   - *Giải pháp:* Thiết kế nút bấm "Kích hoạt Loa gọi số" (Click to Enable Audio) nổi bật khi mở màn hình lần đầu để người vận hành bấm 1 lần, sau đó loa sẽ phát tự động suốt ca trực.
2. **Bảo mật thông tin bệnh nhân ở nơi công cộng (SEC-AI-01):**  
   - Tên bệnh nhân hiển thị trên màn hình ngoài sảnh bắt buộc phải che PII (ví dụ: `Nguyễn Văn B***`), không để lộ bệnh lý hoặc số điện thoại.
3. **Giới hạn Gemini API:**  
   - Endpoint Chatbot sẽ kế thừa cơ chế Multi-model Fallback sẵn có trong `routers/ai.py` để đảm bảo luôn có phản hồi nếu model chính quá tải.

---

### 👑 KÍNH TRÌNH LEAD PHÊ DUYỆT
Bản thảo thiết kế trên đã bao quát toàn bộ các tính năng phân công cho bạn. 
Xin mời bạn xem qua và cho ý kiến: **Bạn có đồng ý phê duyệt bản kế hoạch này để bắt đầu triển khai code không?**
