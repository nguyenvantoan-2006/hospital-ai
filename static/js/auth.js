/* auth.js - Quản lý phân quyền RBAC, kiểm tra Đăng nhập & Đăng xuất đồng bộ hệ thống ClinicAI */

const ROLE_NAMES = {
  admin: "👑 Admin Quản trị",
  bac_si: "🩺 Bác sĩ Chuyên khoa",
  le_tan: "📋 Lễ tân / Tiếp đón",
  ke_toan: "💰 Kế toán / Thu ngân"
};

const DEFAULT_HOME_PAGE = {
  admin: "admin_dashboard.html",
  bac_si: "lap_phieu_kham.html",
  le_tan: "patient_management.html",
  ke_toan: "ke_toan.html"
};

/**
 * Kiểm tra quyền đăng nhập và phân quyền trang (Route Guard)
 * @param {Array<string>} allowedRoles - Danh sách các vai trò được phép truy cập trang
 */
function initAuthGuard(allowedRoles = []) {
  const token = localStorage.getItem("access_token");
  const role = localStorage.getItem("role");

  // 1. Kiểm tra xem người dùng đã đăng nhập chưa
  if (!token || !role) {
    localStorage.clear();
    window.location.href = "login.html";
    return false;
  }

  // 2. Kiểm tra phân quyền truy cập theo vai trò (RBAC)
  if (allowedRoles.length > 0 && !allowedRoles.includes(role)) {
    alert(`Rất tiếc! Vai trò [${ROLE_NAMES[role] || role}] không có quyền truy cập trang này.`);
    const homePage = DEFAULT_HOME_PAGE[role] || "index.html";
    window.location.href = homePage;
    return false;
  }

  // 3. Hiển thị thông tin người dùng lên Navbar / Header
  updateUserHeader();
  return true;
}

/**
 * Hàm Đăng xuất hệ thống - Xóa bộ nhớ tạm và điều hướng về trang Đăng nhập
 */
function logout() {
  localStorage.clear();
  window.location.href = "login.html";
}

/**
 * Cập nhật động Tên, Vai trò và Avatar của người dùng trên giao diện
 */
function updateUserHeader() {
  const username = localStorage.getItem("username") || "Người dùng";
  const role = localStorage.getItem("role") || "";
  const roleText = ROLE_NAMES[role] || role;

  // Cập nhật tên
  document.querySelectorAll("#navUser, #displayUsername, .user-name-display").forEach(el => {
    el.innerText = username;
  });

  // Cập nhật vai trò
  document.querySelectorAll("#navRole, #displayRole, .user-role-display").forEach(el => {
    el.innerText = roleText;
  });

  // Cập nhật Avatar
  document.querySelectorAll(".user-avatar-display").forEach(el => {
    if (role === "admin") el.innerText = "AD";
    else if (role === "bac_si") el.innerText = "BS";
    else if (role === "le_tan") el.innerText = "LT";
    else if (role === "ke_toan") el.innerText = "KT";
    else el.innerText = username.substring(0, 2).toUpperCase();
  });
}
/**
 * Lấy Header Authentication chuẩn JWT Bearer token cho các yêu cầu fetch()
 */
function getAuthHeaders() {
  const token = localStorage.getItem("access_token");
  return {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
  };
}

// Tự động gán sự kiện click Đăng xuất cho các element có class/id tương ứng khi DOM tải xong
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".btn-logout, #btnLogout, a[href='#logout']").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      logout();
    });
  });
});

