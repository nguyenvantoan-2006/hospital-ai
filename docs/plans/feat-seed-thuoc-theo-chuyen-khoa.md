# Kế Hoạch Triển Khai: Nạp Danh Mục Thuốc Chuyên Sâu Theo 37 Chuyên Khoa (FR-06 & Quầy Dược)

**Dự án:** Hospital-AI Management System  
**Nhánh:** `feat/seed-thuoc-theo-chuyen-khoa`  
**Chức năng:** Bổ sung danh mục thuốc chuyên khoa đa dạng (Tim Mạch, Hô Hấp, Tiêu Hóa, Cơ Xương Khớp, Thần Kinh, Tai Mũi Họng, Răng Hàm Mặt, Mắt, Da Liễu, Nhi Khoa, Sản Phụ Khoa, Nội Tiết, Cấp Cứu, v.v.)  
**Ngày:** 24/09/2026  

---

## 🎯 I. MỤC TIÊU
Cung cấp một kho dược phẩm phong phú, đầy đủ thuốc đặc trị chuẩn phác đồ của Bộ Y tế cho tất cả các chuyên khoa khám bệnh, giúp:
1. Bác sĩ ở từng chuyên khoa khi mở form khám bệnh đều có sẵn các loại thuốc chuyên ngành tương ứng để kê đơn.
2. Dược sĩ tại Quầy Dược và Kế toán theo dõi tồn kho, xuất nhập kho chính xác.
3. Người dùng tìm kiếm thuốc theo tên hoạt chất, tên thương mại hoặc tên chuyên khoa đều tìm thấy dễ dàng.

---

## 📁 II. DANH SÁCH FILE THAY ĐỔI
| File | Loại | Mục đích |
|---|:---:|---|
| `seed_medicines.py` | Sửa / Mở rộng | Bổ sung hơn 100+ mặt hàng thuốc và vật tư y tế phân loại theo 37 chuyên khoa |
| `docs/plans/feat-seed-thuoc-theo-chuyen-khoa.md` | Tạo mới | Kế hoạch thực hiện theo chuẩn AGENTS.md |

---

## 🪜 III. THỨ TỰ THỰC HIỆN
1. Biên soạn danh mục thuốc chi tiết cho các nhóm chuyên khoa chính (Tim mạch, Hô hấp, Tiêu hóa, Thần kinh, Da liễu, Tai Mũi Họng, Mắt, Sản Phụ Khoa, Nhi khoa, Xương khớp, Tiểu đường, Cấp cứu...).
2. Cập nhật script `seed_medicines.py` đảm bảo cập nhật hoặc thêm mới an toàn (UPSERT tránh trùng lặp).
3. Chạy nạp dữ liệu vào Database MySQL/SQLite.
4. Kiểm tra số lượng thuốc trong kho và kiểm thử tìm kiếm.
5. Commit code và báo cáo kết quả.
