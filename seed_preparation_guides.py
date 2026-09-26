# seed_preparation_guides.py
# Kịch bản nạp dữ liệu chuẩn bị khám y tế (Ground Truth RAG cho AI Chatbot)
# Lưu trữ các quy định nhịn ăn, giấy tờ cần mang, lưu ý cận lâm sàng chuẩn xác
# ════════════════════════════════════════════════════════════════════════════════

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from database import SessionLocal, engine, Base
import models

PREPARATION_GUIDES_DATA = [
    {
        "ten_dich_vu": "Xét nghiệm máu & Sinh hóa máu",
        "tu_khoa": "máu, xét nghiệm, sinh hóa, đường huyết, tiểu đường, mỡ máu, chức năng gan, thận, gout, axit uric, huyết học",
        "chuyen_khoa_ten": "Xét Nghiệm Y Học",
        "huong_dan_nhin_an": "Cần nhịn ăn hoàn toàn ít nhất 8 - 12 tiếng trước khi lấy mẫu máu. Tuyệt đối không uống nước ngọt, sữa, nước hoa quả, trà hoặc cà phê. Chỉ được uống một lượng nhỏ nước lọc tinh khiết.",
        "giay_to_can_mang": "Căn cước công dân (CCCD), Thẻ BHYT (nếu có), Sổ khám bệnh hoặc kết quả xét nghiệm cũ trong vòng 6 tháng.",
        "luu_y_quan_trong": "Nên đi lấy máu vào buổi sáng (07:30 - 09:30). Không sử dụng rượu bia, thuốc lá hoặc chất kích thích trong 24 giờ trước khi xét nghiệm. Nếu đang dùng thuốc điều trị mạn tính (huyết áp, tim mạch), hãy thông báo cho nhân viên y tế."
    },
    {
        "ten_dich_vu": "Nội soi dạ dày - thực quản - tá tràng",
        "tu_khoa": "nội soi, dạ dày, bao tử, thực quản, tá tràng, ợ chua, trào ngược, đau thượng vị, vi khuẩn hp, xuất huyết tiêu hóa",
        "chuyen_khoa_ten": "Nội Soi Tiêu Hóa Can Thiệp",
        "huong_dan_nhin_an": "Nhịn ăn ít nhất 6 - 8 tiếng trước khi nội soi (tốt nhất là nhịn từ 22h đêm hôm trước nếu khám buổi sáng). Ngừng uống nước trước giờ nội soi ít nhất 2 - 3 tiếng để tránh trào ngược dịch vào phổi khi gây mê/gây tê.",
        "giay_to_can_mang": "CCCD, Thẻ BHYT, Đơn thuốc dạ dày đang uống, Kết quả nội soi trước đó (nếu có).",
        "luu_y_quan_trong": "Nếu lựa chọn nội soi không đau (tiền mê), BẮT BUỘC phải có người nhà đi cùng và không tự lái xe sau khi nội soi. Báo trước cho bác sĩ nếu có tiền sử bệnh tim mạch, hen suyễn, dị ứng thuốc gây mê hoặc đang dùng thuốc chống đông máu."
    },
    {
        "ten_dich_vu": "Nội soi đại tràng trực tràng",
        "tu_khoa": "đại tràng, ruột già, trực tràng, polyp đại tràng, đi ngoài ra máu, táo bón kéo dài, tiêu chảy mạn tính",
        "chuyen_khoa_ten": "Nội Soi Tiêu Hóa Can Thiệp",
        "huong_dan_nhin_an": "Ăn thức ăn nhẹ, ít chất xơ (cháo loãng, canh trong) trước ngày nội soi 1 ngày. Uống thuốc làm sạch ruột (thuốc xổ) theo chỉ dẫn của phòng khám. Nhịn ăn hoàn toàn sáng ngày nội soi.",
        "giay_to_can_mang": "CCCD, Thẻ BHYT, Hồ sơ bệnh án tiêu hóa cũ.",
        "luu_y_quan_trong": "Cần có người thân đi cùng hỗ trợ. Khung thời gian nội soi đại tràng thường mất 2-3 tiếng bao gồm cả thời gian chuẩn bị sạch ruột và theo dõi sau mê."
    },
    {
        "ten_dich_vu": "Siêu âm ổ bụng tổng quát",
        "tu_khoa": "siêu âm, siêu âm bụng, gan, mật, tụy, lách, thận, bàng quang, đau bụng",
        "chuyen_khoa_ten": "Chẩn Đoán Hình Ảnh",
        "huong_dan_nhin_an": "Nên nhịn ăn từ 4 - 6 tiếng trước khi siêu âm để túi mật căng to, giúp quan sát rõ sỏi và tổn thương đường mật.",
        "giay_to_can_mang": "CCCD, Thẻ BHYT, Kết quả siêu âm cũ để so sánh tiến triển kích thước nốt gan/sỏi.",
        "luu_y_quan_trong": "Trước khi siêu âm 30 - 45 phút, cần uống 2 - 3 cốc nước lọc và nhịn tiểu để bàng quang căng đầy, giúp bác sĩ quan sát rõ tử cung, buồng trứng (ở nữ) hoặc tuyến tiền liệt (ở nam)."
    },
    {
        "ten_dich_vu": "Khám Tai Mũi Họng & Nội soi TMH",
        "tu_khoa": "tai mũi họng, viêm xoang, viêm họng, viêm tai giữa, ù tai, nghẹt mũi, khản tiếng, amidan, hóc xương",
        "chuyen_khoa_ten": "Tai Mũi Họng",
        "huong_dan_nhin_an": "Không cần nhịn ăn uống nghiêm ngặt, nhưng nên tránh ăn quá no ngay trước khi nội soi để giảm cảm giác buồn nôn khi đưa que soi vào vòm họng.",
        "giay_to_can_mang": "CCCD, Thẻ BHYT, Đơn thuốc kháng sinh/kháng viêm đang dùng (nếu có).",
        "luu_y_quan_trong": "Không dùng các loại thuốc xịt mũi co mạch hoặc ngậm kẹo cay màu đỏ/xanh trước khi khám vì sẽ làm sai lệch màu sắc niêm mạc xoang họng."
    },
    {
        "ten_dich_vu": "Khám Da Liễu & Thẩm mỹ Da",
        "tu_khoa": "da liễu, mụn trứng cá, mẩn ngứa, phát ban, vảy nến, chàm, dị ứng da, zona, ghẻ, nấm da, sạm nám",
        "chuyen_khoa_ten": "Da Liễu - Thẩm Mỹ Da",
        "huong_dan_nhin_an": "Không cần nhịn ăn uống.",
        "giay_to_can_mang": "CCCD, Thẻ BHYT, Vỏ tuýp thuốc bôi hoặc mỹ phẩm nghi ngờ gây kích ứng.",
        "luu_y_quan_trong": "Tuyệt đối KHÔNG bôi kem trang điểm, kem nền, phấn phủ hoặc các loại thuốc bôi có màu (như thuốc tím, xanh Methylen, kem nghệ) lên vùng da tổn thương trong 24 giờ trước khi khám."
    },
    {
        "ten_dich_vu": "Khám Tim Mạch & Đo điện tim (ECG/Holter)",
        "tu_khoa": "tim mạch, huyết áp, cao huyết áp, đau ngực, khó thở, hồi hộp, tim đập nhanh, thiếu máu cơ tim, van tim",
        "chuyen_khoa_ten": "Tim Mạch",
        "huong_dan_nhin_an": "Không cần nhịn ăn nếu chỉ khám và đo điện tim. Nếu có kết hợp xét nghiệm mỡ máu (Lipid) hoặc đường huyết thì cần nhịn ăn 8-10 tiếng.",
        "giay_to_can_mang": "CCCD, Thẻ BHYT, Toàn bộ đơn thuốc tim mạch / huyết áp đang uống hàng ngày, Sổ theo dõi huyết áp tại nhà.",
        "luu_y_quan_trong": "Vẫn uống thuốc hạ huyết áp buổi sáng bình thường cùng một ngụm nước lọc nhỏ (trừ khi có dặn dò riêng của bác sĩ). Không uống trà đặc, cà phê, nước tăng lực trong ngày khám vì làm tăng nhịp tim."
    },
    {
        "ten_dich_vu": "Khám Sản Phụ Khoa & Tầm soát ung thư cổ tử cung",
        "tu_khoa": "phụ khoa, sản khoa, khám thai, siêu âm thai, rong kinh, viêm âm đạo, pap smear, hpv, tử cung, buồng trứng",
        "chuyen_khoa_ten": "Sản Phụ Khoa",
        "huong_dan_nhin_an": "Không cần nhịn ăn đối với khám thông thường. Khám thai sàng lọc tiểu đường thai kỳ sẽ có hướng dẫn nhịn ăn riêng.",
        "giay_to_can_mang": "CCCD, Thẻ BHYT, Sổ theo dõi thai định kỳ hoặc phiếu kết quả khám phụ khoa gần nhất.",
        "luu_y_quan_trong": "Không quan hệ tình dục, không thụt rửa sâu âm đạo hoặc đặt thuốc phụ khoa trong vòng 48 giờ trước khi làm xét nghiệm Pap smear hoặc xét nghiệm dịch âm đạo. Nên đi khám sau khi sạch kinh nguyệt ít nhất 3 - 5 ngày."
    },
    {
        "ten_dich_vu": "Khám Mắt (Nhãn Khoa)",
        "tu_khoa": "mắt, cận thị, loạn thị, viễn thị, đục thủy tinh thể, cườm khô, cườm nước, glocom, đỏ mắt, mờ mắt, rách giác mạc",
        "chuyen_khoa_ten": "Mắt (Nhãn Khoa)",
        "huong_dan_nhin_an": "Không cần nhịn ăn uống.",
        "giay_to_can_mang": "CCCD, Thẻ BHYT, Kính mắt đang đeo và đơn kính cũ.",
        "luu_y_quan_trong": "Tháo kính áp tròng ít nhất 24 giờ trước khi đo thị lực khúc xạ. Nếu có chỉ định nhỏ thuốc giãn đồng tử để soi đáy mắt, tầm nhìn sẽ mờ tạm thời trong 3-4 tiếng, không nên tự lái xe sau khi khám."
    },
    {
        "ten_dich_vu": "Khám Nhi Khoa (Trẻ sơ sinh và trẻ nhỏ)",
        "tu_khoa": "nhi khoa, trẻ em, sốt, ho, sổ mũi, nôn trớ, biếng ăn, tiêu chảy ở trẻ, viêm tiểu phế quản, phát ban trẻ em",
        "chuyen_khoa_ten": "Nhi Khoa",
        "huong_dan_nhin_an": "Cho trẻ ăn nhẹ hoặc bú trước giờ khám khoảng 1 tiếng, tránh cho ăn quá no ngay trước khi bác sĩ khám họng đề phòng nôn trớ.",
        "giay_to_can_mang": "Giấy khai sinh hoặc thẻ BHYT của trẻ, Sổ tiêm chủng vắc-xin, Đơn thuốc đang uống.",
        "luu_y_quan_trong": "Mang theo đồ chơi quen thuộc, bình nước hoặc sữa của trẻ. Phụ huynh nên ghi chép trước thời điểm trẻ bắt đầu sốt, nhiệt độ cao nhất và các biểu hiện bất thường."
    },
    {
        "ten_dich_vu": "Chụp X-quang & Chụp Cắt lớp vi tính (CT) / MRI",
        "tu_khoa": "x-quang, chụp phim, ct, scanner, mri, cộng hưởng từ, gãy xương, cột sống, sọ não, ngực phổi",
        "chuyen_khoa_ten": "Chẩn Đoán Hình Ảnh",
        "huong_dan_nhin_an": "Chụp X-quang thường quy không cần nhịn ăn. Nếu chụp CT/MRI có tiêm thuốc cản quang, cần nhịn ăn ít nhất 4 - 6 tiếng trước giờ chụp.",
        "giay_to_can_mang": "CCCD, Thẻ BHYT, Các phim chụp và kết quả X-quang/CT cũ để đối chiếu.",
        "luu_y_quan_trong": "Tháo bỏ toàn bộ trang sức kim loại, kẹp tóc, thắt lưng, kính mắt trước khi vào phòng chụp. Phụ nữ trong độ tuổi sinh đẻ BẮT BUỘC thông báo cho bác sĩ nếu đang mang thai hoặc nghi ngờ có thai."
    },
    {
        "ten_dich_vu": "Khám Sức Khỏe Tổng Quát & Tầm soát định kỳ",
        "tu_khoa": "tổng quát, khám sức khỏe, định kỳ, kiểm tra toàn diện, gói khám, tầm soát ung thư",
        "chuyen_khoa_ten": "Kiểm Tra Sức Khỏe Tổng Quát",
        "huong_dan_nhin_an": "Bắt buộc nhịn ăn sáng hoàn toàn (nhịn ăn 8 - 10 tiếng qua đêm). Không uống sữa, nước ngọt, cà phê. Được uống ít nước lọc.",
        "giay_to_can_mang": "CCCD gốc, Thẻ BHYT, Ảnh thẻ 3x4 (nếu khám sức khỏe lái xe / xin việc), Toàn bộ hồ sơ bệnh án cũ.",
        "luu_y_quan_trong": "Mặc trang phục thoải mái, áo ngắn tay hoặc rộng rãi để thuận tiện đo huyết áp, lấy máu và siêu âm. Nên đến vào khung giờ sáng từ 07:30 để hoàn thành gói khám trong buổi sáng."
    }
]

def run_seed(db):
    print("--- [Seed] Bắt đầu nạp Hướng dẫn chuẩn bị khám (RAG Knowledge Base) ---")
    
    # 1. Đảm bảo bảng đã được tạo
    Base.metadata.create_all(bind=engine)

    # 2. Map chuyên khoa theo tên để lấy foreign key chuyen_khoa_id
    specialties_map = {}
    specs = db.query(models.ChuyenKhoa).all()
    for s in specs:
        specialties_map[s.ten_chuyen_khoa.strip().lower()] = s.id

    inserted = 0
    updated = 0

    for item in PREPARATION_GUIDES_DATA:
        # Tìm chuyên khoa tương ứng
        spec_name = item["chuyen_khoa_ten"].strip().lower()
        chuyen_khoa_id = specialties_map.get(spec_name)

        existing = db.query(models.HuongDanChuanBiKham).filter(
            models.HuongDanChuanBiKham.ten_dich_vu == item["ten_dich_vu"]
        ).first()

        if existing:
            existing.tu_khoa_nhan_dien = item["tu_khoa"]
            existing.chuyen_khoa_id = chuyen_khoa_id
            existing.huong_dan_nhin_an = item["huong_dan_nhin_an"]
            existing.giay_to_can_mang = item["giay_to_can_mang"]
            existing.luu_y_quan_trong = item["luu_y_quan_trong"]
            existing.trang_thai = True
            updated += 1
        else:
            new_guide = models.HuongDanChuanBiKham(
                ten_dich_vu=item["ten_dich_vu"],
                tu_khoa_nhan_dien=item["tu_khoa"],
                chuyen_khoa_id=chuyen_khoa_id,
                huong_dan_nhin_an=item["huong_dan_nhin_an"],
                giay_to_can_mang=item["giay_to_can_mang"],
                luu_y_quan_trong=item["luu_y_quan_trong"],
                trang_thai=True
            )
            db.add(new_guide)
            inserted += 1

    db.commit()
    print(f"  ✓ Đã nạp xong: Thêm mới {inserted} mục, Cập nhật {updated} mục hướng dẫn chuẩn bị khám.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()
