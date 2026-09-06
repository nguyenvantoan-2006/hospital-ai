---
name: requirements-analysis
description: Phân tích yêu cầu phần mềm và chuyển đổi yêu cầu ngôn ngữ tự nhiên thành yêu cầu chức năng có cấu trúc, yêu cầu phi chức năng, user stories, acceptance criteria và thông tin truy vết — áp dụng cho Hệ thống Quản lý Phòng Khám có tích hợp AI.
---

# Requirements Analysis Skill — Hospital AI System

## Objective
Phân tích yêu cầu phần mềm một cách có hệ thống và tạo ra đặc tả có cấu trúc phù hợp với tài liệu SRS (NHÓM_03.docx) của Hệ thống Quản lý Phòng Khám.

## Inputs
Đọc các tài liệu sau khi có sẵn:
- `docs/customer-requirement.md` — yêu cầu khách hàng
- `NHÓM_03.docx` / SRS tài liệu tham chiếu
- Kết quả khảo sát hiện trạng phòng khám
- Ràng buộc pháp lý: Luật 15/2023/QH15, Nghị định 13/2023/NĐ-CP, Thông tư 46/2017/TT-BYT

## Process

### 1. Identify Stakeholders (Xác định các bên liên quan)
- Giảng viên hướng dẫn (TS. Nguyễn Đình Dũng)
- Nhóm phát triển (Nhóm 03 - KTPM K23C)
- Nhân viên phòng khám (Quản trị viên, Lễ tân, Bác sĩ, Kế toán)
- Bệnh nhân

### 2. Identify Actors (Xác định tác nhân)
Xác định đầy đủ 5 tác nhân:
- **Quản trị viên (Admin)** — quản lý toàn hệ thống, phân quyền RBAC
- **Lễ tân (Receptionist)** — tiếp nhận bệnh nhân, đặt lịch, hóa đơn
- **Bác sĩ (Doctor)** — khám bệnh, kê đơn, sử dụng AI
- **Kế toán (Accountant)** — thanh toán, báo cáo tài chính
- **Bệnh nhân (Patient)** — đặt lịch trực tuyến, AI Chatbot

### 3. Identify Functional Requirements (Yêu cầu chức năng)
Sử dụng mã chuẩn từ SRS:

| Mã | Tên chức năng |
|---|---|
| FR-01 | Đăng nhập và phân quyền (RBAC) |
| FR-02 | Quản lý bệnh nhân |
| FR-03 | Quản lý bác sĩ và chuyên khoa |
| FR-04 | Quản lý lịch khám |
| FR-05 | Khám bệnh và lập phiếu khám |
| FR-06 | Kê đơn thuốc điện tử |
| FR-07 | Quản lý thanh toán viện phí |
| FR-08 | Báo cáo và thống kê |
| FR-09 | Đặt lịch khám trực tuyến (OTP + reCAPTCHA) |
| FR-10 | Tra cứu thông tin cá nhân (Patient Portal) |
| FR-AI-01 | AI tóm tắt hồ sơ bệnh án |
| FR-AI-02 | AI Chatbot hỏi đáp quy trình |
| FR-AI-03 | AI sinh hướng dẫn sau khám và nhắc lịch tái khám |

### 4. Identify Non-Functional Requirements (Yêu cầu phi chức năng)

| Mã | Phân loại |
|---|---|
| NFR-PER-01 | Hiệu năng: đăng nhập ≤3s, tìm kiếm ≤2s, AI ≤5s |
| NFR-SEC-01 | Bảo mật: bcrypt, RBAC, Data Masking, Audit Logs, AI Logs |
| NFR-REL-01 | Độ tin cậy: Fallback khi AI lỗi, dữ liệu không mất |
| NFR-USM-01 | Khả năng sử dụng & bảo trì: responsive, tài liệu đầy đủ |
| NFR-SCA-01 | Khả năng mở rộng: thêm module không phá vỡ hệ thống hiện có |
| SEC-AI-01 | Data Masking trước khi gửi dữ liệu lên AI |
| SEC-AI-02 | AI không chẩn đoán, không kê đơn, không thay thế bác sĩ |
| SEC-AI-03 | Fallback mechanism khi AI không khả dụng |
| SEC-AI-04 | AI Logs ghi đầy đủ: thời gian, người dùng, chức năng, trạng thái |

### 5. Identify Business Rules (Quy tắc nghiệp vụ)
- Một bác sĩ không được có nhiều lịch khám tại cùng một thời điểm.
- Hồ sơ khám bệnh chỉ được tạo sau khi bệnh nhân hoàn tất tiếp nhận.
- Chỉ bác sĩ được lập phiếu khám và kê đơn thuốc.
- Chỉ kế toán được xác nhận thanh toán.
- AI chỉ hỗ trợ hành chính — **tuyệt đối không** chẩn đoán hay kê đơn.
- Mọi nội dung AI tạo ra phải được bác sĩ phê duyệt trước khi sử dụng.
- Một bệnh nhân chỉ có một hồ sơ duy nhất trong hệ thống.

### 6. Identify Assumptions (Giả thiết)
- Phòng khám có kết nối Internet ổn định.
- Thiết bị đầu cuối hỗ trợ trình duyệt Web hiện đại (Chrome, Edge, Firefox).
- API LLM (Gemini/OpenAI) hoạt động bình thường trong điều kiện sử dụng thông thường.
- Dữ liệu ban đầu (bác sĩ, chuyên khoa, dịch vụ) được admin nhập trước khi vận hành.

### 7. Identify Ambiguities (Điểm mơ hồ cần làm rõ)
- Ghi rõ bất kỳ yêu cầu nào còn mơ hồ, mâu thuẫn hoặc không thể kiểm thử được.
- **Không** tự suy diễn yêu cầu không có trong SRS.

### 8. Create User Stories
Định dạng chuẩn:
```
As a <actor>,
I want <capability>,
so that <benefit>.
```

### 9. Create Acceptance Criteria
Mỗi user story quan trọng phải có acceptance criteria có thể kiểm thử được (Given/When/Then).

### 10. Traceability
Mỗi user story phải truy vết được đến ≥1 yêu cầu FR hoặc NFR.

## Rules
- **Không** viết source code.
- **Không** thiết kế database hay kiến trúc.
- **Không** tự tạo yêu cầu không có trong tài liệu nguồn.
- Phân biệt rõ requirements với assumptions.
- Ghi rõ thông tin còn thiếu.
- Tuân thủ IEEE Std 830-1998 và ISO/IEC/IEEE 29148:2018.

## Outputs
Tạo hoặc cập nhật:
- `docs/requirements.md`
- `docs/user-stories.md`
- `docs/acceptance-criteria.md`
- `docs/requirements-issues.md`

## Verification
Trước khi hoàn thành, kiểm tra:
- [ ] Tất cả FR có mã định danh (FR-01 đến FR-AI-03)
- [ ] Tất cả NFR có mã định danh (NFR-PER-01, NFR-SEC-01, ...)
- [ ] User stories truy vết đến requirements
- [ ] Acceptance criteria có thể kiểm thử được
- [ ] Ambiguities được ghi rõ
- [ ] Không có AI hallucination (đảm bảo không tự thêm thắt yêu cầu ngoài tài liệu gốc)
