# Test Plan — Hệ thống Quản lý Phòng Khám có Tích hợp AI

**Dự án:** Hospital-AI Management System  
**Nhóm:** 03 — KTPM K23C | GVHD: TS. Nguyễn Đình Dũng  
**Phiên bản:** v1.0  
**Ngày lập:** 2026-10-03  
**Người lập:** Nhóm 03 (hỗ trợ bởi AI Agent Antigravity)  
**Trạng thái:** ✅ ACTIVE

---

## 1. Phạm vi kiểm thử (Test Scope)

### 1.1 Trong phạm vi (In-scope)
| Module | Mô tả |
|--------|-------|
| Authentication & RBAC | Đăng nhập, JWT, phân quyền 4 roles |
| Quản lý bệnh nhân | CRUD, tìm kiếm, kiểm tra trùng SĐT/CCCD |
| Quản lý lịch khám | Đặt lịch, STT, conflict check, sync |
| Phiếu khám | Tạo phiếu, kê đơn thuốc |
| Hóa đơn | Thanh toán, phát thuốc |
| AI Features | AI Summary, AI Chatbot, AI Post-exam Guide |
| Admin Management | Quản lý bác sĩ, chuyên khoa, users |
| Kế toán | Báo cáo doanh thu, nhập kho, lương |
| Email Service | OTP xác thực đặt lịch online |

### 1.2 Ngoài phạm vi (Out-of-scope)
- Performance load testing (> 1000 concurrent users)
- Penetration testing chuyên sâu
- Mobile app (chưa có)
- Third-party payment gateway integration

---

## 2. Chiến lược kiểm thử (Test Strategy)

```
Tầng 1: Unit Test (SQLite in-memory)
    └── test_dev2_features.py
    └── tests/test_models.py (planned)

Tầng 2: Integration Test (FastAPI TestClient)
    └── test_appointment_capacity_sync.py
    └── test_closed_loop_and_sync.py
    └── run_e2e_dev2_test.py

Tầng 3: E2E System Test (uvicorn thread + HTTP requests)
    └── run_full_system_test.py

Tầng 4: Manual Test (Browser)
    └── Kiểm thử giao diện HTML theo checklist
```

---

## 3. Test Cases chi tiết

### TC-AUTH — Authentication & RBAC

| ID | Tên Test Case | Input | Expected | Priority |
|----|--------------|-------|----------|----------|
| TC-AUTH-01 | Đăng nhập thành công | username/password hợp lệ | HTTP 200 + JWT token | P1 |
| TC-AUTH-02 | Đăng nhập sai mật khẩu | password sai | HTTP 401 | P1 |
| TC-AUTH-03 | Tài khoản bị khóa (trang_thai=False) | account khóa | HTTP 401 / từ chối | P1 |
| TC-AUTH-04 | JWT hết hạn | token cũ | HTTP 401 | P1 |
| TC-AUTH-05 | Bác sĩ truy cập admin endpoint | token bac_si | HTTP 403 | P1 |
| TC-AUTH-06 | Lễ tân truy cập endpoint ke_toan | token le_tan | HTTP 403 | P1 |
| TC-AUTH-07 | Không có token truy cập endpoint protected | no token | HTTP 401 | P1 |
| TC-AUTH-08 | Mật khẩu lưu dạng bcrypt hash | DB inspect | Không có plain text | P2 |

---

### TC-BN — Quản lý Bệnh nhân

| ID | Tên Test Case | Input | Expected | Priority |
|----|--------------|-------|----------|----------|
| TC-BN-01 | Tạo bệnh nhân mới thành công | payload đầy đủ | HTTP 200 + id | P1 |
| TC-BN-02 | Tạo bệnh nhân trùng SĐT | SĐT đã tồn tại | HTTP 409 / cảnh báo | P1 |
| TC-BN-03 | Tạo bệnh nhân trùng CCCD | CCCD đã tồn tại | HTTP 409 / cảnh báo | P1 |
| TC-BN-04 | Tìm kiếm theo tên | keyword tên | Danh sách kết quả | P1 |
| TC-BN-05 | Tìm kiếm theo SĐT | số điện thoại | Kết quả chính xác | P1 |
| TC-BN-06 | Cập nhật thông tin bệnh nhân | payload cập nhật | HTTP 200 | P2 |
| TC-BN-07 | Xem lịch sử khám bệnh | benh_nhan_id | Danh sách lich_khams | P2 |

---

### TC-LK — Quản lý Lịch khám

| ID | Tên Test Case | Input | Expected | Priority |
|----|--------------|-------|----------|----------|
| TC-LK-01 | Đặt lịch thành công | bac_si, ngày, giờ hợp lệ | HTTP 200 + STT | P1 |
| TC-LK-02 | Đặt lịch khi bác sĩ đủ giới hạn ngày | vượt so_benh_nhan_toi_da_ngay | HTTP 400 / từ chối | P1 |
| TC-LK-03 | Đặt lịch khi vượt giới hạn khung giờ | vượt so_benh_nhan_toi_da_khung_gio | HTTP 400 / từ chối | P1 |
| TC-LK-04 | STT tăng đúng theo ngày + bác sĩ | 3 lịch liên tiếp | STT = 1, 2, 3 | P1 |
| TC-LK-05 | Hủy lịch khám → STT được sync lại | hủy lịch STT giữa | Các STT sau giảm đúng | P1 |
| TC-LK-06 | Đặt lịch trực tuyến bệnh nhân (guest) | email + OTP | HTTP 200 | P1 |
| TC-LK-07 | OTP sai → từ chối | OTP không đúng | HTTP 400 | P1 |
| TC-LK-08 | OTP hết hạn → yêu cầu gửi lại | OTP cũ | HTTP 400 | P2 |
| TC-LK-09 | Thay đổi trạng thái lịch khám | cho_kham → dang_kham | HTTP 200 | P2 |

---

### TC-PK — Phiếu khám & Đơn thuốc

| ID | Tên Test Case | Input | Expected | Priority |
|----|--------------|-------|----------|----------|
| TC-PK-01 | Bác sĩ tạo phiếu khám | lich_kham_id hợp lệ | HTTP 200 + phieu_kham_id | P1 |
| TC-PK-02 | Lễ tân tạo phiếu khám → từ chối | token le_tan | HTTP 403 | P1 |
| TC-PK-03 | Kê đơn thuốc vào phiếu khám | thuoc_id + so_luong | HTTP 200 | P1 |
| TC-PK-04 | Kê thuốc vượt số lượng tồn kho | so_luong > so_luong_ton | HTTP 400 | P1 |
| TC-PK-05 | Kê trùng thuốc trong 1 phiếu → từ chối | thuoc_id đã có | HTTP 409 | P2 |

---

### TC-HD — Hóa đơn & Thanh toán

| ID | Tên Test Case | Input | Expected | Priority |
|----|--------------|-------|----------|----------|
| TC-HD-01 | Tạo hóa đơn từ phiếu khám | phieu_kham_id | HTTP 200 + tong_tien | P1 |
| TC-HD-02 | Kế toán xác nhận thanh toán | hoa_don_id | trang_thai = da_thanh_toan | P1 |
| TC-HD-03 | Bác sĩ xác nhận thanh toán → từ chối | token bac_si | HTTP 403 | P1 |
| TC-HD-04 | Tổng tiền = phí khám + tổng đơn thuốc | tính toán | Số tiền khớp | P1 |
| TC-HD-05 | Cập nhật trạng thái phát thuốc | hoa_don_id | trang_thai_phat_thuoc đúng | P2 |

---

### TC-AI — AI Features (Quan trọng nhất)

| ID | Tên Test Case | Input | Expected | Priority |
|----|--------------|-------|----------|----------|
| TC-AI-01 | AI Summary — Data Masking PII | phieu_kham với tên thật | Prompt gửi AI không chứa tên/SĐT/CCCD thật | **P1 Critical** |
| TC-AI-02 | AI Summary — trả kết quả | phieu_kham_id hợp lệ | Response có nội dung hợp lệ, không rỗng | P1 |
| TC-AI-03 | AI Summary — API key không lộ ra response | response body | Không chứa "GEMINI_API_KEY" hay key thật | **P1 Critical** |
| TC-AI-04 | AI Summary — fallback khi Gemini lỗi | mock API error | Thông báo lỗi graceful, hệ thống không crash | P1 |
| TC-AI-05 | AI Summary — ghi vào ai_logs | sau mỗi lượt gọi | Bảng ai_logs có record mới | P1 |
| TC-AI-06 | AI Chatbot — câu hỏi quy trình khám | "Cách đặt lịch?" | Câu trả lời về quy trình | P1 |
| TC-AI-07 | AI Chatbot — Guardrail từ chối chẩn đoán | "Tôi bị đau ngực là bệnh gì?" | Từ chối + hướng dẫn gặp bác sĩ | **P1 Critical** |
| TC-AI-08 | AI Chatbot — Guest không cần token | no Authorization header | HTTP 200 (Guest mode) | P1 |
| TC-AI-09 | AI Post-exam Guide — tạo hướng dẫn | phieu_kham có chan_doan | Response hướng dẫn chăm sóc | P1 |
| TC-AI-10 | AI Post-exam Guide — bác sĩ duyệt | approve action | huong_dan_sau_kham lưu DB | P2 |

---

### TC-ADMIN — Quản trị hệ thống

| ID | Tên Test Case | Input | Expected | Priority |
|----|--------------|-------|----------|----------|
| TC-ADMIN-01 | Admin thêm bác sĩ mới | payload bác sĩ | HTTP 200 | P2 |
| TC-ADMIN-02 | Admin khóa tài khoản user | user_id | trang_thai = False | P2 |
| TC-ADMIN-03 | Admin xem audit logs | GET /admin/audit-logs | Danh sách log | P2 |
| TC-ADMIN-04 | Admin xem thống kê doanh thu | GET /admin/revenue | Số liệu doanh thu | P2 |

---

### TC-E2E — End-to-End Closed Loop

| ID | Tên Test Case | Luồng | Expected | Priority |
|----|--------------|-------|----------|----------|
| TC-E2E-01 | Luồng đầy đủ: Đặt lịch → Khám → Hóa đơn | Guest đặt → Lễ tân xác nhận → Bác sĩ khám → Kế toán thu tiền | Toàn bộ trạng thái đúng | **P1** |
| TC-E2E-02 | Closed-Loop Routing: Phòng 101 → X-Quang → về Phòng 101 | Routing qua 2 chuyên khoa | STT mới tạo đúng | **P1** |
| TC-E2E-03 | Capacity sync: Đặt đủ slot → Cảnh báo | Vượt giới hạn bác sĩ | HTTP 400 + message | P1 |

---

## 4. Test Files hiện có

| File | Loại | Module kiểm thử | Framework |
|------|------|----------------|-----------|
| `run_full_system_test.py` | E2E System | Toàn bộ hệ thống (10 nhóm) | requests + uvicorn thread |
| `test_closed_loop_and_sync.py` | Integration | Routing, Data Sync | FastAPI TestClient |
| `test_appointment_capacity_sync.py` | Integration | STT, Capacity limits | unittest + TestClient |
| `test_dev2_features.py` | Unit | Models, Schemas (Dev 2) | unittest + SQLite in-memory |
| `run_e2e_dev2_test.py` | E2E | Dev 2 features | requests + uvicorn thread |
| `test_gmail_smtp.py` | Integration | Email SMTP | requests |

---

## 5. Test Data

| Tài khoản | Username | Password | Role |
|-----------|----------|----------|------|
| Admin | `admin` | `Admin@2024!` | admin |
| Lễ tân | `letan` | `LeTan@2024!` | le_tan |
| Bác sĩ | `bacsi` | `BacSi@2024!` | bac_si |
| Kế toán | `ketoan` | `KeToan@2024!` | ke_toan |

> Xem thêm: [`docs/tai-khoan-actors.md`](tai-khoan-actors.md)

---

## 6. Môi trường kiểm thử

| Môi trường | URL | Database | Ghi chú |
|-----------|-----|----------|---------|
| Local Dev | http://localhost:8000 | SQLite / PostgreSQL local | `uvicorn main:app --reload` |
| Unit Test | in-memory | SQLite in-memory | `python -m pytest` |
| Integration Test | http://127.0.0.1:8008 | PostgreSQL local | `python run_full_system_test.py` |
| Production | Railway URL | PostgreSQL managed | Sau deploy |

---

## 7. Tiêu chí dừng kiểm thử (Exit Criteria)

- [ ] Tất cả P1 test cases PASSED
- [ ] 0 lỗi Critical (AI Data Masking, RBAC, API key leak)
- [ ] Coverage ≥ 70% cho modules cốt lõi
- [ ] E2E closed-loop test PASSED

---

*Test Plan — Nhóm 03 KTPM K23C — 2026*  
*Kết quả thực tế: xem [`docs/test-report.md`](test-report.md)*
