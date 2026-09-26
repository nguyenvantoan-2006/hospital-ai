"""
seed_medicines.py — Nạp danh mục Thuốc Tân Dược Chuyên Sâu & Vật Tư Y Tế theo 37 Chuyên Khoa
Dự án: Hospital-AI Management System / Clinova Clinic
"""

import sys
import os
from dotenv import load_dotenv

# Đảm bảo in tiếng Việt trên console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from database import SessionLocal
import models

load_dotenv()

# Danh mục thuốc tân dược và vật tư y tế phân loại theo chuyên khoa
SPECIALTY_MEDICINES = [
    # ─── 1. VẬT TƯ Y TẾ & TIÊU HAO ──────────────────────────────────────────
    {
        "ten_thuoc": "Nước muối sinh lý NaCl 0.9% (Chai 500ml)",
        "don_vi_tinh": "Chai",
        "gia_nhap": 10000.0,
        "don_gia": 18000.0,
        "so_luong_ton": 300
    },
    {
        "ten_thuoc": "Bơm tiêm vô trùng 5ml (Kim tiêm y tế)",
        "don_vi_tinh": "Cái",
        "gia_nhap": 1500.0,
        "don_gia": 3000.0,
        "so_luong_ton": 1000
    },
    {
        "ten_thuoc": "Bơm tiêm vô trùng 10ml",
        "don_vi_tinh": "Cái",
        "gia_nhap": 2000.0,
        "don_gia": 4000.0,
        "so_luong_ton": 800
    },
    {
        "ten_thuoc": "Băng gạc y tế tiệt trùng 10x10cm",
        "don_vi_tinh": "Gói",
        "gia_nhap": 5000.0,
        "don_gia": 9000.0,
        "so_luong_ton": 500
    },
    {
        "ten_thuoc": "Cồn y tế 70 độ sát khuẩn (Chai 500ml)",
        "don_vi_tinh": "Chai",
        "gia_nhap": 15000.0,
        "don_gia": 25000.0,
        "so_luong_ton": 200
    },
    {
        "ten_thuoc": "Dung dịch sát trùng Povidone Iodine 10% (100ml)",
        "don_vi_tinh": "Chai",
        "gia_nhap": 20000.0,
        "don_gia": 32000.0,
        "so_luong_ton": 150
    },
    {
        "ten_thuoc": "Khẩu trang y tế 4 lớp kháng khuẩn N95",
        "don_vi_tinh": "Hộp 20 cái",
        "gia_nhap": 50000.0,
        "don_gia": 85000.0,
        "so_luong_ton": 120
    },
    {
        "ten_thuoc": "Găng tay y tế cao su có bột (Hộp 100 chiếc)",
        "don_vi_tinh": "Hộp",
        "gia_nhap": 65000.0,
        "don_gia": 95000.0,
        "so_luong_ton": 100
    },
    {
        "ten_thuoc": "Dây truyền dịch vô trùng có bầu đếm giọt",
        "don_vi_tinh": "Bộ",
        "gia_nhap": 8000.0,
        "don_gia": 15000.0,
        "so_luong_ton": 250
    },

    # ─── 2. TIM MẠCH & HUYẾT ÁP (Cardiology) ──────────────────────────────────
    {
        "ten_thuoc": "Amlodipine 5mg (Thuốc hạ huyết áp chẹn kênh canxi)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 2500.0,
        "don_gia": 4500.0,
        "so_luong_ton": 500
    },
    {
        "ten_thuoc": "Losartan 50mg (Thuốc huyết áp ức chế thụ thể ARB)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 3000.0,
        "don_gia": 5500.0,
        "so_luong_ton": 400
    },
    {
        "ten_thuoc": "Atorvastatin 20mg (Thuốc hạ mỡ máu Lipitor)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 6000.0,
        "don_gia": 11000.0,
        "so_luong_ton": 350
    },
    {
        "ten_thuoc": "Concor 2.5mg (Bisoprolol điều hòa nhịp tim)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 4000.0,
        "don_gia": 7500.0,
        "so_luong_ton": 300
    },
    {
        "ten_thuoc": "Betaloc ZOK 50mg (Metoprolol succinate)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 5500.0,
        "don_gia": 9500.0,
        "so_luong_ton": 250
    },
    {
        "ten_thuoc": "Aspirin pH8 81mg (Thuốc chống kết tập tiểu cầu ngừa đột quỵ)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 1200.0,
        "don_gia": 2500.0,
        "so_luong_ton": 600
    },
    {
        "ten_thuoc": "Plavix 75mg (Clopidogrel chống đông máu)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 15000.0,
        "don_gia": 24000.0,
        "so_luong_ton": 200
    },

    # ─── 3. HÔ HẤP - PHỔI (Pulmonology) ──────────────────────────────────────
    {
        "ten_thuoc": "Ventolin Inhaler 100mcg (Bình xịt cắt cơn hen suyễn)",
        "don_vi_tinh": "Bình",
        "gia_nhap": 85000.0,
        "don_gia": 125000.0,
        "so_luong_ton": 80
    },
    {
        "ten_thuoc": "Symbicort Turbuhaler 160/4.5mcg (Xịt điều trị hen & COPD)",
        "don_vi_tinh": "Bình",
        "gia_nhap": 280000.0,
        "don_gia": 360000.0,
        "so_luong_ton": 40
    },
    {
        "ten_thuoc": "Acetylcystein 200mg (Thuốc tiêu nhầy, long đờm)",
        "don_vi_tinh": "Gói",
        "gia_nhap": 1800.0,
        "don_gia": 3500.0,
        "so_luong_ton": 600
    },
    {
        "ten_thuoc": "Siro Ho Eugica thảo dược (Chai 100ml)",
        "don_vi_tinh": "Chai",
        "gia_nhap": 25000.0,
        "don_gia": 42000.0,
        "so_luong_ton": 150
    },
    {
        "ten_thuoc": "Bisolvon 8mg (Bromhexine tiêu chất nhầy hô hấp)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 2000.0,
        "don_gia": 3800.0,
        "so_luong_ton": 400
    },
    {
        "ten_thuoc": "Singulair 10mg (Montelukast trị hen dị ứng)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 16000.0,
        "don_gia": 25000.0,
        "so_luong_ton": 180
    },

    # ─── 4. TIÊU HÓA - GAN MẬT (Gastroenterology) ───────────────────────────
    {
        "ten_thuoc": "Nexium Mups 40mg (Esomeprazole trào ngược dạ dày)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 18000.0,
        "don_gia": 28000.0,
        "so_luong_ton": 300
    },
    {
        "ten_thuoc": "Gaviscon Dual Action (Gói hỗn dịch uống trị trào ngược)",
        "don_vi_tinh": "Gói",
        "gia_nhap": 8000.0,
        "don_gia": 14000.0,
        "so_luong_ton": 450
    },
    {
        "ten_thuoc": "Phosphalugel (Gel chữ P bảo vệ niêm mạc dạ dày)",
        "don_vi_tinh": "Gói",
        "gia_nhap": 4500.0,
        "don_gia": 7500.0,
        "so_luong_ton": 500
    },
    {
        "ten_thuoc": "Motilium-M 10mg (Domperidone chống nôn, đầy hơi)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 2200.0,
        "don_gia": 4000.0,
        "so_luong_ton": 350
    },
    {
        "ten_thuoc": "Smecta 3g (Thuốc trị tiêu chảy cấp)",
        "don_vi_tinh": "Gói",
        "gia_nhap": 3200.0,
        "don_gia": 5500.0,
        "so_luong_ton": 400
    },
    {
        "ten_thuoc": "Men vi sinh Enterogermina 2 tỷ bào tử (Ống 5ml)",
        "don_vi_tinh": "Ống",
        "gia_nhap": 7000.0,
        "don_gia": 11500.0,
        "so_luong_ton": 300
    },
    {
        "ten_thuoc": "Boganic Forte (Viên bổ gan, giải độc gan thảo dược)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 1500.0,
        "don_gia": 2800.0,
        "so_luong_ton": 500
    },
    {
        "ten_thuoc": "Hepa-Merz 5g (L-ornithine L-aspartate điều trị gan)",
        "don_vi_tinh": "Gói",
        "gia_nhap": 28000.0,
        "don_gia": 42000.0,
        "so_luong_ton": 120
    },

    # ─── 5. CƠ XƯƠNG KHỚP (Rheumatology & Orthopedics) ───────────────────────
    {
        "ten_thuoc": "Celebrex 200mg (Celecoxib kháng viêm giảm đau khớp)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 18000.0,
        "don_gia": 29000.0,
        "so_luong_ton": 250
    },
    {
        "ten_thuoc": "Arcoxia 90mg (Etoricoxib giảm đau thoái hóa khớp, gout)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 17000.0,
        "don_gia": 27000.0,
        "so_luong_ton": 200
    },
    {
        "ten_thuoc": "Mydocalm 150mg (Tolperisone giãn cơ giảm co thắt)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 3500.0,
        "don_gia": 6000.0,
        "so_luong_ton": 350
    },
    {
        "ten_thuoc": "Glucosamine Sulfat 1500mg (Bổ khớp, tái tạo sụn)",
        "don_vi_tinh": "Gói",
        "gia_nhap": 12000.0,
        "don_gia": 19500.0,
        "so_luong_ton": 200
    },
    {
        "ten_thuoc": "Voltaren Emulgel 50g (Gel bôi xoa bóp giảm đau ngoài da)",
        "don_vi_tinh": "Tuýp",
        "gia_nhap": 65000.0,
        "don_gia": 95000.0,
        "so_luong_ton": 90
    },
    {
        "ten_thuoc": "Medrol 16mg (Methylprednisolone kháng viêm mạnh)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 3800.0,
        "don_gia": 6800.0,
        "so_luong_ton": 280
    },

    # ─── 6. THẦN KINH & TÂM LÝ (Neurology) ──────────────────────────────────
    {
        "ten_thuoc": "Tanakan 40mg (Chiết xuất Ginkgo Biloba bổ não, tuần hoàn)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 4500.0,
        "don_gia": 7800.0,
        "so_luong_ton": 400
    },
    {
        "ten_thuoc": "Nootropil 800mg (Piracetam cải thiện trí nhớ, chóng mặt)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 4000.0,
        "don_gia": 7000.0,
        "so_luong_ton": 350
    },
    {
        "ten_thuoc": "Sibelium 5mg (Flunarizine phòng ngừa đau nửa đầu Migraine)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 5000.0,
        "don_gia": 8500.0,
        "so_luong_ton": 220
    },
    {
        "ten_thuoc": "Magne-B6 Corbiere (Bổ sung Magie và Vitamin B6 giảm căng thẳng)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 1800.0,
        "don_gia": 3200.0,
        "so_luong_ton": 500
    },
    {
        "ten_thuoc": "Rotunda 30mg (Rotundin thảo dược an thần, dễ ngủ)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 1000.0,
        "don_gia": 2000.0,
        "so_luong_ton": 450
    },
    {
        "ten_thuoc": "Citicoline 500mg (Somazina phục hồi chức năng sau tai biến)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 14000.0,
        "don_gia": 23000.0,
        "so_luong_ton": 150
    },

    # ─── 7. TAI MŨI HỌNG (ENT - Otorhinolaryngology) ─────────────────────────
    {
        "ten_thuoc": "Otrivin 0.05% (Dung dịch nhỏ mũi trị nghẹt mũi trẻ em)",
        "don_vi_tinh": "Lọ 10ml",
        "gia_nhap": 32000.0,
        "don_gia": 48000.0,
        "so_luong_ton": 100
    },
    {
        "ten_thuoc": "Otrivin 0.1% (Thuốc xịt mũi co mạch trị viêm xoang, nghẹt mũi)",
        "don_vi_tinh": "Lọ 10ml",
        "gia_nhap": 38000.0,
        "don_gia": 56000.0,
        "so_luong_ton": 120
    },
    {
        "ten_thuoc": "Avamys 27.5mcg (Xịt mũi Fluticasone trị viêm mũi dị ứng)",
        "don_vi_tinh": "Bình 120 liều",
        "gia_nhap": 190000.0,
        "don_gia": 255000.0,
        "so_luong_ton": 60
    },
    {
        "ten_thuoc": "Betadine Gargle 1% (Nước súc họng sát trùng diệt khuẩn 125ml)",
        "don_vi_tinh": "Chai",
        "gia_nhap": 55000.0,
        "don_gia": 79000.0,
        "so_luong_ton": 90
    },
    {
        "ten_thuoc": "Cốm Bạc Hà súc miệng sát khuẩn họng",
        "don_vi_tinh": "Gói",
        "gia_nhap": 3000.0,
        "don_gia": 5000.0,
        "so_luong_ton": 250
    },

    # ─── 8. MẮT / NHÃN KHOA (Ophthalmology) ──────────────────────────────────
    {
        "ten_thuoc": "Tobradex Eye Drops (Thuốc nhỏ mắt kháng sinh Tobramycin + Dexamethasone)",
        "don_vi_tinh": "Lọ 5ml",
        "gia_nhap": 48000.0,
        "don_gia": 68000.0,
        "so_luong_ton": 80
    },
    {
        "ten_thuoc": "Sanlein 0.1% (Thuốc nhỏ mắt Natri Hyaluronate dưỡng ẩm, chống khô mắt)",
        "don_vi_tinh": "Lọ 5ml",
        "gia_nhap": 55000.0,
        "don_gia": 78000.0,
        "so_luong_ton": 110
    },
    {
        "ten_thuoc": "Vismed 0.18% (Nước mắt nhân tạo không chất bảo quản)",
        "don_vi_tinh": "Hộp 20 tép",
        "gia_nhap": 180000.0,
        "don_gia": 240000.0,
        "so_luong_ton": 45
    },
    {
        "ten_thuoc": "Cravit 0.5% (Levofloxacin nhỏ mắt điều trị viêm kết mạc)",
        "don_vi_tinh": "Lọ 5ml",
        "gia_nhap": 75000.0,
        "don_gia": 105000.0,
        "so_luong_ton": 70
    },

    # ─── 9. DA LIỄU & THẨM MỸ DA (Dermatology) ──────────────────────────────
    {
        "ten_thuoc": "Fucidin 2% (Kem bôi kháng sinh Acid Fusidic trị mụn mủ, nhiễm trùng da)",
        "don_vi_tinh": "Tuýp 15g",
        "gia_nhap": 68000.0,
        "don_gia": 96000.0,
        "so_luong_ton": 85
    },
    {
        "ten_thuoc": "Differin Gel 0.1% (Adapalene trị mụn trứng cá viêm)",
        "don_vi_tinh": "Tuýp 30g",
        "gia_nhap": 190000.0,
        "don_gia": 265000.0,
        "so_luong_ton": 50
    },
    {
        "ten_thuoc": "Silkron Cream (Kem 7 màu trị nấm da, hắc lào, lang ben)",
        "don_vi_tinh": "Tuýp 10g",
        "gia_nhap": 18000.0,
        "don_gia": 29000.0,
        "so_luong_ton": 150
    },
    {
        "ten_thuoc": "Bepanthen Balm (Kem bôi mỡ cừu làm dịu da, chống hăm, bỏng nhẹ)",
        "don_vi_tinh": "Tuýp 30g",
        "gia_nhap": 52000.0,
        "don_gia": 75000.0,
        "so_luong_ton": 120
    },
    {
        "ten_thuoc": "Kem bôi Acyclovir 5% (Trị Herpes môi, Zona thần kinh)",
        "don_vi_tinh": "Tuýp 5g",
        "gia_nhap": 15000.0,
        "don_gia": 25000.0,
        "so_luong_ton": 140
    },

    # ─── 10. RĂNG HÀM MẶT (Dentistry & Maxillofacial) ─────────────────────────
    {
        "ten_thuoc": "Rodogyl (Spiramycin + Metronidazole trị nhiễm trùng răng miệng, nha chu)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 8000.0,
        "don_gia": 13500.0,
        "so_luong_ton": 300
    },
    {
        "ten_thuoc": "Nước súc miệng Kin Gingival 0.12% Chlorhexidine trị viêm nướu (250ml)",
        "don_vi_tinh": "Chai",
        "gia_nhap": 95000.0,
        "don_gia": 135000.0,
        "so_luong_ton": 70
    },
    {
        "ten_thuoc": "Kamistad-Gel N (Gel bôi nhiệt miệng, giảm đau nướu răng)",
        "don_vi_tinh": "Tuýp 10g",
        "gia_nhap": 38000.0,
        "don_gia": 58000.0,
        "so_luong_ton": 100
    },

    # ─── 11. NỘI TIẾT & TIỂU ĐƯỜNG (Endocrinology & Diabetology) ──────────────
    {
        "ten_thuoc": "Glucophage 850mg (Metformin điều trị đái tháo đường type 2)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 3500.0,
        "don_gia": 6000.0,
        "so_luong_ton": 400
    },
    {
        "ten_thuoc": "Diamicron MR 60mg (Gliclazide kích thích tiết Insulin)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 5000.0,
        "don_gia": 8500.0,
        "so_luong_ton": 300
    },
    {
        "ten_thuoc": "Forxiga 10mg (Dapagliflozin hạ đường huyết bảo vệ tim thận)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 24000.0,
        "don_gia": 36000.0,
        "so_luong_ton": 150
    },
    {
        "ten_thuoc": "Levothyrox 50mcg (Bổ sung hormone tuyến giáp trị suy giáp)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 1500.0,
        "don_gia": 2800.0,
        "so_luong_ton": 350
    },

    # ─── 12. SẢN PHỤ KHOA & SỨC KHỎE PHỤ NỮ (Obstetrics & Gynecology) ─────────
    {
        "ten_thuoc": "Duphaston 10mg (Dydrogesterone dưỡng thai, điều hòa kinh nguyệt)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 9000.0,
        "don_gia": 15000.0,
        "so_luong_ton": 200
    },
    {
        "ten_thuoc": "Viên đặt âm đạo Polygynax (Trị nấm và viêm phụ khoa)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 12000.0,
        "don_gia": 19000.0,
        "so_luong_ton": 160
    },
    {
        "ten_thuoc": "Viên sắt Ferrovit bổ máu (Acid Folic + Sắt cho mẹ bầu)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 1500.0,
        "don_gia": 2800.0,
        "so_luong_ton": 400
    },
    {
        "ten_thuoc": "Canxi Corbiere 10ml (Bổ sung canxi hữu cơ dạng ống)",
        "don_vi_tinh": "Ống",
        "gia_nhap": 6000.0,
        "don_gia": 9500.0,
        "so_luong_ton": 250
    },

    # ─── 13. NHI KHOA (Pediatrics) ──────────────────────────────────────────
    {
        "ten_thuoc": "Hapacol 150mg (Thuốc hạ sốt giảm đau cho trẻ em 1-3 tuổi)",
        "don_vi_tinh": "Gói",
        "gia_nhap": 1200.0,
        "don_gia": 2200.0,
        "so_luong_ton": 500
    },
    {
        "ten_thuoc": "Hapacol 250mg (Thuốc hạ sốt cho trẻ từ 4-6 tuổi)",
        "don_vi_tinh": "Gói",
        "gia_nhap": 1500.0,
        "don_gia": 2600.0,
        "so_luong_ton": 450
    },
    {
        "ten_thuoc": "Siro Ho Prospan Đức (Trị ho long đờm cho trẻ nhỏ 100ml)",
        "don_vi_tinh": "Chai",
        "gia_nhap": 170000.0,
        "don_gia": 235000.0,
        "so_luong_ton": 60
    },
    {
        "ten_thuoc": "Oresol 245 vị cam (Bù nước và điện giải khi sốt, tiêu chảy)",
        "don_vi_tinh": "Gói",
        "gia_nhap": 2000.0,
        "don_gia": 3800.0,
        "so_luong_ton": 600
    },
    {
        "ten_thuoc": "Kẽm ZinC Biolizin (Bổ sung kẽm kích thích ăn ngon, tiêu hóa)",
        "don_vi_tinh": "Chai 50ml",
        "gia_nhap": 120000.0,
        "don_gia": 175000.0,
        "so_luong_ton": 50
    },

    # ─── 14. THẬN - TIẾT NIỆU & NAM KHOA (Urology & Andrology) ────────────────
    {
        "ten_thuoc": "Duodart 0.5mg/0.4mg (Trị phì đại tiền liệt tuyến lành tính)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 22000.0,
        "don_gia": 33000.0,
        "so_luong_ton": 120
    },
    {
        "ten_thuoc": "Rowatinex (Viên nang mềm hỗ trợ bài sỏi đường tiết niệu, sỏi thận)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 6500.0,
        "don_gia": 10500.0,
        "so_luong_ton": 250
    },
    {
        "ten_thuoc": "Kim Tiền Thảo OPC (Thảo dược bài thạch, thông tiểu)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 600.0,
        "don_gia": 1200.0,
        "so_luong_ton": 800
    },

    # ─── 15. DỊ ỨNG & MIỄN DỊCH (Allergy & Immunology) ───────────────────────
    {
        "ten_thuoc": "Telfast HD 180mg (Fexofenadine thuốc chống dị ứng không gây buồn ngủ)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 9500.0,
        "don_gia": 15000.0,
        "so_luong_ton": 300
    },
    {
        "ten_thuoc": "Zyrtec 10mg (Cetirizine trị dị ứng mày đay, ngứa)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 6000.0,
        "don_gia": 9500.0,
        "so_luong_ton": 350
    },
    {
        "ten_thuoc": "Loratadin 10mg (Thuốc kháng Histamin dị ứng)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 1200.0,
        "don_gia": 2500.0,
        "so_luong_ton": 500
    },

    # ─── 16. KHÁNG SINH PHỔ RỘNG & ĐẶC TRỊ (Antibiotics) ─────────────────────
    {
        "ten_thuoc": "Augmentin 1g (Amoxicillin + Acid Clavulanic kháng sinh phổ rộng)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 14500.0,
        "don_gia": 22000.0,
        "so_luong_ton": 400
    },
    {
        "ten_thuoc": "Klamentin 875/125mg (Kháng sinh điều trị nhiễm khuẩn hô hấp)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 11000.0,
        "don_gia": 17500.0,
        "so_luong_ton": 300
    },
    {
        "ten_thuoc": "Zithromax 500mg (Azithromycin kháng sinh 3 ngày)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 32000.0,
        "don_gia": 48000.0,
        "so_luong_ton": 150
    },
    {
        "ten_thuoc": "Cefuroxim 500mg (Zinnat kháng sinh thế hệ 2)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 16000.0,
        "don_gia": 25000.0,
        "so_luong_ton": 250
    },
    {
        "ten_thuoc": "Ciprofloxacin 500mg (Kháng sinh điều trị tiết niệu, tiêu hóa)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 3500.0,
        "don_gia": 6500.0,
        "so_luong_ton": 350
    },

    # ─── 17. GIẢM ĐAU & HẠ SỐT THÔNG THƯỜNG ──────────────────────────────────
    {
        "ten_thuoc": "Paracetamol 500mg (Hạ sốt, giảm đau nhanh)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 800.0,
        "don_gia": 1500.0,
        "so_luong_ton": 1000
    },
    {
        "ten_thuoc": "Panadol Extra đỏ (Paracetamol + Caffeine giảm đau đầu mạnh)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 1800.0,
        "don_gia": 3000.0,
        "so_luong_ton": 600
    },
    {
        "ten_thuoc": "Efferalgan 500mg viên sủi (Hạ sốt sủi bọt tác dụng nhanh)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 3500.0,
        "don_gia": 5500.0,
        "so_luong_ton": 400
    },
    {
        "ten_thuoc": "Ibuprofen 400mg (Kháng viêm hạ sốt giảm đau)",
        "don_vi_tinh": "Viên",
        "gia_nhap": 1500.0,
        "don_gia": 2800.0,
        "so_luong_ton": 450
    }
]


def _do_seed_medicines(db):
    """Logic seed thuốc nội bộ — dùng chung cho cả seed_medicines() và run_seed(db)."""
    print("=" * 70)
    print("🏥 BẮT ĐẦU NẠP DANH MỤC THUỐC TÂN DƯỢC & VẬT TƯ Y TẾ THEO CHUYÊN KHOA")
    print("=" * 70)

    total_added = 0
    total_updated = 0

    for med_data in SPECIALTY_MEDICINES:
        ten = med_data["ten_thuoc"].strip()
        # Kiểm tra xem thuốc đã tồn tại trong kho chưa (theo tên)
        existing = db.query(models.Thuoc).filter(models.Thuoc.ten_thuoc == ten).first()
        if existing:
            existing.don_vi_tinh = med_data["don_vi_tinh"]
            existing.gia_nhap = med_data["gia_nhap"]
            existing.don_gia = med_data["don_gia"]
            existing.so_luong_ton = med_data["so_luong_ton"]
            total_updated += 1
        else:
            new_thuoc = models.Thuoc(
                ten_thuoc=ten,
                don_vi_tinh=med_data["don_vi_tinh"],
                gia_nhap=med_data["gia_nhap"],
                don_gia=med_data["don_gia"],
                so_luong_ton=med_data["so_luong_ton"]
            )
            db.add(new_thuoc)
            total_added += 1

    db.commit()
    total_in_db = db.query(models.Thuoc).count()

    print(f"✅ Đã thêm mới: {total_added} mặt hàng thuốc chuyên khoa")
    print(f"🔄 Đã cập nhật: {total_updated} mặt hàng thuốc có sẵn")
    print(f"📦 TỔNG SỐ MẶT HÀNG TRONG KHO DƯỢC HIỆN TẠI: {total_in_db} mặt hàng")
    print("=" * 70)
    print("🎉 Nạp dữ liệu thuốc theo chuyên khoa thành công!")


def run_seed(db):
    """
    Wrapper được gọi từ startup.py khi deploy Railway.
    Nhận session DB từ ngoài — KHÔNG tự tạo/đóng session.
    """
    try:
        _do_seed_medicines(db)
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi khi nạp dữ liệu thuốc (run_seed): {e}")
        return False


def seed_medicines():
    """Chạy độc lập bằng: python seed_medicines.py"""
    db = SessionLocal()
    try:
        _do_seed_medicines(db)
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi khi nạp dữ liệu thuốc: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    seed_medicines()
