// ══════════════════════════════════════
// BILIM AL — Main JavaScript
// ══════════════════════════════════════

let currentTask = null;

// ── ТАПСЫРМА ГЕНЕРАЦИЯСЫ ───────────────
async function generateTask() {
    const topic      = document.getElementById('topic').value;
    const difficulty = document.getElementById('difficulty').value;
    const btn        = document.getElementById('gen-btn');

    btn.disabled = true;
    btn.textContent = 'Генерациялануда...';

    const taskSection = document.getElementById('task-section');
    taskSection.style.display = 'block';
    document.getElementById('task-content').innerHTML =
        '<div class="loader"><div class="spinner"></div>AI тапсырманы генерациялауда...</div>';

    try {
        const res = await fetch('/tasks/generate_task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, difficulty, language: 'Python' })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        currentTask = { ...data, topic, difficulty };

        const hints = (data.hints || []).map(h => `<li>${h}</li>`).join('');
        document.getElementById('task-content').innerHTML = `
            <p style="font-weight:600; margin-bottom:0.5rem">${data.title}</p>
            <p style="font-size:13.5px; color:var(--text-secondary); line-height:1.65; margin-bottom:0.8rem">
                ${data.description}
            </p>
            ${hints ? `
            <div style="background:var(--amber-50); border-left:3px solid var(--amber-500);
                        padding:0.75rem 1rem; border-radius:var(--r-sm); margin-bottom:0.8rem">
                <div style="font-size:12px; font-weight:600; color:var(--amber-600); margin-bottom:0.4rem">
                    Кеңестер
                </div>
                <ul style="padding-left:1.2rem; font-size:13px; color:var(--amber-600)">
                    ${hints}
                </ul>
            </div>` : ''}
            <div style="font-size:12.5px; color:var(--text-muted); background:var(--surface-2);
                        padding:0.5rem 0.8rem; border-radius:var(--r-sm)">
                <strong>Күтілетін нәтиже:</strong> ${data.expected_output}
            </div>
        `;
    } catch (e) {
        document.getElementById('task-content').innerHTML =
            `<div class="alert alert-error">${e.message}</div>`;
    } finally {
        btn.disabled = false;
        btn.textContent = 'Тапсырма алу';
    }
}

// ── КОДТЫ ТЕКСЕРУ ─────────────────────
async function checkCode() {
    const code = document.getElementById('student-code').value.trim();
    if (!code) { alert('Код жазыңыз!'); return; }

    showResult('<div class="loader"><div class="spinner"></div>Код тексерілуде...</div>');

    try {
        const res = await fetch('/checker/check_code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                task_description: currentTask?.description || 'Python тапсырмасы',
                student_code: code,
                topic: currentTask?.topic || '',
                difficulty: currentTask?.difficulty || 'beginner',
                task_title: currentTask?.title || 'Тапсырма'
            })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        const cls = data.score >= 80 ? 'good' : data.score >= 50 ? 'medium' : 'bad';
        const label = data.is_correct ? 'Дұрыс' : 'Қателер бар';
        const suggestions = (data.suggestions || []).map(s => `<li>${s}</li>`).join('');

        showResult(`
            <div class="result-score ${cls}">${label} - ${data.score}/100</div>
            <p style="font-size:13.5px; line-height:1.65; margin-bottom:1rem">${data.feedback}</p>
            ${data.execution_result ? `
                <div style="font-size:12px; font-weight:600; color:var(--text-muted);
                            margin-bottom:0.4rem; text-transform:uppercase; letter-spacing:.05em">
                    Бағдарлама нәтижесі
                </div>
                <div class="output-block">${data.execution_result}</div>
            ` : ''}
            ${suggestions ? `
                <div style="font-size:12px; font-weight:600; color:var(--text-muted);
                            margin-bottom:0.4rem; text-transform:uppercase; letter-spacing:.05em">
                    Кеңестер
                </div>
                <ul style="padding-left:1.2rem; font-size:13.5px; color:var(--text-secondary);
                           display:flex; flex-direction:column; gap:0.3rem">
                    ${suggestions}
                </ul>
            ` : ''}
        `);
    } catch (e) {
        showResult(`<div class="alert alert-error">${e.message}</div>`);
    }
}

// ── ҚАТЕНІ ТҮСІНДІРУ ─────────────────
async function explainError() {
    const code = document.getElementById('student-code').value.trim();
    if (!code) { alert('Код жазыңыз!'); return; }

    showResult('<div class="loader"><div class="spinner"></div>Қате талдануда...</div>');

    try {
        const res = await fetch('/explainer/explain_error', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                code,
                error_message: 'Найди и объясни ошибку в коде',
                student_level: 'beginner'
            })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        showResult(`
            <div style="margin-bottom:1rem">
                <span style="font-size:12px; color:var(--text-muted)">Қате түрі</span><br>
                <code style="font-family:var(--font-mono); font-size:13px;
                             background:var(--red-50); color:var(--red-600);
                             padding:2px 8px; border-radius:4px">
                    ${data.error_type}
                </code>
            </div>
            <div style="margin-bottom:1rem">
                <div style="font-size:12px; font-weight:600; color:var(--text-muted);
                            margin-bottom:0.4rem; text-transform:uppercase; letter-spacing:.05em">
                    Түсіндірме
                </div>
                <p style="font-size:13.5px; line-height:1.65">${data.explanation}</p>
            </div>
            <div style="margin-bottom:1rem">
                <div style="font-size:12px; font-weight:600; color:var(--text-muted);
                            margin-bottom:0.4rem; text-transform:uppercase; letter-spacing:.05em">
                    Қалай түзету керек
                </div>
                <p style="font-size:13.5px; line-height:1.65">${data.fix_suggestion}</p>
            </div>
            ${data.example ? `
                <div style="font-size:12px; font-weight:600; color:var(--text-muted);
                            margin-bottom:0.4rem; text-transform:uppercase; letter-spacing:.05em">
                    Мысал
                </div>
                <div class="output-block">${data.example}</div>
            ` : ''}
        `);
    } catch (e) {
        showResult(`<div class="alert alert-error">${e.message}</div>`);
    }
}

// ── АВТОРИЗАЦИЯ ────────────────────────
async function loginUser() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    if (!username || !password) { showAuthError('Барлық өрістерді толтырыңыз'); return; }

    try {
        const res = await fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();

        if (!res.ok) {
            if (res.status === 403) {
                const parts = data.detail.split('|');
                const email = parts[1] || '';
                window.location.href = `/verify-email?username=${username}&email=${encodeURIComponent(email)}`;
                return;
            }
            throw new Error(data.detail);
        }

        window.location.href = '/quiz';

    } catch (e) { showAuthError(e.message); }
}

async function registerUser() {
    const full_name = document.getElementById('full_name').value.trim();
    const username  = document.getElementById('username').value.trim();
    const email     = document.getElementById('email').value.trim();
    const password  = document.getElementById('password').value;

    if (!username || !email || !password) {
        showAuthError('Барлық міндетті өрістерді толтырыңыз!'); return;
    }
    if (password.length < 6) {
        showAuthError('Құпиясөз кемінде 6 символ!'); return;
    }

    try {
        const res = await fetch('/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ full_name, username, email, password })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        window.location.href = `/verify-email?username=${username}&email=${encodeURIComponent(email)}`;

    } catch (e) { showAuthError(e.message); }
}

async function logout() {
    await fetch('/auth/logout', { method: 'POST' });
    window.location.href = '/login';
}

// ── ТАҚЫРЫП ────────────────────────────
function syncThemeControl() {
    const dark = document.documentElement.getAttribute('data-theme') === 'dark';
    const button = document.getElementById('theme-btn');
    if (button) {
        button.textContent = dark ? 'Күндізгі режим' : 'Түнгі режим';
        button.setAttribute('aria-pressed', String(dark));
    }
}

function toggleTheme() {
    const html = document.documentElement;
    const dark = html.getAttribute('data-theme') === 'dark';
    html.setAttribute('data-theme', dark ? 'light' : 'dark');
    localStorage.setItem('theme', dark ? 'light' : 'dark');
    syncThemeControl();
}

function toggleSidebar() {
    const nav = document.getElementById('sidebar');
    if (!nav) return;
    const open = nav.classList.toggle('open');
    document.querySelector('.header-menu')?.setAttribute('aria-expanded', String(open));
}

// ── HELPERS ────────────────────────────
function showResult(html) {
    const s = document.getElementById('result-section');
    if (!s) return;
    s.style.display = 'block';
    document.getElementById('result-content').innerHTML = html;
    s.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showAuthError(msg) {
    const el = document.getElementById('auth-error');
    if (!el) return;
    el.classList.remove('hidden');
    el.textContent = msg;
}

// ── CODE BLOCKS ────────────────────────
function initCodeBlocks() {
    document.querySelectorAll('.code-block').forEach(block => {
        const btn = block.querySelector('.code-copy-btn');
        const content = block.querySelector('.code-content');
        if (!btn || !content) return;

        btn.addEventListener('click', () => {
            navigator.clipboard.writeText(content.textContent.trim()).then(() => {
                btn.textContent = '✓ Көшірілді';
                btn.classList.add('copied');
                setTimeout(() => {
                    btn.textContent = 'Көшіру';
                    btn.classList.remove('copied');
                }, 2000);
            });
        });
    });
}

document.addEventListener('DOMContentLoaded', initCodeBlocks);

// Restore the selected theme and its accessible control state.
(function() {
    const theme = localStorage.getItem('theme');
    if (theme === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
    syncThemeControl();
})();