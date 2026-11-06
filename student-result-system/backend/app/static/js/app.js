const tokenKey = "student-result-token";
const state = { user: null, view: "dashboard" };

const ui = {
  login: document.querySelector("#login-view"),
  shell: document.querySelector("#app-shell"),
  loginForm: document.querySelector("#login-form"),
  loginMessage: document.querySelector("#login-message"),
  nav: document.querySelector("#navigation"),
  title: document.querySelector("#page-title"),
  content: document.querySelector("#page-content"),
  summary: document.querySelector("#user-summary"),
  message: document.querySelector("#global-message"),
  sidebar: document.querySelector(".sidebar"),
  menu: document.querySelector("#menu-button"),
};

const menuItems = [
  ["dashboard", "Dashboard", ["student", "professor", "admin"]],
  ["profile", "My profile", ["student", "professor"]],
  ["departments", "Departments", ["student", "professor", "admin"]],
  ["subjects", "Subjects", ["student", "professor", "admin"]],
  ["users", "Admin users", ["admin"]],
  ["course-offerings", "Course Offerings"],
  ["enrollments", "Enrollments"],
  ["marks", "Marks"],
  ["grade-scale", "Grade Scale"],
  ["revaluation", "Revaluation Requests"],
  ["transcript", "Transcript"],
];

function token() { return sessionStorage.getItem(tokenKey); }
function esc(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
}
function detail(payload) {
  if (typeof payload?.detail === "string") return payload.detail;
  if (Array.isArray(payload?.detail)) return payload.detail.map((item) => item.msg).join(", ");
  return "Something went wrong. Please try again.";
}
function notice(message = "", error = false) {
  ui.message.textContent = message;
  ui.message.classList.toggle("error", error);
}
function logout(message = "") {
  sessionStorage.removeItem(tokenKey);
  state.user = null;
  ui.shell.hidden = true;
  ui.login.hidden = false;
  ui.loginForm.reset();
  ui.loginMessage.textContent = message;
}

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (token()) headers.set("Authorization", `Bearer ${token()}`);
  if (options.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const response = await fetch(path, { ...options, headers });
  const isJson = (response.headers.get("content-type") || "").includes("application/json");
  const payload = isJson ? await response.json() : null;
  if (response.status === 401) {
    logout("Your session has expired. Please sign in again.");
    throw new Error("Your session has expired.");
  }
  if (!response.ok) throw new Error(detail(payload));
  return payload;
}

function renderNav() {
  ui.nav.innerHTML = menuItems.filter(([, , roles]) => !roles || roles.includes(state.user.role)).map(([view, label, roles]) => {
    const coming = !roles;
    return `<button class="nav-button" data-view="${view}" type="button" ${coming ? "disabled" : ""} aria-current="${state.view === view ? "page" : "false"}">${esc(label)}${coming ? '<span class="coming-label">Soon</span>' : ""}</button>`;
  }).join("");
}

function showApp() {
  ui.login.hidden = true;
  ui.shell.hidden = false;
  ui.summary.innerHTML = `<strong>${esc(state.user.name)}</strong><span>${esc(state.user.role)}</span>`;
  go("dashboard");
}

function unavailable(title, text) {
  return `<section class="empty-state unavailable"><h2>${esc(title)}</h2><p>${esc(text)}</p></section>`;
}

async function go(view) {
  state.view = view;
  renderNav();
  ui.sidebar.classList.remove("is-open");
  ui.menu.setAttribute("aria-expanded", "false");
  notice();
  ui.title.textContent = menuItems.find(([key]) => key === view)?.[1] || "Dashboard";
  try {
    if (view === "dashboard") renderDashboard();
    if (view === "profile") await renderProfile();
    if (view === "departments") await renderDepartments();
    if (view === "subjects") await renderSubjects();
    if (view === "users") await renderUsers();
  } catch (error) {
    ui.content.innerHTML = unavailable("Unable to load this page", error.message);
  }
}

function renderDashboard() {
  const copy = {
    student: "Review your profile, department, and subjects.",
    professor: "Review department and subject information.",
    admin: "Manage Member 1 data and user accounts.",
  };
  ui.content.innerHTML = `<section class="panel"><p class="eyebrow">Welcome back</p><h2>${esc(state.user.name)}</h2><p class="muted">${copy[state.user.role]}</p></section><section class="card-grid"><article class="card"><strong>${state.user.role === "admin" ? "Manage" : "Browse"}</strong><p>Departments and subjects</p></article><article class="card"><strong>${state.user.role === "student" ? "Profile" : "Access"}</strong><p>Role-based information</p></article><article class="card"><strong>6</strong><p>Future academic modules</p></article></section>`;
}

async function renderProfile() {
  if (state.user.role === "professor") {
    ui.content.innerHTML = unavailable("Professor profile unavailable", "The backend needs GET /professors/me. The current token has no employee ID, so this portal will not guess one.");
    return;
  }
  const students = await api("/students/");
  const student = students[0];
  if (!student) {
    ui.content.innerHTML = unavailable("Student profile unavailable", "No student profile is linked to this account.");
    return;
  }
  const fields = [["Roll number", student.roll_no], ["Name", student.name], ["Email", student.email], ["Department", student.department_name], ["Admission year", student.admission_year], ["Current semester", student.current_semester], ["CGPA", student.cgpa], ["Backlogs", student.backlog_count]];
  ui.content.innerHTML = `<section class="panel"><p class="eyebrow">Student profile</p><h2>${esc(student.name)}</h2><dl class="profile-list">${fields.map(([label, value]) => `<div><dt>${esc(label)}</dt><dd>${esc(value)}</dd></div>`).join("")}</dl></section>`;
}

function departmentsTable(rows) {
  const actions = state.user.role === "admin" ? "<th>Actions</th>" : "";
  return `<div class="table-wrap"><table><thead><tr><th>Code</th><th>Department</th><th>Head user ID</th>${actions}</tr></thead><tbody>${rows.map((row) => `<tr><td>${esc(row.department_code)}</td><td>${esc(row.department_name)}</td><td>${row.head_professor_id ?? "Not assigned"}</td>${state.user.role === "admin" ? `<td class="row-actions"><button class="button button-secondary button-small" data-edit-department="${esc(row.department_code)}">Edit</button><button class="button button-danger button-small" data-delete-department="${esc(row.department_code)}">Delete</button></td>` : ""}</tr>`).join("") || "<tr><td colspan=4>No departments found.</td></tr>"}</tbody></table></div>`;
}

async function renderDepartments() {
  const rows = await api("/departments/");
  const admin = state.user.role === "admin" ? `<aside class="panel"><h3 id="department-title">Create department</h3><form id="department-form"><input id="department-original" type="hidden"><label for="department-code">Department code</label><input id="department-code" required maxlength="10"><label for="department-name">Department name</label><input id="department-name" required maxlength="100"><div class="form-actions"><button class="button button-primary">Save department</button><button id="department-cancel" class="button button-secondary" type="button" hidden>Cancel</button></div></form><hr><h3>Assign department head</h3><p class="subtle">Enter the professor user ID from the backend.</p><form id="head-form"><label for="head-code">Department</label><select id="head-code">${rows.map((row) => `<option value="${esc(row.department_code)}">${esc(row.department_code)}</option>`).join("")}</select><label for="head-id">Professor user ID</label><input id="head-id" type="number" min="1" required><div class="form-actions"><button class="button button-primary">Assign head</button></div></form></aside>` : "";
  ui.content.innerHTML = `<div class="split-layout"><section class="panel"><div class="section-heading"><div><p class="eyebrow">Member 1 master data</p><h2>Departments</h2></div><p class="subtle">${rows.length} total</p></div>${departmentsTable(rows)}</section>${admin}</div>`;
  if (state.user.role === "admin") bindDepartments(rows);
}

function bindDepartments(rows) {
  document.querySelector("#department-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const original = document.querySelector("#department-original").value;
    const code = document.querySelector("#department-code").value.trim();
    const name = document.querySelector("#department-name").value.trim();
    try {
      await api(original ? `/departments/${encodeURIComponent(original)}` : "/departments/", { method: original ? "PUT" : "POST", body: JSON.stringify(original ? { department_name: name } : { department_code: code, department_name: name }) });
      notice("Department saved successfully."); renderDepartments();
    } catch (error) { notice(error.message, true); }
  });
  document.querySelector("#department-cancel").addEventListener("click", renderDepartments);
  document.querySelector("#head-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    try { await api(`/departments/${encodeURIComponent(document.querySelector("#head-code").value)}/head`, { method: "PUT", body: JSON.stringify({ head_professor_id: Number(document.querySelector("#head-id").value) }) }); notice("Department head assigned successfully."); renderDepartments(); } catch (error) { notice(error.message, true); }
  });
  document.querySelectorAll("[data-edit-department]").forEach((button) => button.addEventListener("click", () => {
    const row = rows.find((item) => item.department_code === button.dataset.editDepartment);
    document.querySelector("#department-original").value = row.department_code;
    document.querySelector("#department-code").value = row.department_code;
    document.querySelector("#department-code").disabled = true;
    document.querySelector("#department-name").value = row.department_name;
    document.querySelector("#department-title").textContent = `Edit ${row.department_code}`;
    document.querySelector("#department-cancel").hidden = false;
  }));
  document.querySelectorAll("[data-delete-department]").forEach((button) => button.addEventListener("click", async () => {
    const code = button.dataset.deleteDepartment;
    if (!window.confirm(`Delete department ${code}? This cannot be undone.`)) return;
    try { await api(`/departments/${encodeURIComponent(code)}`, { method: "DELETE" }); notice("Department deleted successfully."); renderDepartments(); } catch (error) { notice(error.message, true); }
  }));
}

function subjectsTable(rows) {
  const actions = state.user.role === "admin" ? "<th>Actions</th>" : "";
  return `<div class="table-wrap"><table><thead><tr><th>Code</th><th>Subject</th><th>Credits</th><th>Department</th>${actions}</tr></thead><tbody>${rows.map((row) => `<tr><td>${esc(row.subject_code)}</td><td>${esc(row.subject_name)}</td><td>${esc(row.credits)}</td><td>${esc(row.department_name)} (${esc(row.department_code)})</td>${state.user.role === "admin" ? `<td class="row-actions"><button class="button button-secondary button-small" data-edit-subject="${esc(row.subject_code)}">Edit</button><button class="button button-danger button-small" data-delete-subject="${esc(row.subject_code)}">Delete</button></td>` : ""}</tr>`).join("") || "<tr><td colspan=5>No subjects found.</td></tr>"}</tbody></table></div>`;
}

async function renderSubjects() {
  const rows = await api("/subjects/");
  const departments = state.user.role === "admin" ? await api("/departments/") : [];
  const admin = state.user.role === "admin" ? `<aside class="panel"><h3 id="subject-title">Create subject</h3><form id="subject-form"><input id="subject-original" type="hidden"><label for="subject-code">Subject code</label><input id="subject-code" required maxlength="20"><label for="subject-name">Subject name</label><input id="subject-name" required maxlength="150"><label for="subject-credits">Credits</label><input id="subject-credits" type="number" min="1" required><label for="subject-department">Department</label><select id="subject-department">${departments.map((row) => `<option value="${esc(row.department_code)}">${esc(row.department_code)} — ${esc(row.department_name)}</option>`).join("")}</select><div class="form-actions"><button class="button button-primary">Save subject</button><button id="subject-cancel" class="button button-secondary" type="button" hidden>Cancel</button></div></form></aside>` : "";
  ui.content.innerHTML = `<div class="split-layout"><section class="panel"><div class="section-heading"><div><p class="eyebrow">Member 1 master data</p><h2>Subjects</h2></div><p class="subtle">${rows.length} total</p></div>${subjectsTable(rows)}</section>${admin}</div>`;
  if (state.user.role === "admin") bindSubjects(rows);
}

function bindSubjects(rows) {
  document.querySelector("#subject-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const original = document.querySelector("#subject-original").value;
    const data = { subject_code: document.querySelector("#subject-code").value.trim(), subject_name: document.querySelector("#subject-name").value.trim(), credits: Number(document.querySelector("#subject-credits").value), department_code: document.querySelector("#subject-department").value };
    try { await api(original ? `/subjects/${encodeURIComponent(original)}` : "/subjects/", { method: original ? "PUT" : "POST", body: JSON.stringify(original ? { subject_name: data.subject_name, credits: data.credits, department_code: data.department_code } : data) }); notice("Subject saved successfully."); renderSubjects(); } catch (error) { notice(error.message, true); }
  });
  document.querySelector("#subject-cancel").addEventListener("click", renderSubjects);
  document.querySelectorAll("[data-edit-subject]").forEach((button) => button.addEventListener("click", () => {
    const row = rows.find((item) => item.subject_code === button.dataset.editSubject);
    document.querySelector("#subject-original").value = row.subject_code;
    document.querySelector("#subject-code").value = row.subject_code;
    document.querySelector("#subject-code").disabled = true;
    document.querySelector("#subject-name").value = row.subject_name;
    document.querySelector("#subject-credits").value = row.credits;
    document.querySelector("#subject-department").value = row.department_code;
    document.querySelector("#subject-title").textContent = `Edit ${row.subject_code}`;
    document.querySelector("#subject-cancel").hidden = false;
  }));
  document.querySelectorAll("[data-delete-subject]").forEach((button) => button.addEventListener("click", async () => {
    const code = button.dataset.deleteSubject;
    if (!window.confirm(`Delete subject ${code}? This cannot be undone.`)) return;
    try { await api(`/subjects/${encodeURIComponent(code)}`, { method: "DELETE" }); notice("Subject deleted successfully."); renderSubjects(); } catch (error) { notice(error.message, true); }
  }));
}

async function renderUsers() {
  const rows = await api("/users/");
  ui.content.innerHTML = `<div class="split-layout"><section class="panel"><div class="section-heading"><div><p class="eyebrow">Admin only</p><h2>Users</h2></div><p class="subtle">${rows.length} total</p></div><div class="table-wrap"><table><thead><tr><th>Name</th><th>Username</th><th>Email</th><th>Role</th><th>Actions</th></tr></thead><tbody>${rows.map((row) => `<tr><td>${esc(row.name)}</td><td>${esc(row.username)}</td><td>${esc(row.email)}</td><td>${esc(row.role)}</td><td class="row-actions"><button class="button button-secondary button-small" data-edit-user="${row.user_id}">Edit</button><button class="button button-danger button-small" data-delete-user="${row.user_id}">Delete</button></td></tr>`).join("")}</tbody></table></div></section><aside class="panel"><h3 id="user-title">Edit user</h3><p class="subtle">Select Edit to load a user. Deleting a user removes any linked student or professor profile.</p><form id="user-form" hidden><input id="user-id" type="hidden"><label for="user-name">Name</label><input id="user-name" required><label for="user-username">Username</label><input id="user-username" required><label for="user-email">Email</label><input id="user-email" type="email" required><label><input id="user-admin" type="checkbox"> Administrator account</label><div class="form-actions"><button class="button button-primary">Save user</button><button id="user-cancel" class="button button-secondary" type="button">Cancel</button></div></form></aside></div>`;
  document.querySelectorAll("[data-edit-user]").forEach((button) => button.addEventListener("click", () => {
    const row = rows.find((item) => item.user_id === Number(button.dataset.editUser));
    document.querySelector("#user-form").hidden = false;
    document.querySelector("#user-id").value = row.user_id;
    document.querySelector("#user-name").value = row.name;
    document.querySelector("#user-username").value = row.username;
    document.querySelector("#user-email").value = row.email;
    document.querySelector("#user-admin").checked = row.role === "admin";
    document.querySelector("#user-title").textContent = `Edit ${row.username}`;
  }));
  document.querySelector("#user-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const id = document.querySelector("#user-id").value;
    const data = { name: document.querySelector("#user-name").value.trim(), username: document.querySelector("#user-username").value.trim(), email: document.querySelector("#user-email").value.trim(), is_admin: document.querySelector("#user-admin").checked };
    try { await api(`/users/${encodeURIComponent(id)}`, { method: "PUT", body: JSON.stringify(data) }); notice("User updated successfully."); renderUsers(); } catch (error) { notice(error.message, true); }
  });
  document.querySelector("#user-cancel").addEventListener("click", renderUsers);
  document.querySelectorAll("[data-delete-user]").forEach((button) => button.addEventListener("click", async () => {
    if (!window.confirm("Delete this user and linked profile? This cannot be undone.")) return;
    try { await api(`/users/${encodeURIComponent(button.dataset.deleteUser)}`, { method: "DELETE" }); notice("User deleted successfully."); renderUsers(); } catch (error) { notice(error.message, true); }
  }));
}

ui.loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  ui.loginMessage.textContent = "";
  const form = new FormData(ui.loginForm);
  try {
    const result = await api("/auth/login", { method: "POST", body: JSON.stringify({ username: form.get("username"), password: form.get("password") }) });
    sessionStorage.setItem(tokenKey, result.access_token);
    state.user = await api("/users/me");
    showApp();
  } catch (error) { ui.loginMessage.textContent = error.message; }
});

ui.nav.addEventListener("click", (event) => {
  const button = event.target.closest("[data-view]");
  if (button && !button.disabled) go(button.dataset.view);
});
document.querySelector("#logout-button").addEventListener("click", () => logout("You have signed out."));
ui.menu.addEventListener("click", () => {
  const open = ui.sidebar.classList.toggle("is-open");
  ui.menu.setAttribute("aria-expanded", String(open));
});

(async () => {
  if (!token()) return;
  try { state.user = await api("/users/me"); showApp(); } catch (_) { /* api handles expired sessions */ }
})();
