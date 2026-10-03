-- ============================================================
-- schema.sql — DDL Schema PostgreSQL
-- Hệ thống Quản lý Phòng Khám có Tích hợp AI
-- Nhóm 03 — KTPM K23C | GVHD: TS. Nguyễn Đình Dũng
--
-- NOTE: File này là tài liệu tham khảo DDL.
--       Source of truth là models.py (SQLAlchemy ORM).
--       Alembic / SQLAlchemy tự tạo/migrate tables khi chạy.
-- ============================================================

-- ============================================================
-- 1. USERS — Bảng tài khoản hệ thống
--    Role hợp lệ: 'admin' | 'le_tan' | 'bac_si' | 'ke_toan'
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(20)  NOT NULL,             -- RBAC role
    email         VARCHAR(100) UNIQUE,
    trang_thai    BOOLEAN      NOT NULL DEFAULT TRUE  -- TRUE = active
);
CREATE INDEX IF NOT EXISTS ix_users_username ON users (username);


-- ============================================================
-- 2. BENH_NHANS — Bảng hồ sơ bệnh nhân
-- ============================================================
CREATE TABLE IF NOT EXISTS benh_nhans (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id) ON DELETE SET NULL,
    ho_ten          VARCHAR(100) NOT NULL,
    ngay_sinh       DATE,
    gio_tinh        VARCHAR(10),                     -- Nam / Nữ / Khác
    so_dien_thoai   VARCHAR(20),
    cccd            VARCHAR(20)  UNIQUE,
    dia_chi         VARCHAR(255),
    ma_bhyt         VARCHAR(20)  UNIQUE,
    tien_su_benh    TEXT
);
CREATE INDEX IF NOT EXISTS ix_benh_nhans_so_dien_thoai ON benh_nhans (so_dien_thoai);
CREATE INDEX IF NOT EXISTS ix_benh_nhans_cccd          ON benh_nhans (cccd);


-- ============================================================
-- 3. CHUYEN_KHOA — Danh mục chuyên khoa
-- ============================================================
CREATE TABLE IF NOT EXISTS chuyen_khoa (
    id                  SERIAL PRIMARY KEY,
    ten_chuyen_khoa     VARCHAR(100) NOT NULL UNIQUE,
    mo_ta               TEXT,
    gia_kham_tieu_chuan FLOAT        NOT NULL DEFAULT 100000.0,
    trang_thai          BOOLEAN      NOT NULL DEFAULT TRUE
);


-- ============================================================
-- 4. BAC_SI — Danh mục bác sĩ phòng khám
-- ============================================================
CREATE TABLE IF NOT EXISTS bac_si (
    id                              SERIAL PRIMARY KEY,
    user_id                         INTEGER REFERENCES users(id) ON DELETE SET NULL,
    ma_bac_si                       VARCHAR(50),
    ho_ten                          VARCHAR(100) NOT NULL,
    hoc_vi                          VARCHAR(50)  DEFAULT 'BS.',
    chuyen_khoa                     VARCHAR(100),
    so_dien_thoai                   VARCHAR(20),
    phong_kham                      VARCHAR(100),
    lich_truc                       VARCHAR(200),
    trang_thai                      BOOLEAN      NOT NULL DEFAULT TRUE,
    so_benh_nhan_toi_da_ngay        INTEGER      NOT NULL DEFAULT 200,
    so_benh_nhan_toi_da_khung_gio   INTEGER      NOT NULL DEFAULT 20
);
CREATE INDEX IF NOT EXISTS ix_bac_si_ma_bac_si ON bac_si (ma_bac_si);


-- ============================================================
-- 5. LICH_KHAMS — Bảng lịch khám bệnh
--    trang_thai: 'cho_xac_nhan' | 'da_dat_lich' | 'cho_kham'
--              | 'dang_kham' | 'hoan_thanh' | 'huy'
-- ============================================================
CREATE TABLE IF NOT EXISTS lich_khams (
    id              SERIAL PRIMARY KEY,
    benh_nhan_id    INTEGER NOT NULL REFERENCES benh_nhans(id) ON DELETE CASCADE,
    bac_si_id       INTEGER REFERENCES users(id) ON DELETE SET NULL,
    chuyen_khoa_id  INTEGER REFERENCES chuyen_khoa(id) ON DELETE SET NULL,
    stt             INTEGER,                         -- Số thứ tự xếp hàng
    thoi_gian       TIMESTAMP NOT NULL,
    trang_thai      VARCHAR(30) NOT NULL DEFAULT 'cho_xac_nhan',
    ly_do_kham      TEXT
);


-- ============================================================
-- 6. PHIEU_KHAMS — Bảng phiếu khám (kết quả khám bệnh)
--    ai_summary: bản tóm tắt do AI sinh ra
-- ============================================================
CREATE TABLE IF NOT EXISTS phieu_khams (
    id                  SERIAL PRIMARY KEY,
    lich_kham_id        INTEGER NOT NULL UNIQUE
                            REFERENCES lich_khams(id) ON DELETE CASCADE,
    trieu_chung         TEXT,                        -- Triệu chứng bệnh nhân mô tả
    chan_doan           TEXT,                        -- Chẩn đoán của bác sĩ
    ai_summary          TEXT,                        -- Tóm tắt do AI sinh ra
    huong_dan_sau_kham  TEXT                         -- Lời dặn dò sau khám (Bác sĩ duyệt)
);


-- ============================================================
-- 7. THUOCS — Danh mục thuốc
-- ============================================================
CREATE TABLE IF NOT EXISTS thuocs (
    id              SERIAL PRIMARY KEY,
    ten_thuoc       VARCHAR(200) NOT NULL,
    don_vi_tinh     VARCHAR(50),                     -- viên, chai, ống
    gia_nhap        FLOAT        NOT NULL DEFAULT 0.0,
    don_gia         FLOAT        NOT NULL DEFAULT 0.0,
    so_luong_ton    INTEGER      NOT NULL DEFAULT 100
);
CREATE INDEX IF NOT EXISTS ix_thuocs_ten_thuoc ON thuocs (ten_thuoc);


-- ============================================================
-- 8. DON_THUOCS — Chi tiết đơn thuốc
--    Bảng trung gian giữa phieu_khams và thuocs
-- ============================================================
CREATE TABLE IF NOT EXISTS don_thuocs (
    id              SERIAL PRIMARY KEY,
    phieu_kham_id   INTEGER NOT NULL REFERENCES phieu_khams(id) ON DELETE CASCADE,
    thuoc_id        INTEGER NOT NULL REFERENCES thuocs(id) ON DELETE RESTRICT,
    so_luong        INTEGER      NOT NULL DEFAULT 1,
    lieu_dung       VARCHAR(255),                    -- '2 viên/ngày, sau ăn'
    CONSTRAINT uq_don_thuoc_phieu_thuoc UNIQUE (phieu_kham_id, thuoc_id)
);


-- ============================================================
-- 9. HOA_DONS — Bảng hóa đơn thanh toán
--    trang_thai: 'chua_thanh_toan' | 'da_thanh_toan' | 'huy'
--    hinh_thuc_tt: 'tien_mat' | 'chuyen_khoan' | 'bao_hiem'
--    trang_thai_phat_thuoc: 'cho_lay_thuoc' | 'da_lay_thuoc' | 'khong_co_thuoc'
-- ============================================================
CREATE TABLE IF NOT EXISTS hoa_dons (
    id                      SERIAL PRIMARY KEY,
    phieu_kham_id           INTEGER NOT NULL UNIQUE
                                REFERENCES phieu_khams(id) ON DELETE CASCADE,
    tong_tien               FLOAT        NOT NULL DEFAULT 0.0,
    trang_thai              VARCHAR(30)  NOT NULL DEFAULT 'chua_thanh_toan',
    hinh_thuc_tt            VARCHAR(30),
    trang_thai_phat_thuoc   VARCHAR(30)  NOT NULL DEFAULT 'cho_lay_thuoc',
    thoi_gian_phat_thuoc    TIMESTAMP,
    duoc_si_phat            VARCHAR(100),
    ghi_chu_phat            TEXT
);


-- ============================================================
-- 10. AUDIT_LOGS — Nhật ký hoạt động hệ thống
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER,
    action       VARCHAR(50)  NOT NULL,              -- CREATE | UPDATE | DELETE | LOGIN
    target_table VARCHAR(100),
    target_id    INTEGER,
    mo_ta        TEXT,
    ip_address   VARCHAR(50),
    thoi_gian    TIMESTAMP    NOT NULL DEFAULT NOW()
);


-- ============================================================
-- 11. PHIEU_NHAP_KHO — Phiếu nhập kho thuốc/vật tư
-- ============================================================
CREATE TABLE IF NOT EXISTS phieu_nhap_kho (
    id            SERIAL PRIMARY KEY,
    ma_phieu      VARCHAR(50)  UNIQUE,               -- PNK20260901...
    nha_cung_cap  VARCHAR(200) NOT NULL,
    ngay_nhap     TIMESTAMP    NOT NULL DEFAULT NOW(),
    tong_tien     FLOAT        NOT NULL DEFAULT 0.0,
    nguoi_nhap    VARCHAR(100),
    ghi_chu       TEXT
);
CREATE INDEX IF NOT EXISTS ix_phieu_nhap_kho_ma_phieu ON phieu_nhap_kho (ma_phieu);


-- ============================================================
-- 12. CHI_TIET_NHAP_KHO — Chi tiết từng thuốc trong phiếu nhập
-- ============================================================
CREATE TABLE IF NOT EXISTS chi_tiet_nhap_kho (
    id              SERIAL PRIMARY KEY,
    phieu_nhap_id   INTEGER NOT NULL REFERENCES phieu_nhap_kho(id) ON DELETE CASCADE,
    thuoc_id        INTEGER NOT NULL REFERENCES thuocs(id) ON DELETE RESTRICT,
    so_luong        INTEGER NOT NULL DEFAULT 1,
    don_gia_nhap    FLOAT   NOT NULL DEFAULT 0.0,
    thanh_tien      FLOAT   NOT NULL DEFAULT 0.0
);


-- ============================================================
-- 13. BANG_LUONG — Quản lý tính lương & phát lương nhân viên
-- ============================================================
CREATE TABLE IF NOT EXISTS bang_luong (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id) ON DELETE SET NULL,
    ho_ten          VARCHAR(100) NOT NULL,
    chuc_vu         VARCHAR(50)  NOT NULL,            -- Bác sĩ | Lễ tân | Kế toán | Admin
    thang           INTEGER      NOT NULL,            -- 1-12
    nam             INTEGER      NOT NULL,
    luong_co_ban    FLOAT        NOT NULL DEFAULT 0.0,
    phu_cap         FLOAT        NOT NULL DEFAULT 0.0,
    thuong          FLOAT        NOT NULL DEFAULT 0.0,
    khau_tru        FLOAT        NOT NULL DEFAULT 0.0,
    thuc_linh       FLOAT        NOT NULL DEFAULT 0.0, -- = luong_co_ban + phu_cap + thuong - khau_tru
    trang_thai      VARCHAR(30)  NOT NULL DEFAULT 'chua_chi', -- chua_chi | da_chi
    ngay_tra        TIMESTAMP,
    ghi_chu         TEXT
);


-- ============================================================
-- 14. AI_LOGS — Nhật ký kiểm toán các lượt gọi AI
--     (SEC-AI-04 & NFR-SEC-01)
-- ============================================================
CREATE TABLE IF NOT EXISTS ai_logs (
    id                SERIAL PRIMARY KEY,
    user_id           INTEGER,                        -- Bác sĩ/nhân viên hoặc NULL nếu guest
    chuc_nang         VARCHAR(50)  NOT NULL,          -- ai_summary | ai_post_exam | ai_chatbot
    prompt_masked     TEXT         NOT NULL,          -- Prompt đã che giấu PII
    response_text     TEXT,
    model_name        VARCHAR(100),                   -- gemini-1.5-flash
    response_time_ms  INTEGER,
    trang_thai        VARCHAR(30)  NOT NULL DEFAULT 'success', -- success | error | fallback
    thoi_gian         TIMESTAMP    NOT NULL DEFAULT NOW()
);
