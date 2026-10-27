/* auth.js - Quản lý phân quyền RBAC, kiểm tra Đăng nhập, Đăng xuất & Ẩn/Hiện Menu động theo vai trò */

const ROLE_NAMES = {
  admin: "👑 Admin Quản trị",
  bac_si: "🩺 Bác sĩ Chuyên khoa",
  le_tan: "📋 Lễ tân / Tiếp đón",
  ke_toan: "💰 Kế toán / Thu ngân"
};

const DEFAULT_HOME_PAGE = {
  admin: "admin_dashboard.html",
  bac_si: "lap_phieu_kham.html",
  le_tan: "lich_kham.html",
  ke_toan: "ke_toan.html"
};

/**
 * Ma trận phân quyền truy cập và hiển thị điều hướng (RBAC Route & Menu Matrix)
 */
const ROLE_ALLOWED_PAGES = {
  admin: [
    "index.html", "dashboard.html", "admin_dashboard.html", 
    "lap_phieu_kham.html", "lich_kham.html", "danh_sach_benh_nhan.html", 
    "thanh_toan.html", "quay_thuoc.html", "ke_toan.html"
  ],
  bac_si: [
    "index.html", "dashboard.html", "lap_phieu_kham.html", 
    "lich_kham.html", "danh_sach_benh_nhan.html"
  ],
  le_tan: [
    "index.html", "dashboard.html", "lich_kham.html", "danh_sach_benh_nhan.html"
  ],
  ke_toan: [
    "index.html", "dashboard.html", "thanh_toan.html", "quay_thuoc.html", 
    "ke_toan.html", "danh_sach_benh_nhan.html"
  ]
};

const RESTRICTED_PAGES = [
  "lap_phieu_kham.html",
  "lich_kham.html",
  "thanh_toan.html",
  "quay_thuoc.html",
  "ke_toan.html",
  "admin_dashboard.html"
];

/**
 * Ẩn/hiện menu điều hướng (Sidebar/Navbar) tự động dựa trên vai trò người dùng (RBAC)
 */
function applyDynamicSidebarNav() {
  const role = localStorage.getItem("role");
  if (!role) return;

  const allowedPages = ROLE_ALLOWED_PAGES[role] || [];
  
  // 1. Quét tất cả thẻ a trong sidebar và navbar
  const navLinks = document.querySelectorAll(
    "aside.sidebar a, nav.sidebar a, .sidebar a, nav.navbar a, .navbar-custom a"
  );

  navLinks.forEach(link => {
    const href = link.getAttribute("href");
    if (!href) return;

    // Trích xuất tên trang từ href (ví dụ: "thanh_toan.html" hoặc "/thanh_toan.html")
    const cleanHref = href.split("?")[0].split("#")[0].replace(/^.*\//, "");
    
    // Nếu là trang nằm trong danh sách kiểm soát quyền
    if (RESTRICTED_PAGES.includes(cleanHref)) {
      if (!allowedPages.includes(cleanHref)) {
        // Vai trò không có quyền -> ẩn hoàn toàn khỏi giao diện
        link.style.display = "none";
        link.classList.add("d-none");
      } else {
        link.style.display = "";
        link.classList.remove("d-none");
      }
    }
  });

  // 2. Tinh chỉnh tiêu đề nhóm trong sidebar nếu nhóm đó không có liên kết con nào hiển thị
  document.querySelectorAll("aside.sidebar, nav.sidebar, .sidebar").forEach(sidebar => {
    const titles = sidebar.querySelectorAll(".sidebar-section-title");
    titles.forEach(title => {
      let next = title.nextElementSibling;
      let hasVisibleChild = false;
      while (next && !next.classList.contains("sidebar-section-title")) {
        if (next.tagName === "A" && next.style.display !== "none" && !next.classList.contains("d-none")) {
          hasVisibleChild = true;
          break;
        }
        next = next.nextElementSibling;
      }
      if (!hasVisibleChild) {
        title.style.display = "none";
      } else {
        title.style.display = "";
      }
    });
  });
}

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
    const homePage = DEFAULT_HOME_PAGE[role] || "dashboard.html";
    window.location.href = homePage;
    return false;
  }

  // 3. Hiển thị thông tin người dùng lên Navbar / Header & Ẩn hiện Menu theo vai trò
  updateUserHeader();
  applyDynamicSidebarNav();
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
  document.querySelectorAll("#navUser, #displayUsername, #displayUser, .user-name-display").forEach(el => {
    el.innerText = username;
  });

  // Cập nhật vai trò
  document.querySelectorAll("#navRole, #displayRole, .user-role-display").forEach(el => {
    el.innerText = roleText;
  });

  // Cập nhật Avatar
  document.querySelectorAll(".user-avatar-display, .user-avatar-mini").forEach(el => {
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

// Tự động gán sự kiện click Đăng xuất & áp dụng ẩn/hiện menu khi DOM tải xong
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".btn-logout, #btnLogout, a[href='#logout']").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      logout();
    });
  });
  
  // Áp dụng bộ lọc thanh menu động
  applyDynamicSidebarNav();
  updateUserHeader();
});
