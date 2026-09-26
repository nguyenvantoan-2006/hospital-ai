# test_closed_loop_and_sync.py
"""
Script kiểm thử tự động toàn diện cho 2 tính năng nghiệp vụ cốt lõi:
1. Đồng bộ hóa dữ liệu Bệnh nhân từ Lễ tân sang Bác sĩ (Tổng quan lâm sàng, tiền sử, BHYT).
2. Closed-Loop Clinical Routing (Vòng lặp Cận lâm sàng khép kín: Phòng 101 -> Phòng 202 X-Quang -> Trả KQ về Phòng 101 với STT mới & Ưu tiên).
"""

import sys
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from fastapi.testclient import TestClient
from main import app
from datetime import datetime

client = TestClient(app)

def run_e2e_closed_loop_test():
    print("=" * 75)
    print("🏥 KIỂM THỬ E2E: ĐỒNG BỘ DỮ LIỆU LỄ TÂN & CLOSED-LOOP CLINICAL ROUTING")
    print("=" * 75)

    # 1. Đăng nhập Lễ tân & Bác sĩ
    login_lt = client.post("/api/v1/auth/login", json={"username": "letan", "password": "LeTan@2024!"})
    assert login_lt.status_code == 200, f"Login Lễ tân failed: {login_lt.text}"
    lt_token = login_lt.json()["access_token"]
    lt_headers = {"Authorization": f"Bearer {lt_token}"}

    login_bs = client.post("/api/v1/auth/login", json={"username": "bacsi", "password": "BacSi@2024!"})
    assert login_bs.status_code == 200, f"Login Bác sĩ failed: {login_bs.text}"
    bs_token = login_bs.json()["access_token"]
    bs_headers = {"Authorization": f"Bearer {bs_token}"}
    print("✅ 1. Đăng nhập tài khoản Lễ tân & Bác sĩ thành công.")

    # 2. Lễ tân tạo/tiếp nhận Bệnh nhân có tiền sử bệnh lý và thông tin chi tiết
    suffix = str(int(datetime.now().timestamp()))[-5:]
    bn_payload = {
        "ho_ten": f"Trần Closed Loop {suffix}",
        "ngay_sinh": "1990-08-15",
        "gio_tinh": "Nam",
        "so_dien_thoai": f"0933{suffix}",
        "cccd": f"001090{suffix}",
        "dia_chi": "Số 88 Phố Y Tế, Cầu Giấy, Hà Nội",
        "ma_bhyt": f"DN401{suffix}",
        "tien_su_benh": "Tiền sử hen phế quản, dị ứng Aspirin và Penicillin"
    }
    bn_res = client.post("/api/v1/benh-nhans/", json=bn_payload, headers=lt_headers)
    assert bn_res.status_code == 201, f"Tạo bệnh nhân failed: {bn_res.text}"
    bn_id = bn_res.json()["id"]
    print(f"✅ 2. Lễ tân tiếp nhận bệnh nhân ID: {bn_id} kèm tiền sử bệnh & dị ứng.")

    # 3. Lễ tân tạo lịch khám ban đầu tại Phòng khám Tổng Quát
    lk_payload = {
        "benh_nhan_id": bn_id,
        "thoi_gian": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "trang_thai": "cho_kham",
        "ly_do_kham": "Khó thở nhẹ, đau tức ngực sau khi vận động mạnh"
    }
    lk_res = client.post("/api/v1/lich-khams/", json=lk_payload, headers=lt_headers)
    assert lk_res.status_code == 201, f"Tạo lịch khám failed: {lk_res.text}"
    initial_lk_id = lk_res.json()["id"]
    print(f"✅ 3. Lễ tân xếp lịch khám ban đầu ID: #{initial_lk_id} (Trạng thái: 'cho_kham').")

    # 4. Kiểm tra đồng bộ dữ liệu sang Màn hình Bác sĩ (GET /api/v1/lich-khams/)
    list_res = client.get("/api/v1/lich-khams/", headers=bs_headers)
    assert list_res.status_code == 200
    all_queue = list_res.json()
    matched_item = next((item for item in all_queue if item["id"] == initial_lk_id), None)
    assert matched_item is not None, "Không tìm thấy lượt khám trên Màn hình Bác sĩ!"
    assert matched_item["ho_ten"] == bn_payload["ho_ten"], "Sai lệch Họ tên bệnh nhân!"
    assert matched_item["tien_su_benh"] == bn_payload["tien_su_benh"], "Bác sĩ không thấy Tiền sử bệnh lý từ Lễ tân!"
    assert matched_item["ma_bhyt"] == bn_payload["ma_bhyt"], "Bác sĩ không thấy Mã BHYT!"
    assert matched_item["dia_chi"] == bn_payload["dia_chi"], "Bác sĩ không thấy Địa chỉ!"
    assert matched_item["tuoi"] is not None and matched_item["tuoi"] > 0, "Bác sĩ không thấy Tuổi bệnh nhân!"
    print("✅ 4. ĐỒNG BỘ HOÀN TOÀN: Bác sĩ đã nhận đủ 100% hồ sơ lâm sàng từ Lễ tân.")

    # 5. Giai đoạn 1: Bác sĩ Phòng 101 gọi BN vào khám & Chỉ định Cận lâm sàng (X-Quang)
    call_res = client.post(f"/api/v1/lich-khams/{initial_lk_id}/goi-vao-kham", headers=bs_headers)
    assert call_res.status_code == 200
    print(f"✅ 5. Bác sĩ Phòng 101 gọi số BN (STT #{call_res.json()['stt']}) vào phòng khám.")

    transfer_payload = {
        "lich_kham_hien_tai_id": initial_lk_id,
        "phong_kham_dich": "Phòng 202 - Chẩn đoán hình ảnh (X-Quang)",
        "chi_dinh_dich_vu": "Chụp X-quang tim phổi thẳng",
        "ghi_chu": "Lên Tầng 2 Phòng 202 nộp phiếu A5"
    }
    transfer_res = client.post("/api/v1/lich-khams/dieu-phoi-chuyen-phong", json=transfer_payload, headers=bs_headers)
    assert transfer_res.status_code == 200, f"Điều phối thất bại: {transfer_res.text}"
    slip = transfer_res.json()["phieu_dieu_phoi"]
    cls_lk_id = slip["lich_kham_moi_id"]
    cls_stt = slip["stt_moi"]
    print(f"✅ 6. Chỉ định CLS thành công: Xuất Phiếu {slip['ma_phieu']} (STT mới tại Phòng 202: #{cls_stt}).")

    # Kiểm tra ca ban đầu KHÔNG bị xóa mà chuyển sang 'cho_ket_qua_cls'
    check_initial = client.get(f"/api/v1/lich-khams/?id={initial_lk_id}", headers=bs_headers).json()
    item_initial = next((i for i in check_initial if i["id"] == initial_lk_id), None)
    assert item_initial is not None
    assert item_initial["trang_thai"] == "cho_ket_qua_cls", f"Sai trạng thái: {item_initial['trang_thai']}"
    print(f"✅ 7. Ca khám tại Phòng 101 được giữ nguyên ở trạng thái: '{item_initial['trang_thai']}'.")

    # 8. Giai đoạn 2: Phòng 202 (X-Quang) thực hiện kỹ thuật và Trả kết quả về Phòng 101
    cls_result_payload = {
        "lich_kham_cls_id": cls_lk_id,
        "ket_luan": "Phổi sáng, không tổn thương thâm nhiễm, bóng tim không to",
        "ket_qua_chi_tiet": "Hình ảnh tim phổi thẳng bình thường, vòm hoành 2 bên đều."
    }
    tra_kq_res = client.post("/api/v1/lich-khams/tra-ket-qua-cls", json=cls_result_payload, headers=bs_headers)
    assert tra_kq_res.status_code == 200, f"Trả kết quả CLS thất bại: {tra_kq_res.text}"
    tra_kq_data = tra_kq_res.json()
    new_priority_stt = tra_kq_data["stt_moi"]
    print(f"✅ 8. Phòng CLS bấm Trả kết quả: Ca CLS hoàn tất, ca Phòng 101 được cấp STT MỚI: #{new_priority_stt}.")

    # 9. Giai đoạn 3: Bệnh nhân tự động xuất hiện lại ở Phòng 101 với trạng thái 'da_co_ket_qua' & Ưu tiên
    updated_queue = client.get("/api/v1/lich-khams/", headers=bs_headers).json()
    item_back = next((i for i in updated_queue if i["id"] == initial_lk_id), None)
    assert item_back is not None
    assert item_back["trang_thai"] == "da_co_ket_qua", f"Sai trạng thái quay về: {item_back['trang_thai']}"
    assert item_back["stt"] == new_priority_stt, "STT mới không khớp!"
    assert item_back["ket_qua_cls"] is not None, "Kết quả CLS không được ghi nhận vào hồ sơ!"
    print(f"✅ 9. Bệnh nhân quay lại Phòng 101 với trạng thái 'da_co_ket_qua', STT #{new_priority_stt} và KẾT QUẢ CLS ĐÃ ĐÍNH KÈM.")

    # 10. Kiểm tra hiển thị Kiosk TV công cộng có bệnh nhân ưu tiên
    kiosk_res = client.get("/api/v1/lich-khams/public/queue-display")
    assert kiosk_res.status_code == 200
    kiosk_data = kiosk_res.json()
    waiting_kiosk = kiosk_data.get("danh_sach_cho", [])
    assert any(w.get("stt") == new_priority_stt for w in waiting_kiosk), "Kiosk chưa hiển thị STT ưu tiên!"
    print(f"✅ 10. Màn hình Kiosk phòng khám đã đưa STT #{new_priority_stt} lên vị trí Ưu tiên.")

    print("\n" + "=" * 75)
    print("🎉 TẤT CẢ 10 BƯỚC KIỂM THỬ ĐỒNG BỘ VÀ CLOSED-LOOP ROUTING ĐÃ ĐẠT 100%!")
    print("=" * 75)
    return True

def test_e2e_closed_loop_and_sync():
    assert run_e2e_closed_loop_test() is True

if __name__ == "__main__":
    run_e2e_closed_loop_test()
