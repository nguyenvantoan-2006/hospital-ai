# email_service.py
# Module Dịch Vụ Gửi Email Xác Thực & Thông Báo Qua Gmail SMTP
# Tích hợp cho Đặt Lịch Khám Bệnh Nhân Trực Tuyến (FR-09)
# ════════════════════════════════════════════════════════════════════════════════

import os
import smtplib
import threading
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, Tuple, Optional
from dotenv import load_dotenv

load_dotenv()

# ─── CẤU HÌNH SMTP GMAIL ───────────────────────────────────────────────────────
# Hướng dẫn tạo Gmail App Password:
# 1. Truy cập Google Account -> Security (Bảo mật) -> 2-Step Verification
# 2. Tạo "App Passwords" (Mật khẩu ứng dụng), đặt tên "Hospital-AI"
# 3. Điền vào .env: GMAIL_USER=your_email@gmail.com và GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_SERVER       = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT         = int(os.getenv("SMTP_PORT", 587))
GMAIL_USER        = os.getenv("GMAIL_USER") or os.getenv("MAIL_USERNAME") or ""
GMAIL_APP_PASSWORD= os.getenv("GMAIL_APP_PASSWORD") or os.getenv("MAIL_PASSWORD") or ""
SENDER_NAME       = os.getenv("EMAIL_SENDER_NAME", "CLINOVA Smart Clinic")

# ─── BỘ ĐỆM LƯU MÃ OTP TRONG BỘ NHỚ (In-memory Store) ──────────────────────────
# Cấu trúc: { email: { "otp": "123456", "expires_at": datetime, "data": {...} } }
_otp_lock = threading.Lock()
_otp_store: Dict[str, Dict[str, Any]] = {}


def save_otp(email: str, otp_code: str, booking_details: Dict[str, Any], ttl_minutes: int = 10) -> None:
    """
    Lưu mã OTP và thông tin đặt lịch vào bộ nhớ đệm với thời hạn hết hạn.
    """
    clean_email = email.strip().lower()
    expires_at = datetime.now() + timedelta(minutes=ttl_minutes)
    with _otp_lock:
        _otp_store[clean_email] = {
            "otp": str(otp_code).strip(),
            "expires_at": expires_at,
            "data": booking_details or {}
        }


def verify_stored_otp(clean_email: str, clean_otp: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Xác minh mã OTP của bệnh nhân.
    Trả về: (hợp_lệ: bool, dữ_liệu_lưu: dict, thông_báo_lỗi: str)
    """
    clean_email = clean_email.strip().lower()
    clean_otp = str(clean_otp).strip()

    with _otp_lock:
        record = _otp_store.get(clean_email)
        if not record:
            return False, None, "Mã xác thực OTP không tồn tại hoặc chưa được gửi đến email này."

        if datetime.now() > record["expires_at"]:
            del _otp_store[clean_email]
            return False, None, "Mã OTP đã hết hạn (chỉ có hiệu lực trong 10 phút). Vui lòng yêu cầu gửi lại mã mới!"

        if record["otp"] != clean_otp:
            return False, None, "Mã xác thực OTP không chính xác. Vui lòng kiểm tra lại hộp thư!"

        saved_data = record["data"]
        # Xóa OTP sau khi xác minh thành công để chống replay attack
        del _otp_store[clean_email]
        return True, saved_data, ""


def _send_email_smtp(to_email: str, subject: str, html_body: str) -> Tuple[bool, str]:
    """
    Hàm nội bộ gửi email qua Gmail SMTP.
    Hỗ trợ graceful fallback khi chưa thiết lập GMAIL_USER/PASSWORD.
    """
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print(f"\n[EMAIL SIMULATION] Đến: {to_email} | Tiêu đề: {subject}")
        print("  --> Chưa cấu hình GMAIL_USER hoặc GMAIL_APP_PASSWORD trong .env. Email được mô phỏng thành công!")
        return True, "Chưa cấu hình tài khoản Gmail. Đang chạy chế độ mô phỏng gửi email."

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{SENDER_NAME} <{GMAIL_USER}>"
        msg["To"] = to_email

        html_part = MIMEText(html_body, "html", "utf-8")
        msg.attach(html_part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=12) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD.replace(" ", ""))
            server.sendmail(GMAIL_USER, [to_email], msg.as_string())

        print(f"✅ Đã gửi email thành công tới: {to_email}")
        return True, "Email đã được gửi thành công qua Gmail SMTP."
    except Exception as e:
        err_str = str(e)
        print(f"⚠️ Lỗi khi kết nối Gmail SMTP ({err_str}). Kiểm tra App Password!")
        # Không làm sập luồng đặt lịch, trả về thông báo lỗi chi tiết
        return False, f"Lỗi gửi email qua máy chủ: {err_str}"


def send_booking_otp_email(
    clean_email: str,
    ho_ten: str,
    otp_code: str,
    booking_details: Dict[str, Any]
) -> Tuple[bool, str]:
    """
    Gửi mã OTP xác thực đăng ký lịch khám bệnh qua Gmail.
    """
    chuyen_khoa = booking_details.get("chuyen_khoa", "Đa khoa")
    bac_si = booking_details.get("bac_si", "Bác sĩ phụ trách")
    thoi_gian = booking_details.get("thoi_gian", "Theo lịch hẹn")

    subject = f"[{SENDER_NAME}] Mã Xác Thực Đặt Lịch Khám: {otp_code}"

    html_body = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
      <meta charset="UTF-8">
      <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f1f5f9; margin: 0; padding: 20px; }}
        .container {{ max-width: 580px; margin: auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }}
        .header {{ background: linear-gradient(135deg, #1A73E8 0%, #0d47a1 100%); padding: 32px 24px; text-align: center; color: #ffffff; }}
        .header h1 {{ margin: 0; font-size: 24px; font-weight: 700; letter-spacing: 0.5px; }}
        .content {{ padding: 32px 28px; color: #334155; line-height: 1.6; }}
        .otp-box {{ background: #eff6ff; border: 2px dashed #1A73E8; border-radius: 12px; padding: 20px; text-align: center; margin: 24px 0; }}
        .otp-code {{ font-size: 36px; font-weight: 800; color: #1A73E8; letter-spacing: 8px; margin: 8px 0; }}
        .info-card {{ background: #f8fafc; border-left: 4px solid #1A73E8; padding: 14px 18px; border-radius: 8px; margin: 20px 0; font-size: 14px; }}
        .footer {{ background: #f8fafc; padding: 20px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>🏥 PHÒNG KHÁM ĐA KHOA CLINOVA</h1>
          <p style="margin: 6px 0 0 0; opacity: 0.9; font-size: 14px;">Xác thực thông tin đặt lịch khám trực tuyến</p>
        </div>
        <div class="content">
          <p>Xin chào <strong>{ho_ten}</strong>,</p>
          <p>Bạn đang thực hiện thao tác đăng ký lịch khám bệnh trực tuyến tại hệ thống <strong>CLINOVA Smart Clinic</strong>. Vui lòng sử dụng mã OTP dưới đây để hoàn tất đăng ký:</p>
          
          <div class="otp-box">
            <div style="font-size: 13px; color: #64748b; font-weight: 600; text-transform: uppercase;">MÃ XÁC THỰC CỦA BẠN</div>
            <div class="otp-code">{otp_code}</div>
            <div style="font-size: 12px; color: #dc2626;">⏰ Mã có hiệu lực trong vòng <strong>10 phút</strong>. Tuyệt đối không chia sẻ mã này cho người khác.</div>
          </div>

          <div class="info-card">
            <div style="font-weight: 700; color: #1e293b; margin-bottom: 6px;">📋 Chi tiết lịch hẹn đăng ký:</div>
            <div>• <strong>Chuyên khoa:</strong> {chuyen_khoa}</div>
            <div>• <strong>Bác sĩ:</strong> {bac_si}</div>
            <div>• <strong>Thời gian dự kiến:</strong> {thoi_gian}</div>
          </div>

          <p style="font-size: 13px; color: #64748b;">Nếu bạn không yêu cầu mã này, vui lòng bỏ qua email này.</p>
        </div>
        <div class="footer">
          © 2026 CLINOVA Smart Clinic System — Hotline Hỗ trợ: 1900 8888
        </div>
      </div>
    </body>
    </html>
    """
    return _send_email_smtp(clean_email, subject, html_body)


def send_booking_confirmation_email(
    clean_email: str,
    ho_ten: str,
    confirm_info: Dict[str, Any]
) -> Tuple[bool, str]:
    """
    Gửi email thông báo và biên nhận đặt lịch khám thành công cho bệnh nhân.
    """
    ma_lich = confirm_info.get("ma_lich", "LK0000")
    chuyen_khoa = confirm_info.get("chuyen_khoa", "Đa khoa")
    bac_si = confirm_info.get("bac_si", "Bác sĩ phụ trách")
    phong_kham = confirm_info.get("phong_kham", "Phòng tiếp nhận")
    thoi_gian = confirm_info.get("thoi_gian", "Theo thông báo")

    subject = f"[{SENDER_NAME}] Xác Nhận Đặt Lịch Khám Thành Công — Mã: {ma_lich}"

    html_body = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
      <meta charset="UTF-8">
      <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f1f5f9; margin: 0; padding: 20px; }}
        .container {{ max-width: 580px; margin: auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }}
        .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 32px 24px; text-align: center; color: #ffffff; }}
        .header h1 {{ margin: 0; font-size: 24px; font-weight: 700; }}
        .content {{ padding: 32px 28px; color: #334155; line-height: 1.6; }}
        .ticket {{ background: #f0fdf4; border: 2px solid #86efac; border-radius: 12px; padding: 20px; margin: 20px 0; }}
        .ticket-code {{ font-size: 24px; font-weight: 800; color: #059669; letter-spacing: 2px; text-align: center; margin-bottom: 12px; }}
        .row-item {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px dashed #cbd5e1; font-size: 14px; }}
        .row-item:last-child {{ border-bottom: none; }}
        .footer {{ background: #f8fafc; padding: 20px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>🎉 ĐẶT LỊCH KHÁM THÀNH CÔNG</h1>
          <p style="margin: 6px 0 0 0; opacity: 0.9; font-size: 14px;">Hệ thống Phòng Khám Đa Khoa CLINOVA</p>
        </div>
        <div class="content">
          <p>Kính gửi <strong>{ho_ten}</strong>,</p>
          <p>Yêu cầu đặt lịch khám bệnh trực tuyến của quý khách đã được tiếp nhận và lưu vào hệ thống thành công.</p>
          
          <div class="ticket">
            <div class="ticket-code">MÃ LỊCH HẸN: {ma_lich}</div>
            <div class="row-item"><span>Chuyên khoa:</span><strong>{chuyen_khoa}</strong></div>
            <div class="row-item"><span>Bác sĩ phụ trách:</span><strong>{bac_si}</strong></div>
            <div class="row-item"><span>Địa điểm phòng khám:</span><strong>{phong_kham}</strong></div>
            <div class="row-item"><span>Thời gian khám:</span><strong style="color: #059669;">{thoi_gian}</strong></div>
            <div class="row-item"><span>Trạng thái:</span><span style="color: #d97706; font-weight: 600;">Chờ tiếp nhận tại quầy</span></div>
          </div>

          <p style="font-size: 14px;"><strong>Lưu ý quan trọng:</strong></p>
          <ul style="font-size: 13px; color: #475569; padding-left: 20px;">
            <li>Quý khách vui lòng đến trước giờ hẹn 15 phút tại Quầy Tiếp Đón Lễ Tân để nhận Số Thứ Tự (STT) khám bệnh.</li>
            <li>Xuất trình mã lịch hẹn <strong>{ma_lich}</strong> hoặc số điện thoại đăng ký khi đến quầy.</li>
            <li>Mang theo CCCD và Thẻ BHYT (nếu có) để làm thủ tục nhanh chóng.</li>
          </ul>
        </div>
        <div class="footer">
          © 2026 CLINOVA Smart Clinic — Địa chỉ: 123 Đường Y Tế, TP. Hồ Chí Minh — Hotline: 1900 8888
        </div>
      </div>
    </body>
    </html>
    """
    return _send_email_smtp(clean_email, subject, html_body)
