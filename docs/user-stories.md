# User Stories — Hệ Thống Quản Lý Phòng Khám có Tích Hợp AI

**Nguồn:** Dựa trên docs/requirements.md và NHÓM_03.docx  
**Ngày:** 2026-08-30

---

## Authentication & Authorization

**US-01: Đăng nhập hệ thống**
```
As a Quản trị viên / Lễ tân / Bác sĩ / Kế toán,
I want to login with username and password,
so that I can access functions according to my role.
```
→ Truy vết: FR-01

**US-02: Phân quyền truy cập**
```
As a system administrator,
I want users to only access functions assigned to their role,
so that data security and access control are enforced.
```
→ Truy vết: FR-01, NFR-SEC-01

---

## Patient Management

**US-03: Tạo hồ sơ bệnh nhân mới**
```
As a Lễ tân,
I want to create a new patient record with their personal information,
so that the patient can be served in the system.
```
→ Truy vết: FR-02

**US-04: Tìm kiếm bệnh nhân**
```
As a Lễ tân / Bác sĩ,
I want to search patients by name, phone number, or patient ID,
so that I can quickly find the correct patient record.
```
→ Truy vết: FR-02

**US-05: Xem lịch sử khám bệnh**
```
As a Bác sĩ,
I want to view a patient's medical history,
so that I can understand their health background before examination.
```
→ Truy vết: FR-02, FR-05

---

## Schedule Management

**US-06: Đặt lịch khám**
```
As a Lễ tân,
I want to create a new appointment for a patient with a specific doctor and time slot,
so that the patient has a confirmed visit schedule.
```
→ Truy vết: FR-04

**US-07: Kiểm tra xung đột lịch**
```
As a Lễ tân,
I want the system to automatically detect scheduling conflicts,
so that no two patients are assigned to the same doctor at the same time.
```
→ Truy vết: FR-04, BR-01

**US-08: Đặt lịch trực tuyến (bệnh nhân)**
```
As a Bệnh nhân,
I want to book an appointment online by selecting specialty, doctor, date and time,
so that I don't need to come to the clinic or call in advance.
```
→ Truy vết: FR-09

**US-09: Xác minh OTP email**
```
As a Bệnh nhân,
I want to verify my email address via OTP before confirming my appointment,
so that the system can ensure the email I provided is valid.
```
→ Truy vết: FR-09, NFR-SEC-01

---

## Medical Examination

**US-10: Lập phiếu khám**
```
As a Bác sĩ,
I want to create an electronic examination record with symptoms, diagnosis and conclusion,
so that the patient's medical information is stored digitally and accurately.
```
→ Truy vết: FR-05, BR-03

**US-11: Kê đơn thuốc điện tử**
```
As a Bác sĩ,
I want to prescribe medicines from the catalog with dosage and usage instructions,
so that the patient receives accurate medication information.
```
→ Truy vết: FR-06, BR-03

---

## Payment

**US-12: Xác nhận thanh toán viện phí**
```
As a Kế toán,
I want to review the invoice and confirm payment after the patient completes their visit,
so that the financial record is accurate and the invoice status is updated.
```
→ Truy vết: FR-07, BR-04

---

## AI Features

**US-13: AI tóm tắt hồ sơ bệnh án**
```
As a Bác sĩ,
I want to view an AI-generated summary of the patient's medical history,
so that I can quickly understand their health background before the examination.
```
→ Truy vết: FR-AI-01, SEC-AI-01, SEC-AI-02

**US-14: AI Chatbot hỏi quy trình**
```
As a Bệnh nhân,
I want to ask the AI chatbot about the clinic's procedures, working hours, and fees,
so that I can get quick answers without waiting for staff.
```
→ Truy vết: FR-AI-02, SEC-AI-02

**US-15: AI sinh hướng dẫn sau khám**
```
As a Bác sĩ,
I want to use AI to generate post-exam care instructions based on my notes,
so that I can save time while providing clear guidance to patients.
```
→ Truy vết: FR-AI-03, SEC-AI-02

---

## Reports

**US-16: Xem báo cáo thống kê**
```
As a Quản trị viên / Kế toán,
I want to view reports on patient visits, revenue, and doctor efficiency,
so that I can make informed management decisions.
```
→ Truy vết: FR-08
