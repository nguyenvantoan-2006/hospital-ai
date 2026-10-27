# KẾ HOẠCH CHI TIẾT CHỈNH SỬA SLIDE BÁO CÁO ĐỒ ÁN (Tem_5C.pptx)
## Hệ thống Quản lý Phòng khám Thông minh Clinova — Nhóm 03 (KTPM K23C)
**Giảng viên hướng dẫn:** TS. Nguyễn Đình Dũng  
**Sinh viên thực hiện:** Nguyễn Văn Toàn (DTC245180042) - Trần Thị Loan (DTC245180058)

---

## 1. MỤC TIÊU VÀ ĐỊNH HƯỚNG TỔNG THỂ
1. **Triển khai chiến lược "Bottom-Line First":** Đưa kết quả đột phá, minh chứng vận hành và tính an toàn lên ngay đầu bài thuyết trình để chiếm trọn sự chú ý và thiện cảm của hội đồng.
2. **Khắc phục lỗi định vị "AI làm hết":** Viết lại mô hình AI-Augmented SDLC để khẳng định kỹ sư là người làm chủ (Human-in-the-Loop), AI chỉ là Co-pilot gia tốc tuân thủ bộ Skill.
3. **Loại bỏ trùng lặp và slide rác:** Rút gọn 3 slide mục lục (Slide 6, 7, 8) thành 1 slide; thay thế slide 17 (bị lặp lại slide 5) bằng slide Kiến trúc hệ thống & CSDL 11 bảng 3NF.
4. **Bổ sung các khoảng trống:** Điền nội dung cho Slide 16 (SRS), cập nhật số liệu kiểm thử tự động thực tế từ hệ thống test E2E.

---

## 2. BẢNG ĐỐI CHIẾU THAY ĐỔI CHI TIẾT TỪNG SLIDE (19 SLIDE CŨ -> 16 SLIDE TINH GỌN)

| STT Mới | Slide Gốc | Tên Slide Mới | Nội dung chi tiết cần sửa / bổ sung |
| :---: | :---: | :--- | :--- |
| **01** | Slide 1 | **Trang bìa báo cáo** | • Giữ nguyên thông tin trường, khoa, đề tài, GVHD và 2 sinh viên.<br>• Thêm dòng định vị: *"Ứng dụng phương pháp AI-Augmented SDLC & An toàn Y tế có kiểm soát"*. |
| **02** | Slide 2 | **Kết quả đạt được & Đóng góp (Executive Summary)** | • Thay vì chỉ có 4 ô chữ chung chung, bổ sung các **Metrics định lượng**:<br>  + Chu trình lâm sàng: 6 bước liên thông số hóa 100%.<br>  + 3 Phân hệ GenAI: Đa phương thức (Multimodal Flash), Tóm tắt bệnh sử 10s, Dặn dò sau khám.<br>  + Kiểm thử an toàn: 100% Data Masking PII, Fallback < 50ms, 100% test E2E Passed. |
| **03** | Slide 3 | **Minh chứng Chu trình Lâm sàng khép kín (UI Flow)** | • Giữ 6 bước cốt lõi: *Đặt lịch -> Check-in -> Khám lâm sàng -> Kê đơn kiểm kho -> Dặn dò sau khám -> Thu viện phí VietQR*.<br>• **Sửa:** Bổ sung khung ảnh chụp giao diện UI thực tế của hệ thống tương ứng với từng bước thay vì chỉ để chữ. |
| **04** | Slide 4 | **3 Phân hệ Trí tuệ Nhân tạo đột phá** | • Giữ 3 phân hệ: *AI Chatbot Cổng thông tin, AI Summary Bệnh sử, AI Post-Exam Guide*.<br>• **Sửa:** Thêm ảnh chụp màn hình trực quan từng phân hệ: Chatbot đọc ảnh đơn thuốc cũ/xét nghiệm; Khung AI Summary 3 phần trong trang bác sĩ; Bản hướng dẫn dặn dò xuất ra. |
| **05** | Slide 5 | **Kiểm thử chuyên sâu Chất lượng & An toàn Y tế** | • Giữ 4 trụ cột an toàn: *Adversarial Testing, PII Data Masking, Fallback Resilience, Bảng AI_Logs*.<br>• **Sửa:** Làm nổi bật con số thực nghiệm: 100 mẫu hồ sơ bệnh án ẩn danh hoàn toàn; 0% AI chẩn đoán bừa; Cơ chế phục hồi 50ms khi ngắt mạng internet. |
| **06** | Slide 6<br>(Gộp 6, 7, 8) | **Nội dung trình bày (Agenda tinh gọn)** | • **Bỏ Slide 7 & Slide 8** (mất thời gian, gây loãng).<br>• Gộp thành 1 slide Agenda duy nhất với 4 phần mạch lạc:<br>  *Phần I: Bối cảnh, Mục tiêu & Phạm vi*<br>  *Phần II: Phương pháp AI-Augmented SDLC (Human-in-the-Loop)*<br>  *Phần III: Thiết kế Kiến trúc & An toàn Y tế*<br>  *Phần IV: Đánh giá, Hạn chế & Hướng phát triển* |
| **07** | Slide 9 + 10 | **Thực trạng y tế & Cơ hội đột phá từ GenAI** | • Gộp bối cảnh quá tải hành chính và tiềm năng đột phá của GenAI vào 1 slide so sánh đối ứng trực quan: *Vấn đề y tế thực tế vs Giải pháp phần mềm Clinova*. |
| **08** | Slide 11 + 12 | **Mục tiêu nghiên cứu & Phạm vi hệ thống** | • Tóm lược 4 mục tiêu tổng quát.<br>• Phạm vi 5 vai trò (Bệnh nhân, Lễ tân, Bác sĩ, Dược sĩ, Thu ngân/Admin).<br>• **Minh bạch giới hạn:** Chưa tích hợp ảnh DICOM, dùng VietQR tĩnh Napas247, AI chỉ là trợ lý tham vấn. |
| **09** | Slide 13 + 14 + 15 | **Phương pháp AI-Augmented SDLC: Kỹ sư làm chủ** | • **SỬA LỖI NGUY HIỂM Ở SLIDE 14:** Xóa bỏ cách ghi "Bước 2-5 AI làm".<br>• Viết lại theo mô hình: **Kỹ sư là người ra đề bài, thiết lập tiêu chuẩn Skill, định hình Schema & Guardrails, rà soát từng Pull Request. AI đóng vai trò Co-pilot gia tốc thực thi**.<br>• Minh chứng quy trình Git Feature Branch Workflow & kiểm soát chất lượng. |
| **10** | Slide 16 | **Phân tích yêu cầu hệ thống (SRS & Use Cases)** | • **SỬA LỖI SLIDE TRỐNG:** Thay 4 gạch đầu dòng tiêu đề bằng nội dung thực tế:<br>  + Danh mục 10 ca sử dụng lâm sàng (UC-01 đến UC-10).<br>  + Ma trận phân quyền RBAC đa vai trò.<br>  + Yêu cầu phi chức năng: Latency < 200ms, JWT auth, bcrypt password, audit logging. |
| **11** | Mới<br>(Thay Slide 17 bị trùng) | **Kiến trúc phân tầng & Cơ sở dữ liệu 11 bảng 3NF** | • **Nội dung mới thay thế:**<br>  + Sơ đồ Layered Architecture (FastAPI async, Pydantic V2, SQLAlchemy 2.0).<br>  + Sơ đồ cơ sở dữ liệu quan hệ 11 bảng chuẩn hóa 3NF (liên kết khóa ngoại chặt chẽ, bảng `ai_logs` độc lập). |
| **12** | Slide 17 cũ | **Thiết kế System Prompt & Quy trình Data Masking** | • Mô tả luồng xử lý dữ liệu nhạy cảm PII qua Regex Filter.<br>• 5 Nguyên tắc vàng của Medical Guardrails (Không chẩn đoán bừa, không kê đơn, cảnh báo cấp cứu). |
| **13** | Mới | **Kết quả kiểm thử tự động toàn diện (Test Automation)** | • Đưa số liệu thực tế từ bộ test `run_full_system_test.py` và `test_dev2_features.py`:<br>  + 100% Test cases Pass.<br>  + Xử lý chặn xung đột lịch khám bác sĩ (Capacity conflict check).<br>  + Kiểm thử giao diện và tích hợp API. |
| **14** | Mới | **Bài học kinh nghiệm & Thách thức vượt qua** | • Thách thức xử lý ảo giác (Hallucination) của AI -> Giải pháp Few-shot & Context injection.<br>• Thách thức đồng bộ quy trình lâm sàng 2 dev -> Giải pháp Git Branching & Pair Programming. |
| **15** | Slide 18 | **Hướng phát triển trong tương lai** | • Giữ nguyên 4 hướng mở rộng: Mobile App Flutter, AI đọc ảnh DICOM, Chuẩn hóa HL7/FHIR, Tổng đài ảo Voicebot. |
| **16** | Slide 19 | **Kết luận & Lời cảm ơn** | • Lời cảm ơn sâu sắc tới TS. Nguyễn Đình Dũng và Hội đồng.<br>• Sẵn sàng chuyển sang phần Demo trực tiếp hệ thống. |

---

## 3. DANH SÁCH FILE SẼ THAY ĐỔI
1. `Tem_5C.pptx`: File PowerPoint gốc được chỉnh sửa cấu trúc nội dung, xóa slide dư thừa, cập nhật chữ và bố cục.
2. `docs/plans/ke-hoach-chinh-sua-slide-thuyet-trinh.md`: File kế hoạch chi tiết (file này).
3. `tools/update_slides.py` (Script bổ trợ nếu cần tự động sửa qua `python-pptx`): Tạo file slide mới `Clinova_Bao_Cao_Nhom03.pptx` để giữ an toàn tuyệt đối cho file gốc `Tem_5C.pptx`.

---

## 4. THỨ TỰ CÁC BƯỚC THỰC HIỆN
- **Bước 1:** Trình kế hoạch chỉnh sửa này cho người dùng duyệt.
- **Bước 2 (Sau khi duyệt):** Sử dụng thư viện `python-pptx` để đọc template gốc, điều chỉnh lại thứ tự slide, xóa 2 slide mục lục thừa, sửa nội dung các slide có lỗi định vị AI và bổ sung các slide kỹ thuật (Kiến trúc, CSDL, Test suite).
- **Bước 3:** Tạo ra file PowerPoint hoàn thiện mới (ví dụ: `Clinova_Slide_Bao_Cao_Chuan_10D.pptx`).
- **Bước 4:** Báo cáo chi tiết kết quả cho người dùng, cung cấp hướng dẫn chèn các ảnh chụp giao diện UI tương ứng.

---

## 5. RỦI RO VÀ LƯU Ý
- **Giữ nguyên file gốc:** Không ghi đè trực tiếp lên `Tem_5C.pptx`, tạo file output riêng để người dùng dễ dàng so sánh trước - sau.
- **Giữ đồng bộ font chữ & theme màu:** Kế thừa layout và màu sắc xanh y tế sẵn có của template `Tem_5C.pptx` để đảm bảo tính thẩm mỹ đồng nhất.

