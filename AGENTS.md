# AGENTS.md — Quy tắc làm việc cho AI Agents trong dự án Hospital-AI
# File này được TỰ ĐỘNG ĐỌC bởi Antigravity và các AI agents khác.
# Mọi AI agent làm việc trong repo này PHẢI TUÂN THỦ các quy tắc dưới đây.

## 🏥 Dự án: Hospital-AI Management System
- **Nhóm:** 03 — KTPM K23C | GVHD: TS. Nguyễn Đình Dũng
- **Mô hình làm việc:** 2 người dùng Antigravity cùng làm việc song song
- **VCS:** Git — Feature Branch Workflow + Squash Merge vào `main`

---

## 🔄 LUỒNG XỬ LÝ CHUẨN — BẮT BUỘC VỚI MỌI CHỨC NĂNG / BUG

> AI Agent PHẢI tuân thủ đúng 6 bước sau theo thứ tự. KHÔNG được bỏ qua bước nào.
> KHÔNG được tự ý thực hiện bước tiếp theo khi chưa có xác nhận của người dùng.

### BƯỚC 1 — Phân tích yêu cầu
- Đọc kỹ yêu cầu của người dùng
- Xác định rõ: chức năng gì, FR nào liên quan, file nào cần sửa
- Hỏi lại nếu yêu cầu chưa rõ ràng — KHÔNG tự đoán và code ngay

### BƯỚC 2 — Tạo branch
- Kiểm tra branch hiện tại: `git branch --show-current`
- Nếu đang ở `main` hoặc branch không phù hợp → tạo/chuyển sang branch đúng
- Thông báo cho user: "Đang làm việc trên branch: feat/xxx"

### BƯỚC 3 — Lập kế hoạch thực hiện (TẠO FILE PLAN)
- Tạo file kế hoạch trong thư mục `docs/plans/` với tên mô tả chức năng
  Ví dụ: `docs/plans/feat-bac-si-dashboard.md`
- Nội dung kế hoạch bao gồm:
  * Mục tiêu và FR liên quan
  * Danh sách file sẽ thay đổi (kèm lý do)
  * Thứ tự thực hiện các bước
  * Rủi ro hoặc điểm cần chú ý
- DỪNG LẠI và chờ người dùng xác nhận kế hoạch trước khi code

### BƯỚC 4 — Thực hiện code (Sau khi được xác nhận)
- Code theo đúng kế hoạch đã được duyệt
- COMMIT TỪNG NHÓM FILE LIÊN QUAN — không commit tất cả một lúc:
  * Ví dụ: commit 1 = model + schema, commit 2 = router, commit 3 = template HTML
  * Mỗi commit phải có message rõ ràng theo convention
- Thông báo tiến độ sau mỗi commit

### BƯỚC 5 — Tự kiểm tra sau khi hoàn thành
AI Agent phải tự rà soát trước khi báo cho user:
- [ ] Không có lỗi syntax (import sai, thiếu dấu, v.v.)
- [ ] Logic xử lý đúng với yêu cầu FR
- [ ] Không vô tình xóa hoặc ghi đè code cũ đang hoạt động
- [ ] Không commit file: .env, __pycache__, *.db, *.pyc
- [ ] Không có hardcode password, API key
- Sau đó báo cho user: "Đã hoàn thành, mời bạn test. Dưới đây là những gì đã thay đổi: ..."
- DỪNG LẠI và chờ người dùng test

### BƯỚC 6 — Push / PR / Squash Merge (CHỈ KHI ĐƯỢC PHÉP)
> ⚠️ AI Agent TUYỆT ĐỐI KHÔNG tự thực hiện bước này khi chưa có xác nhận rõ ràng từ người dùng.
> Người dùng phải nói rõ: "push đi", "merge vào main", "tạo PR" hoặc tương tự.

Khi được phép:
```bash
# 1. Rebase với main mới nhất
git checkout main && git pull origin main
git checkout feat/<ten-chuc-nang>
git rebase main

# 2. Squash merge
git checkout main
git merge --squash feat/<ten-chuc-nang>
git commit -m "feat(<scope>): <tom tat tinh nang>"

# 3. Push và dọn branch
git push origin main
git branch -d feat/<ten-chuc-nang>
git push origin --delete feat/<ten-chuc-nang>
```

---

## ⚙️ QUY TẮC COMMIT — TÁCH RIÊNG TỪNG NHÓM FILE

KHÔNG được commit tất cả file thay đổi vào 1 commit duy nhất.
Phải tách theo nhóm logic:

| Nhóm | Ví dụ file | Ví dụ commit message |
|------|-----------|---------------------|
| Database/Model | models.py, schemas.py | `feat(model): them truong X vao bang Y` |
| Backend/Router | routers/xxx.py | `feat(api): them endpoint GET /xxx` |
| Frontend | templates/xxx.html | `feat(ui): them trang dashboard bac si` |
| Static assets | static/js/xxx.js | `feat(js): them logic dat lich online` |
| Docs/Plan | docs/plans/xxx.md | `docs(plan): them ke hoach feat-xxx` |

---

## ⚠️ QUY TẮC GIT — BẮT BUỘC TUYỆT ĐỐI

### RULE-GIT-01: KHÔNG BAO GIỜ làm việc trên branch `main`
> AI Agent TUYỆT ĐỐI KHÔNG được commit hay push bất kỳ thay đổi nào lên branch `main`.
> `main` chỉ nhận code qua squash merge từ feature branch đã hoàn thành.

### RULE-GIT-02: Mỗi chức năng = 1 branch riêng
Trước khi bắt đầu bất kỳ tác vụ code nào, AI Agent PHẢI:
1. Kiểm tra branch hiện tại: `git branch --show-current`
2. Nếu đang ở `main` → tạo feature branch mới theo đúng convention
3. Nếu đã có branch phù hợp → checkout sang branch đó
4. Chỉ sau khi đang ở đúng feature branch mới được viết/sửa code

### RULE-GIT-03: Quy ước đặt tên branch (BẮT BUỘC)
```
feat/<ten-chuc-nang>       # Tính năng mới
fix/<mo-ta-loi>            # Sửa lỗi
refactor/<phan-he>         # Cấu trúc lại code
docs/<noi-dung>            # Tài liệu
test/<ten-module>          # Kiểm thử
```

Ví dụ hợp lệ:
- feat/benh-nhan-portal
- feat/bac-si-dashboard
- fix/lich-kham-conflict-check
- refactor/auth-middleware
- docs/api-documentation

Ví dụ KHÔNG hợp lệ (bị cấm):
- main (cam tuyet doi)
- my-branch (khong dung convention)
- test123 (khong co y nghia)
- temp (khong ro rang)

### RULE-GIT-04: Quy ước commit message (BẮT BUỘC)
Format: `<type>(<scope>): <mo ta ngan gon>`

Ví dụ đúng:
- feat(benh-nhan): them trang dat lich online FR-09
- fix(auth): sua loi JWT token het han
- refactor(admin): to chuc lai routes quan ly bac si
- docs(api): cap nhat mo ta endpoints lich_khams
- test(hoa-don): them test case xac nhan thanh toan

Types hợp lệ: feat | fix | refactor | docs | test | style | chore

### RULE-GIT-05: Workflow khi bắt đầu task mới
Trước khi code, AI Agent PHẢI chạy và thông báo kết quả của các lệnh:

Bước 1 — Cập nhật main:
  git checkout main
  git pull origin main

Bước 2 — Tạo hoặc checkout feature branch:
  git checkout -b feat/<ten-chuc-nang>
  (hoặc: git checkout feat/<ten-da-ton-tai>)

Bước 3 — Làm việc và commit:
  git add <files>
  git commit -m "feat(<scope>): <mo ta>"

Bước 4 — Push branch:
  git push -u origin feat/<ten-chuc-nang>

### RULE-GIT-06: Workflow khi hoàn thành feature (Squash Merge)
Bước 1 — Rebase với main mới nhất:
  git checkout main && git pull origin main
  git checkout feat/<ten-chuc-nang>
  git rebase main

Bước 2 — Squash merge (KHONG dung merge thuong):
  git checkout main
  git merge --squash feat/<ten-chuc-nang>
  git commit -m "feat(<scope>): <tom tat tinh nang hoan chinh>"

Bước 3 — Push và dọn dẹp:
  git push origin main
  git branch -d feat/<ten-chuc-nang>
  git push origin --delete feat/<ten-chuc-nang>

---

## 📋 QUY TẮC CODE — AI AGENT TUÂN THỦ

### RULE-CODE-01: Kiểm tra branch trước khi code
AI Agent PHẢI chạy `git branch --show-current` và thông báo cho user biết đang ở branch nào TRƯỚC KHI bắt đầu viết bất kỳ dòng code nào.

### RULE-CODE-02: Phân công chức năng theo branch
| Branch | Chức năng | Actor |
|--------|-----------|-------|
| feat/benh-nhan-portal | Dat lich online, tra cuu, chatbot | Benh nhan |
| feat/bac-si-dashboard | Dashboard bac si, phieu kham | Bac si |
| feat/le-tan-dashboard | Dashboard le tan | Le tan |
| feat/ke-toan-dashboard | Bao cao, thong ke | Ke toan |
| feat/admin-* | Cac tinh nang admin | Admin |

### RULE-CODE-03: Tránh conflict — Quy tắc phân chia file
Người 1 (bạn - ưu tiên):
  templates/ (frontend HTML), routers/admin.py, routers/lich_khams.py

Người 2 (bạn cùng nhóm - ưu tiên):
  models.py, schemas.py, routers/phieu_khams.py, routers/hoa_dons.py

File chung (main.py, database.py):
  Chỉ sửa khi cần thiết, thông báo cho nhau trước

### RULE-CODE-04: Không sửa file của người khác đang làm
Nếu cần sửa file mà người kia đang làm trên branch khác → thông báo, KHÔNG tự sửa.

---

## 🤝 QUY TẮC PHỐI HỢP

### RULE-COLLAB-01: Xử lý conflict
1. git pull origin main — lấy code mới nhất
2. Giải quyết conflict cẩn thận — KHÔNG xóa code của người kia
3. Test lại trước khi push
4. Thông báo cho người kia biết đã resolve conflict

### RULE-COLLAB-02: Commit thường xuyên
AI Agent nên commit sau mỗi chức năng nhỏ hoàn chỉnh, không để tồn đọng nhiều thay đổi lớn chưa commit.

---

## ✅ CHECKLIST TRƯỚC KHI PUSH

AI Agent PHẢI tự kiểm tra trước khi git push:
- Dang o dung feature branch (khong phai main)
- Commit message dung format
- Code khong co syntax error
- Khong commit file .env, __pycache__, *.db, *.pyc
- Khong co hardcode password hay API key trong code
