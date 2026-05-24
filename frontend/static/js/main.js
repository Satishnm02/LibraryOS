/* ─── LibraryOS Main JS ─────────────────────────────── */

// ── THEME TOGGLE ─────────────────────────────────────
const root        = document.documentElement;
const themeToggle = document.getElementById('themeToggle');
const saved       = localStorage.getItem('lms_theme') || 'light';
root.setAttribute('data-theme', saved);
updateThemeIcon(saved);

themeToggle?.addEventListener('click', () => {
  const current = root.getAttribute('data-theme');
  const next    = current === 'light' ? 'dark' : 'light';
  root.setAttribute('data-theme', next);
  localStorage.setItem('lms_theme', next);
  updateThemeIcon(next);
});

function updateThemeIcon(theme) {
  if (!themeToggle) return;
  themeToggle.innerHTML = theme === 'dark'
    ? '<i class="bi bi-sun-fill"></i>'
    : '<i class="bi bi-moon-stars-fill"></i>';
}

// ── SIDEBAR TOGGLE (mobile) ───────────────────────────
document.getElementById('sidebarToggle')?.addEventListener('click', () => {
  document.getElementById('sidebar')?.classList.toggle('open');
});

// ── EDIT BOOK MODAL ───────────────────────────────────
document.getElementById('editBookModal')?.addEventListener('show.bs.modal', e => {
  const btn = e.relatedTarget;
  document.getElementById('edit_title').value     = btn.dataset.title;
  document.getElementById('edit_author').value    = btn.dataset.author;
  document.getElementById('edit_isbn').value      = btn.dataset.isbn;
  document.getElementById('edit_publisher').value = btn.dataset.publisher;
  document.getElementById('edit_year').value      = btn.dataset.year;
  document.getElementById('edit_qty').value       = btn.dataset.qty;
  document.getElementById('edit_catid').value     = btn.dataset.catid;
  document.getElementById('editBookForm').action  = `/books/edit/${btn.dataset.id}`;
});

// ── EDIT MEMBER MODAL ─────────────────────────────────
document.getElementById('editMemberModal')?.addEventListener('show.bs.modal', e => {
  const btn = e.relatedTarget;
  document.getElementById('em_name').value   = btn.dataset.name;
  document.getElementById('em_email').value  = btn.dataset.email;
  document.getElementById('em_phone').value  = btn.dataset.phone;
  document.getElementById('em_dept').value   = btn.dataset.dept;
  document.getElementById('em_status').value = btn.dataset.status;
  document.getElementById('editMemberForm').action = `/members/edit/${btn.dataset.id}`;
});

// ── TABS (works for reports AND requests pages) ───────
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    // find the parent tabs-container
    const container = btn.closest('.tabs-container');
    if (!container) return;
    // deactivate all buttons and panels in THIS container only
    container.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    container.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    // activate clicked button and matching panel
    btn.classList.add('active');
    const tabId = btn.dataset.tab;
    const panel = container.querySelector(`#tab-${tabId}`);
    if (panel) panel.classList.add('active');
  });
});

// ── PRINT TABLE ───────────────────────────────────────
function printTable(panelId) {
  const content = document.getElementById(panelId).innerHTML;
  const win     = window.open('', '_blank');
  win.document.write(`
    <html><head><title>LibraryOS Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet"/>
    <style>body{padding:20px;font-family:sans-serif}table{width:100%}th,td{border:1px solid #ddd;padding:8px}thead{background:#6366f1;color:#fff}</style>
    </head><body>${content}</body></html>`);
  win.document.close();
  win.print();
}

// ── AUTO-DISMISS FLASH MESSAGES ───────────────────────
setTimeout(() => {
  document.querySelectorAll('.toast-msg').forEach(t => {
    t.style.transition = 'opacity .5s';
    t.style.opacity    = '0';
    setTimeout(() => t.remove(), 500);
  });
}, 4000);