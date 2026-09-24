# Kế Hoạch Triển Khai: Tự Động Đề Xuất Kho Thuốc Khi Kê Đơn (FR-06)

**Dự án:** Hospital-AI Management System  
**Nhánh:** `feat/de-xuat-kho-thuoc-ke-don`  
**Chức năng:** FR-06 — Kê đơn thuốc điện tử & Đề xuất danh mục kho thuốc thông minh  
**Ngày:** 24/09/2026  

---

## 🎯 I. MỤC TIÊU
Khi Bác sĩ click hoặc focus vào ô "Tên thuốc & Quy cách" trong bảng kê đơn (`lap_phieu_kham.html`), hệ thống sẽ:
1. **Tự động mở Dropdown Đề xuất Kho thuốc** hiển thị danh sách tất cả các mặt hàng thuốc & vật tư y tế có sẵn trong kho phòng khám (kèm số lượng tồn kho, đơn vị tính, đơn giá).
2. Bác sĩ có thể click chọn ngay thuốc từ danh sách đề xuất mà không bắt buộc phải gõ chính xác tên thuốc.
3. Khi gõ từ khóa: Hệ thống tự động lọc nhanh (hỗ trợ cả tìm kiếm linh hoạt, tiếng Việt có dấu/không dấu) và cập nhật danh sách đề xuất.
4. Tự động đóng dropdown khi click ra ngoài.

---

## 📁 II. DANH SÁCH FILE THAY ĐỔI
| File | Loại | Mục đích |
|---|:---:|---|
| `templates/lap_phieu_kham.html` | Sửa | Thêm sự kiện `onfocus`, `onclick` mở danh sách đề xuất kho thuốc, hỗ trợ lọc thông minh và UI dropdown chuyên nghiệp |
| `docs/plans/feat-de-xuat-kho-thuoc-ke-don.md` | Tạo mới | Kế hoạch thực hiện theo chuẩn AGENTS.md |

---

## 🪜 III. THỨ TỰ THỰC HIỆN
1. Cập nhật hàm `handleMedSearch` và `loadInitialMedicines` trong `lap_phieu_kham.html`.
2. Gắn sự kiện `onfocus`, `onclick` trên ô input tìm kiếm thuốc của từng dòng đơn thuốc.
3. Bổ sung sự kiện đóng dropdown khi click bên ngoài vùng chọn.
4. Tự kiểm tra cú pháp và giao diện.
