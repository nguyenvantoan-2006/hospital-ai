/* admin.js - Logic cho Admin Dashboard */
const B = "http://localhost:8000/api/v1/admin";
const RL = { admin:"👑 Admin", le_tan:"📋 Lễ tân", bac_si:"🩺 Bác sĩ", ke_toan:"💰 Kế toán" };
const RB = { admin:"bg-danger", le_tan:"bg-success", bac_si:"bg-primary", ke_toan:"bg-warning text-dark" };

document.addEventListener("DOMContentLoaded", () => {
  if (typeof initAuthGuard === "function") {
    if (!initAuthGuard(["admin"])) return;
  } else if (localStorage.getItem("role") !== "admin") {
    location.href = "login.html";
    return;
  }
  document.getElementById("navUser").innerText = localStorage.getItem("username") || "Admin";
  showSection("dashboard");
});

function logout() { localStorage.clear(); location.href = "login.html"; }

function showSection(name, el) {
  document.querySelectorAll(".panel").forEach(p => p.classList.add("d-none"));
  document.querySelectorAll(".nav-link").forEach(l => l.classList.remove("active"));
  const panel = document.getElementById("p-" + name);
  if (panel) panel.classList.remove("d-none");
  if (el) el.classList.add("active");
  // If no el passed (called programmatically), activate matching sidebar link
  if (!el) {
    document.querySelectorAll(".nav-link").forEach(l => {
      if (l.getAttribute("onclick") && l.getAttribute("onclick").includes(`'${name}'`)) l.classList.add("active");
    });
  }
  const fn = { dashboard: loadDashboard, accounts: loadUsers, doctors: loadDoctors, specialties: loadSpecialties, revenue: loadRevenue, logs: loadLogs };
  if (fn[name]) fn[name]();
}

function fmt(v) { return new Intl.NumberFormat("vi-VN",{style:"currency",currency:"VND"}).format(v||0); }
function esc(t) { return String(t||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }

function toast(msg, type="success") {
  const box = document.getElementById("toastBox");
  const el = document.createElement("div");
  el.className = `toast show align-items-center text-white bg-${type} border-0 mb-2 shadow`;
  el.innerHTML = `<div class="d-flex"><div class="toast-body fw-semibold">${msg}</div><button class="btn-close btn-close-white me-2 m-auto" onclick="this.closest('.toast').remove()"></button></div>`;
  box.appendChild(el); setTimeout(()=>el.remove(), 4000);
}

async function api(path, method="GET", body=null) {
  const opts = { method, headers: {"Content-Type":"application/json"} };
  if (body) opts.body = JSON.stringify(body);
  const r = await fetch(B + path, opts);
  const d = await r.json();
  if (!r.ok) throw new Error(d.detail || "Lỗi server");
  return d;
}

/* ── DASHBOARD ── */
async function loadDashboard() {
  const d = await api("/reports/overview").catch(()=>null);
  if (d) {
    if (document.getElementById("statPatients")) document.getElementById("statPatients").innerText = d.tong_benh_nhan;
    if (document.getElementById("statAppointments")) document.getElementById("statAppointments").innerText = d.tong_lich_kham;
    if (document.getElementById("statExams")) document.getElementById("statExams").innerText = d.tong_phieu_kham;
    if (document.getElementById("statInvoices")) document.getElementById("statInvoices").innerText = d.tong_hoa_don;
    if (document.getElementById("statRevenue")) document.getElementById("statRevenue").innerText = fmt(d.tong_doanh_thu);
    if (document.getElementById("statUsers")) document.getElementById("statUsers").innerText = d.tong_tai_khoan;
    if (document.getElementById("statDoctors")) document.getElementById("statDoctors").innerText = d.tong_bac_si || 0;
  }
  loadUsers();
  loadDoctors();
}

/* ── USERS ── */
async function loadUsers() {
  const t1 = document.getElementById("tUsers");
  const t2 = document.getElementById("tUsersDash");
  if (t1) t1.innerHTML = `<tr><td colspan="6" class="text-center py-3"><i class="fa-solid fa-spinner fa-spin me-2"></i>Đang tải...</td></tr>`;
  if (t2) t2.innerHTML = `<tr><td colspan="6" class="text-center py-3"><i class="fa-solid fa-spinner fa-spin me-2"></i>Đang tải...</td></tr>`;
  try {
    const data = await api("/users");
    const html = (!data || !data.length) 
      ? `<tr><td colspan="6" class="text-center text-muted py-3">Chưa có tài khoản</td></tr>`
      : data.map(u=>`
      <tr>
        <td class="ps-3 fw-bold text-muted">#${u.id}</td>
        <td class="fw-bold">${esc(u.username)}</td>
        <td><span class="badge ${RB[u.role]||'bg-secondary'}">${RL[u.role]||u.role}</span></td>
        <td class="small text-muted">${u.email||"---"}</td>
        <td>${u.trang_thai?'<span class="badge bg-success-subtle text-success">Hoạt động</span>':'<span class="badge bg-danger-subtle text-danger">Đã khóa</span>'}</td>
        <td class="text-center">
          <button class="btn btn-xs btn-outline-info me-1 py-0 px-2" onclick="viewUserProfile(${u.id})" title="Xem hồ sơ chi tiết"><i class="fa-solid fa-eye"></i></button>
          <button class="btn btn-xs btn-outline-warning me-1 py-0 px-2" onclick="openReset(${u.id},'${esc(u.username)}')" title="Đặt lại MK"><i class="fa-solid fa-key"></i></button>
          <button class="btn btn-xs ${u.trang_thai?'btn-outline-danger':'btn-outline-success'} py-0 px-2" onclick="toggleStatus(${u.id},${u.trang_thai})"><i class="fa-solid ${u.trang_thai?'fa-lock':'fa-lock-open'}"></i></button>
        </td>
      </tr>`).join("");
    if (t1) t1.innerHTML = html;
    if (t2) t2.innerHTML = html;
  } catch(e) { 
    const err = `<tr><td colspan="6" class="text-center text-danger py-3">${e.message}</td></tr>`;
    if (t1) t1.innerHTML = err;
    if (t2) t2.innerHTML = err;
  }
}

async function viewUserProfile(userId) {
  try {
    const p = await api(`/users/${userId}/profile`);
    document.getElementById("profHoTen").innerText = p.ho_ten || `Hồ sơ #${p.user_id}`;
    document.getElementById("profRoleBadge").innerText = RL[p.role] || p.role;
    document.getElementById("profUsername").innerText = p.username;
    document.getElementById("profEmail").innerText = p.email || "Chưa cập nhật";
    document.getElementById("profTrangThai").innerHTML = p.trang_thai 
      ? '<span class="badge bg-success-subtle text-success">Hoạt động</span>'
      : '<span class="badge bg-danger-subtle text-danger">Tài khoản bị khóa</span>';
    
    document.getElementById("profChucVu").innerText = p.chuc_vu || "---";
    document.getElementById("profSDT").innerText = p.so_dien_thoai || "---";
    document.getElementById("profHocVi").innerText = p.hoc_vi || "---";
    document.getElementById("profChuyenKhoa").innerText = p.chuyen_khoa || "Không thuộc khối khám";
    document.getElementById("profPhongKham").innerText = p.phong_kham || "---";
    document.getElementById("profLich").innerText = p.lich_lam_viec || "Hành chính";

    new bootstrap.Modal(document.getElementById("userProfileModal")).show();
  } catch(e) {
    toast("❌ " + e.message, "danger");
  }
}


async function handleAddUser(e) {
  e.preventDefault();
  const btn = document.getElementById("btnAddUser"); btn.disabled=true;
  try {
    const d = await api("/users","POST",{
      username: document.getElementById("uName").value.trim(),
      password: document.getElementById("uPass").value,
      role: document.getElementById("uRole").value,
      email: document.getElementById("uEmail").value||null
    });
    bootstrap.Modal.getInstance(document.getElementById("mAddUser")).hide();
    document.getElementById("fAddUser").reset();
    toast("✅ "+d.message); 
    loadDashboard();
  } catch(e){ toast("❌ "+e.message,"danger"); }
  finally { btn.disabled=false; }
}

async function toggleStatus(id, cur) {
  try { const d = await api(`/users/${id}/status`,"PATCH",{trang_thai:!cur}); toast("✅ "+d.message); loadDashboard(); }
  catch(e){ toast("❌ "+e.message,"danger"); }
}

function openReset(id, name) {
  document.getElementById("rUId").value=id;
  document.getElementById("rUName").innerText=name;
  document.getElementById("rPwd").value="";
  new bootstrap.Modal(document.getElementById("mReset")).show();
}

async function submitReset() {
  const pwd = document.getElementById("rPwd").value.trim();
  if (!pwd) { toast("⚠️ Nhập mật khẩu mới!","warning"); return; }
  try {
    const d = await api(`/users/${document.getElementById("rUId").value}/reset-password`,"POST",{new_password:pwd});
    bootstrap.Modal.getInstance(document.getElementById("mReset")).hide();
    toast("✅ "+d.message);
  } catch(e){ toast("❌ "+e.message,"danger"); }
}

/* ── DOCTORS ── */
// Cache dữ liệu bác sĩ — tránh truyền chuỗi qua onclick attribute (gây lỗi escape)
const _docCache = {};

async function loadDoctors() {
  const t1 = document.getElementById("tDocs");
  const t2 = document.getElementById("tDocsDash");
  if (t1) t1.innerHTML=`<tr><td colspan="8" class="text-center py-3"><i class="fa-solid fa-spinner fa-spin me-2"></i>Đang tải...</td></tr>`;
  if (t2) t2.innerHTML=`<tr><td colspan="8" class="text-center py-3"><i class="fa-solid fa-spinner fa-spin me-2"></i>Đang tải...</td></tr>`;
  try {
    const data = await api("/doctors");

    // Lưu vào cache — key là id (số)
    data.forEach(d => { _docCache[d.id] = d; });

    const html = (!data || !data.length)
      ? `<tr><td colspan="8" class="text-center text-muted py-3">Chưa có bác sĩ nào trong CSDL</td></tr>`
      : data.map(d=>`
        <tr>
          <td class="ps-3 fw-bold text-muted">#${d.id}</td>
          <td><span class="badge bg-primary-subtle text-primary border border-primary-subtle fw-bold">${esc(d.ma_bac_si)}</span></td>
          <td><div class="fw-bold text-dark">${esc(d.hoc_vi)} ${esc(d.ho_ten)}</div></td>
          <td><span class="badge bg-light text-dark border"><i class="fa-solid fa-user me-1 text-secondary"></i>${esc(d.username)}</span></td>
          <td><span class="badge bg-info-subtle text-info border border-info-subtle">${esc(d.chuyen_khoa||"Chưa phân")}</span></td>
          <td class="small">${esc(d.phong_kham||"---")}</td>
          <td class="small text-muted">${esc(d.lich_truc||"---")}</td>
          <td class="text-center">
            <button class="btn btn-xs btn-outline-primary py-0 px-2 me-1" onclick="openEditDoc(${d.id})" title="Sửa thông tin"><i class="fa-solid fa-pen"></i></button>
            <button class="btn btn-xs btn-danger py-0 px-2" onclick="openDeleteDocModal(${d.id})" title="Xóa / Ngừng hoạt động"><i class="fa-solid fa-trash me-1"></i>Xóa</button>
          </td>
        </tr>`).join("");
    if (t1) t1.innerHTML = html;
    if (t2) t2.innerHTML = html;
  } catch(e) {
    const err = `<tr><td colspan="8" class="text-center text-danger py-3">${e.message}</td></tr>`;
    if (t1) t1.innerHTML = err;
    if (t2) t2.innerHTML = err;
  }
}

async function handleAddDoc(e) {
  e.preventDefault();
  const btn=document.getElementById("btnAddDoc"); btn.disabled=true;
  try {
    const ma_bac_si = document.getElementById("dMaBS").value.trim();
    const username = document.getElementById("dUsername").value.trim();
    const password = document.getElementById("dPassword").value;
    const ho_ten = document.getElementById("dHoTen").value.trim();
    
    if (!ho_ten) { toast("⚠️ Vui lòng nhập Họ và tên Bác sĩ!","warning"); return; }
    if (!password) { toast("⚠️ Vui lòng nhập mật khẩu cấp cho Bác sĩ!","warning"); return; }

    const d = await api("/doctors","POST",{
      ma_bac_si,
      username,
      password,
      ho_ten,
      hoc_vi: document.getElementById("dHocVi").value,
      chuyen_khoa: document.getElementById("dChuyenKhoa").value,
      so_dien_thoai: document.getElementById("dSDT").value,
      phong_kham: document.getElementById("dPhong").value,
      lich_truc: document.getElementById("dLichTruc").value
    });
    bootstrap.Modal.getInstance(document.getElementById("mAddDoc")).hide();
    document.getElementById("fAddDoc").reset();
    toast("✅ "+d.message); 
    loadDashboard();
  } catch(e){ toast("❌ "+e.message,"danger"); }
  finally { btn.disabled=false; }
}

function openEditDoc(id) {
  const d = _docCache[id];
  if (!d) { toast("⚠️ Không tìm thấy dữ liệu bác sĩ!", "warning"); return; }
  document.getElementById("eDocId").value = d.id;
  document.getElementById("eMaBS").value = d.ma_bac_si || "";
  document.getElementById("eHoTen").value = d.ho_ten || "";
  document.getElementById("eHocVi").value = d.hoc_vi || "";
  document.getElementById("eChuyenKhoa").value = d.chuyen_khoa || "";
  document.getElementById("eSDT").value = d.so_dien_thoai || "";
  document.getElementById("ePhong").value = d.phong_kham || "";
  document.getElementById("eLichTruc").value = d.lich_truc || "";
  if (document.getElementById("ePassword")) document.getElementById("ePassword").value = "";
  new bootstrap.Modal(document.getElementById("mEditDoc")).show();
}

async function handleEditDoc(e) {
  e.preventDefault();
  const id = document.getElementById("eDocId").value;
  const payload = {
    ma_bac_si: document.getElementById("eMaBS").value.trim(),
    ho_ten: document.getElementById("eHoTen").value.trim(),
    hoc_vi: document.getElementById("eHocVi").value,
    chuyen_khoa: document.getElementById("eChuyenKhoa").value,
    so_dien_thoai: document.getElementById("eSDT").value,
    phong_kham: document.getElementById("ePhong").value,
    lich_truc: document.getElementById("eLichTruc").value
  };
  const pwd = document.getElementById("ePassword") ? document.getElementById("ePassword").value : "";
  if (pwd) payload.password = pwd;

  try {
    const d = await api(`/doctors/${id}`,"PUT", payload);
    bootstrap.Modal.getInstance(document.getElementById("mEditDoc")).hide();
    toast("✅ "+d.message); loadDashboard();
  } catch(e){ toast("❌ "+e.message,"danger"); }
}

// ── Delete Doctor Modal ──────────────────────────────────────────────────────
let _deleteDocId = null;

function openDeleteDocModal(id) {
  const d = _docCache[id];
  if (!d) { toast("⚠️ Không tìm thấy dữ liệu bác sĩ!", "warning"); return; }
  _deleteDocId = id;
  const nameEl = document.getElementById("delDocName");
  const codeEl = document.getElementById("delDocCode");
  if (nameEl) nameEl.innerText = `${d.hoc_vi || ''} ${d.ho_ten || ''}`.trim();
  if (codeEl) codeEl.innerText = d.ma_bac_si || `BS${d.id}`;
  new bootstrap.Modal(document.getElementById("mDeleteDoc")).show();
}

async function confirmDeleteDoc() {
  if (!_deleteDocId) return;
  const btn = document.getElementById("btnConfirmDelete");
  if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-1"></i>Đang xóa...'; }
  try {
    const d = await api(`/doctors/${_deleteDocId}`, "DELETE");
    bootstrap.Modal.getInstance(document.getElementById("mDeleteDoc")).hide();
    toast("✅ " + d.message);
    loadDashboard();
  } catch(e) {
    toast("❌ " + e.message, "danger");
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-trash me-1"></i>Xác nhận xóa'; }
    _deleteDocId = null;
  }
}

/* ── SPECIALTIES ── */
async function loadSpecialties() {
  const tbody = document.getElementById("tSpecs");
  tbody.innerHTML=`<tr><td colspan="5" class="text-center py-3"><i class="fa-solid fa-spinner fa-spin me-2"></i></td></tr>`;
  try {
    const data = await api("/specialties");
    if (!data.length){ tbody.innerHTML=`<tr><td colspan="5" class="text-center text-muted py-3">Chưa có chuyên khoa</td></tr>`; return; }
    tbody.innerHTML = data.map(s=>`
      <tr>
        <td class="ps-3 fw-bold text-muted">#${s.id}</td>
        <td class="fw-bold">${esc(s.ten_chuyen_khoa)}</td>
        <td class="small text-muted">${esc(s.mo_ta||"---")}</td>
        <td class="fw-semibold text-success">${fmt(s.gia_kham_tieu_chuan)}</td>
        <td>${s.trang_thai?'<span class="badge bg-success-subtle text-success">Đang dùng</span>':'<span class="badge bg-secondary-subtle text-secondary">Ngừng</span>'}
          <button class="btn btn-xs btn-outline-danger ms-2 py-0 px-2" onclick="removeSpec(${s.id},'${esc(s.ten_chuyen_khoa)}')"><i class="fa-solid fa-ban"></i></button>
        </td>
      </tr>`).join("");
  } catch(e){ tbody.innerHTML=`<tr><td colspan="5" class="text-center text-danger py-3">${e.message}</td></tr>`; }
}

async function handleAddSpec(e) {
  e.preventDefault();
  const btn=document.getElementById("btnAddSpec"); btn.disabled=true;
  try {
    const d=await api("/specialties","POST",{
      ten_chuyen_khoa: document.getElementById("sName").value.trim(),
      mo_ta: document.getElementById("sMoTa").value,
      gia_kham_tieu_chuan: parseFloat(document.getElementById("sGia").value)||100000
    });
    bootstrap.Modal.getInstance(document.getElementById("mAddSpec")).hide();
    document.getElementById("fAddSpec").reset();
    toast("✅ "+d.message); loadSpecialties();
  } catch(e){ toast("❌ "+e.message,"danger"); }
  finally { btn.disabled=false; }
}

async function removeSpec(id, name) {
  if (!confirm(`Xác nhận ngừng chuyên khoa "${name}"?`)) return;
  try { const d=await api(`/specialties/${id}`,"DELETE"); toast("✅ "+d.message); loadSpecialties(); }
  catch(e){ toast("❌ "+e.message,"danger"); }
}

/* ── REVENUE ── */
let _chartLine = null;
let _chartDonut = null;

async function loadRevenue() {
  try {
    // Load KPI stats from /stats endpoint
    const stats = await api("/stats").catch(() => null);
    if (stats) {
      const rp = document.getElementById("revPatients");
      const rd = document.getElementById("revDoctors");
      if (rp) rp.innerText = stats.total_patients;
      if (rd) rd.innerText = stats.active_doctors;
    }

    // Load revenue report
    const d = await api("/reports/revenue");
    document.getElementById("revTotal").innerText = fmt(d.tong_doanh_thu);
    document.getElementById("revCount").innerText = d.so_hoa_don;

    const TTL = {tien_mat:"💵 Tiền mặt", chuyen_khoan:"🏦 Chuyển khoản", bao_hiem:"🏥 Bảo hiểm", qr:"📱 QR"};
    document.getElementById("tRev").innerHTML = (d.data && d.data.length)
      ? d.data.map(r => `
          <tr>
            <td class="ps-3 fw-bold text-muted">#HD-${r.hoa_don_id}</td>
            <td><span class="badge bg-light text-dark border">PK-${r.hoa_don_id}</span></td>
            <td>${esc(r.ho_ten)}</td>
            <td><span class="badge bg-light text-dark border">${TTL[r.hinh_thuc_tt]||r.hinh_thuc_tt||"---"}</span></td>
            <td class="fw-bold text-success">${fmt(r.tong_tien)}</td>
            <td><span class="badge bg-success-subtle text-success">✓ Đã thanh toán</span></td>
          </tr>`).join("")
      : `<tr><td colspan="6" class="text-center text-muted py-3">Chưa có dữ liệu hóa đơn</td></tr>`;

    // Load and render charts
    await loadCharts();
  } catch(e) { toast("❌ "+e.message, "danger"); }
}

async function loadCharts() {
  try {
    const c = await api("/revenue-chart");

    // ── Line Chart ────────────────────────────────────────────────────────────
    const ctxLine = document.getElementById("chartLine");
    if (ctxLine) {
      if (_chartLine) _chartLine.destroy();
      _chartLine = new Chart(ctxLine, {
        type: "line",
        data: {
          labels: c.line_chart.labels,
          datasets: [{
            label: "Doanh thu (VNĐ)",
            data: c.line_chart.values,
            borderColor: "#1A73E8",
            backgroundColor: "rgba(26,115,232,0.10)",
            borderWidth: 2,
            pointBackgroundColor: "#1A73E8",
            pointRadius: 5,
            tension: 0.4,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: ctx => " " + fmt(ctx.parsed.y)
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: v => (v >= 1000000 ? (v/1000000).toFixed(1)+"M" : (v/1000).toFixed(0)+"K")
              },
              grid: { color: "#F1F5F9" }
            },
            x: { grid: { display: false } }
          }
        }
      });
    }

    // ── Doughnut Chart ────────────────────────────────────────────────────────
    const ctxDonut = document.getElementById("chartDonut");
    if (ctxDonut) {
      if (_chartDonut) _chartDonut.destroy();
      const COLORS = ["#1A73E8","#0EA5E9","#10B981","#F59E0B","#8B5CF6","#EF4444","#06B6D4","#84CC16"];
      const labels = c.doughnut_chart.labels.length ? c.doughnut_chart.labels : ["Chưa có dữ liệu"];
      const values = c.doughnut_chart.values.length ? c.doughnut_chart.values : [1];
      _chartDonut = new Chart(ctxDonut, {
        type: "doughnut",
        data: {
          labels,
          datasets: [{
            data: values,
            backgroundColor: COLORS.slice(0, labels.length),
            borderWidth: 2,
            borderColor: "#fff"
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: "65%",
          plugins: {
            legend: {
              position: "bottom",
              labels: { boxWidth: 12, font: { size: 11 } }
            }
          }
        }
      });
    }
  } catch(e) { console.warn("Chart load error:", e.message); }
}

/* ── AUDIT & AI LOGS ── */
let currentLogTab = "audit";

function switchLogsTab(tab) {
  currentLogTab = tab;
  document.getElementById("btnTabAudit").className = `btn btn-sm ${tab==='audit'?'btn-primary active':'btn-outline-primary'} fw-bold`;
  document.getElementById("btnTabAI").className = `btn btn-sm ${tab==='ai'?'btn-primary active':'btn-outline-primary'} fw-bold`;
  loadLogs();
}

async function loadLogs() {
  const tbody = document.getElementById("tLogs");
  tbody.innerHTML=`<tr><td colspan="5" class="text-center py-3"><i class="fa-solid fa-spinner fa-spin me-2"></i>Đang tải nhật ký...</td></tr>`;
  try {
    const endpoint = currentLogTab === "ai" ? "/logs/ai" : "/logs/audit";
    const data = await api(endpoint);
    if (!data.length){ tbody.innerHTML=`<tr><td colspan="5" class="text-center text-muted py-3">Chưa có nhật ký ${currentLogTab.toUpperCase()}</td></tr>`; return; }
    const AC={CREATE:"bg-success",UPDATE:"bg-primary",DELETE:"bg-danger",LOGIN:"bg-info",LOGOUT:"bg-secondary",AI_SUMMARY:"bg-purple text-white"};
    tbody.innerHTML = data.map(l=>`
      <tr>
        <td class="ps-3 fw-bold text-muted">#${l.id}</td>
        <td><span class="badge ${AC[l.action]||'bg-secondary'}">${l.action}</span></td>
        <td class="small fw-semibold text-primary">${l.target_table}</td>
        <td class="small text-dark">${esc(l.mo_ta||"---")}</td>
        <td class="small text-muted">${l.thoi_gian||"---"}</td>
      </tr>`).join("");
  } catch(e){ tbody.innerHTML=`<tr><td colspan="5" class="text-center text-danger py-3">${e.message}</td></tr>`; }
}

/* ── SEARCH FILTERS (Tra cứu) ── */
function filterTable(inputId, tableBodyId) {
  const q = document.getElementById(inputId).value.toLowerCase();
  const rows = document.querySelectorAll(`#${tableBodyId} tr`);
  rows.forEach(r => {
    const text = r.innerText.toLowerCase();
    r.style.display = text.includes(q) ? "" : "none";
  });
}
function filterUsers() { filterTable("searchUser", "tUsers"); }
function filterDocs() { filterTable("searchDoc", "tDocs"); }
function filterSpecs() { filterTable("searchSpec", "tSpecs"); }
function filterLogs() { filterTable("searchLog", "tLogs"); }

/* ── EXPORT REPORTS ── */

// Hàm gọi đúng format tương ứng
async function exportReport(format, type) {
  if (format === 'pdf') { exportToPDF(type); }
  else { await exportToCSV(type); }
}

// ── Excel: Xuất CSV thực sự (Excel mở được ngay) ──────────────────────────
async function exportToCSV(type) {
  try {
    const d = await api("/reports/revenue");
    const rows = d.data || [];
    const TTL = { tien_mat: "Tiền mặt", chuyen_khoan: "Chuyển khoản", bao_hiem: "Bảo hiểm", qr: "QR Code" };
    const now = new Date().toLocaleString("vi-VN");

    // Header info
    const header = [
      ["BÁO CÁO DOANH THU - CLINOVA"],
      [`Ngày xuất: ${now}`],
      [`Tổng doanh thu: ${d.tong_doanh_thu} VNĐ`],
      [`Số hóa đơn: ${d.so_hoa_don}`],
      [],
      ["Mã HĐ", "Mã Phiếu Khám", "Bệnh nhân", "Hình thức TT", "Tổng tiền (VNĐ)", "Trạng thái"]
    ];

    const dataRows = rows.map(r => [
      `HD-${r.hoa_don_id}`,
      `PK-${r.hoa_don_id}`,
      r.ho_ten,
      TTL[r.hinh_thuc_tt] || r.hinh_thuc_tt || "---",
      r.tong_tien,
      r.trang_thai === "da_thanh_toan" ? "Đã thanh toán" : "Chưa thanh toán"
    ]);

    const allRows = [...header, ...dataRows];
    // Encode CSV với dấu phẩy, wrap chuỗi có dấu phẩy bằng ngoặc kép
    const csvContent = allRows
      .map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(","))
      .join("\n");

    // BOM UTF-8 để Excel hiển thị tiếng Việt đúng
    const bom = "\uFEFF";
    const blob = new Blob([bom + csvContent], { type: "text/csv;charset=utf-8;" });
    const dateStr = new Date().toISOString().slice(0, 10).replace(/-/g, "");
    const filename = `BaoCao_DoanhThu_${dateStr}.csv`;

    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(a.href);

    // Ghi audit log
    api("/reports/export?format=excel&type=revenue").catch(() => {});
    toast("📊 Đã tải xuống " + filename + " — Mở bằng Excel!");
  } catch(e) { toast("❌ Lỗi xuất Excel: " + e.message, "danger"); }
}

// ── PDF: Mở cửa sổ in đẹp, Save as PDF từ browser ────────────────────────
async function exportToPDF(type) {
  try {
    const d = await api("/reports/revenue");
    const rows = d.data || [];
    const TTL = { tien_mat: "Tiền mặt", chuyen_khoan: "Chuyển khoản", bao_hiem: "Bảo hiểm", qr: "QR Code" };
    const now = new Date().toLocaleString("vi-VN");
    const totalFmt = new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(d.tong_doanh_thu || 0);

    const tableRows = rows.map(r => `
      <tr>
        <td>#HD-${r.hoa_don_id}</td>
        <td>PK-${r.hoa_don_id}</td>
        <td>${r.ho_ten}</td>
        <td>${TTL[r.hinh_thuc_tt] || r.hinh_thuc_tt || "---"}</td>
        <td style="text-align:right;font-weight:bold;color:#16a34a">${new Intl.NumberFormat("vi-VN",{style:"currency",currency:"VND"}).format(r.tong_tien)}</td>
        <td><span style="color:#16a34a;font-weight:600">✓ Đã thanh toán</span></td>
      </tr>`).join("");

    const html = `<!DOCTYPE html><html lang="vi"><head>
      <meta charset="UTF-8">
      <title>Báo cáo Doanh thu - Clinova</title>
      <style>
        body { font-family: Arial, sans-serif; padding: 32px; color: #1e293b; }
        .header { text-align: center; margin-bottom: 24px; }
        .header h1 { color: #1A73E8; font-size: 22px; margin: 0; }
        .header p { color: #64748b; margin: 4px 0; font-size: 13px; }
        .kpi { display: flex; gap: 24px; margin-bottom: 24px; }
        .kpi-card { border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 20px; flex: 1; text-align: center; }
        .kpi-card .val { font-size: 20px; font-weight: bold; color: #1A73E8; }
        .kpi-card .lbl { font-size: 12px; color: #64748b; margin-top: 4px; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        thead th { background: #1A73E8; color: white; padding: 10px 12px; text-align: left; }
        tbody tr:nth-child(even) { background: #f8fafc; }
        tbody td { padding: 9px 12px; border-bottom: 1px solid #e2e8f0; }
        .footer { margin-top: 20px; text-align: right; font-size: 11px; color: #94a3b8; }
        @media print { body { padding: 16px; } @page { margin: 1.5cm; } }
      </style></head><body>
      <div class="header">
        <h1>🏥 BÁO CÁO DOANH THU - CLINOVA</h1>
        <p>Ngày xuất: ${now}</p>
      </div>
      <div class="kpi">
        <div class="kpi-card"><div class="val">${totalFmt}</div><div class="lbl">Tổng doanh thu</div></div>
        <div class="kpi-card"><div class="val">${d.so_hoa_don}</div><div class="lbl">Số hóa đơn</div></div>
      </div>
      <table>
        <thead><tr><th>Mã HĐ</th><th>Mã Phiếu Khám</th><th>Bệnh nhân</th><th>Hình thức TT</th><th style="text-align:right">Tổng tiền</th><th>Trạng thái</th></tr></thead>
        <tbody>${tableRows || '<tr><td colspan="6" style="text-align:center;color:#94a3b8;padding:20px">Chưa có dữ liệu</td></tr>'}</tbody>
      </table>
      <div class="footer">Clinova — Hệ thống quản lý phòng khám tích hợp AI | ${now}</div>
      <script>window.onload = () => { window.print(); }<\/script>
    </body></html>`;

    const win = window.open("", "_blank", "width=900,height=700");
    if (!win) { toast("⚠️ Trình duyệt chặn popup. Hãy cho phép popup để xuất PDF!", "warning"); return; }
    win.document.write(html);
    win.document.close();

    // Ghi audit log
    api("/reports/export?format=pdf&type=revenue").catch(() => {});
    toast("🖨️ Cửa sổ in đã mở — Chọn 'Save as PDF' để lưu!");
  } catch(e) { toast("❌ Lỗi xuất PDF: " + e.message, "danger"); }
}
