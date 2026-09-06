---
name: testing
description: Kiểm thử toàn diện Hệ thống Quản lý Phòng Khám có tích hợp AI — từ requirements xây dựng test scenarios, test cases, unit tests, integration tests đến báo cáo kết quả và defect.
---

# Testing Skill — Hospital AI System

## Objective
Kiểm thử hệ thống dựa trên acceptance criteria đã phê duyệt, đảm bảo coverage cho cả nghiệp vụ và AI.

## Inputs
Đọc:
- `docs/requirements.md`
- `docs/user-stories.md`
- `docs/acceptance-criteria.md`

## Process
```
Requirements
    → Test Scenario (kịch bản)
    → Test Case (trường hợp kiểm thử)
    → Automated Test (pytest)
    → Execution
    → Result
    → Defect Report
```

## Test Scope

### FR-01: Đăng nhập & RBAC
- TC-01-01: Đăng nhập thành công (username/password hợp lệ)
- TC-01-02: Đăng nhập sai mật khẩu → 401
- TC-01-03: Tài khoản bị khóa → từ chối
- TC-01-04: JWT hết hạn → 401
- TC-01-05: Role doctor không truy cập được admin endpoint → 403
- TC-01-06: Mật khẩu lưu dạng bcrypt hash (không plain text)

### FR-02: Quản lý bệnh nhân
- TC-02-01: Tạo bệnh nhân mới thành công
- TC-02-02: Tạo bệnh nhân trùng SĐT → cảnh báo/từ chối
- TC-02-03: Tìm kiếm bệnh nhân theo họ tên
- TC-02-04: Tìm kiếm theo SĐT
- TC-02-05: Cập nhật thông tin bệnh nhân
- TC-02-06: Xem lịch sử khám bệnh

### FR-04: Quản lý lịch khám
- TC-04-01: Đặt lịch thành công (bác sĩ, ngày, giờ hợp lệ)
- TC-04-02: Đặt trùng lịch bác sĩ → từ chối (conflict detection)
- TC-04-03: Hủy lịch khám
- TC-04-04: Thay đổi lịch khám

### FR-05: Khám bệnh & Phiếu khám
- TC-05-01: Bác sĩ tạo phiếu khám thành công
- TC-05-02: Lễ tân không tạo được phiếu khám → 403
- TC-05-03: Phiếu khám lưu đúng thông tin (triệu chứng, chẩn đoán)

### FR-06: Kê đơn thuốc
- TC-06-01: Kê đơn thuốc hợp lệ
- TC-06-02: Kê quá số lượng tồn kho → từ chối

### FR-07: Thanh toán
- TC-07-01: Kế toán xác nhận thanh toán → status "đã thanh toán"
- TC-07-02: Bác sĩ không xác nhận được thanh toán → 403
- TC-07-03: Tổng tiền khớp với hệ thống tính toán

### FR-09: Đặt lịch trực tuyến
- TC-09-01: Gửi OTP thành công tới email
- TC-09-02: OTP sai → thông báo lỗi
- TC-09-03: OTP hết hạn → yêu cầu gửi lại
- TC-09-04: Quá Rate Limiting → từ chối
- TC-09-05: Đặt lịch tạo trạng thái "Chờ xác nhận"

### FR-AI-01: AI Summary
- TC-AI-01-01: Data Masking ẩn đúng PII trước khi gửi LLM
- TC-AI-01-02: Kết quả trả về dạng bản nháp (chưa phê duyệt)
- TC-AI-01-03: AI lỗi → Fallback, hệ thống vẫn chạy bình thường
- TC-AI-01-04: AI Log ghi nhận đầy đủ

### FR-AI-02: AI Chatbot
- TC-AI-02-01: Chatbot trả lời câu hỏi về quy trình khám
- TC-AI-02-02: Câu hỏi về chẩn đoán → từ chối, hướng dẫn gặp bác sĩ
- TC-AI-02-03: API key không lộ ra response

### FR-AI-03: Post-exam Guide
- TC-AI-03-01: AI tạo hướng dẫn từ ghi chú bác sĩ
- TC-AI-03-02: Nội dung ở trạng thái "bản nháp"
- TC-AI-03-03: Bác sĩ phê duyệt → lưu chính thức

## Test Template (pytest)
```python
# tests/test_auth.py
def test_login_success(client):
    response = client.post("/auth/login", json={
        "username": "admin", "password": "Admin@123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client):
    response = client.post("/auth/login", json={
        "username": "admin", "password": "wrong"
    })
    assert response.status_code == 401

def test_doctor_cannot_access_admin(client, doctor_token):
    response = client.get("/admin/users",
        headers={"Authorization": f"Bearer {doctor_token}"})
    assert response.status_code == 403
```

## Rules
- **Không** sửa test chỉ để làm test pass.
- **Không** bỏ qua test AI Guardrails (SEC-AI-02).
- Kiểm tra Data Masking là test ưu tiên cao.
- Coverage phải đạt ≥70% cho các module nghiệp vụ cốt lõi.

## Outputs
- `docs/test-plan.md`
- `docs/test-report.md`
- `tests/test_auth.py`
- `tests/test_patients.py`
- `tests/test_schedules.py`
- `tests/test_ai_service.py`
