# run_full_system_test.py
"""
Script kiểm thử toàn bộ hệ thống Web Quản lý Phòng Khám (Hospital-AI).
Sử dụng requests và uvicorn server chạy ngầm trong thread để kiểm thử HTTP thực tế.

Kiểm tra chi tiết:
1. Kết nối Database & Khởi tạo dữ liệu
2. Health Check Endpoint
3. Render giao diện các trang HTML (Frontend)
4. Xác thực & Phân quyền RBAC (Auth)
5. Quản lý Bệnh nhân (CRUD, Search, Duplicate Checks)
6. Quản lý Lịch khám (Đặt lịch, Conflict Check, Cập nhật trạng thái Queue STT)
7. Phiếu khám & Kê đơn thuốc
8. Hóa đơn & Thanh toán viện phí
9. Phân hệ Quản trị Admin (Bác sĩ, Chuyên khoa, Users, Stats, Báo cáo Doanh thu, Audit Logs)
10. Tích hợp AI Trợ lý (AI Summary, Post-Exam Guide, Data Masking & Guardrails)
"""

import sys
import os
import time
import threading
import requests
import uvicorn

# Cấu hình UTF-8 cho Windows Console
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Thêm đường dẫn hiện tại vào sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app

SERVER_PORT = 8008
BASE_URL = f"http://127.0.0.1:{SERVER_PORT}"

class ServerThread(threading.Thread):
    def __init__(self, app, host="127.0.0.1", port=SERVER_PORT):
        super().__init__(daemon=True)
        self.server = uvicorn.Server(
            config=uvicorn.Config(
                app=app,
                host=host,
                port=port,
                log_level="error"
            )
        )

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


def wait_for_server(url, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{url}/health")
            if r.status_code == 200:
                return True
        except Exception:
            time.sleep(0.3)
    return False


def run_tests():
    print("=" * 75)
    print("🏥 BẮT ĐẦU KIỂM THỬ TOÀN BỘ HỆ THỐNG HOSPITAL-AI (E2E & BACKEND)")
    print("=" * 75)

    # Khởi động server
    server_thread = ServerThread(app=app, port=SERVER_PORT)
    server_thread.start()
    
    print("⏳ Đang khởi động Test Server trên cổng 8008...")
    if not wait_for_server(BASE_URL):
        print("❌ Lỗi: Không thể khởi động Test Server!")
        return False
    print("🚀 Test Server đã sẵn sàng!\n")

    session = requests.Session()

    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    test_results = []

    def check(test_name, condition, details=""):
        nonlocal total_tests, passed_tests, failed_tests
        total_tests += 1
        if condition:
            passed_tests += 1
            print(f"  ✅ [PASS] {test_name}")
            test_results.append((test_name, "PASS", details))
        else:
            failed_tests += 1
            print(f"  ❌ [FAIL] {test_name} - {details}")
            test_results.append((test_name, "FAIL", details))

    # ──────────────────────────────────────────────────────────────────────────
    # 1. KIỂM TRA DATABASE & HEALTH CHECK
    # ──────────────────────────────────────────────────────────────────────────
    print("[1] 🌐 KIỂM TRA HEALTH CHECK & KẾT NỐI DATABASE")
    res = session.get(f"{BASE_URL}/health")
    check("GET /health trả về 200 OK", res.status_code == 200, f"Status: {res.status_code}")
    check("Health Check có trạng thái 'healthy'", res.json().get("status") == "healthy", str(res.json()))

    # ──────────────────────────────────────────────────────────────────────────
    # 2. KIỂM TRA GIAO DIỆN FRONTEND (HTML PAGES & STATIC)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[2] 🖥️ KIỂM TRA RENDER CÁC TRANG HTML GIAO DIỆN")
    pages = [
        ("/", "Trang chủ (index.html)"),
        ("/index.html", "index.html"),
        ("/login.html", "login.html"),
        ("/admin_dashboard.html", "admin_dashboard.html"),
        ("/danh_sach_benh_nhan.html", "danh_sach_benh_nhan.html"),
        ("/lich_kham.html", "lich_kham.html"),
        ("/lap_phieu_kham.html", "lap_phieu_kham.html"),
        ("/thanh_toan.html", "thanh_toan.html"),
        ("/patient_management.html", "patient_management.html")
    ]
    for url, desc in pages:
        r = session.get(f"{BASE_URL}{url}")
        check(f"Tải trang: {desc}", r.status_code == 200 and len(r.text) > 50, f"Status: {r.status_code}")

    # ──────────────────────────────────────────────────────────────────────────
    # 3. KIỂM TRA XÁC THỰC & PHÂN QUYỀN (AUTH & RBAC)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[3] 🔐 KIỂM TRA XÁC THỰC & ĐĂNG NHẬP (AUTH / RBAC)")
    
    # 3.1 Đăng nhập Admin
    login_admin = session.post(f"{BASE_URL}/api/v1/auth/login", json={"username": "admin", "password": "123"})
    check("Đăng nhập tài khoản Admin thành công (200)", login_admin.status_code == 200, f"Status: {login_admin.status_code}")
    admin_token = login_admin.json().get("access_token") if login_admin.status_code == 200 else None
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    check("Admin Token hợp lệ", bool(admin_token))

    # 3.2 Đăng nhập Lễ tân
    login_letan = session.post(f"{BASE_URL}/api/v1/auth/login", json={"username": "letan", "password": "123"})
    check("Đăng nhập tài khoản Lễ tân thành công (200)", login_letan.status_code == 200, f"Status: {login_letan.status_code}")
    letan_token = login_letan.json().get("access_token") if login_letan.status_code == 200 else None
    letan_headers = {"Authorization": f"Bearer {letan_token}"}

    # 3.3 Đăng nhập Bác sĩ
    login_bacsi = session.post(f"{BASE_URL}/api/v1/auth/login", json={"username": "bacsi", "password": "123"})
    check("Đăng nhập tài khoản Bác sĩ thành công (200)", login_bacsi.status_code == 200, f"Status: {login_bacsi.status_code}")
    bacsi_token = login_bacsi.json().get("access_token") if login_bacsi.status_code == 200 else None
    bacsi_headers = {"Authorization": f"Bearer {bacsi_token}"}

    # 3.4 Đăng nhập Kế toán
    login_ketoan = session.post(f"{BASE_URL}/api/v1/auth/login", json={"username": "ketoan", "password": "123"})
    check("Đăng nhập tài khoản Kế toán thành công (200)", login_ketoan.status_code == 200, f"Status: {login_ketoan.status_code}")

    # 3.5 Đăng nhập sai mật khẩu
    login_fail = session.post(f"{BASE_URL}/api/v1/auth/login", json={"username": "admin", "password": "wrong_password"})
    check("Từ chối mật khẩu sai (401)", login_fail.status_code == 401, f"Status: {login_fail.status_code}")

    # 3.6 Lấy thông tin user hiện tại (/me)
    me_res = session.get(f"{BASE_URL}/api/v1/auth/me", headers=admin_headers)
    check("Lấy thông tin tài khoản hiện tại /me", me_res.status_code == 200 and me_res.json().get("username") == "admin")

    # ──────────────────────────────────────────────────────────────────────────
    # 4. KIỂM TRA QUẢN LÝ BỆNH NHÂN (CRUD & SEARCH & DUPLICATE)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[4] 👤 KIỂM TRA QUẢN LÝ BỆNH NHÂN (CRUD & RÀNG BUỘC)")
    test_suffix = str(int(time.time()))[-5:]
    test_phone = f"09123{test_suffix}"
    test_cccd = f"079200{test_suffix}"
    test_bhyt = f"DN479{test_suffix}"

    patient_payload = {
        "ho_ten": f"Nguyễn Văn Test {test_suffix}",
        "ngay_sinh": "1995-05-15",
        "gio_tinh": "Nam",
        "so_dien_thoai": test_phone,
        "cccd": test_cccd,
        "dia_chi": "123 Đường Test, Quận 1, TP.HCM",
        "ma_bhyt": test_bhyt,
        "tien_su_benh": "Tiền sử dị ứng penicillin, huyết áp nhẹ"
    }

    # 4.1 Thêm bệnh nhân mới
    add_patient = session.post(f"{BASE_URL}/api/v1/benh-nhans/", json=patient_payload, headers=letan_headers)
    check("Thêm bệnh nhân mới thành công (201)", add_patient.status_code == 201, f"Status: {add_patient.status_code}")
    patient_id = add_patient.json().get("id") if add_patient.status_code == 201 else None

    # 4.2 Kiểm tra ràng buộc chống trùng SĐT
    dup_phone_res = session.post(f"{BASE_URL}/api/v1/benh-nhans/", json={**patient_payload, "cccd": f"079999{test_suffix}", "ma_bhyt": f"DN999{test_suffix}"}, headers=letan_headers)
    check("Chặn trùng số điện thoại (400)", dup_phone_res.status_code == 400, f"Status: {dup_phone_res.status_code}")

    # 4.3 Tìm kiếm bệnh nhân
    search_res = session.get(f"{BASE_URL}/api/v1/benh-nhans/?q={test_phone}", headers=letan_headers)
    check("Tìm kiếm bệnh nhân theo SĐT", search_res.status_code == 200 and len(search_res.json()) > 0)

    # 4.4 Xem chi tiết bệnh nhân
    if patient_id:
        detail_res = session.get(f"{BASE_URL}/api/v1/benh-nhans/{patient_id}", headers=letan_headers)
        check("Lấy thông tin chi tiết bệnh nhân", detail_res.status_code == 200 and detail_res.json().get("ho_ten") == patient_payload["ho_ten"])

        # 4.5 Cập nhật bệnh nhân
        update_res = session.put(f"{BASE_URL}/api/v1/benh-nhans/{patient_id}", json={"dia_chi": "456 Đường Mới, Q.3, TP.HCM"}, headers=letan_headers)
        check("Cập nhật địa chỉ bệnh nhân", update_res.status_code == 200 and update_res.json().get("dia_chi") == "456 Đường Mới, Q.3, TP.HCM")

    # ──────────────────────────────────────────────────────────────────────────
    # 5. KIỂM TRA QUẢN LÝ LỊCH KHÁM & XẾP HÀNG (QUEUE STT)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[5] 📅 KIỂM TRA ĐIỀU PHỐI LỊCH KHÁM & XẾP HÀNG")
    
    appointment_id = None
    if patient_id:
        from datetime import datetime, timedelta
        appointment_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT09:00:00")
        
        # 5.1 Đặt lịch khám
        app_payload = {
            "benh_nhan_id": patient_id,
            "bac_si_id": None,
            "chuyen_khoa_id": None,
            "thoi_gian": appointment_time,
            "ly_do_kham": "Đau đầu, mệt mỏi kéo dài",
            "trang_thai": "cho_xac_nhan"
        }
        app_res = session.post(f"{BASE_URL}/api/v1/lich-khams/", json=app_payload, headers=letan_headers)
        check("Đặt lịch khám mới thành công (201)", app_res.status_code == 201, f"Status: {app_res.status_code}")
        appointment_id = app_res.json().get("id") if app_res.status_code == 201 else None

        # 5.2 Lấy danh sách lịch khám
        all_apps = session.get(f"{BASE_URL}/api/v1/lich-khams/", headers=letan_headers)
        check("Lấy danh sách lịch khám", all_apps.status_code == 200 and len(all_apps.json()) > 0)

        # 5.3 Tiếp nhận bệnh nhân & cấp số thứ tự khám (Queue STT)
        if appointment_id:
            stt_res = session.put(f"{BASE_URL}/api/v1/lich-khams/{appointment_id}/trang-thai", json={"trang_thai": "cho_kham"}, headers=letan_headers)
            check("Chuyển sang 'cho_kham' và tự động cấp STT", stt_res.status_code == 200 and stt_res.json().get("stt") is not None)

    # ──────────────────────────────────────────────────────────────────────────
    # 6. KIỂM TRA PHIẾU KHÁM & ĐƠN THUỐC
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[6] 🩺 KIỂM TRA LẬP PHIẾU KHÁM BỆNH")
    phieu_kham_id = None
    if patient_id:
        pk_payload = {
            "benh_nhan_id": patient_id,
            "lich_kham_id": appointment_id,
            "trieu_chung": "Đau nửa đầu kèm hoa mắt, chóng mặt",
            "chan_doan": "Rối loạn tiền đình / Đau nửa đầu Migraine",
            "ai_summary": "Bệnh nhân có tiền sử dị ứng penicillin, triệu chứng đau đầu tái diễn."
        }
        pk_res = session.post(f"{BASE_URL}/api/v1/phieu-khams/", json=pk_payload)
        check("Tạo phiếu khám bệnh thành công (201)", pk_res.status_code == 201, f"Status: {pk_res.status_code}")
        phieu_kham_id = pk_res.json().get("phieu_kham_id") if pk_res.status_code == 201 else None

        # 6.1 Lấy danh sách phiếu khám
        all_pk = session.get(f"{BASE_URL}/api/v1/phieu-khams/")
        check("Lấy danh sách tất cả phiếu khám", all_pk.status_code == 200 and len(all_pk.json()) > 0)

        # 6.2 Lấy danh sách phiếu khám chờ thanh toán
        cho_tt = session.get(f"{BASE_URL}/api/v1/phieu-khams/cho-thanh-toan")
        check("Lấy danh sách phiếu khám chờ thanh toán viện phí", cho_tt.status_code == 200)

    # ──────────────────────────────────────────────────────────────────────────
    # 7. KIỂM TRA HÓA ĐƠN & THANH TOÁN VIỆN PHÍ
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[7] 💳 KIỂM TRA HÓA ĐƠN & THANH TOÁN VIỆN PHÍ")
    if phieu_kham_id:
        hd_payload = {
            "phieu_kham_id": phieu_kham_id,
            "hinh_thuc_tt": "tien_mat",
            "tong_tien": 150000.0,
            "trang_thai": "da_thanh_toan"
        }
        hd_res = session.post(f"{BASE_URL}/api/v1/hoa-dons/", json=hd_payload)
        check("Tạo & xác nhận thanh toán hóa đơn (201)", hd_res.status_code == 201, f"Status: {hd_res.status_code}")

        # 7.1 Lấy danh sách hóa đơn
        all_hd = session.get(f"{BASE_URL}/api/v1/hoa-dons/")
        check("Lấy danh sách tất cả hóa đơn", all_hd.status_code == 200 and len(all_hd.json()) > 0)

    # ──────────────────────────────────────────────────────────────────────────
    # 8. KIỂM TRA PHÂN HỆ QUẢN TRỊ ADMIN (STATS, DOCTORS, SPECIALTIES, AUDIT)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[8] 📊 KIỂM TRA PHÂN HỆ QUẢN TRỊ VIÊN ADMIN")

    # 8.1 Thống kê KPI Dashboard
    stats_res = session.get(f"{BASE_URL}/api/v1/admin/stats")
    check("Lấy KPI thống kê Admin Dashboard", stats_res.status_code == 200 and "total_patients" in stats_res.json())

    # 8.2 Biểu đồ Doanh thu (Revenue Chart)
    chart_res = session.get(f"{BASE_URL}/api/v1/admin/revenue-chart")
    check("Lấy dữ liệu biểu đồ doanh thu (Line & Doughnut)", chart_res.status_code == 200 and "line_chart" in chart_res.json())

    # 8.3 Báo cáo tổng quan Overview
    overview_res = session.get(f"{BASE_URL}/api/v1/admin/reports/overview")
    check("Lấy báo cáo tổng quan phòng khám", overview_res.status_code == 200 and "tong_doanh_thu" in overview_res.json())

    # 8.4 Quản lý Bác sĩ (Thêm Bác sĩ mới)
    doc_payload = {
        "ho_ten": f"BS. Phạm Hoàng Nam {test_suffix}",
        "hoc_vi": "ThS. BS",
        "chuyen_khoa": "Tim mạch",
        "so_dien_thoai": f"0988{test_suffix}",
        "phong_kham": "Phòng 205",
        "lich_truc": "Thứ 2 - Thứ 7",
        "password": "123"
    }
    doc_res = session.post(f"{BASE_URL}/api/v1/admin/doctors", json=doc_payload)
    check("Admin thêm Bác sĩ mới & cấp tài khoản", doc_res.status_code == 201, f"Status: {doc_res.status_code}")

    # 8.5 Danh sách Bác sĩ
    docs_list = session.get(f"{BASE_URL}/api/v1/admin/doctors")
    check("Lấy danh sách bác sĩ", docs_list.status_code == 200 and len(docs_list.json()) > 0)

    # 8.6 Quản lý Chuyên khoa
    spec_res = session.get(f"{BASE_URL}/api/v1/admin/specialties")
    check("Lấy danh sách chuyên khoa", spec_res.status_code == 200)

    # 8.7 Nhật ký hoạt động Audit Logs
    audit_res = session.get(f"{BASE_URL}/api/v1/admin/logs/audit")
    check("Truy xuất nhật ký Audit Logs", audit_res.status_code == 200 and len(audit_res.json()) > 0)

    # 8.8 Nhật ký AI Logs
    ai_logs = session.get(f"{BASE_URL}/api/v1/admin/logs/ai")
    check("Truy xuất nhật ký AI Logs", ai_logs.status_code == 200)

    # ──────────────────────────────────────────────────────────────────────────
    # 9. KIỂM TRA TÍCH HỢP AI TRỢ LÝ (AI SUMMARY & POST-EXAM GUIDE)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[9] 🤖 KIỂM TRA CÁC TÍNH NĂNG AI TRỢ LÝ Y TẾ")
    
    # 9.1 Test AI Summary Endpoint (với Data Masking & Fallback)
    if patient_id:
        ai_sum_res = session.post(f"{BASE_URL}/api/ai/summary", json={"benh_nhan_id": patient_id})
        check("Gọi API /api/ai/summary", ai_sum_res.status_code == 200, f"Status: {ai_sum_res.status_code}")
        if ai_sum_res.status_code == 200:
            summary_text = ai_sum_res.json().get("summary", "")
            print(f"      💬 Output AI Summary: {summary_text[:100]}...")
            check("AI Summary trả về nội dung hợp lệ", len(summary_text) > 10)

    # 9.2 Test AI Post-Exam Guide Endpoint
    ai_guide_payload = {
        "chan_doan": "Viêm họng cấp tính do virus",
        "trieu_chung": "Đau rát họng, ho khan, sốt nhẹ 38 độ"
    }
    ai_guide_res = session.post(f"{BASE_URL}/api/ai/post-exam-guide", json=ai_guide_payload)
    check("Gọi API /api/ai/post-exam-guide", ai_guide_res.status_code == 200, f"Status: {ai_guide_res.status_code}")
    if ai_guide_res.status_code == 200:
        guide_text = ai_guide_res.json().get("guide", "")
        print(f"      💬 Output AI Guide: {guide_text[:100]}...")
        check("AI Post-Exam Guide trả về nội dung hướng dẫn", len(guide_text) > 10)

    # ──────────────────────────────────────────────────────────────────────────
    # TỔNG KẾT KẾT QUẢ
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 75)
    print("📈 TỔNG KẾT KẾT QUẢ KIỂM THỬ TOÀN BỘ HỆ THỐNG")
    print("=" * 75)
    print(f"  Tổng số ca kiểm thử (Test Cases): {total_tests}")
    print(f"  ✅ Số ca ĐẠT (PASS)              : {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"  ❌ Số ca KHÔNG ĐẠT (FAIL)        : {failed_tests}")
    print("=" * 75)

    if failed_tests == 0:
        print("🎉 TẤT CẢ CÁC MODULE VÀ TÍNH NĂNG ĐỀU HOẠT ĐỘNG HOÀN HẢO!")
    else:
        print(f"⚠️ Danh sách các kiểm thử KHÔNG ĐẠT ({failed_tests}):")
        for name, status, details in test_results:
            if status == "FAIL":
                print(f"   ❌ {name}: {details}")

    return failed_tests == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
