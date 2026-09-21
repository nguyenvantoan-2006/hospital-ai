# BẢNG PHÂN CÔNG NHIỆM VỤ & QUY TRÌNH PHỐI HỢP CODE 2 DEV
*(Zero-Conflict Protocol — Áp dụng cho Dự án Hospital-AI)*

**Dự án:** Hospital-AI Management System  
**Nhóm:** 03 — KTPM K23C | GVHD: TS. Nguyễn Đình Dũng  
**Ngày lập:** 21/09/2026  
**Trạng thái:** 🚀 ĐANG TRIỂN KHAI  

---

## 🛡️ I. NGUYÊN TẮC VÀNG TRÁNH CONFLICT (ZERO-CONFLICT PROTOCOL)

Để 2 người code song song **100% không bao giờ bị conflict**, bắt buộc tuân thủ các điều sau:
1. **Tuyệt đối tuân thủ bản thiết kế gốc (`NHÓM_03.docx` & `1_Thuc_hanh_AI_Augmented_SDLC.docx`):** Mọi chức năng, bảng CSDL, API, và logic nghiệp vụ phải bám sát 100% tài liệu thiết kế Word gốc đã được phê duyệt.
2. **Quyền hạn của Lead:** **BẤT KỲ THAY ĐỔI NÀO** (sửa đổi kiến trúc, thêm bớt cột CSDL, đổi luồng nghiệp vụ) **BẮT BUỘC PHẢI ĐƯỢC BẠN (LEAD) THÔNG QUA VÀ PHÊ DUYỆT** trước khi code. Dev 2 không được tự ý thay đổi thiết kế khi chưa có sự đồng ý của Lead.
3. **Ranh giới File bất khả xâm phạm:** Mỗi người chỉ được tạo/sửa các file thuộc phạm vi phân công. Tuyệt đối không tự ý sửa file của người kia.
4. **Không commit trực tiếp lên `main`:** Tất cả code phải thực hiện trên Feature Branch riêng. Nhánh `main` chỉ nhận code qua Squash Merge khi tính năng đã hoàn thiện và kiểm thử xong.
5. **Không commit Database:** File SQLite `clinic.db` chạy độc lập trên máy từng người, đã có trong `.gitignore`, tuyệt đối không commit lên repo.
6. **Rebase trước khi Merge:** Khi một người merge vào `main` trước, người còn lại cập nhật code bằng `git pull origin main` sau đó `git rebase main`.
7. **Đồng bộ qua giao diện API:** Khi Dev 1 cần dữ liệu từ Dev 2 (ví dụ: danh sách thuốc), Dev 2 cung cấp Endpoint API và Schema rõ ràng theo đúng thiết kế để Dev 1 gọi từ Frontend.

---

## 👑 II. PHÂN CÔNG NHIỆM VỤ: BẠN (TECH LEAD / PHỤ TRÁCH CHÍNH)

* **Vai trò:** Quản lý kiến trúc, phụ trách toàn bộ Giao diện người dùng (Frontend UI/UX), Trải nghiệm Cổng bệnh nhân, Hệ thống Màn hình hiển thị phòng khám và Tích hợp AI Chatbot.
* **Phạm vi file được phép sửa:**  
  `templates/*`, `routers/lich_khams.py`, `routers/ai.py` *(phần Chatbot)*, `email_service.py`, `static/*`, `main.py` *(chỉ mount trang)*.
* **Tên Branch làm việc:** `feat/man-hinh-kham-va-chatbot`

### Các Module công việc cụ thể:

| STT | Module chức năng | File thực hiện | Tiêu chí hoàn thành (Acceptance Criteria) |
|:---:|---|---|---|
| **1** | **Màn hình Kiosk gọi số từng phòng khám (Room Queue Display)** | • `templates/man_hinh_phong_kham.html`<br>• `routers/lich_khams.py` | • Màn hình Smart TV tối ưu độ phân giải Full HD.<br>• Hiển thị nổi bật: **STT ĐANG KHÁM** (kèm tên bệnh nhân đã che PII `Nguyễn Văn B***`), **DANH SÁCH CHUẨN BỊ VÀO** (3-5 ca tiếp theo), Bác sĩ trực.<br>• Tự động polling cập nhật realtime mỗi 3-4s.<br>• **Web Speech API:** Tự động phát loa tiếng Việt: *"Xin mời bệnh nhân số 05 vào phòng khám..."* khi đổi sang `dang_kham`.<br>• Endpoint API: `GET /api/v1/lich-khams/public/queue-display`. |
| **2** | **Cổng Bệnh nhân: AI Chatbot tư vấn quy trình (FR-AI-02)** | • `routers/ai.py`<br>• `templates/index.html`<br>• `templates/dat_lich_online.html` | • Endpoint `POST /api/ai/chatbot` với prompt knowledge base phòng khám (giờ làm việc, quy trình, giá khám 100k).<br>• AI Guardrails y tế: Từ chối chẩn đoán bệnh, từ chối kê đơn, chỉ hướng dẫn hành chính.<br>• Floating Chat Widget nổi ở góc dưới các trang để bệnh nhân chat trực tiếp 24/7. |
| **3** | **Cổng Bệnh nhân: Tra cứu lịch hẹn & Kết quả cá nhân (FR-10)** | • `routers/lich_khams.py`<br>• `templates/dat_lich_online.html` | • Endpoint `GET /api/v1/lich-khams/public/tra-cuu`.<br>• Form cho bệnh nhân nhập Số điện thoại + Mã lịch hẹn.<br>• Hiển thị: Trạng thái duyệt, STT, Bác sĩ, phòng khám, lời dặn sau khám. |
| **4** | **Nâng cấp Dashboard Bác sĩ & Mẫu in ấn (UI)** | • `templates/lap_phieu_kham.html`<br>• `templates/thanh_toan.html` | • Nút "Gọi khám tiếp theo" đồng bộ sang màn hình Kiosk.<br>• Autocomplete chọn thuốc từ danh mục (gọi API do Dev 2 cung cấp).<br>• Tính năng in ấn định dạng CSS `@media print` A4/A5 cho Đơn thuốc, Phiếu khám, Hóa đơn viện phí. |
| **5** | **Rate Limiting OTP Email (FR-09)** | • `email_service.py` | • Giới hạn tối đa 3 lần gửi OTP/email/giờ để chống spam. |

---

## 🛠️ III. PHÂN CÔNG NHIỆM VỤ: DEV 2 (ĐỒNG ĐỘI — BACKEND CORE & DƯỢC - KẾ TOÁN)

* **Vai trò:** Phụ trách CSDL, Model ORM, Transaction kế toán - kho dược, logic lưu đơn thuốc điện tử và bảo mật RBAC router.
* **Phạm vi file được phép sửa:**  
  `models.py`, `schemas.py`, `routers/phieu_khams.py`, `routers/hoa_dons.py`, `routers/ke_toan.py`.
* **Tên Branch làm việc:** `feat/backend-don-thuoc-va-ailog`

### Các Module công việc cụ thể:

| STT | Module chức năng | File thực hiện | Tiêu chí hoàn thành (Acceptance Criteria) |
|:---:|---|---|---|
| **1** | **Bảng CSDL `AILog` & Hướng dẫn sau khám (SEC-AI-04)** | • `models.py`<br>• `schemas.py` | • Tạo bảng `AILog` lưu vết: `thoi_gian`, `chuc_nang`, `prompt_masked`, `response_text`, `model_name`, `response_time_ms`, `trang_thai`.<br>• Thêm cột `huong_dan_sau_kham` vào model `PhieuKham`.<br>• Viết hàm tiện ích `log_ai_call()` để ghi log mọi lượt gọi Gemini. |
| **2** | **Backend Kê đơn thuốc điện tử (FR-05 & FR-06)** | • `routers/phieu_khams.py`<br>• `schemas.py` | • Mở rộng `POST /api/v1/phieu-khams/` nhận mảng `don_thuocs`.<br>• Lưu chi tiết đơn thuốc vào bảng `don_thuocs`.<br>• Ràng buộc: Kiểm tra và chặn kê thuốc vượt số lượng tồn kho `thuocs.so_luong_ton`.<br>• Cung cấp API `GET /api/v1/thuocs/search?q=...` để Dev 1 làm Autocomplete trên UI. |
| **3** | **Trừ tồn kho thuốc an toàn qua Transaction ACID (FR-07)** | • `routers/hoa_dons.py`<br>• `routers/ke_toan.py` | • Khi Kế toán bấm "Xác nhận thanh toán" (`da_thanh_toan`), tự động duyệt qua các `don_thuoc` của phiếu khám và trừ số lượng trong bảng `thuocs.so_luong_ton`.<br>• Bọc toàn bộ quá trình trừ kho trong 1 Database Transaction để đảm bảo tính toàn vẹn. |
| **4** | **Quản lý Danh mục Dược phẩm & Cảnh báo tồn kho** | • `routers/ke_toan.py`<br>• `templates/ke_toan.html` | • API CRUD danh mục thuốc (thêm mới, cập nhật giá nhập/giá bán, tồn kho).<br>• Cảnh báo các loại thuốc có `so_luong_ton < 10`. |
| **5** | **Siết chặt Bảo mật RBAC trên API Routers** | • `routers/phieu_khams.py`<br>• `routers/hoa_dons.py` | • Bổ sung middleware `Depends(require_roles(["bac_si", "admin"]))` cho phiếu khám.<br>• Bổ sung middleware `Depends(require_roles(["ke_toan", "admin"]))` cho hóa đơn. |

---

## 🔄 IV. LỘ TRÌNH TRIỂN KHAI VÀ GIAO NHAU

```
TUẦN LÀM VIỆC:
┌────────────────────────────────────────────────────────────────────────┐
│ GIAI ĐOẠN 1: CODE SONG SONG (Độc lập 100% không chạm file nhau)       │
│                                                                        │
│ • BẠN: Checkout 'feat/man-hinh-kham-va-chatbot'                       │
│   --> Code Màn hình Kiosk phòng khám + Web Speech API phát loa         │
│   --> Code Chatbot Widget AI & Tra cứu lịch hẹn                        │
│                                                                        │
│ • DEV 2: Checkout 'feat/backend-don-thuoc-va-ailog'                    │
│   --> Code Model AILog + cột huong_dan_sau_kham                        │
│   --> Code Backend nhận đơn thuốc & Trừ kho Transaction                │
│   --> Cung cấp API search thuốc                                        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ GIAI ĐOẠN 2: GHÉP NỐI & TÍCH HỢP HOÀN THIỆN                           │
│                                                                        │
│ 1. Dev 2 hoàn thành, Squash Merge vào main và push origin.             │
│ 2. Bạn: git checkout main && git pull origin main                     │
│ 3. Bạn: git checkout feat/man-hinh-kham-va-chatbot && git rebase main   │
│ 4. Bạn tích hợp: Form Bác sĩ gọi API search thuốc của Dev 2 + In ấn   │
│ 5. Bạn Squash Merge vào main -> Hệ thống hoàn tất 100%!               │
└────────────────────────────────────────────────────────────────────────┘
```

---

## ✅ V. KẾ HOẠCH BẮT ĐẦU CỦA BẠN (BƯỚC 1)

Với vai trò **Lead**, chúng ta sẽ bắt tay thực hiện ngay:
1. Tạo branch: `git checkout -b feat/man-hinh-kham-va-chatbot`
2. Tạo file plan chi tiết: `docs/plans/feat-man-hinh-kham-va-chatbot.md`
3. Tiến hành code Màn hình Kiosk gọi số phòng khám (`man_hinh_phong_kham.html`) và API hàng đợi `queue-display`.
