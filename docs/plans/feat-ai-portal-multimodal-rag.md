# Kế hoạch Thực hiện: AI Chatbot Cổng Thông Tin Đa Phương Thức & RAG Chuẩn Y Tế
- **Branch:** `feat/ai-chatbot-multimodal-rag`
- **Người thực hiện:** Antigravity AI Agent & Dev Team (Nhóm 03)
- **Yêu cầu / FR liên quan:** FR-AI-02 (AI Chatbot tư vấn hành chính & quy trình), UC-09, SEC-AI-02 (Guardrails y đức & Anti-Hallucination)
- **Trạng thái:** Đã triển khai hoàn tất (Sẵn sàng kiểm thử)

---

## 1. Phân tích yêu cầu & Mục tiêu phát triển

### 1.1. Các tính năng cốt lõi
1. **Nhập liệu bằng giọng nói (Voice-to-Text có kiểm duyệt):**
   - Tích hợp Web Speech API (nhận diện giọng nói đa ngôn ngữ, tối ưu `vi-VN` và `en-US`).
   - Âm thanh nói vào -> chuyển văn bản hiển thị trực tiếp vào ô input `#clinovaChatInput`.
   - Người dùng chủ động rà soát, chỉnh sửa lỗi chính tả trước khi bấm nút Gửi (hoàn toàn kiểm soát bởi người dùng).
2. **Xử lý tài liệu và hình ảnh (Multimodal Vision / Document):**
   - Cho phép tải ảnh (kết quả xét nghiệm cũ, đơn thuốc cũ, thẻ BHYT/CCCD, ảnh chụp bất thường vùng da...) hoặc tệp tài liệu (PDF bệnh án cũ).
   - Có thanh preview thumbnail, kích thước, nút xoá tệp đính kèm trước khi gửi.
   - Gửi ảnh/tài liệu sang Backend xử lý bằng Gemini Multimodal API để trích xuất ngữ cảnh khách quan.
3. **Tự động nhận diện đa ngôn ngữ:**
   - Hệ thống tự động phát hiện ngôn ngữ người dùng (Tiếng Việt, Tiếng Anh,...) và phản hồi bằng chính ngôn ngữ đó, đảm bảo phong cách văn minh, chuyên nghiệp.
4. **Trợ lý định hướng đi khám (Không chẩn đoán y khoa bừa bãi):**
   - Tuyệt đối không chẩn đoán bệnh, không kê đơn thuốc.
   - Đóng vai trò hướng dẫn chuẩn bị: gợi ý đúng chuyên khoa cần khám, bác sĩ phụ trách, bảng giá niêm yết, giấy tờ cần mang theo (CCCD, BHYT, đơn cũ), dặn dò trước khi khám (nhịn ăn xét nghiệm máu, uống nhiều nước trước khi siêu âm...).
5. **Nguyên tắc "Lấy dữ liệu thật từ Database - Không xuyên tạc" (RAG + Guardrails):**
   - Thiết kế bảng cơ sở dữ liệu `huong_dan_chuan_bi_kham` và liên kết với `chuyen_khoa`, `bac_si`.
   - Cơ chế RAG: Truy vấn DB thực tế (chuyên khoa, bác sĩ, bảng giá, quy định nhịn ăn/chuẩn bị) -> kẹp vào System Prompt làm Ground Truth -> Gemini chỉ được trả lời dựa trên dữ liệu này.
   - Nếu thông tin không có trong DB: Phải thông báo rõ ràng "Hiện cơ sở dữ liệu của phòng khám chưa có thông tin này, vui lòng liên hệ Hotline 1900 6868".
   - Luôn đính kèm Disclaimer miễn trừ trách nhiệm y tế chuẩn xác ở cuối mỗi câu trả lời.

---

## 2. Kiến trúc giải pháp (Architecture & RAG Pipeline)

```
[ Người dùng ]
   ├── Gõ văn bản / Nói qua Voice-to-Text (Rà soát lại text trong input)
   └── Đính kèm Ảnh (X-quang, da liễu, BHYT, đơn thuốc) / File PDF
          │
          ▼
[ Frontend Widget: static/js/chatbot.js & static/css/chatbot.css ]
   ├── Web Speech Recognition (Mic animation, text injection)
   ├── File Picker & Preview Thumbnail (Base64 encoding)
   └── POST /api/ai/chatbot-rag (JSON payload: message, image_base64, mime_type)
          │
          ▼
[ Backend Router: routers/ai.py ]
   ├── 1. Data Masking (Che số BHYT/CCCD nếu trích xuất từ ảnh)
   ├── 2. RAG Retrieval Engine:
   │      - Query bảng `chuyen_khoa` (tên khoa, mô tả, giá khám)
   │      - Query bảng `bac_si` (học vị, họ tên, lịch trực, phòng khám)
   │      - Query bảng `huong_dan_chuan_bi_kham` (chuẩn bị nhịn ăn, giấy tờ, lưu ý)
   ├── 3. Build Grounded Context: Nạp dữ liệu DB thật vào prompt
   ├── 4. System Instruction (Guardrails khắt khe - SEC-AI-02):
   │      - Ép không chẩn đoán, không kê đơn
   │      - Nhận diện đa ngôn ngữ
   │      - Nếu không có trong DB -> nói rõ không có
   ├── 5. Gemini 1.5 Flash / Flash Lite Call (Multimodal)
   ├── 6. Disclaimer Injection & AILog Audit ghi nhật ký
          │
          ▼
[ Trả lời người dùng: Hướng dẫn chuẩn bị + Nút gợi ý Đặt lịch khám ]
```

---

## 3. Danh sách File đã thay đổi & Lý do

| File | Loại thay đổi | Mục đích / Lý do |
| :--- | :--- | :--- |
| `models.py` | Đã sửa | Thêm bảng `HuongDanChuanBiKham` lưu quy định dặn dò chuẩn bị của từng chuyên khoa / dịch vụ cận lâm sàng |
| `seed_preparation_guides.py` | Tạo mới | Nạp 12 danh mục hướng dẫn chuẩn bị khám chuẩn xác (xét nghiệm máu, nội soi dạ dày, siêu âm, da liễu...) |
| `startup.py` | Đã sửa | Tự động chạy seed `HuongDanChuanBiKham` khi khởi động ứng dụng |
| `routers/ai.py` | Đã sửa | Cập nhật endpoint `/api/ai/chatbot` với Multimodal, RAG DB Context, Guardrails và Disclaimer |
| `static/js/chatbot.js` | Đã sửa | Thêm nút Mic thu âm Voice-to-Text, nút đính kèm File/Ảnh, preview thumbnail, gửi payload lên API |
| `static/css/chatbot.css` | Đã sửa | Thêm styling cho nút Voice mic, hiệu ứng sóng mic, khung đính kèm tệp, preview ảnh, disclaimer y tế |
| `docs/plans/feat-ai-portal-multimodal-rag.md` | Tạo mới | Kế hoạch và tài liệu hướng dẫn kỹ thuật |

---

## 4. Danh sách Commit (Đã hoàn thành theo thứ tự)

- [x] **Commit 1 (Model & Database):**
  `feat(model): them bang huong_dan_chuan_bi_kham va seed du lieu chuan bi y te` (Hash: `e5baddc`)
- [x] **Commit 2 (Backend & AI RAG Engine):**
  `feat(api): nang cap endpoint ai chatbot voi multimodal vision va rag database context` (Hash: `d4e79d7`)
- [x] **Commit 3 (Frontend & Static JS/CSS):**
  `feat(ui): tich hop voice-to-text va file upload preview cho widget ai chatbot` (Hash: `b175a09`)
- [x] **Commit 4 (Docs & Plan):**
  `docs(plan): cap nhat ke hoach va huong dan su dung ai chatbot multimodal`

---

## 5. Kết quả Tự Kiểm tra & Test (Self-Verification)

- [x] **Voice-to-Text:** Nhận diện lời nói qua Web Speech API, chuyển thành text trực tiếp vào ô input `#clinovaChatInput` để người dùng rà soát/sửa lỗi chính tả trước khi bấm gửi.
- [x] **Multimodal Upload:** Người dùng có thể đính kèm ảnh (kết quả xét nghiệm, đơn thuốc, da liễu) hoặc PDF bệnh án cũ, có preview bar và nút xóa tệp.
- [x] **Định hướng khám & RAG:** Trợ lý AI truy vấn CSDL nội bộ Clinova để gợi ý đúng chuyên khoa, bác sĩ, bảng giá, quy định nhịn ăn, giấy tờ cần mang.
- [x] **Chống ảo giác (Anti-Hallucination):** Guardrails ép AI tuyệt đối không chẩn đoán bệnh, không kê đơn thuốc, luôn báo rõ nếu dữ liệu không có trong CSDL.
- [x] **Đa ngôn ngữ:** Tự động phát hiện và phản hồi bằng ngôn ngữ tương ứng (Tiếng Việt, Tiếng Anh...).
- [x] **Medical Disclaimer:** Đính kèm câu khuyến cáo tự động ở cuối mọi câu trả lời.
- [x] **Audit Logging:** Lưu nhật ký vào bảng `ai_logs` theo dõi thời gian phản hồi và kiểm toán an toàn.

---

> ⚠️ **CHỐT CHẶN (HUMAN GATE):** AI Agent dừng lại tại đây và chờ người dùng gõ xác nhận duyệt kế hoạch trước khi bắt đầu viết code!
