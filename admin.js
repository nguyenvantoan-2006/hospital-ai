/* admin.js - Logic cho Admin Dashboard */
const B = "http://localhost:8000/api/v1/admin";
const RL = { admin:"👑 Admin", le_tan:"📋 Lễ tân", bac_si:"🩺 Bác sĩ", ke_toan:"💰 Kế toán" };
const RB = { admin:"bg-danger", le_tan:"bg-success", bac_si:"bg-primary", ke_toan:"bg-warning text-dark" };

document.addEventListener("DOMContentLoaded", () => {
  if (localStorage.getItem("role") !== "admin") { location.href = "login.html"; return; }
  document.getElementById("navUser").innerText = localStorage.getItem("username") || "Admin";
  showSection("dashboard");
});

function logout() { localStorage.clear(); location.href = "login.html"; }

function showSection(name, el) {
  document.querySelectorAll(".panel").forEach(p => p.classList.add("d-none"));
  document.querySelectorAll(".nav-link").forEach(l => l.classList.remove("active"));
  document.getElementById("p-" + name).classList.remove("d-none");
  if (el) el.classList.add("active");
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
  const tbody = document.getElementById("tUsers");
  tbody.innerHTML = `<tr><td colspan="6" class="text-center py-3"><i class="fa-solid fa-spinner fa-spin me-2"></i>Đang tải...</td></tr>`;
  try {
    const data = await api("/users");
    if (!data.length) { tbody.innerHTML=`<tr><td colspan="6" class="text-center text-muted py-3">Chưa có tài khoản</td></tr>`; return; }
    tbody.innerHTML = data.map(u=>`
      <tr>
        <td class="ps-3 fw-bold text-muted">#${u.id}</td>
        <td class="fw-bold">${esc(u.username)}</td>
        <td><span class="badge ${RB[u.role]||'bg-secondary'}">${RL[u.role]||u.role}</span></td>
        <td class="small text-muted">${u.email||"---"}</td>
        <td>${u.trang_thai?'<span class="badge bg-success-subtle text-success">Hoạt động</span>':'<span class="badge bg-danger-subtle text-danger">Đã khóa</span>'}</td>
        <td class="text-center">
          <button class="btn btn-xs btn-outline-warning me-1 py-0 px-2" onclick="openReset(${u.id},'${esc(u.username)}')" title="Đặt lại MK"><i class="fa-solid fa-key"></i></button>
          <button class="btn btn-xs ${u.trang_thai?'btn-outline-danger':'btn-outline-success'} py-0 px-2" onclick="toggleStatus(${u.id},${u.trang_thai})"><i class="fa-solid ${u.trang_thai?'fa-lock':'fa-lock-open'}"></i></button>
        </td>
      </tr>`).join("");
  } catch(e){ tbody.innerHTML=`<tr><td colspan="6" class="text-center text-danger py-3">${e.message}</td></tr>`; }
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
async function loadDoctors() {
  const t1 = document.getElementById("tDocs");
  const t2 = document.getElementById("tDocsDash");
  if (t1) t1.innerHTML=`<tr><td colspan="8" class="text-center py-3"><i class="fa-solid fa-spinner fa-spin me-2"></i>Đang tải...</td></tr>`;
  if (t2) t2.innerHTML=`<tr><td colspan="8" class="text-center py-3"><i class="fa-solid fa-spinner fa-spin me-2"></i>Đang tải...</td></tr>`;
  try {
    const data = await api("/doctors");
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
            <button class="btn btn-xs btn-outline-primary py-0 px-2 me-1" onclick="openEditDoc(${d.id},'${esc(d.ho_ten)}','${esc(d.hoc_vi||"")}','${esc(d.chuyen_khoa||"")}','${esc(d.so_dien_thoai||"")}','${esc(d.phong_kham||"")}','${esc(d.lich_truc||"")}')"><i class="fa-solid fa-pen"></i></button>
            <button class="btn btn-xs btn-outline-danger py-0 px-2" onclick="deactivateDoc(${d.id})"><i class="fa-solid fa-ban"></i></button>
          </td>
        </tr>`).join("");
    if (t1) t1.innerHTML = html;
    if (t2) t2.innerHTML = html;
  } catch(e){ 
    const err = `<tr><td colspan="8" class="text-center text-danger py-3">${e.message}</td></tr>`;
    if (t1) t1.innerHTML = err;
    if (t2) t2.innerHTML = err;
  }
}

async function handleAddDoc(e) {
  e.preventDefault();
  const btn=document.getElementById("btnAddDoc"); btn.disabled=true;
  try {
    const d = await api("/doctors","POST",{
      ma_bac_si: document.getElementById("dMaBS").value.trim(),
      username: document.getElementById("dUsername").value.trim() || undefined,
      ho_ten: document.getElementById("dHoTen").value.trim(),
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

function openEditDoc(id, ht, hv, ck, sdt, pk, lt) {
  document.getElementById("eDocId").value=id;
  document.getElementById("eHoTen").value=ht;
  document.getElementById("eHocVi").value=hv;
  document.getElementById("eChuyenKhoa").value=ck;
  document.getElementById("eSDT").value=sdt;
  document.getElementById("ePhong").value=pk;
  document.getElementById("eLichTruc").value=lt;
  new bootstrap.Modal(document.getElementById("mEditDoc")).show();
}

async function handleEditDoc(e) {
  e.preventDefault();
  const id = document.getElementById("eDocId").value;
  try {
    const d = await api(`/doctors/${id}`,"PUT",{
      ho_ten: document.getElementById("eHoTen").value,
      hoc_vi: document.getElementById("eHocVi").value,
      chuyen_khoa: document.getElementById("eChuyenKhoa").value,
      so_dien_thoai: document.getElementById("eSDT").value,
      phong_kham: document.getElementById("ePhong").value,
      lich_truc: document.getElementById("eLichTruc").value
    });
    bootstrap.Modal.getInstance(document.getElementById("mEditDoc")).hide();
    toast("✅ "+d.message); loadDoctors();
  } catch(e){ toast("❌ "+e.message,"danger"); }
}

async function deactivateDoc(id) {
  if (!confirm("Xác nhận ngừng hoạt động bác sĩ này?")) return;
  try { const d=await api(`/doctors/${id}`,"DELETE"); toast("✅ "+d.message); loadDoctors(); }
  catch(e){ toast("❌ "+e.message,"danger"); }
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
async function loadRevenue() {
  try {
    const d = await api("/reports/revenue");
    document.getElementById("revTotal").innerText = fmt(d.tong_doanh_thu);
    document.getElementById("revCount").innerText = d.so_hoa_don;
    const TTL = {tien_mat:"💵 Tiền mặt", chuyen_khoan:"🏦 Chuyển khoản", qr:"📱 QR"};
    document.getElementById("tRev").innerHTML = d.data.map(r=>`
      <tr>
        <td class="ps-3 fw-bold text-muted">#HD-${r.hoa_don_id}</td>
        <td>${esc(r.ho_ten)}</td>
        <td><span class="badge bg-light text-dark border">${TTL[r.hinh_thuc_tt]||r.hinh_thuc_tt}</span></td>
        <td class="fw-bold text-success">${fmt(r.tong_tien)}</td>
        <td><span class="badge bg-success-subtle text-success">✓ Đã thanh toán</span></td>
      </tr>`).join("") || `<tr><td colspan="5" class="text-center text-muted py-3">Chưa có dữ liệu</td></tr>`;
  } catch(e){ toast("❌ "+e.message,"danger"); }
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

/* ── EXPORT REPORTS (Xuất Excel / PDF) ── */
async function exportReport(format, type) {
  try {
    const d = await api(`/reports/export?format=${format}&type=${type}`);
    toast(`📥 ${d.message}`);
    // Giả lập tải xuống tệp file báo cáo
    const blob = new Blob([`BAO CAO CLINICAI (${type.toUpperCase()})\nFormat: ${format.toUpperCase()}\nNgay xuất: ${new Date().toLocaleString()}`], {type: "text/plain"});
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = d.filename;
    a.click();
  } catch(e) { toast("❌ Lỗi xuất báo cáo: "+e.message, "danger"); }
}
