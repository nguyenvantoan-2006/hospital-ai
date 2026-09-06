# Git Workflow — Hospital-AI Team

## Quy trình chuẩn cho nhóm 2 người dùng Antigravity

### Nguyên tắc cốt lõi

1. Branch `main` chỉ nhận code từ squash merge — không commit trực tiếp
2. Mỗi tính năng = 1 branch = 1 squash commit khi hoàn thành
3. AI agent phải kiểm tra và thông báo branch hiện tại trước khi code

### Quy ước đặt tên branch

```
feat/<ten-chuc-nang>   →  feat/bac-si-dashboard
fix/<mo-ta-loi>        →  fix/auth-jwt-expired
refactor/<phan-he>     →  refactor/admin-routes
docs/<noi-dung>        →  docs/api-swagger
test/<module>          →  test/hoa-don-payment
```

### Quy ước commit message

```
feat(benh-nhan): them trang dat lich online FR-09
fix(auth): sua loi JWT het han
refactor(admin): to chuc lai routes bac si
docs(requirements): cap nhat user stories
test(lich-kham): them test conflict check
```

### Luồng làm việc — Bắt đầu task mới

```bash
# 1. Cập nhật main trước
git checkout main
git pull origin main

# 2. Tạo branch mới
git checkout -b feat/ten-chuc-nang

# 3. Code & commit thường xuyên
git add <files>
git commit -m "feat(scope): mo ta"

# 4. Push branch
git push -u origin feat/ten-chuc-nang
```

### Luồng làm việc — Hoàn thành & merge vào main

```bash
# 1. Lấy main mới nhất
git checkout main
git pull origin main

# 2. Rebase feature branch lên main mới
git checkout feat/ten-chuc-nang
git rebase main
# (giải quyết conflict nếu có, rồi: git rebase --continue)

# 3. Squash merge vào main
git checkout main
git merge --squash feat/ten-chuc-nang
git commit -m "feat(scope): tom tat tinh nang hoan chinh"

# 4. Push và dọn branch
git push origin main
git branch -d feat/ten-chuc-nang
git push origin --delete feat/ten-chuc-nang
```

### Khi bị conflict

```bash
# Xem file conflict
git status

# Mở file, tìm và sửa các đoạn:
# <<<<<<< HEAD
# (code của bạn)
# =======
# (code của người kia)
# >>>>>>> feat/ten-branch

# Sau khi sửa xong
git add <file-da-sua>
git rebase --continue   # (nếu đang rebase)
# hoặc
git commit              # (nếu đang merge)
```

### Phân công file để tránh conflict

| Người 1 | Người 2 |
|---------|---------|
| templates/ (HTML frontend) | models.py |
| routers/admin.py | schemas.py |
| routers/lich_khams.py | routers/phieu_khams.py |
| routers/benh_nhans.py | routers/hoa_dons.py |
| static/ (CSS/JS) | routers/ai.py |

File dùng chung — thông báo nhau trước khi sửa:
- main.py
- database.py
- .env.example

### Branches hiện có / đề xuất

| Branch | Chức năng | Người phụ trách |
|--------|-----------|-----------------|
| `main` | Production code — chỉ nhận squash merge | — |
| `feat/benh-nhan-portal` | Trang bệnh nhân (FR-09, FR-10, FR-AI-02) | Người 1 |
| `feat/bac-si-dashboard` | Dashboard bác sĩ (FR-05, FR-06, FR-AI-01) | Người 2 |
| `feat/le-tan-dashboard` | Dashboard lễ tân (FR-02, FR-04) | Thoả thuận |
| `feat/ke-toan-dashboard` | Báo cáo kế toán (FR-07, FR-08) | Thoả thuận |
