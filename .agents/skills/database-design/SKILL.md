---
name: database-design
description: Thiết kế cơ sở dữ liệu PostgreSQL từ requirements đã phê duyệt cho Hệ thống Quản lý Phòng Khám có tích hợp AI — đảm bảo normalization, ràng buộc toàn vẹn và bảo mật dữ liệu y tế.
---

# Database Design Skill — Hospital AI System

## Objective
Thiết kế schema CSDL an toàn, chuẩn 3NF, phù hợp với nghiệp vụ y tế và ràng buộc pháp lý.

## Inputs
Đọc: `docs/requirements.md`, `docs/architecture.md`

## Process
```
Requirements → Entities → Relationships → Normalization (3NF)
    → PK/FK → Constraints → Indexes → SQL Schema → Verification
```

## Entities & Schema

### users (tài khoản hệ thống)
```sql
CREATE TABLE users (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(100) NOT NULL UNIQUE,
    email       VARCHAR(200) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt, KHÔNG SHA256
    role        VARCHAR(50)  NOT NULL CHECK (role IN ('admin','receptionist','doctor','accountant')),
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);
```

### specialties (chuyên khoa)
```sql
CREATE TABLE specialties (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL UNIQUE,
    description TEXT
);
```

### doctors (bác sĩ)
```sql
CREATE TABLE doctors (
    id            SERIAL PRIMARY KEY,
    user_id       INT REFERENCES users(id),
    specialty_id  INT NOT NULL REFERENCES specialties(id),
    full_name     VARCHAR(200) NOT NULL,
    degree        VARCHAR(100),  -- Tiến sĩ, Thạc sĩ...
    phone         VARCHAR(20),
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT NOW()
);
```

### patients (bệnh nhân)
```sql
CREATE TABLE patients (
    id              SERIAL PRIMARY KEY,
    full_name       VARCHAR(200) NOT NULL,
    date_of_birth   DATE,
    gender          VARCHAR(10) CHECK (gender IN ('Nam','Nữ','Khác')),
    phone           VARCHAR(20) NOT NULL UNIQUE,  -- tránh trùng hồ sơ
    address         TEXT,
    insurance_number VARCHAR(100),
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_patients_phone ON patients(phone);
CREATE INDEX idx_patients_name  ON patients(full_name);
```

### schedules (lịch khám)
```sql
CREATE TABLE schedules (
    id            SERIAL PRIMARY KEY,
    patient_id    INT NOT NULL REFERENCES patients(id),
    doctor_id     INT NOT NULL REFERENCES doctors(id),
    specialty_id  INT NOT NULL REFERENCES specialties(id),
    scheduled_at  TIMESTAMP NOT NULL,
    reason        TEXT,
    status        VARCHAR(50) DEFAULT 'cho_xac_nhan'
                  CHECK (status IN ('cho_xac_nhan','da_xac_nhan','dang_kham','hoan_thanh','da_huy','khong_den')),
    source        VARCHAR(20) DEFAULT 'direct' CHECK (source IN ('direct','online')),
    booking_code  VARCHAR(50) UNIQUE,  -- mã lịch hẹn online
    created_by    INT REFERENCES users(id),
    created_at    TIMESTAMP DEFAULT NOW(),
    UNIQUE (doctor_id, scheduled_at)   -- KHÔNG trùng lịch bác sĩ
);
CREATE INDEX idx_schedules_doctor   ON schedules(doctor_id, scheduled_at);
CREATE INDEX idx_schedules_patient  ON schedules(patient_id);
CREATE INDEX idx_schedules_status   ON schedules(status);
```

### exam_records (phiếu khám)
```sql
CREATE TABLE exam_records (
    id              SERIAL PRIMARY KEY,
    schedule_id     INT NOT NULL REFERENCES schedules(id),
    patient_id      INT NOT NULL REFERENCES patients(id),
    doctor_id       INT NOT NULL REFERENCES doctors(id),
    symptoms        TEXT,
    diagnosis       TEXT,
    conclusion      TEXT,
    treatment_notes TEXT,
    status          VARCHAR(50) DEFAULT 'dang_kham'
                    CHECK (status IN ('dang_kham','hoan_thanh')),
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);
```

### medicines (danh mục thuốc)
```sql
CREATE TABLE medicines (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    unit        VARCHAR(50),
    price       DECIMAL(12,0) NOT NULL CHECK (price >= 0),
    stock_qty   INT DEFAULT 0 CHECK (stock_qty >= 0),
    is_active   BOOLEAN DEFAULT TRUE
);
```

### prescriptions (đơn thuốc)
```sql
CREATE TABLE prescriptions (
    id            SERIAL PRIMARY KEY,
    exam_id       INT NOT NULL REFERENCES exam_records(id),
    medicine_id   INT NOT NULL REFERENCES medicines(id),
    quantity      INT NOT NULL CHECK (quantity > 0),
    dosage        VARCHAR(200),
    usage_note    TEXT,
    created_at    TIMESTAMP DEFAULT NOW()
);
```

### services (dịch vụ khám)
```sql
CREATE TABLE services (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(200) NOT NULL,
    price DECIMAL(12,0) NOT NULL CHECK (price >= 0)
);
```

### invoices (hóa đơn)
```sql
CREATE TABLE invoices (
    id              SERIAL PRIMARY KEY,
    exam_id         INT NOT NULL REFERENCES exam_records(id),
    patient_id      INT NOT NULL REFERENCES patients(id),
    subtotal_exam   DECIMAL(12,0) DEFAULT 0,
    subtotal_meds   DECIMAL(12,0) DEFAULT 0,
    subtotal_services DECIMAL(12,0) DEFAULT 0,
    total_amount    DECIMAL(12,0) NOT NULL CHECK (total_amount >= 0),
    payment_method  VARCHAR(50) CHECK (payment_method IN ('tien_mat','chuyen_khoan')),
    status          VARCHAR(50) DEFAULT 'chua_thanh_toan'
                    CHECK (status IN ('chua_thanh_toan','da_thanh_toan')),
    paid_by         INT REFERENCES users(id),
    paid_at         TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### audit_logs (nhật ký truy cập hệ thống)
```sql
CREATE TABLE audit_logs (
    id          SERIAL PRIMARY KEY,
    user_id     INT REFERENCES users(id),
    action      VARCHAR(200) NOT NULL,
    table_name  VARCHAR(100),
    record_id   INT,
    ip_address  VARCHAR(50),
    created_at  TIMESTAMP DEFAULT NOW()
);
```

### ai_logs (nhật ký sử dụng AI — SEC-AI-04)
```sql
CREATE TABLE ai_logs (
    id           SERIAL PRIMARY KEY,
    user_id      INT REFERENCES users(id),
    function_name VARCHAR(100) NOT NULL,  -- 'ai_summary','chatbot','post_exam_guide'
    input_masked TEXT,    -- dữ liệu ĐÃ được Data Masking
    output_text  TEXT,
    status       VARCHAR(50) CHECK (status IN ('success','error','fallback')),
    duration_ms  INT,
    created_at   TIMESTAMP DEFAULT NOW()
);
```

### online_booking_otp (OTP đặt lịch trực tuyến)
```sql
CREATE TABLE online_booking_otp (
    id         SERIAL PRIMARY KEY,
    email      VARCHAR(200) NOT NULL,
    otp_code   VARCHAR(10) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used    BOOLEAN DEFAULT FALSE,
    attempts   INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Relationships
```
users 1 ──── 1 doctors
specialties 1 ──── N doctors
patients 1 ──── N schedules
doctors 1 ──── N schedules
schedules 1 ──── 1 exam_records
exam_records 1 ──── N prescriptions
medicines 1 ──── N prescriptions
exam_records 1 ──── 1 invoices
users 1 ──── N audit_logs
users 1 ──── N ai_logs
```

## Security Requirements
- `password_hash` phải dùng **bcrypt** — KHÔNG SHA256.
- Không lưu thông tin PII (họ tên, SĐT) trong `ai_logs.input_masked`.
- `audit_logs` ghi đầy đủ mọi thao tác CRUD quan trọng.

## Rules
- Không viết Flask/FastAPI source code.
- Mọi FK phải có constraint rõ ràng.
- Không để orphan records.

## Outputs
- `docs/database-design.md`
- `database/schema.sql`
