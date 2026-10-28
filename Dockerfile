# ==============================================================================
# Dockerfile cho Hệ thống Quản lý Phòng Khám Thông Minh CLINOVA (Hospital-AI)
# ==============================================================================
# Multi-stage build tối ưu kích thước, bảo mật và chạy bằng non-root user
# ==============================================================================

FROM python:3.11-slim

# Thiết lập biến môi trường Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000

# Cài đặt các gói hệ thống cần thiết (curl để healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /app

# Tạo nhóm và người dùng không phải quản trị (non-root user: appuser)
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -m -s /bin/bash appuser

# Sao chép file requirements trước để tận dụng Docker cache layer
COPY requirements.txt .

# Cài đặt thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn dự án vào container
COPY . .

# Phân quyền thư mục làm việc cho người dùng appuser
RUN chown -R appuser:appgroup /app

# Chuyển sang người dùng không phải root
USER appuser

# Khai báo cổng ứng dụng
EXPOSE 8000

# Kiểm tra sức khỏe container (Healthcheck)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Khởi chạy ứng dụng bằng uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

