# Kế hoạch Thực hiện: [Tên tính năng / Tên Bugfix]
- **Branch:** `feat/<ten-chuc-nang>` hoặc `fix/<ten-bug>`
- **Người thực hiện:** [User 1 / User 2]
- **Yêu cầu / FR liên quan:** [Ví dụ: FR-05, FR-06...]
- **Trạng thái:** Chờ xác nhận từ người dùng

---

## 1. Phân tích yêu cầu & Mục tiêu
- **Mục tiêu chức năng:** [Mô tả chi tiết những gì cần đạt được]
- **Luồng người dùng (User Flow):** [Các bước người dùng tương tác]

---

## 2. Danh sách File cần thay đổi (Kèm lý do)
| File | Loại thay đổi (Thêm mới / Sửa) | Mục đích / Lý do |
| :--- | :--- | :--- |
| `models.py` | Sửa | Thêm cột hoặc bảng mới |
| `routers/...` | Thêm mới / Sửa | Viết API xử lý logic |
| `templates/...` | Sửa | Thêm giao diện hiển thị |

---

## 3. Kế hoạch Tách Commit (BẮT BUỘC TÁCH RIÊNG TỪNG NHÓM FILE)
- [ ] **Commit 1 (Model & Database):** `feat(model): ...`
- [ ] **Commit 2 (Backend & Router):** `feat(api): ...`
- [ ] **Commit 3 (Frontend Template):** `feat(ui): ...`
- [ ] **Commit 4 (Static JS/CSS):** `feat(js): ...`

---

## 4. Kế hoạch Tự Kiểm tra & Test (Self-Verification)
- [ ] Kiểm tra lỗi cú pháp (Syntax errors, import thiếu)
- [ ] Kiểm tra logic nghiệp vụ theo đúng yêu cầu
- [ ] Kiểm tra bảo mật: Không hardcode API key/password, không vi phạm role
- [ ] Chạy thử ứng dụng local và test luồng hoạt động

---

> ⚠️ **CHỐT CHẶN (HUMAN GATE):** AI Agent phải dừng tại đây và chờ người dùng gõ xác nhận duyệt kế hoạch trước khi bắt đầu viết code!
