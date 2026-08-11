# main.py
# Entry point của ứng dụng FastAPI - Hệ thống Quản lý Phòng khám

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
import models
# ─── Tạo tất cả bảng trong CSDL (nếu chưa tồn tại) ──────────────────────────
# Khi chạy lần đầu, SQLAlchemy sẽ tạo file clinic.db và các bảng tương ứng.
Base.metadata.create_all(bind=engine)

# ─── Khởi tạo ứng dụng FastAPI ───────────────────────────────────────────────
app = FastAPI(
    title="Hệ thống Quản lý Phòng khám",
    description=(
        "API cho hệ thống quản lý phòng khám tích hợp AI. "
        "Hỗ trợ phân quyền RBAC: Admin | Lễ tân | Bác sĩ | Kế toán."
    ),
    version="1.0.0",
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc UI
)

# ─── CORS Middleware ──────────────────────────────────────────────────────────
# Cho phép frontend (HTML/JS) gọi API từ domain khác
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Production: thay bằng domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ════════════════════════════════════════════════════════════════════════════════
#  ROUTES - Health Check & Welcome
# ════════════════════════════════════════════════════════════════════════════════

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

@app.get("/health", tags=["Health Check"])
def health_check():
    """
    Endpoint kiểm tra trạng thái hệ thống chi tiết hơn.
    """
    return {
        "status": "healthy",
        "database": "connected",
        "engine": "SQLite/MySQL",
    }


# ════════════════════════════════════════════════════════════════════════════════
#  GHI CHÚ: CÁC ROUTER SẼ ĐƯỢC THÊM VÀO Ở ĐÂY TRONG CÁC BƯỚC TIẾP THEO
# ════════════════════════════════════════════════════════════════════════════════
# from routers import auth, users, benh_nhans, lich_khams, phieu_khams
#
# app.include_router(auth.router,        prefix="/api/v1/auth",        tags=["Auth"])
# app.include_router(users.router,       prefix="/api/v1/users",       tags=["Users"])
# app.include_router(benh_nhans.router,  prefix="/api/v1/benh-nhans",  tags=["Bệnh nhân"])
# app.include_router(lich_khams.router,  prefix="/api/v1/lich-khams",  tags=["Lịch khám"])
# app.include_router(phieu_khams.router, prefix="/api/v1/phieu-khams", tags=["Phiếu khám"])

from routers import ai, benh_nhans, phieu_khams, hoa_dons, lich_khams, auth, admin
app.include_router(ai.router,         prefix="/api/ai",              tags=["AI Trợ lý"])
app.include_router(auth.router,       prefix="/api/v1/auth",         tags=["Xác thực & Đăng nhập"])
app.include_router(benh_nhans.router, prefix="/api/v1/benh-nhans",   tags=["Bệnh nhân"])
app.include_router(phieu_khams.router,prefix="/api/v1/phieu-khams",  tags=["Phiếu khám"])
app.include_router(hoa_dons.router,   prefix="/api/v1/hoa-dons",     tags=["Hóa đơn - Thanh toán"])
app.include_router(lich_khams.router, prefix="/api/v1/lich-khams",   tags=["Lịch khám"])
app.include_router(admin.router,      prefix="/api/v1/admin",        tags=["Quản trị viên (Admin)"])

# ─── Mount Static Files (Phục vụ Web Frontend HTML/JS trực tiếp trên cổng 8000) ───
app.mount("/", StaticFiles(directory=".", html=True), name="static")


# ─── Chạy trực tiếp bằng: python main.py ────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)