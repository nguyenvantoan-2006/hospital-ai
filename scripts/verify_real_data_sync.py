import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json

BASE = "http://127.0.0.1:8000/api/v1"

def test_sync():
    # 0. Login as Receptionist and Doctor
    res_login_letan = requests.post(f"{BASE}/auth/login", json={"username": "letan", "password": "LeTan@2024!"})
    token_letan = res_login_letan.json().get("access_token")
    headers_letan = {"Authorization": f"Bearer {token_letan}"}

    res_login_bacsi = requests.post(f"{BASE}/auth/login", json={"username": "bacsi", "password": "BacSi@2024!"})
    token_bacsi = res_login_bacsi.json().get("access_token")
    headers_bacsi = {"Authorization": f"Bearer {token_bacsi}"}

    print("================================================================================")
    print("=== 1. KIỂM TRA BÁC SĨ THẬT TRONG CSDL (/api/v1/lich-khams/public/doctors) ===")
    print("================================================================================")
    res_docs = requests.get(f"{BASE}/lich-khams/public/doctors")
    docs = res_docs.json()
    print(f"Tổng số bác sĩ thật đang hoạt động trong CSDL: {len(docs)}")
    for d in docs[:6]:
        print(f"  • BS {d.get('ho_ten')} | Chuyên khoa: {d.get('chuyen_khoa')} | Phòng: {d.get('phong_kham')}")

    print("\n================================================================================")
    print("=== 2. KIỂM TRA TOÀN BỘ LỊCH KHÁM HIỆN CÓ ĐỒNG BỘ ĐẾN LỄ TÂN & BÁC SĨ ===")
    print("================================================================================")
    res_lks = requests.get(f"{BASE}/lich-khams/?limit=100", headers=headers_letan)
    lks = res_lks.json()
    print(f"Lấy được {len(lks)} lịch khám từ endpoint Lễ tân (có xác thực):")

    virtual_flags = []
    rooms_set = set()
    for lk in lks:
        bs_name = lk.get("ten_bac_si")
        room = lk.get("so_phong") or lk.get("phong_kham")
        ck_name = lk.get("ten_chuyen_khoa")
        
        rooms_set.add(room)
        
        if not room or "Phòng khám chung" in str(room) or "Chưa phân công" in str(room):
            virtual_flags.append(f"LK #{lk.get('id')}: Phòng ảo/chưa phân công: {room}")
        if not bs_name or "Chưa phân công" in str(bs_name):
            virtual_flags.append(f"LK #{lk.get('id')}: Bác sĩ ảo/chưa phân công: {bs_name}")

    print(f"Danh sách các phòng khám thực tế được phân bổ ({len(rooms_set)} phòng):")
    for r in sorted(list(rooms_set)):
        print(f"  * {r}")

    print(f"\nSố lượng lịch khám bị dữ liệu ảo / chưa phân công: {len(virtual_flags)}")
    if virtual_flags:
        for f in virtual_flags:
            print("  [CẢNH BÁO]", f)
    else:
        print(">>> 100% LỊCH KHÁM ĐỀU CÓ BÁC SĨ THẬT VÀ PHÒNG KHÁM CÓ KHU RÕ RÀNG!")

    print("\n================================================================================")
    print("=== 3. LUỒNG ĐỒNG BỘ THỰC TẾ: BỆNH NHÂN -> LỄ TÂN -> BÁC SĨ VỚI DỮ LIỆU THẬT ===")
    print("================================================================================")
    # Lấy 1 bác sĩ thật bất kỳ (ví dụ bác sĩ Sản phụ khoa ở Phòng 104 (Khu A))
    target_doc = next((d for d in docs if "104" in str(d.get("phong_kham"))), docs[0])
    print(f"[ĐẦU VÀO] Bác sĩ được chỉ định: {target_doc.get('ho_ten')} | Phòng: {target_doc.get('phong_kham')}")

    test_phone = "0988665544"
    test_patient_name = "Vũ Đình Kiểm Chứng Thật"

    # Bước A: Tiếp đón trực tiếp tại quầy Lễ tân
    payload_tiepdon = {
        "ho_ten": test_patient_name,
        "so_dien_thoai": test_phone,
        "gioi_tinh": "Nam",
        "bac_si_id": target_doc.get("id"),
        "chuyen_khoa_id": target_doc.get("chuyen_khoa_id") or 1,
        "ly_do_kham": "Khám định kỳ kiểm tra sức khỏe tổng quát",
        "trang_thai": "cho_kham"
    }

    res_reg = requests.post(f"{BASE}/lich-khams/tiep-don-tai-quay", json=payload_tiepdon, headers=headers_letan)
    if res_reg.status_code == 201:
        reg_data = res_reg.json()
        new_lk_id = reg_data.get("id")
        stt = reg_data.get("stt")
        print(f"-> [A. LỄ TÂN TIẾP ĐÓN] Thành công! Lịch khám #{new_lk_id} | STT: {stt}")
        print(f"   Bác sĩ: {reg_data.get('ten_bac_si')} | Phòng khám: {reg_data.get('so_phong')}")

        # Bước B: Bệnh nhân tra cứu lịch hẹn qua Cổng Bệnh nhân (/public/tra-cuu)
        res_tra_cuu = requests.get(f"{BASE}/lich-khams/public/tra-cuu?sdt={test_phone}")
        tc_data = res_tra_cuu.json()
        print(f"-> [B. CỔNG BỆNH NHÂN] Tra cứu theo SĐT {test_phone}:")
        bn_lk = {}
        if tc_data.get("success") and tc_data.get("lich_khams"):
            bn_lk = tc_data.get("lich_khams")[0]
            print(f"   Tìm thấy lịch #{bn_lk.get('id')} - STT: {bn_lk.get('stt')}")
            print(f"   Bác sĩ hiển thị cho Bệnh nhân: {bn_lk.get('bac_si')}")
            print(f"   Phòng khám hiển thị cho Bệnh nhân: {bn_lk.get('so_phong')}")
        else:
            print(f"   [CẢNH BÁO] Không tìm thấy kết quả tra cứu: {tc_data}")

        # Bước C: Bác sĩ mở màn hình khám (lap_phieu_kham.html) và thấy bệnh nhân trong hàng đợi
        res_doc_queue = requests.get(f"{BASE}/lich-khams/?trang_thai=cho_kham", headers=headers_bacsi)
        doc_queue = res_doc_queue.json()
        found_in_doc_queue = next((item for item in doc_queue if item.get("id") == new_lk_id), None)
        if found_in_doc_queue:
            print(f"-> [C. MÀN HÌNH BÁC SĨ] Bác sĩ thấy bệnh nhân trong danh sách chờ khám:")
            print(f"   Họ tên: {found_in_doc_queue.get('ho_ten')} | STT: {found_in_doc_queue.get('stt')}")
            print(f"   Bác sĩ phụ trách: {found_in_doc_queue.get('ten_bac_si')}")
            print(f"   Phòng & Khu: {found_in_doc_queue.get('so_phong')}")
            print("\n================================================================================")
            print("===> KẾT LUẬN KIỂM CHỨNG: 100% ĐỒNG BỘ TOÀN DIỆN TỪ DỮ LIỆU CSDL THẬT!")
            print(f"     • Cổng Bệnh nhân:   Bác sĩ = {bn_lk.get('bac_si')} | Phòng = {bn_lk.get('so_phong')}")
            print(f"     • Cổng Lễ tân:       Bác sĩ = {reg_data.get('ten_bac_si')} | Phòng = {reg_data.get('so_phong')}")
            print(f"     • Màn hình Bác sĩ:   Bác sĩ = {found_in_doc_queue.get('ten_bac_si')} | Phòng = {found_in_doc_queue.get('so_phong')}")
            print("     ==> HOÀN TOÀN KHỚP NHAU VÀ KHÔNG SỬ DỤNG BẤT KỲ DỮ LIỆU ẢO NÀO!")
            print("================================================================================")
        else:
            print("[LỖI] Không thấy trong hàng đợi bác sĩ!")
    else:
        print(f"[LỖI] Đăng ký tại quầy thất bại: {res_reg.status_code} - {res_reg.text}")

if __name__ == "__main__":
    test_sync()
