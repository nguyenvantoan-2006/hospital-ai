# Git Workflow Rules — Hospital-AI
# Áp dụng cho TẤT CẢ Antigravity agents làm việc trong repo này.

## Bắt buộc kiểm tra branch trước khi code

Trước khi bắt đầu BẤT KỲ tác vụ nào liên quan đến viết hoặc sửa code, agent PHẢI:

1. Chạy lệnh `git branch --show-current` để xác định branch hiện tại
2. Thông báo kết quả cho user: "Hiện tại đang ở branch: <tên branch>"
3. Nếu đang ở `main` → DỪNG LẠI, đề xuất tạo feature branch phù hợp, hỏi user xác nhận
4. Chỉ tiếp tục code sau khi đã ở đúng feature branch

## Cấm tuyệt đối

- KHÔNG commit trực tiếp lên `main`
- KHÔNG push lên `main` bằng `git push origin main` trừ khi đang thực hiện squash merge đã được user xác nhận
- KHÔNG tạo branch với tên không theo convention (main, temp, test, fix1, v.v.)
- KHÔNG commit file: .env, __pycache__/, *.db, *.pyc, clinic.db

## Convention đặt tên branch

Chỉ chấp nhận các prefix sau:
- feat/   — tính năng mới
- fix/    — sửa lỗi
- refactor/ — cấu trúc lại
- docs/   — tài liệu
- test/   — kiểm thử

## Convention commit message

Format bắt buộc: `<type>(<scope>): <mô tả>`
Ví dụ: `feat(benh-nhan): them trang dat lich online FR-09`

## Khi được yêu cầu merge / hoàn thành feature

Agent phải hướng dẫn user chạy squash merge theo đúng workflow trong docs/git-workflow.md
KHÔNG tự ý merge mà không có sự xác nhận của user.

## Tham khảo chi tiết

Xem đầy đủ trong: docs/git-workflow.md và AGENTS.md
