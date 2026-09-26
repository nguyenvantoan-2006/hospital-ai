# test_gmail_smtp.py
"""
Script kiểm tra kết nối và gửi thử email thật qua Gmail SMTP.
Cách dùng:
  python test_gmail_smtp.py [email_nhan_thu]
"""

import sys
import os

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from email_service import get_smtp_config, send_booking_otp_email, send_booking_confirmation_email

def test_smtp():
    server, port, user, pwd, sender = get_smtp_config()
    print("=" * 65)
    print("📧 KIỂM TRA CẤU HÌNH GMAIL SMTP THỰC TẾ")
    print("=" * 65)
    print(f"• Máy chủ SMTP   : {server}:{port}")
    print(f"• Tên người gửi  : {sender}")
    print(f"• Tài khoản gửi  : {user if user else '[CHƯA ĐIỀN TRONG .ENV]'}")
    print(f"• Mật khẩu App   : {'*' * len(pwd) if pwd else '[CHƯA ĐIỀN TRONG .ENV]'}")
    print("-" * 65)

    if not user or not pwd:
        print("⚠️ CHƯA ĐỦ THÔNG TIN CẤU HÌNH!")
        print("👉 Vui lòng mở file .env và điền:")
        print("   GMAIL_USER=email_cua_ban@gmail.com")
        print("   GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx")
        return False

    recipient = sys.argv[1] if len(sys.argv) > 1 else user
    print(f"🚀 Đang gửi thử Email xác thực OTP đến: {recipient} ...")

    sample_booking = {
        "chuyen_khoa": "Tim Mạch",
        "bac_si": "PGS.TS. BS. Nguyễn Văn A",
        "thoi_gian": "2026-09-25 08:30",
        "ly_do_kham": "Khám định kỳ sức khỏe tim mạch"
    }

    ok, msg = send_booking_otp_email(
        clean_email=recipient,
        ho_ten="Nguyễn Văn Toàn",
        otp_code="889966",
        booking_details=sample_booking
    )

    if ok:
        print("🎉 GỬI EMAIL THÀNH CÔNG! Vui lòng kiểm tra Hộp thư đến (hoặc thư mục Spam).")
        return True
    else:
        print(f"❌ GỬI EMAIL THẤT BẠI: {msg}")
        return False

if __name__ == "__main__":
    test_smtp()
