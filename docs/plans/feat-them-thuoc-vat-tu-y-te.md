# Kế hoạch thực hiện: Bổ sung thuốc và vật tư y tế vào Kho Thuốc (FR-12)

## 🎯 Mục tiêu
Bổ sung danh mục Thuốc tân dược, thuốc điều trị và Vật tư y tế tiêu chuẩn (bơm tiêm, cồn y tế, băng gạc, khẩu trang, nước muối...) vào kho thuốc phòng khám.

## 📁 Danh sách file thay đổi
1. `seed_medicines.py` [NEW]: Script nạp 19 mặt hàng thuốc & vật tư y tế mới vào bảng `thuocs`.
2. `docs/plans/feat-them-thuoc-vat-tu-y-te.md` [NEW]: File kế hoạch lưu vết.

## 📋 Thứ tự thực hiện
1. Kiểm tra branch hiện tại.
2. Tạo file `seed_medicines.py` nạp dữ liệu.
3. Chạy script nạp vào Database.
4. Kiểm tra số lượng tồn kho và thông tin đơn giá trong CSDL.
5. Commit code và báo cáo người dùng.

## ⚠️ Rủi ro & Điểm chú ý
- Đảm bảo trùng tên thuốc sẽ được cập nhật số lượng tồn kho chứ không bị lỗi duplicate key.
