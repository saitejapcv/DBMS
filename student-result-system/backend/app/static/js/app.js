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
  ["course-offerings", "Teaching Assignments", ["student", "professor", "admin"]],
  ["enrollments", "Enrollments", ["professor", "admin"]],
  ["marks", "Marks", ["professor", "admin"]],
  ["grade-scale", "Grade Scale", ["student", "professor", "admin"]],
  ["revaluation", "Revaluation Requests", ["student", "professor", "admin"]],
  ["transcript", "Transcript", ["student"]],
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
    if (view === "course-offerings") await renderAssignments();
    if (view === "enrollments") await renderEnrollments();
    if (view === "marks") await renderMarks();
    if (view === "grade-scale") await renderGradeScale();
    if (view === "revaluation") await renderRevaluation();
    if (view === "transcript") await renderTranscript();
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

function assignmentOptions(rows) {
  return rows.map((row) => `<option value="${row.assignment_id}">${esc(row.subject_code)} — ${esc(row.academic_year)} ${esc(row.term)} (#${row.assignment_id})</option>`).join("");
}

async function renderAssignments() {
  const rows = await api("/assignments/");
  const professors = state.user.role === "admin" ? await api("/professors/") : [];
  const create = state.user.role === "admin" ? `<aside class="panel"><h3>Create teaching assignment</h3><form id="assignment-form"><label>Subject code<input id="assignment-subject" required maxlength="20"></label><label>Professor<select id="assignment-professor" required>${professors.map((row) => `<option value="${row.user_id}">${esc(row.name)} — ${esc(row.employee_id)} (ID ${row.user_id})</option>`).join("")}</select></label><label>Academic year<input id="assignment-year" required maxlength="10" placeholder="2025"></label><label>Term<select id="assignment-term"><option>ODD</option><option>EVEN</option><option>SUMMER</option></select></label><div class="form-actions"><button class="button button-primary">Create assignment</button></div></form></aside>` : "";
  ui.content.innerHTML = `<div class="split-layout"><section class="panel"><div class="section-heading"><div><p class="eyebrow">Member 2 &amp; 3 academic flow</p><h2>Teaching assignments</h2></div><p class="subtle">${rows.length} total</p></div><div class="table-wrap"><table><thead><tr><th>ID</th><th>Subject</th><th>Professor</th><th>Year / term</th><th>Status</th><th>Action</th></tr></thead><tbody>${rows.map((row) => { const status = row.published_at ? "Published" : row.submitted_at ? "Submitted" : "Draft"; const action = state.user.role === "professor" && !row.published_at ? (row.submitted_at ? `<button class="button button-secondary button-small" data-publish-assignment="${row.assignment_id}">Publish results</button>` : `<button class="button button-secondary button-small" data-submit-assignment="${row.assignment_id}">Submit marks</button>`) : "—"; return `<tr><td>${row.assignment_id}</td><td>${esc(row.subject_code)}</td><td>${row.professor_id}</td><td>${esc(row.academic_year)} / ${esc(row.term)}</td><td>${status}</td><td>${action}</td></tr>`; }).join("") || "<tr><td colspan=6>No assignments found.</td></tr>"}</tbody></table></div></section>${create}</div>`;
  document.querySelectorAll("[data-submit-assignment]").forEach((button) => button.addEventListener("click", async () => {
    try { await api(`/assignments/${button.dataset.submitAssignment}/submit`, { method: "PATCH" }); notice("Marks submitted. You can publish the results now."); renderAssignments(); } catch (error) { notice(error.message, true); }
  }));
  document.querySelectorAll("[data-publish-assignment]").forEach((button) => button.addEventListener("click", async () => {
    try { await api(`/results/assignments/${button.dataset.publishAssignment}/publish`, { method: "POST" }); notice("Results published successfully."); renderAssignments(); } catch (error) { notice(error.message, true); }
  }));
  if (state.user.role === "admin") document.querySelector("#assignment-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = { subject_code: document.querySelector("#assignment-subject").value.trim(), professor_id: Number(document.querySelector("#assignment-professor").value), academic_year: document.querySelector("#assignment-year").value.trim(), term: document.querySelector("#assignment-term").value };
    try { await api("/assignments/", { method: "POST", body: JSON.stringify(data) }); notice("Teaching assignment created."); renderAssignments(); } catch (error) { notice(error.message, true); }
  });
}

async function renderEnrollments() {
  const assignments = await api("/assignments/");
  const students = state.user.role === "admin" ? (await api("/users/")).filter((row) => row.role === "student") : [];
  ui.content.innerHTML = `<section class="panel"><div class="section-heading"><div><p class="eyebrow">Course roster</p><h2>Enrollments</h2></div></div><label for="enrollment-assignment">Teaching assignment</label><select id="enrollment-assignment">${assignmentOptions(assignments)}</select><div id="enrollment-content" class="page-content"></div></section>`;
  const select = document.querySelector("#enrollment-assignment");
  const load = async () => {
    const assignmentId = select.value;
    const rows = await api(`/assignments/${assignmentId}/enrollments`);
    document.querySelector("#enrollment-content").innerHTML = `<div class="table-wrap"><table><thead><tr><th>Enrollment</th><th>Student</th><th>Enrolled</th><th>Grade</th></tr></thead><tbody>${rows.map((row) => `<tr><td>${row.enrollment_id}</td><td>${row.student_id}</td><td>${esc(row.enrolled_on)}</td><td>${esc(row.grade || "Pending")}</td></tr>`).join("") || "<tr><td colspan=4>No enrollments found.</td></tr>"}</tbody></table></div>${state.user.role === "admin" ? `<form id="enrollment-form" class="panel"><h3>Enroll a student</h3><label>Student<select id="enrollment-student" required>${students.map((row) => `<option value="${row.user_id}">${esc(row.name)} — ${esc(row.username)} (ID ${row.user_id})</option>`).join("")}</select></label><div class="form-actions"><button class="button button-primary">Enroll student</button></div></form>` : ""}`;
    if (state.user.role === "admin") document.querySelector("#enrollment-form").addEventListener("submit", async (event) => { event.preventDefault(); try { await api(`/assignments/${assignmentId}/enrollments`, { method: "POST", body: JSON.stringify({ student_id: Number(document.querySelector("#enrollment-student").value) }) }); notice("Student enrolled."); load(); } catch (error) { notice(error.message, true); } });
  };
  if (assignments.length) { select.addEventListener("change", load); await load(); } else document.querySelector("#enrollment-content").innerHTML = unavailable("No assignments", "Create a teaching assignment first.");
}

async function renderMarks() {
  const assignments = await api("/assignments/");
  ui.content.innerHTML = `<section class="panel"><div class="section-heading"><div><p class="eyebrow">Evaluation and marks</p><h2>Marks</h2></div></div><label for="marks-assignment">Teaching assignment</label><select id="marks-assignment">${assignmentOptions(assignments)}</select><div id="marks-content" class="page-content"></div></section>`;
  const select = document.querySelector("#marks-assignment");
  const load = async () => {
    const assignmentId = select.value;
    const components = await api(`/assignments/${assignmentId}/components`);
    const componentOptions = components.map((row) => `<option value="${row.component_id}">${esc(row.name)} (max ${row.max_marks}, ${row.weightage}%)</option>`).join("");
    document.querySelector("#marks-content").innerHTML = `${state.user.role === "professor" ? `<form id="component-form" class="panel"><h3>Add evaluation component</h3><div class="form-grid"><label>Name<input id="component-name" required maxlength="100"></label><label>Max marks<input id="component-max" type="number" min="0.01" step="0.01" required></label><label>Weightage<input id="component-weight" type="number" min="1" max="100" step="0.01" required></label></div><div class="form-actions"><button class="button button-primary">Add component</button></div></form>` : ""}<section class="panel"><h3>Components</h3><div class="table-wrap"><table><thead><tr><th>ID</th><th>Name</th><th>Max marks</th><th>Weightage</th></tr></thead><tbody>${components.map((row) => `<tr><td>${row.component_id}</td><td>${esc(row.name)}</td><td>${row.max_marks}</td><td>${row.weightage}%</td></tr>`).join("") || "<tr><td colspan=4>No components found.</td></tr>"}</tbody></table></div></section>${state.user.role === "professor" && components.length ? `<form id="marks-form" class="panel"><h3>Bulk upload marks</h3><label>Component<select id="marks-component">${componentOptions}</select></label><label>Marks JSON<textarea id="marks-json" rows="5" placeholder='[{"enrollment_id": 1, "marks_obtained": 82}]' required></textarea></label><div class="form-actions"><button class="button button-primary">Save marks</button></div></form>` : ""}<section id="component-marks"></section>`;
    if (state.user.role === "professor") document.querySelector("#component-form").addEventListener("submit", async (event) => { event.preventDefault(); try { await api(`/assignments/${assignmentId}/components`, { method: "POST", body: JSON.stringify({ name: document.querySelector("#component-name").value.trim(), max_marks: Number(document.querySelector("#component-max").value), weightage: Number(document.querySelector("#component-weight").value) }) }); notice("Evaluation component added."); load(); } catch (error) { notice(error.message, true); } });
    if (state.user.role === "professor" && components.length) document.querySelector("#marks-form").addEventListener("submit", async (event) => { event.preventDefault(); try { const componentId = Number(document.querySelector("#marks-component").value); const marks = JSON.parse(document.querySelector("#marks-json").value); await api(`/assignments/${assignmentId}/marks/bulk`, { method: "POST", body: JSON.stringify({ component_id: componentId, marks }) }); notice("Marks saved successfully."); } catch (error) { notice(error.message, true); } });
    if (components.length) { const marks = await api(`/assignments/components/${components[0].component_id}/marks`); document.querySelector("#component-marks").innerHTML = `<section class="panel"><h3>Saved marks</h3><div class="table-wrap"><table><thead><tr><th>Enrollment</th><th>Student</th><th>Marks</th><th>Entered</th></tr></thead><tbody>${marks.map((row) => `<tr><td>${row.enrollment_id}</td><td>${row.student_id}</td><td>${row.marks_obtained}</td><td>${esc(row.entered_at)}</td></tr>`).join("") || "<tr><td colspan=4>No marks found.</td></tr>"}</tbody></table></div></section>`; }
  };
  if (assignments.length) { select.addEventListener("change", load); await load(); } else document.querySelector("#marks-content").innerHTML = unavailable("No assignments", "Create a teaching assignment first.");
}

async function renderGradeScale() {
  const rows = await api("/results/grade-scale");
  ui.content.innerHTML = `<section class="panel"><p class="eyebrow">Result rules</p><h2>Grade scale</h2><div class="table-wrap"><table><thead><tr><th>Grade</th><th>Minimum marks</th><th>Grade points</th></tr></thead><tbody>${rows.map((row) => `<tr><td>${esc(row.letter_grade)}</td><td>${row.min_marks ?? "—"}</td><td>${row.grade_points}</td></tr>`).join("")}</tbody></table></div></section>`;
}

async function renderTranscript() {
  const [summary, transcript, backlogs] = await Promise.all([api("/results/me/summary"), api("/results/me/transcript"), api("/results/me/backlogs")]);
  ui.content.innerHTML = `<section class="card-grid"><article class="card"><strong>${summary.cgpa ?? "—"}</strong><p>CGPA</p></article><article class="card"><strong>${summary.backlog_count}</strong><p>Current backlogs</p></article><article class="card"><strong>${transcript.length}</strong><p>Published subjects</p></article></section><section class="panel"><p class="eyebrow">Academic record</p><h2>Transcript</h2><form id="sgpa-form" class="inline-form"><label for="sgpa-semester">Semester</label><input id="sgpa-semester" type="number" min="1" required><button class="button button-secondary">Calculate SGPA</button><strong id="sgpa-result"></strong></form><div class="table-wrap"><table><thead><tr><th>Subject</th><th>Semester</th><th>Marks</th><th>Grade</th><th>Status</th></tr></thead><tbody>${transcript.map((row) => `<tr><td>${esc(row.subject_code)} — ${esc(row.subject_name)}</td><td>${row.semester_no}</td><td>${row.total_marks ?? "—"}</td><td>${esc(row.grade)}</td><td>${esc(row.result_status)}</td></tr>`).join("") || "<tr><td colspan=5>No published results yet.</td></tr>"}</tbody></table></div></section>${backlogs.length ? `<section class="panel"><h2>Backlogs</h2><p>${backlogs.map((row) => `${esc(row.subject_code)} (${esc(row.grade)})`).join(", ")}</p></section>` : ""}`;
  document.querySelector("#sgpa-form").addEventListener("submit", async (event) => { event.preventDefault(); try { const semester = Number(document.querySelector("#sgpa-semester").value); const result = await api(`/results/me/sgpa/${semester}`); document.querySelector("#sgpa-result").textContent = `SGPA: ${result.sgpa ?? "—"}`; } catch (error) { notice(error.message, true); } });
}

async function renderRevaluation() {
  const rows = await api("/results/revaluation");
  const create = state.user.role === "student" ? `<aside class="panel"><h3>Request revaluation</h3><form id="revaluation-form"><label>Enrollment ID<input id="reval-enrollment" type="number" min="1" required></label><label>Component ID<input id="reval-component" type="number" min="1" required></label><label>Reason<textarea id="reval-reason" rows="4" required></textarea></label><label>Window (days)<input id="reval-window" type="number" min="1" max="90" value="15" required></label><div class="form-actions"><button class="button button-primary">Submit request</button></div></form></aside>` : state.user.role === "admin" ? `<aside class="panel"><h3>Administrator view</h3><p class="subtle">Administrators can review request status. Decisions remain restricted to the assigned professor.</p></aside>` : "";
  ui.content.innerHTML = `<div class="split-layout"><section class="panel"><p class="eyebrow">Academic review</p><h2>Revaluation requests</h2><div class="table-wrap"><table><thead><tr><th>Request</th><th>Enrollment</th><th>Component</th><th>Reason</th><th>Status</th><th>Decision</th></tr></thead><tbody>${rows.map((row) => `<tr><td>${row.request_id}</td><td>${row.enrollment_id}</td><td>${row.component_id}</td><td>${esc(row.reason)}</td><td>${esc(row.revaluation_status)}</td><td>${state.user.role === "professor" && !row.decision ? `<button class="button button-secondary button-small" data-reval-decision="${row.request_id}" data-decision="Approved">Approve</button> <button class="button button-danger button-small" data-reval-decision="${row.request_id}" data-decision="Rejected">Reject</button>` : esc(row.decision || "Pending")}</td></tr>`).join("") || "<tr><td colspan=6>No requests found.</td></tr>"}</tbody></table></div></section>${create}</div>`;
  if (state.user.role === "student") document.querySelector("#revaluation-form").addEventListener("submit", async (event) => { event.preventDefault(); const data = { enrollment_id: Number(document.querySelector("#reval-enrollment").value), component_id: Number(document.querySelector("#reval-component").value), reason: document.querySelector("#reval-reason").value.trim(), window_days: Number(document.querySelector("#reval-window").value) }; try { await api("/results/revaluation", { method: "POST", body: JSON.stringify(data) }); notice("Revaluation request submitted."); renderRevaluation(); } catch (error) { notice(error.message, true); } });
  document.querySelectorAll("[data-reval-decision]").forEach((button) => button.addEventListener("click", async () => { const decision = button.dataset.decision; let newMarks = null; if (decision === "Approved") { const value = window.prompt("Enter the new marks:"); if (value === null) return; newMarks = Number(value); } try { await api(`/results/revaluation/${button.dataset.revalDecision}`, { method: "PATCH", body: JSON.stringify({ decision, new_marks: newMarks }) }); notice("Revaluation decision saved."); renderRevaluation(); } catch (error) { notice(error.message, true); } }));
}

async function renderProfile() {
  if (state.user.role === "professor") {
    const professor = await api("/professors/me");
    const fields = [["Employee ID", professor.employee_id], ["Name", professor.name], ["Email", professor.email], ["Designation", professor.designation], ["Department", `${professor.department_name} (${professor.department_code})`]];
    ui.content.innerHTML = `<section class="panel"><p class="eyebrow">Professor profile</p><h2>${esc(professor.name)}</h2><dl class="profile-list">${fields.map(([label, value]) => `<div><dt>${esc(label)}</dt><dd>${esc(value)}</dd></div>`).join("")}</dl></section>`;
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
  ui.content.innerHTML = `<div class="split-layout"><section class="panel"><div class="section-heading"><div><p class="eyebrow">Admin only</p><h2>Users</h2></div><p class="subtle">${rows.length} total</p></div><div class="table-wrap"><table><thead><tr><th>Name</th><th>Username</th><th>Email</th><th>Role</th><th>Actions</th></tr></thead><tbody>${rows.map((row) => `<tr><td>${esc(row.name)}</td><td>${esc(row.username)}</td><td>${esc(row.email)}</td><td>${esc(row.role)}</td><td class="row-actions"><button class="button button-secondary button-small" data-edit-user="${row.user_id}">Edit</button><button class="button button-danger button-small" data-delete-user="${row.user_id}">Delete</button></td></tr>`).join("")}</tbody></table></div></section><aside class="panel"><h3 id="user-title">Edit user</h3><p class="subtle">Select Edit to load a user. Deleting a user removes any linked student or professor profile.</p><form id="user-form" hidden><input id="user-id" type="hidden"><label for="user-name">Name</label><input id="user-name" required><label for="user-username">Username</label><input id="user-username" required><label for="user-email">Email</label><input id="user-email" type="email" required><label><input id="user-admin" type="checkbox"> Administrator account</label><div class="form-actions"><button class="button button-primary">Save user</button><button id="user-cancel" class="button button-secondary" type="button">Cancel</button></div></form></aside></div><section class="registration-grid"><form id="student-registration-form" class="panel"><p class="eyebrow">Create account</p><h3>Register student</h3><label>Username<input name="username" required maxlength="50"></label><label>Email<input name="email" type="email" required></label><label>Full name<input name="name" required maxlength="100"></label><label>Password<input name="password" type="password" minlength="8" required></label><label>Roll number<input name="roll_no" required maxlength="20"></label><label>Admission year<input name="admission_year" type="number" min="2000" required></label><label>Current semester<input name="current_semester" type="number" min="1" max="12" required></label><label>Department code<input name="department_code" required maxlength="10" placeholder="CSE"></label><div class="form-actions"><button class="button button-primary">Create student</button></div></form><form id="professor-registration-form" class="panel"><p class="eyebrow">Create account</p><h3>Register professor</h3><label>Username<input name="username" required maxlength="50"></label><label>Email<input name="email" type="email" required></label><label>Full name<input name="name" required maxlength="100"></label><label>Password<input name="password" type="password" minlength="8" required></label><label>Employee ID<input name="employee_id" required maxlength="20"></label><label>Designation<input name="designation" required maxlength="100"></label><label>Department code<input name="department_code" required maxlength="10" placeholder="CSE"></label><div class="form-actions"><button class="button button-primary">Create professor</button></div></form></section>`;
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
  document.querySelector("#student-registration-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form));
    data.admission_year = Number(data.admission_year);
    data.current_semester = Number(data.current_semester);
    try { await api("/students/", { method: "POST", body: JSON.stringify(data) }); notice("Student created successfully."); form.reset(); renderUsers(); } catch (error) { notice(error.message, true); }
  });
  document.querySelector("#professor-registration-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form));
    try { await api("/professors/", { method: "POST", body: JSON.stringify(data) }); notice("Professor created successfully."); form.reset(); renderUsers(); } catch (error) { notice(error.message, true); }
  });
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
