# Kế Hoạch Triển Khai: Backend Đơn Thuốc, AI Log & Kế Toán Dược (DEV 2)

**Dự án:** Hospital-AI Management System  
**Nhánh:** `feat/backend-don-thuoc-va-ailog`  
**Người thực hiện:** DEV 2 (Backend Core & Dược - Kế toán)  
**Ngày:** 21/09/2026  
**Trạng thái:** 📋 CHỜ XÁC NHẬN (Human Gate)

---

## 🎯 I. MỤC TIÊU & CÁC YÊU CẦU CHỨC NĂNG LIÊN QUAN

1. **SEC-AI-04 & FR-AI-03**: Bổ sung bảng CSDL `ai_logs` và trường `huong_dan_sau_kham` vào `phieu_khams` để lưu vết mọi lượt gọi AI an toàn, kiểm toán và lưu hướng dẫn bác sĩ đã duyệt.
2. **FR-05 & FR-06**: Nâng cấp Backend khám bệnh và kê đơn thuốc điện tử. Hỗ trợ nhận danh sách đơn thuốc, kiểm tra số lượng tồn kho `thuocs.so_luong_ton`, lưu vào bảng `don_thuocs`. Cung cấp API tìm kiếm thuốc phục vụ Autocomplete cho Frontend (Dev 1).
3. **FR-07**: Xử lý trừ kho thuốc an toàn qua Transaction ACID khi thanh toán hóa đơn / phát thuốc.
4. **Quản lý Dược phẩm & Cảnh báo tồn kho**: Cung cấp đầy đủ API CRUD danh mục thuốc và danh sách cảnh báo thuốc sắp hết hàng (`so_luong_ton < 10`).
5. **FR-01 & NFR-SEC-01**: Bổ sung phân quyền RBAC chặt chẽ trên các API routers của Bác sĩ (`phieu_khams.py`) và Kế toán (`hoa_dons.py`, `ke_toan.py`).

---

## 📁 II. DANH SÁCH FILE THAY ĐỔI & PHẠM VI (TUÂN THỦ ZERO-CONFLICT)

| File | Hành động | Mục đích |
|---|---|---|
| `models.py` | Chỉnh sửa | Thêm model `AILog`, thêm cột `huong_dan_sau_kham` vào `PhieuKham`, đảm bảo quan hệ ORM chuẩn xác. |
| `schemas.py` | Chỉnh sửa | Thêm schemas cho `AILog`, `DonThuocCreate`, `PhieuKhamCreateWithDonThuoc`, `ThuocCreate/Update`. |
| `routers/phieu_khams.py` | Chỉnh sửa | Endpoint tạo phiếu khám kèm mảng đơn thuốc, kiểm tra tồn kho, cung cấp API search thuốc cho Dev 1, bảo vệ bằng RBAC. |
| `routers/hoa_dons.py` | Chỉnh sửa | Transaction trừ kho khi thanh toán/phát thuốc, RBAC kế toán. |
| `routers/ke_toan.py` | Chỉnh sửa | Hoàn thiện API CRUD danh mục thuốc, cảnh báo tồn kho thấp. |

> ⚠️ **Cam kết:** Không chỉnh sửa `templates/*`, `routers/lich_khams.py`, `routers/ai.py` (để tránh conflict với Dev 1).

---

## 🪜 III. THỨ TỰ THỰC HIỆN CÁC BƯỚC

### Bước 1: Cập nhật CSDL & Schemas (`models.py`, `schemas.py`)
- Thêm model `AILog` vào `models.py`:
  - `id`, `user_id`, `chuc_nang`, `prompt_masked`, `response_text`, `model_name`, `response_time_ms`, `trang_thai`, `thoi_gian`.
- Thêm cột `huong_dan_sau_kham = Column(Text, nullable=True)` vào `PhieuKham`.
- Cập nhật `schemas.py`: Pydantic models cho `AILog`, `ChiTietDonThuocInput`, `PhieuKhamCreateInput`, `ThuocResponse`.
- **Commit 1:** `feat(model): them bang AILog va truong huong_dan_sau_kham vao PhieuKham`

### Bước 2: Nâng cấp Router Phiếu Khám & API Search Thuốc (`routers/phieu_khams.py`)
- Bổ sung API `GET /api/v1/phieu-khams/thuocs/search?q=...`: Tìm kiếm nhanh thuốc còn hàng phục vụ Autocomplete cho Dev 1.
- Nâng cấp `POST /api/v1/phieu-khams/`:
  - Nhận `don_thuocs: List[DonThuocItem]`
  - Kiểm tra nếu `so_luong > thuoc.so_luong_ton` -> Báo lỗi `400 Bad Request`
  - Lưu vào bảng `don_thuocs`
  - Lưu `huong_dan_sau_kham`
- Bổ sung middleware phân quyền RBAC `require_roles(["bac_si", "admin"])`.
- **Commit 2:** `feat(api): them logic ke don thuoc va api search thuoc trong phieu_khams`

### Bước 3: Hoàn thiện Transaction Trừ Kho & Hóa Đơn (`routers/hoa_dons.py`)
- Cập nhật logic khi hóa đơn chuyển sang `da_thanh_toan` hoặc khi phát thuốc:
  - Sử dụng database transaction với `db.commit()` và `db.rollback()` an toàn.
  - Tự động trừ tồn kho: `thuoc.so_luong_ton -= dt.so_luong`.
  - Cập nhật trạng thái phát thuốc `da_lay_thuoc`.
- Bảo vệ router bằng `require_roles(["ke_toan", "admin"])`.
- **Commit 3:** `feat(api): transaction tru ton kho tu dong khi thanh toan hoa don`

### Bước 4: Hoàn thiện Quản lý Danh mục Dược phẩm & Cảnh báo tồn kho (`routers/ke_toan.py`)
- Bổ sung API CRUD thuốc: `POST /api/v1/ke-toan/thuocs/`, `PUT /api/v1/ke-toan/thuocs/{id}`, `DELETE /api/v1/ke-toan/thuocs/{id}`.
- Bổ sung API `GET /api/v1/ke-toan/thuocs/canh-bao-ton-kho`: Lấy danh sách các thuốc có `so_luong_ton < 10`.
- **Commit 4:** `feat(api): api crud thuoc va canh bao ton kho thap`

### Bước 5: Viết hàm Helper ghi AI Log & Test kiểm thử
- Viết tiện ích ghi log `log_ai_call` để lưu vết an toàn.
- Chạy kiểm thử tự động kiểm tra cú pháp và logic các endpoint.
- **Commit 5:** `feat(ai): helper ghi nhan AI logs vao database`

---

## 🛡️ IV. ĐIỂM CHÚ Ý & RỦI RO
- **Ràng buộc SQLite Transaction**: Cần đảm bảo `db.rollback()` khi xảy ra lỗi trừ kho giữa chừng để không làm mất mát dữ liệu kế toán.
- **Tương thích ngược**: Endpoint `POST /api/v1/phieu-khams/` vẫn phải hỗ trợ cả trường hợp không có đơn thuốc (khám tư vấn không kê đơn).
- **Hợp tác API với Dev 1**: Đảm bảo cấu trúc JSON trả về của API search thuốc và tạo phiếu khám đúng hợp đồng giao diện để Dev 1 tích hợp UI mượt mà.
