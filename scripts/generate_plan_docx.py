# scripts/generate_plan_docx.py
# -*- coding: utf-8 -*-
"""
Script tạo file Ke_Hoach_Thuc_Hien_Nhom03_HoanThien.docx đạt chuẩn 10 điểm tuyệt đối
theo Đề cương & Tiêu chí chấm điểm (Rubric) của TS. Nguyễn Đình Dũng (1_Thuc_hanh_AI_Augmented_SDLC.docx).
- Cấu trúc 32 đầu việc chi tiết, sáng rõ, KHÔNG NHỒI NHÉT CHỮ, KHÔNG RỐI MẮT.
- Phân tách rành mạch FRONTEND (FE) và BACKEND (BE) cho CẢ 2 THÀNH VIÊN.
- Có CỘT / DÒNG GHI RÕ GIT COMMIT MESSAGE theo chuẩn Conventional Commits cho từng đầu việc.
- Đầy đủ 11 Skills, Tools & MCP, 5 Human Gates, Artifacts thực tế từ Repository.
"""

import os
import sys
import docx

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def set_cell_background(cell, fill_hex):
    """Đặt màu nền cho ô trong bảng."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
    """Đặt padding cho ô."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def set_table_borders(table, color="D5D8DC", sz="4"):
    """Đặt đường viền thanh lịch cho bảng."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def build_docx(output_path="Ke_Hoach_Thuc_Hien_Nhom03_HoanThien.docx"):
    doc = docx.Document()

    # Thiết lập lề trang A4 Portrait (Trang đứng)
    for section in doc.sections:
        section.top_margin = Cm(1.6)
        section.bottom_margin = Cm(1.6)
        section.left_margin = Cm(1.3)
        section.right_margin = Cm(1.3)
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)

    # ─── TIÊU ĐỀ ĐƠN VỊ ──────────────────────────────────────────────────────────
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_header.paragraph_format.space_before = Pt(0)
    p_header.paragraph_format.space_after = Pt(2)
    run_sch = p_header.add_run("TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG (ICTU)\n")
    run_sch.font.name = "Times New Roman"
    run_sch.font.size = Pt(11)
    run_sch.font.bold = True
    run_sch.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    run_fac = p_header.add_run("KHOA CÔNG NGHỆ THÔNG TIN — BỘ MÔN CÔNG NGHỆ PHẦN MỀM")
    run_fac.font.name = "Times New Roman"
    run_fac.font.size = Pt(10)
    run_fac.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    # ─── TIÊU ĐỀ CHÍNH ───────────────────────────────────────────────────────────
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(6)
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run("KẾ HOẠCH THỰC HIỆN DỰ ÁN\nPHÁT TRIỂN ỨNG DỤNG BẰNG AI-AUGMENTED SDLC")
    run_title.font.name = "Times New Roman"
    run_title.font.size = Pt(13.5)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D) # Navy Blue

    # ─── THÔNG TIN DỰ ÁN ─────────────────────────────────────────────────────────
    p_info = doc.add_paragraph()
    p_info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_info.paragraph_format.space_before = Pt(2)
    p_info.paragraph_format.space_after = Pt(6)
    
    info_text = (
        "Đề tài: Hệ thống Quản lý Phòng khám có tích hợp Trí tuệ Nhân tạo (Hospital-AI)\n"
        "GVHD: TS. Nguyễn Đình Dũng  |  Nhóm: 03  |  Lớp: KTPM K23C\n"
        "Thành viên: Nguyễn Văn Toàn (Trưởng nhóm — DTC245180042) & Trần Thị Loan (DTC245180058)\n"
        "Thời gian thực hiện: Từ 27/07/2026 đến 27/09/2026 (9 tuần)  |  Mô hình: Cả 2 cùng làm Frontend & Backend\n"
        "Phương pháp luận: AI-Augmented SDLC có kiểm soát (Skills, Tools/MCP, 5 Human Gates, Git History)"
    )
    run_info = p_info.add_run(info_text)
    run_info.font.name = "Times New Roman"
    run_info.font.size = Pt(9)
    run_info.font.italic = True
    run_info.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)

    # ─── BẢNG KẾ HOẠCH CHI TIẾT 5 CỘT (32 DÒNG CÔNG VIỆC) ─────────────────────
    headers = [
        "Tuần / Thời gian",
        "Hạng mục công việc & Phân loại\n(Frontend / Backend / AI / Skill)",
        "Thành viên\nthực hiện",
        "Sản phẩm Artifact bàn giao\n& Git Commit Message",
        "Điểm kiểm soát & Ghi chú\n(Human Gates, Tools / MCP)"
    ]

    # Danh sách 32 đầu việc độc lập, sáng rõ
    tasks = [
        # ═══ TUẦN 01 ════════════════════════════════════════════════════════════
        {
            "week": "Tuần 01\n(27/07 - 02/08)\n\nPha 1:\nRequirements\nEngineering",
            "type_tag": "[Nghiệp vụ phòng khám]",
            "task": "Khảo sát thực tế quy trình tiếp đón và khám bệnh tại phòng khám; xác định nỗi đau quá tải giờ cao điểm.",
            "member": "Trần Thị Loan",
            "artifact": "customer-requirement.md",
            "commit": "docs(req): tong hop khao sat nghiep vu phong kham",
            "notes": "Lấy số liệu khảo sát thực tế tại phòng khám."
        },
        {
            "week": "Tuần 01",
            "type_tag": "[AI Skill]",
            "task": "Xây dựng Requirements Analysis Skill cho AI Agent, chuẩn hóa biến yêu cầu tự nhiên thành FR/NFR.",
            "member": "Trần Thị Loan",
            "artifact": ".agents/skills/\nrequirements-analysis/\nSKILL.md",
            "commit": "docs(skill): tao skill requirements-analysis v1",
            "notes": "Tools: view_file, write_to_file."
        },
        {
            "week": "Tuần 01",
            "type_tag": "[Phân tích Actor & FR]",
            "task": "Dùng AI Agent phân tích bóc tách 5 nhóm Actors (Bệnh nhân, Lễ tân, Bác sĩ, Dược sĩ, Kế toán) và 13 FRs.",
            "member": "Nguyễn Văn Toàn",
            "artifact": "docs/requirements.md\ndocs/ai-prompt-history.md",
            "commit": "docs(req): dac ta 5 actors va 13 yeu cau chuc nang",
            "notes": "Lưu nhật ký prompt AI Phase 1."
        },
        {
            "week": "Tuần 01",
            "type_tag": "[AI Scope & Y đức]",
            "task": "Xác định ranh giới an toàn của AI (FR-AI-01 đến 03): AI chỉ hỗ trợ hành chính, tuyệt đối không can thiệp chỉ định y khoa.",
            "member": "Nguyễn Văn Toàn",
            "artifact": "docs/requirements.md\n(Mục FR-AI Scope)",
            "commit": "docs(req): xac dinh ranh gioi y duc cho AI Agent",
            "notes": "Chuẩn mực an toàn thông tin y tế."
        },

        # ═══ TUẦN 02 ════════════════════════════════════════════════════════════
        {
            "week": "Tuần 02\n(03/08 - 09/08)\n\nPha 2:\nArchitecture &\nDatabase Design",
            "type_tag": "[User Stories & AC]",
            "task": "Dùng AI Agent sinh User Stories chi tiết kèm tiêu chuẩn nghiệm thu Acceptance Criteria (Gherkin format).",
            "member": "Nguyễn Văn Toàn",
            "artifact": "docs/user-stories.md\ndocs/acceptance-criteria.md",
            "commit": "docs(srs): them user stories va tieu chi nghiem thu",
            "notes": "🛑 HUMAN GATE 1:\nCon người thẩm định loại bỏ ảo giác AI, ký duyệt SRS."
        },
        {
            "week": "Tuần 02",
            "type_tag": "[AI Skill]",
            "task": "Xây dựng Database Design Skill & Architecture Design Skill phục vụ AI Agent thiết kế chuẩn mực.",
            "member": "Trần Thị Loan &\nNguyễn Văn Toàn",
            "artifact": ".agents/skills/\ndatabase-design/SKILL.md\narchitecture-design/SKILL.md",
            "commit": "docs(skill): them database va architecture skills",
            "notes": "Quản lý version Skill trên Git."
        },
        {
            "week": "Tuần 02",
            "type_tag": "[Backend Database]",
            "task": "Thiết kế ERD 14 bảng CSDL quan hệ, chuẩn hóa 3NF, phân tách dữ liệu y tế nhạy cảm (PII).",
            "member": "Trần Thị Loan",
            "artifact": "database/schema.sql\nERD.md\ndocs/database-design.md",
            "commit": "feat(db): thiet ke ERD 14 bang va script schema.sql",
            "notes": "🛑 HUMAN GATE 2:\nPhê duyệt ERD 14 bảng & mô hình bảo mật dữ liệu PII."
        },
        {
            "week": "Tuần 02",
            "type_tag": "[System Architecture]",
            "task": "Thiết kế Layered Architecture (FastAPI + SQLAlchemy) và biên soạn 8 quyết định kiến trúc ADRs.",
            "member": "Nguyễn Văn Toàn",
            "artifact": "docs/architecture.md\ndocs/architecture-\ndecisions.md",
            "commit": "docs(arch): thiet ke layered architecture va 8 ADRs",
            "notes": "Phân tầng Router - Service - Repository - DB."
        },

        # ═══ TUẦN 03 ════════════════════════════════════════════════════════════
        {
            "week": "Tuần 03\n(10/08 - 16/08)\n\nPha 3:\nCoding Setup &\nUI Foundation",
            "type_tag": "[DevOps & Coding Skill]",
            "task": "Xây dựng FastAPI Pro Skill và tài liệu AGENTS.md định nghĩa quy tắc Git Branching, Zero-Conflict Protocol.",
            "member": "Nguyễn Văn Toàn",
            "artifact": ".agents/skills/\nfastapi-pro/SKILL.md\nAGENTS.md",
            "commit": "chore(devops): thiet lap quy tac git va fastapi-pro skill",
            "notes": "Zero-Conflict Protocol: 2 dev làm trên 2 feature branch độc lập."
        },
        {
            "week": "Tuần 03",
            "type_tag": "[Backend Foundation]",
            "task": "Khởi tạo ORM SQLAlchemy Base, cấu hình database.py, models.py và nạp seed dữ liệu 37 chuyên khoa.",
            "member": "Trần Thị Loan",
            "artifact": "database.py, models.py\nseed_doctors.py",
            "commit": "feat(db): cau hinh sqlalchemy orm va seed 37 chuyen khoa",
            "notes": "Tools & MCP: Database MCP, run_command."
        },
        {
            "week": "Tuần 03",
            "type_tag": "[Frontend UI - Toàn]",
            "task": "Thiết kế Wireframe & UI Cổng Bệnh nhân (index.html, dat_lich_online.html), Kiosk Smart TV, Dashboard Bác sĩ.",
            "member": "Nguyễn Văn Toàn",
            "artifact": "templates/index.html\nman_hinh_phong_kham.html\nlap_phieu_kham.html",
            "commit": "feat(ui): wireframe cong benh nhan, kiosk tv va bac si",
            "notes": "Responsive HTML5/CSS3, Bootstrap 5.3 & Google Fonts."
        },
        {
            "week": "Tuần 03",
            "type_tag": "[Frontend UI - Loan]",
            "task": "Thiết kế Wireframe & UI Màn hình Lễ tân tiếp đón (lich_kham.html), Kế toán viện phí, Quầy thuốc kho dược.",
            "member": "Trần Thị Loan",
            "artifact": "templates/lich_kham.html\nke_toan.html, quay_thuoc.html",
            "commit": "feat(ui): wireframe le tan, ke toan vien phi va quay thuoc",
            "notes": "Dùng AI sinh cấu trúc form giao diện nghiệp vụ."
        },

        # ═══ TUẦN 04 ════════════════════════════════════════════════════════════
        {
            "week": "Tuần 04\n(17/08 - 23/08)\n\nPha 4 (Module 1):\nAuth, RBAC &\nBooking Portal",
            "type_tag": "[Backend API - Loan]",
            "task": "Xây dựng API xác thực JWT, mã hóa bcrypt mật khẩu, middleware phân quyền RBAC 4 vai trò.",
            "member": "Trần Thị Loan",
            "artifact": "routers/auth.py\nschemas.py",
            "commit": "feat(auth): API dang nhap JWT va middleware RBAC 4 roles",
            "notes": "Dùng AI debug logic RBAC (admin, bac_si, le_tan, ke_toan)."
        },
        {
            "week": "Tuần 04",
            "type_tag": "[Frontend UI - Loan]",
            "task": "Xây dựng giao diện Đăng nhập (login.html), quản lý session, guard route và điều hướng phân quyền theo vai trò.",
            "member": "Trần Thị Loan",
            "artifact": "templates/login.html",
            "commit": "feat(ui): giao dien dang nhap va logic session guard",
            "notes": "Tự động điều hướng đúng trang nghiệp vụ khi đăng nhập thành công."
        },
        {
            "week": "Tuần 04",
            "type_tag": "[Backend API - Toàn]",
            "task": "Xây dựng API Đặt lịch online, transaction kiểm soát capacity theo khung giờ, cấp STT tự động, gửi OTP qua Gmail.",
            "member": "Nguyễn Văn Toàn",
            "artifact": "routers/lich_khams.py\nemail_service.py",
            "commit": "feat(api): API dat lich online, kiem soat capacity va OTP",
            "notes": "Transaction an toàn chống quá tải; rate limit 3 lần OTP/email/giờ."
        },
        {
            "week": "Tuần 04",
            "type_tag": "[Frontend UI - Toàn]",
            "task": "Xây dựng Cổng Đặt lịch khám online (dat_lich_online.html) chọn khoa/bác sĩ, popup form xác thực mã OTP Gmail.",
            "member": "Nguyễn Văn Toàn",
            "artifact": "templates/\ndat_lich_online.html",
            "commit": "feat(ui): cong dat lich online chon bac si va xac thuc OTP",
            "notes": "AJAX form đặt lịch, đếm ngược 60s gửi lại OTP."
        },

        # ═══ TUẦN 05 ════════════════════════════════════════════════════════════
        {
            "week": "Tuần 05\n(24/08 - 30/08)\n\nPha 4 (Module 2):\nMedical Exam &\nPharmacy - Billing",
            "type_tag": "[Backend API - Loan]",
            "task": "Xây dựng API Phiếu khám, lưu triệu chứng, chẩn đoán ICD và chi tiết đơn thuốc điện tử (bảng DonThuoc).",
            "member": "Trần Thị Loan",
            "artifact": "routers/phieu_khams.py\nmodels.py (DonThuoc)",
            "commit": "feat(api): API tao phieu kham va luu don thuoc dien tu",
            "notes": "Ràng buộc toàn vẹn: chặn kê đơn thuốc vượt số lượng tồn kho."
        },
        {
            "week": "Tuần 05",
            "type_tag": "[Frontend UI - Toàn]",
            "task": "Xây dựng Giao diện Bác sĩ khám bệnh, hàng đợi gọi số realtime, autocomplete tìm kiếm thuốc, mẫu in ấn CSS A5.",
            "member": "Nguyễn Văn Toàn",
            "artifact": "templates/\nlap_phieu_kham.html",
            "commit": "feat(ui): man hinh bac si kham benh, autocomplete thuoc, in A5",
            "notes": "In ấn @media print định dạng chuẩn A5 y tế."
        },
        {
            "week": "Tuần 05",
            "type_tag": "[Backend API - Loan]",
            "task": "Xây dựng API Kế toán viện phí, xuất hóa đơn và Database Transaction ACID tự động trừ kho dược khi thanh toán.",
            "member": "Trần Thị Loan",
            "artifact": "routers/hoa_dons.py\nrouters/ke_toan.py",
            "commit": "feat(api): API thanh toan vien phi va transaction tru kho duoc",
            "notes": "Tools & MCP: Database MCP. Đảm bảo tính toàn vẹn tồn kho."
        },
        {
            "week": "Tuần 05",
            "type_tag": "[Frontend UI - Loan]",
            "task": "Xây dựng Giao diện Thu ngân viện phí (ke_toan.html) và Quầy thuốc xuất kho (quay_thuoc.html), cảnh báo tồn kho < 10.",
            "member": "Trần Thị Loan",
            "artifact": "templates/ke_toan.html\ntemplates/quay_thuoc.html",
            "commit": "feat(ui): man hinh thu ngan xuat hoa don va quan ly quay thuoc",
            "notes": "Hiển thị chi tiết tiền khám + tiền thuốc, in biên lai."
        },

        # ═══ TUẦN 06 ════════════════════════════════════════════════════════════
        {
            "week": "Tuần 06\n(31/08 - 06/09)\n\nPha 4 (Module 3):\nSmart Kiosk, Portal\n& Security Masking",
            "type_tag": "[FE & BE Kiosk - Toàn]",
            "task": "Xây dựng API GET /queue-display và Màn hình Kiosk Smart TV gọi số phòng khám, polling 3s, Web Speech API phát loa.",
            "member": "Nguyễn Văn Toàn",
            "artifact": "routers/lich_khams.py\ntemplates/\nman_hinh_phong_kham.html",
            "commit": "feat(kiosk): man hinh smart tv goi so va web speech API tieng viet",
            "notes": "Phát âm thanh: 'Xin mời bệnh nhân số XX vào phòng khám...'"
        },
        {
            "week": "Tuần 06",
            "type_tag": "[FE & BE Portal - Toàn]",
            "task": "Xây dựng API GET /tra-cuu và Cổng tra cứu lịch hẹn cá nhân bảo mật theo Số điện thoại + Mã hẹn.",
            "member": "Nguyễn Văn Toàn",
            "artifact": "routers/lich_khams.py\ntemplates/index.html",
            "commit": "feat(portal): cong tra cuu ket qua va lich hen bao mat bang SDT",
            "notes": "Chỉ xem được lịch sử khám khớp số điện thoại chính chủ."
        },
        {
            "week": "Tuần 06",
            "type_tag": "[Backend Security - Loan]",
            "task": "Xây dựng hàm Data Masking mask_pii() loại bỏ họ tên, SĐT, CCCD trước khi gọi LLM và bảng kiểm toán AILog.",
            "member": "Trần Thị Loan",
            "artifact": "routers/ai.py (mask_pii)\nmodels.py (AILog)\nschemas.py",
            "commit": "feat(sec): co che mask_pii an danh PII va bang kiem toan AILog",
            "notes": "Tuân thủ tiêu chuẩn an toàn bảo mật dữ liệu y tế."
        },

        # ═══ TUẦN 07 ════════════════════════════════════════════════════════════
        {
            "week": "Tuần 07\n(07/09 - 13/09)\n\nPha 5:\nAI Features &\nRAG Integration",
            "type_tag": "[Backend AI & RAG - Toàn]",
            "task": "Tích hợp Google Gemini API với Exponential Backoff, xây dựng RAG Pipeline tra cứu cơ sở dữ liệu 37 chuyên khoa.",
            "member": "Nguyễn Văn Toàn",
            "artifact": "routers/ai.py\n.agents/skills/\ngemini-api-integration/SKILL.md\nrag-implementation/SKILL.md",
            "commit": "feat(ai): tich hop gemini api voi exponential backoff va RAG pipeline",
            "notes": "Tự động retry và dự phòng khi gặp sự cố mạng hoặc hạn mức API."
        },
        {
            "week": "Tuần 07",
            "type_tag": "[Frontend AI UI - Toàn]",
            "task": "Xây dựng Floating Chatbot Widget đa phương thức, hỗ trợ nhập giọng nói Microphone (Voice STT) & Vision Upload ảnh.",
            "member": "Nguyễn Văn Toàn",
            "artifact": "static/js/chatbot.js\nstatic/css/chatbot.css",
            "commit": "feat(ui): widget AI chatbot ho tro voice STT va vision upload",
            "notes": "Bệnh nhân có thể nói bằng micro hoặc chụp ảnh gửi bot."
        },
        {
            "week": "Tuần 07",
            "type_tag": "[AI Guardrails & Fallback]",
            "task": "Seed cẩm nang HuongDanChuanBiKham, tối ưu hóa Prompt 3 vòng thử nghiệm và kiểm thử cơ chế Fallback khi offline.",
            "member": "Trần Thị Loan &\nNguyễn Văn Toàn",
            "artifact": "models.py (HuongDan...)\n.agents/skills/\nai-rag-consultant/SKILL.md\nllm-prompt-optimize/SKILL.md",
            "commit": "feat(ai): toi uu prompt 3 vong, medical guardrails va che do fallback",
            "notes": "🛑 HUMAN GATE 3:\nThẩm định Guardrails (từ chối kê đơn); kiểm tra Fallback chạy 100% khi mất mạng."
        },

        # ═══ TUẦN 08 ════════════════════════════════════════════════════════════
        {
            "week": "Tuần 08\n(14/09 - 20/09)\n\nPha 6:\nTesting & QA",
            "type_tag": "[Testing Skill & Plan]",
            "task": "Xây dựng Testing Skill cho AI Agent, thiết kế bộ kịch bản kiểm thử toàn diện gồm 48 test cases (chức năng, ranh giới, AI).",
            "member": "Trần Thị Loan",
            "artifact": ".agents/skills/\ntesting/SKILL.md\ndocs/test-plan.md (48 TCs)",
            "commit": "docs(test): tao testing skill va bo 48 test cases toan he thong",
            "notes": "Bao quát toàn bộ 13 FRs và 3 FR-AI."
        },
        {
            "week": "Tuần 08",
            "type_tag": "[Automation Scripts]",
            "task": "Lập trình test scripts tự động kiểm tra capacity bác sĩ, luồng closed-loop đồng bộ từ đặt lịch ➔ tiếp đón ➔ khám ➔ thanh toán.",
            "member": "Nguyễn Văn Toàn",
            "artifact": "test_appointment_\ncapacity_sync.py\ntest_closed_loop_and_sync.py",
            "commit": "test(auto): viet scripts test tu dong capacity va dong bo hang doi",
            "notes": "Tools & MCP: run_command chạy pytest tự động."
        },
        {
            "week": "Tuần 08",
            "type_tag": "[Test Execution & Fix]",
            "task": "Chạy kiểm thử toàn diện, nghiệm thu Test Report (38 PASS, 10 SKIP/WARN) và khắc phục triệt để lỗi phát hiện BUG-001 trùng số STT.",
            "member": "Trần Thị Loan &\nNguyễn Văn Toàn",
            "artifact": "docs/test-report.md\nrun_full_system_test.py",
            "commit": "fix(lich-kham): sua loi BUG-001 trung STT va hoan tat test report",
            "notes": "🛑 HUMAN GATE 4:\nNghiệm thu kết quả kiểm thử, tỷ lệ pass và độ trễ API < 200ms."
        },

        # ═══ TUẦN 09 ════════════════════════════════════════════════════════════
        {
            "week": "Tuần 09\n(21/09 - 27/09)\n\nPha 7:\nSecurity Audit &\nRelease v1.0.0",
            "type_tag": "[Security & Code Review]",
            "task": "Xây dựng Code Review Skill & Security Review Skill; rà soát OWASP Top 10, quét bảo mật và gỡ bỏ hoàn toàn hardcode credentials.",
            "member": "Nguyễn Văn Toàn &\nTrần Thị Loan",
            "artifact": ".agents/skills/\ncode-review/SKILL.md\nsecurity-review/SKILL.md",
            "commit": "chore(security): ra soat OWASP Top 10 va loai bo hoan toan secret",
            "notes": "🛑 HUMAN GATE 5:\nSecurity Gate: Cam kết không còn API key / pass hardcode trong git."
        },
        {
            "week": "Tuần 09",
            "type_tag": "[Documentation]",
            "task": "Xây dựng Documentation Skill, hoàn thiện README.md, ACCOUNTS.md và cập nhật báo cáo đặc tả đồ án môn học NHÓM_03.docx.",
            "member": "Trần Thị Loan",
            "artifact": ".agents/skills/\ndocumentation/SKILL.md\nREADME.md, ACCOUNTS.md\nBáo cáo NHÓM_03.docx",
            "commit": "docs(full): hoan thien README, ACCOUNTS va bao cao tong ket",
            "notes": "Tài liệu phản ánh đúng 100% implementation thực tế."
        },
        {
            "week": "Tuần 09",
            "type_tag": "[Demo & Release]",
            "task": "Biên soạn kịch bản demo, quay video kịch bản chạy thử, hợp nhất Squash Merge vào main và gắn thẻ Release v1.0.0 trên GitHub.",
            "member": "Nguyễn Văn Toàn",
            "artifact": "docs/plans/demo-script.md\nRelease v1.0.0 trên GitHub\nVideo Demo hoàn chỉnh",
            "commit": "chore(release): hop nhat code main va phat hanh Release v1.0.0",
            "notes": "Bàn giao link GitHub, script CSDL và video kịch bản demo cho GVHD."
        }
    ]

    # Tạo bảng
    table = doc.add_table(rows=1, cols=5)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Độ rộng các cột (tổng 18.4 cm)
    col_widths = [Cm(2.2), Cm(5.2), Cm(2.7), Cm(4.3), Cm(4.0)]

    # Header hàng đầu tiên
    hdr_cells = table.rows[0].cells
    for i, header_text in enumerate(headers):
        hdr_cells[i].text = header_text
        hdr_cells[i].width = col_widths[i]
        set_cell_background(hdr_cells[i], "1B365D") # Navy Blue
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=70, right=70)
        hdr_cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        for p in hdr_cells[i].paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            for run in p.runs:
                run.font.name = "Times New Roman"
                run.font.size = Pt(9)
                run.font.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # Đổ 32 dòng công việc
    current_week_str = ""
    for idx, row_data in enumerate(tasks):
        row = table.add_row()
        cells = row.cells

        for c_idx in range(5):
            cells[c_idx].width = col_widths[c_idx]
            cells[c_idx].vertical_alignment = WD_ALIGN_VERTICAL.TOP
            set_cell_margins(cells[c_idx], top=60, bottom=60, left=60, right=60)

        # Màu nền xen kẽ theo từng tuần
        week_num = row_data["week"].split("\n")[0].strip()
        is_even_week = False
        try:
            w_idx = int(week_num.replace("Tuần", "").strip())
            is_even_week = (w_idx % 2 == 0)
        except:
            is_even_week = (idx % 2 == 1)

        bg_color = "F7F9FB" if is_even_week else "FFFFFF"
        for c_idx in range(5):
            set_cell_background(cells[c_idx], bg_color)

        # Cột 1: Tuần / Thời gian
        p1 = cells[0].paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(row_data["week"])
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(8.5)
        r1.font.bold = True
        r1.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)

        # Cột 2: Hạng mục & Phân loại
        p2 = cells[1].paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(0)
        
        # Tag phân loại
        r_tag = p2.add_run(row_data["type_tag"] + " ")
        r_tag.font.name = "Times New Roman"
        r_tag.font.size = Pt(8.5)
        r_tag.font.bold = True
        if "Frontend" in row_data["type_tag"]:
            r_tag.font.color.rgb = RGBColor(0x02, 0x84, 0xC7) # Blue for FE
        elif "Backend" in row_data["type_tag"]:
            r_tag.font.color.rgb = RGBColor(0x7C, 0x3A, 0xED) # Purple for BE
        elif "AI" in row_data["type_tag"]:
            r_tag.font.color.rgb = RGBColor(0x05, 0x96, 0x69) # Green for AI
        else:
            r_tag.font.color.rgb = RGBColor(0xEA, 0x58, 0x0C) # Orange for other

        r_task = p2.add_run(row_data["task"])
        r_task.font.name = "Times New Roman"
        r_task.font.size = Pt(8.5)
        r_task.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

        # Cột 3: Thành viên thực hiện
        p3 = cells[2].paragraphs[0]
        p3.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p3.paragraph_format.space_before = Pt(0)
        p3.paragraph_format.space_after = Pt(0)
        r3 = p3.add_run(row_data["member"])
        r3.font.name = "Times New Roman"
        r3.font.size = Pt(8.5)
        r3.font.bold = True
        r3.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

        # Cột 4: Sản phẩm Artifact & Git Commit
        p4 = cells[3].paragraphs[0]
        p4.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p4.paragraph_format.space_before = Pt(0)
        p4.paragraph_format.space_after = Pt(0)
        
        r4_art_label = p4.add_run("📦 Artifacts:\n")
        r4_art_label.font.name = "Times New Roman"
        r4_art_label.font.size = Pt(7.5)
        r4_art_label.font.bold = True
        r4_art_label.font.color.rgb = RGBColor(0x15, 0x57, 0x24)

        r4_art = p4.add_run(row_data["artifact"] + "\n\n")
        r4_art.font.name = "Times New Roman"
        r4_art.font.size = Pt(8)
        r4_art.font.color.rgb = RGBColor(0x15, 0x57, 0x24)

        r4_com_label = p4.add_run("🌿 Git Commit:\n")
        r4_com_label.font.name = "Times New Roman"
        r4_com_label.font.size = Pt(7.5)
        r4_com_label.font.bold = True
        r4_com_label.font.color.rgb = RGBColor(0x03, 0x66, 0xD6)

        r4_com = p4.add_run(row_data["commit"])
        r4_com.font.name = "Courier New"
        r4_com.font.size = Pt(7.5)
        r4_com.font.italic = True
        r4_com.font.color.rgb = RGBColor(0x03, 0x66, 0xD6)

        # Cột 5: Ghi chú, Human Gate & Tools/MCP
        p5 = cells[4].paragraphs[0]
        p5.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p5.paragraph_format.space_before = Pt(0)
        p5.paragraph_format.space_after = Pt(0)
        
        notes_text = row_data["notes"]
        if "🛑 HUMAN GATE" in notes_text:
            parts = notes_text.split("🛑 HUMAN GATE")
            if parts[0].strip():
                r_pre = p5.add_run(parts[0].strip() + "\n")
                r_pre.font.name = "Times New Roman"
                r_pre.font.size = Pt(8)
                r_pre.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
            
            gate_content = "🛑 HUMAN GATE" + parts[1]
            r_gate = p5.add_run(gate_content)
            r_gate.font.name = "Times New Roman"
            r_gate.font.size = Pt(8)
            r_gate.font.bold = True
            r_gate.font.color.rgb = RGBColor(0xBA, 0x1A, 0x1A) # Red
        else:
            r_n = p5.add_run(notes_text)
            r_n.font.name = "Times New Roman"
            r_n.font.size = Pt(8)
            r_n.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

    # Đặt viền bảng
    set_table_borders(table, color="D5D8DC", sz="4")

    # ─── PHẦN CAM KẾT & KÝ TÊN ──────────────────────────────────────────────────
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    
    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sign.paragraph_format.space_before = Pt(4)
    p_sign.paragraph_format.space_after = Pt(2)
    r_date = p_sign.add_run("Thái Nguyên, ngày 27 tháng 07 năm 2026\n")
    r_date.font.name = "Times New Roman"
    r_date.font.size = Pt(9.5)
    r_date.font.italic = True

    # Bảng chữ ký 2 cột
    table_sign = doc.add_table(rows=1, cols=2)
    table_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_sign.autofit = False

    t_w = [Cm(9.2), Cm(9.2)]
    s_cells = table_sign.rows[0].cells
    for i in range(2):
        s_cells[i].width = t_w[i]
        set_cell_background(s_cells[i], "FFFFFF")
        set_cell_margins(s_cells[i], top=40, bottom=40, left=40, right=40)

    # Cột bên trái: Thành viên thực hiện
    ps_l = s_cells[0].paragraphs[0]
    ps_l.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rl_title = ps_l.add_run("THÀNH VIÊN THỰC HIỆN\n\n\n\n\n")
    rl_title.font.name = "Times New Roman"
    rl_title.font.size = Pt(10)
    rl_title.font.bold = True
    rl_name = ps_l.add_run("Trần Thị Loan")
    rl_name.font.name = "Times New Roman"
    rl_name.font.size = Pt(10)
    rl_name.font.bold = True

    # Cột bên phải: Trưởng nhóm
    ps_r = s_cells[1].paragraphs[0]
    ps_r.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rr_title = ps_r.add_run("TRƯỞNG NHÓM\n\n\n\n\n")
    rr_title.font.name = "Times New Roman"
    rr_title.font.size = Pt(10)
    rr_title.font.bold = True
    rr_name = ps_r.add_run("Nguyễn Văn Toàn")
    rr_name.font.name = "Times New Roman"
    rr_name.font.size = Pt(10)
    rr_name.font.bold = True

    try:
        doc.save(output_path)
        print(f"✓ Đã tạo thành công tài liệu kế hoạch 10 điểm tại: {output_path}")
    except PermissionError:
        fallback_path = "Ke_Hoach_Thuc_Hien_Nhom03_10Diem.docx"
        doc.save(fallback_path)
        print(f"⚠️ File '{output_path}' đang được mở trong Word.")
        print(f"✓ Đã lưu tài liệu kế hoạch 10 điểm sang file mới: {fallback_path}")

if __name__ == "__main__":
    build_docx()
