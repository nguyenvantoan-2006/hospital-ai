# Git & Workflow Rules — Hospital-AI
# Áp dụng cho TẤT CẢ Antigravity agents làm việc trong repo này.

## LUỒNG XỬ LÝ BẮT BUỘC — 6 BƯỚC TUẦN TỰ

Với MỌI yêu cầu chức năng hoặc fix bug, agent phải đi theo đúng thứ tự:

  BƯỚC 1: Phân tích yêu cầu — hỏi lại nếu chưa rõ, KHÔNG tự đoán rồi code ngay
  BƯỚC 2: Tạo/chuyển sang đúng feature branch — thông báo branch đang dùng
  BƯỚC 3: Tạo file kế hoạch tại docs/plans/<ten-feature>.md — DỪNG chờ user xác nhận
  BƯỚC 4: Code sau khi được xác nhận — commit TỪNG NHÓM FILE, không gộp tất cả
  BƯỚC 5: Tự kiểm tra bugs — báo cáo những gì đã thay đổi — DỪNG chờ user test
  BƯỚC 6: Push/PR/Merge — CHỈ thực hiện khi user nói rõ cho phép

## ĐIỂM DỪNG BẮT BUỘC (HUMAN GATE)

Agent PHẢI dừng và chờ xác nhận của user tại 2 điểm:
  - Sau BƯỚC 3: Chờ user duyệt kế hoạch trước khi bắt đầu code
  - Sau BƯỚC 5: Chờ user test xong trước khi push/merge

## KHÔNG BAO GIỜ tự thực hiện các hành động sau khi chưa có lệnh rõ ràng:
  - git push origin main
  - git merge --squash
  - Tạo Pull Request

## QUY TẮC COMMIT — TÁCH TỪNG NHÓM FILE

Mỗi commit chỉ chứa 1 nhóm thay đổi logic:
  Nhóm 1 (Model/Schema): models.py, schemas.py
  Nhóm 2 (Backend): routers/*.py
  Nhóm 3 (Frontend): templates/*.html
  Nhóm 4 (Static): static/js/*.js, static/css/*.css
  Nhóm 5 (Docs): docs/plans/*.md

## QUY TẮC BRANCH

  - Kiểm tra branch trước mỗi tác vụ: git branch --show-current
  - Nếu đang ở main → DỪNG, tạo/chuyển sang feature branch trước
  - Convention: feat/* | fix/* | refactor/* | docs/* | test/*
  - Cấm: main, temp, test123, my-branch, và bất kỳ tên không có prefix chuẩn

## QUY TẮC COMMIT MESSAGE

  Format: <type>(<scope>): <mo ta ngan gon>
  Ví dụ: feat(bac-si): them trang dashboard quan ly lich kham FR-05

## XEM CHI TIẾT

  Xem đầy đủ tại: AGENTS.md và docs/git-workflow.md

