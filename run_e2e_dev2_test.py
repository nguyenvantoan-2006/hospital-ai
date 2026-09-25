import sys
import os
import random

# Đảm bảo in tiếng Việt và Emoji trên Windows Console không bị lỗi charmap
sys.stdout.reconfigure(encoding='utf-8')

from fastapi.testclient import TestClient
from main import app
from database import get_db, SessionLocal
import models

client = TestClient(app)

def run_dev2_e2e_tests():
    print("=" * 75)
    print("🏥 BẮT ĐẦU KIỂM THỬ TÍCH HỢP TOÀN BỘ CHỨC NĂNG CỦA DEV 2 (BACKEND CORE)")
    print("=" * 75)

    db = SessionLocal()
    pass_count = 0
    total_count = 0

    def check(name, condition, extra=""):
        nonlocal pass_count, total_count
        total_count += 1
        if condition:
            pass_count += 1
            print(f"  ✅ [PASS] {name} {extra}")
        else:
            print(f"  ❌ [FAIL] {name} {extra}")

    try:
        # ──────────────────────────────────────────────────────────────────────────
        # 1. TEST CRUD DANH MỤC THUỐC (routers/ke_toan.py)
        # ──────────────────────────────────────────────────────────────────────────
        print("\n[1] 💊 KIỂM TRA QUẢN LÝ DANH MỤC THUỐC & CẢNH BÁO TỒN KHO")
        
        # 1.1 Thêm thuốc mới
        test_med_name = "Kháng sinh Cefixime 200mg"
        # Xóa nếu đã có trước đó để tránh trùng lặp
        old_med = db.query(models.Thuoc).filter(models.Thuoc.ten_thuoc == test_med_name).first()
        if old_med:
            # Xóa các đơn thuốc liên quan nếu có
            db.query(models.DonThuoc).filter(models.DonThuoc.thuoc_id == old_med.id).delete()
            db.delete(old_med)
            db.commit()

        res_create_thuoc = client.post("/api/v1/ke-toan/thuocs", json={
            "ten_thuoc": test_med_name,
            "don_vi_tinh": "Hộp 10 viên",
            "gia_nhap": 45000.0,
            "don_gia": 75000.0,
            "so_luong_ton": 8  # Đặt số lượng < 10 để test cảnh báo tồn kho thấp
        })
        check("Thêm thuốc mới vào danh mục (POST /api/v1/ke-toan/thuocs)", res_create_thuoc.status_code == 201)
        med_data = res_create_thuoc.json()
        med_id = med_data.get("id")

        # 1.2 Cảnh báo tồn kho thấp (< 10)
        res_low_stock = client.get("/api/v1/ke-toan/thuocs/canh-bao-ton-kho?threshold=10")
        check("API Cảnh báo thuốc sắp hết tồn kho (GET /api/v1/ke-toan/thuocs/canh-bao-ton-kho)", res_low_stock.status_code == 200)
        low_stock_list = res_low_stock.json()
        found_in_low = any(m["id"] == med_id for m in low_stock_list)
        check("Thuốc tồn kho 8 nằm trong danh sách cảnh báo (<10)", found_in_low)

        # 1.3 Cập nhật giá & số lượng tồn kho
        res_update_thuoc = client.put(f"/api/v1/ke-toan/thuocs/{med_id}", json={
            "so_luong_ton": 50,
            "don_gia": 80000.0
        })
        check("Cập nhật thông tin thuốc (PUT /api/v1/ke-toan/thuocs/{id})", res_update_thuoc.status_code == 200)
        check("Số lượng tồn kho sau cập nhật là 50", res_update_thuoc.json().get("so_luong_ton") == 50)

        # ──────────────────────────────────────────────────────────────────────────
        # 2. TEST AUTOCOMPLETE SEARCH THUỐC (routers/phieu_khams.py)
        # ──────────────────────────────────────────────────────────────────────────
        print("\n[2] 🔍 KIỂM TRA API TÌM KIẾM THUỐC AUTOCOMPLETE (CHO DEV 1)")
        res_search = client.get(f"/api/v1/phieu-khams/thuocs/search?q=Cefixime")
        check("API Search thuốc (GET /api/v1/phieu-khams/thuocs/search?q=Cefixime)", res_search.status_code == 200)
        search_results = res_search.json()
        check("Kết quả tìm kiếm chứa đúng thuốc vừa tạo", any(m["id"] == med_id for m in search_results))

        # ──────────────────────────────────────────────────────────────────────────
        # 3. TEST KHÁM BỆNH & KÊ ĐƠN THUỐC ĐIỆN TỬ (routers/phieu_khams.py)
        # ──────────────────────────────────────────────────────────────────────────
        print("\n[3] 🩺 KIỂM TRA BÁC SĨ LẬP PHIẾU KHÁM & KÊ ĐƠN THUỐC")
        
        # 3.1 Tạo bệnh nhân test
        random_phone = f"0988{random.randint(100000, 999999)}"
        res_bn = client.post("/api/v1/benh-nhans/", json={
            "ho_ten": "Nguyễn Văn Test Dev2",
            "so_dien_thoai": random_phone,
            "gio_tinh": "Nam",
            "dia_chi": "Hà Nội"
        })
        if res_bn.status_code in [200, 201]:
            bn_id = res_bn.json().get("id")
        else:
            first_bn = db.query(models.BenhNhan).first()
            bn_id = first_bn.id if first_bn else 1

        # 3.2 Test ràng buộc: Chặn kê vượt quá số lượng tồn kho (Hiện có 50 hộp, cố tình kê 100 hộp)
        res_over_prescribe = client.post("/api/v1/phieu-khams/", json={
            "benh_nhan_id": bn_id,
            "trieu_chung": "Viêm tai giữa",
            "chan_doan": "Viêm tai giữa cấp tính",
            "huong_dan_sau_kham": "Nhỏ tai 2 lần/ngày, tránh nước vào tai",
            "don_thuocs": [
                {
                    "thuoc_id": med_id,
                    "so_luong": 100,  # Vượt quá 50
                    "lieu_dung": "Uống 1 hộp/ngày"
                }
            ]
        })
        check("Chặn kê vượt tồn kho (Trả về 400 Bad Request)", res_over_prescribe.status_code == 400, f"Detail: {res_over_prescribe.json().get('detail')}")

        # 3.3 Kê đơn hợp lệ (kê 5 hộp)
        res_valid_prescribe = client.post("/api/v1/phieu-khams/", json={
            "benh_nhan_id": bn_id,
            "trieu_chung": "Viêm họng, sốt nhẹ",
            "chan_doan": "Viêm đường hô hấp trên",
            "ai_summary": "Bệnh nhân có tiền sử dị ứng thời tiết",
            "huong_dan_sau_kham": "Uống nhiều nước ấm, súc họng nước muối sinh lý 3 lần/ngày, tái khám sau 5 ngày.",
            "don_thuocs": [
                {
                    "thuoc_id": med_id,
                    "so_luong": 5,
                    "lieu_dung": "Uống 1 viên/lần, 2 lần/ngày sau ăn"
                }
            ]
        })
        check("Lập phiếu khám & kê đơn thuốc thành công (201 Created)", res_valid_prescribe.status_code == 201)
        pk_data = res_valid_prescribe.json()
        pk_id = pk_data.get("phieu_kham_id")
        check("Lưu lời dặn sau khám (huong_dan_sau_kham)", pk_data.get("huong_dan_sau_kham") is not None)

        # 3.4 Xem chi tiết phiếu khám
        res_pk_detail = client.get(f"/api/v1/phieu-khams/{pk_id}")
        check("Lấy chi tiết phiếu khám kèm đơn thuốc (GET /api/v1/phieu-khams/{id})", res_pk_detail.status_code == 200)
        pk_detail = res_pk_detail.json()
        check("Chi tiết đơn thuốc có đúng 1 loại thuốc kê", len(pk_detail.get("don_thuocs", [])) == 1)

        # ──────────────────────────────────────────────────────────────────────────
        # 4. TEST THANH TOÁN & QUẦY DƯỢC PHÁT THUỐC TRỪ KHO (routers/hoa_dons.py)
        # ──────────────────────────────────────────────────────────────────────────
        print("\n[4] 💳 KIỂM TRA QUẦY THUỐC, PHÁT THUỐC & TRỪ TỒN KHO AN TOÀN")

        # 4.1 Lấy danh sách đơn thuốc chờ phát tại quầy dược
        res_cho_phat = client.get("/api/v1/hoa-dons/don-thuoc-cho-phat")
        check("Lấy danh sách đơn thuốc chờ phát (GET /api/v1/hoa-dons/don-thuoc-cho-phat)", res_cho_phat.status_code == 200)
        list_cho_phat = res_cho_phat.json()
        check("Phiếu khám vừa tạo nằm trong danh sách quầy thuốc", any(p["phieu_kham_id"] == pk_id for p in list_cho_phat))

        # 4.2 Lấy chi tiết đơn thuốc phục vụ in ấn A4/A5
        res_print = client.get(f"/api/v1/hoa-dons/don-thuoc/{pk_id}")
        check("API Chi tiết in đơn thuốc & biên lai (GET /api/v1/hoa-dons/don-thuoc/{id})", res_print.status_code == 200)
        print_data = res_print.json()
        check("Bản in chứa đúng lời dặn sau khám của bác sĩ", "Uống nhiều nước ấm" in print_data.get("huong_dan_sau_kham", ""))

        # 4.3 Quầy thuốc xác nhận phát thuốc -> Kích hoạt ACID Transaction trừ kho
        db.expire_all()
        med_obj = db.query(models.Thuoc).filter(models.Thuoc.id == med_id).first()
        ton_kho_truoc = med_obj.so_luong_ton if med_obj else 50
        
        res_dispense = client.post("/api/v1/hoa-dons/xac-nhan-phat-thuoc", json={
            "phieu_kham_id": pk_id,
            "duoc_si_phat": "Dược sĩ Nguyễn Thị Hà",
            "ghi_chu_phat": "Đã tư vấn cách uống đầy đủ",
            "da_thanh_toan_ngay": True,
            "hinh_thuc_tt": "tien_mat"
        })
        check("Xác nhận phát thuốc & trừ kho (POST /api/v1/hoa-dons/xac-nhan-phat-thuoc)", res_dispense.status_code == 200)
        
        # 4.4 Kiểm tra số lượng tồn kho trong database đã trừ 5 đơn vị (50 - 5 = 45)
        fresh_db = SessionLocal()
        try:
            thuoc_sau = fresh_db.query(models.Thuoc).filter(models.Thuoc.id == med_id).first()
            check(f"Tồn kho thuốc đã tự động trừ từ {ton_kho_truoc} xuống {thuoc_sau.so_luong_ton} (đã trừ đúng 5)", thuoc_sau.so_luong_ton == (ton_kho_truoc - 5))
        finally:
            fresh_db.close()

        # ──────────────────────────────────────────────────────────────────────────
        # 5. TEST BẢNG CSDL AI_LOGS (SEC-AI-04)
        # ──────────────────────────────────────────────────────────────────────────
        print("\n[5] 🤖 KIỂM TRA BẢNG CSDL AI_LOGS (AUDIT VẾT GỌI AI)")
        
        # Thêm 1 bản ghi AI log mẫu
        ai_log = models.AILog(
            user_id=1,
            chuc_nang="ai_post_exam",
            prompt_masked="Triệu chứng: Viêm họng; Chẩn đoán: Viêm đường hô hấp",
            response_text="Uống nhiều nước ấm, nghỉ ngơi 3 ngày.",
            model_name="gemini-1.5-flash",
            response_time_ms=850,
            trang_thai="success"
        )
        db.add(ai_log)
        db.commit()
        db.refresh(ai_log)

        saved_log = db.query(models.AILog).filter(models.AILog.id == ai_log.id).first()
        check("Ghi nhận bản ghi AILog vào CSDL thành công", saved_log is not None)
        check("AILog lưu đúng tên model và thời gian xử lý", saved_log.model_name == "gemini-1.5-flash" and saved_log.response_time_ms == 850)

    finally:
        db.close()

    print("\n" + "=" * 75)
    print(f"📊 KẾT QUẢ KIỂM THỬ: {pass_count}/{total_count} Ca Kiểm Thử ĐẠT ({pass_count/total_count*100:.1f}%)")
    print("=" * 75)

if __name__ == "__main__":
    run_dev2_e2e_tests()
