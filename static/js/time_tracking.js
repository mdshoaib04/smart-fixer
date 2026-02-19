/**
 * PRODUCTION-LEVEL TIME TRACKER & THEME ENGINE
 * Features:
 * - Real-time Stop Watch (hh:mm:ss)
 * - Heartbeat Sync (30s)
 * - Instagram-style Weekly Graph
 * - Feb 2026 Calendar Modal
 * - Persistent Theme Toggle
 */

let sessionSeconds = 0;
let todayTotalSeconds = 0;
let isTabActive = true;
let heartbeatInterval;
let timerInterval;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    fetchStats();
    startStopwatch();
    startHeartbeat();

    document.addEventListener('visibilitychange', () => {
        isTabActive = (document.visibilityState === 'visible');
        if (isTabActive) fetchStats();
    });
});

// --- THEME SYSTEM ---
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.body.setAttribute('data-theme', theme);
    document.body.classList.toggle('dark-mode', theme === 'dark');
    localStorage.setItem('theme', theme);

    // Update icons
    const moon = document.querySelector('.theme-icon.moon');
    const sun = document.querySelector('.theme-icon.sun');
    if (moon && sun) {
        if (theme === 'dark') {
            moon.style.display = 'none';
            sun.style.display = 'block';
        } else {
            moon.style.display = 'block';
            sun.style.display = 'none';
        }
    }
}

// --- TRACKING LOGIC ---
function startStopwatch() {
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        if (isTabActive) {
            sessionSeconds++;
            todayTotalSeconds++;
            updateTimerDisplays();
        }
    }, 1000);
}

function startHeartbeat() {
    if (heartbeatInterval) clearInterval(heartbeatInterval);
    heartbeatInterval = setInterval(async () => {
        if (isTabActive) {
            await syncTime(30);
            fetchStats(); // Update graph and stats after sync
        }
    }, 30000);
}

async function syncTime(secs) {
    try {
        const res = await fetch('/api/track-time', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ seconds: secs })
        });
        const data = await res.json();
        if (data.success) {
            // Re-sync with server if drift is high
            if (Math.abs(data.today_seconds - todayTotalSeconds) > 5) {
                todayTotalSeconds = data.today_seconds;
            }
        }
    } catch (e) { console.error('Time sync failed', e); }
}

async function fetchStats() {
    try {
        const res = await fetch('/api/time-stats');
        const data = await res.json();
        if (data.success) {
            todayTotalSeconds = data.stats.today_seconds || 0;
            updateUI(data);
        }
    } catch (e) { console.error('Stats fetch failed', e); }
}

function updateTimerDisplays() {
    const sessionStr = formatHHMMSS(sessionSeconds);
    const todayStr = formatHHMMSS(todayTotalSeconds);

    const sessionEl = document.getElementById('session-timer-display');
    const todayEl = document.getElementById('stat-today');

    if (sessionEl) sessionEl.textContent = sessionStr;
    if (todayEl) todayEl.textContent = todayStr;
}

function formatHHMMSS(totalSecs) {
    const h = Math.floor(totalSecs / 3600);
    const m = Math.floor((totalSecs % 3600) / 60);
    const s = totalSecs % 60;
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

// --- UI RENDERING ---
function updateUI(data) {
    updateTimerDisplays();

    // Summaries
    setElText('stat-month', data.stats.month_summary);
    setElText('stat-year', data.stats.year_summary);
    setElText('stat-streak', data.stats.current_streak);
    setElText('stat-longest-streak', data.stats.longest_streak);
    setElText('daily-avg-value', data.stats.daily_average);

    renderInstagramGraph(data.weekly_bars);
    window.dailyMap = data.history; // for calendar
}

function setElText(id, txt) {
    const el = document.getElementById(id);
    if (el) el.textContent = txt;
}

// --- INSTAGRAM GRAPH ---
function renderInstagramGraph(bars) {
    const container = document.getElementById('instagram-graph-bars');
    const avgEl = document.getElementById('daily-avg-display');
    if (!container) return;
    container.innerHTML = '';

    // Convert seconds to hours for all bars
    const hoursData = bars.map(b => b.seconds / 3600);
    const maxHours = Math.max(...hoursData, 1); // Ensure at least 1h for scale if all 0

    bars.forEach((bar, index) => {
        const hours = bar.seconds / 3600;
        const heightPercent = (hours / maxHours) * 100;

        const barWrapper = document.createElement('div');
        barWrapper.className = 'ig-bar-wrapper';

        const barFill = document.createElement('div');
        barFill.className = 'ig-bar-fill';
        // Today is the last bar, reference image style
        if (!bar.is_today) {
            barFill.classList.add('dimmed');
        }

        // Height proportional to hours
        barFill.style.height = `${Math.max(heightPercent, 2)}%`;

        const label = document.createElement('div');
        label.className = 'ig-bar-label';
        if (bar.is_today) label.classList.add('active');
        label.textContent = bar.is_today ? 'Today' : bar.label.substring(0, 3); // Fri, Sat, etc.

        barWrapper.appendChild(barFill);
        barWrapper.appendChild(label);
        container.appendChild(barWrapper);
    });

    // Update Daily Average Display at the top of the graph section
    if (avgEl && bars.length > 0) {
        const totalSecs = bars.reduce((acc, b) => acc + b.seconds, 0);
        const avgSecs = totalSecs / bars.length;
        const h = Math.floor(avgSecs / 3600);
        const m = Math.floor((avgSecs % 3600) / 60);
        avgEl.textContent = `${h}h ${m}m`;
    }
}

// --- CALENDAR MODAL ---
function openCalendarModal() {
    const modal = document.getElementById('calendarModal');
    if (modal) {
        modal.style.display = 'block';
        renderCalendar(2026, 1); // Feb 2026
    }
}

function closeCalendarModal() {
    const modal = document.getElementById('calendarModal');
    if (modal) modal.style.display = 'none';
}

function renderCalendar(year, month) {
    const grid = document.getElementById('calendar-grid');
    if (!grid) return;
    grid.innerHTML = '';

    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    const offset = (firstDay === 0) ? 6 : firstDay - 1;

    for (let i = 0; i < offset; i++) {
        const div = document.createElement('div');
        div.className = 'calendar-day empty';
        grid.appendChild(div);
    }

    for (let d = 1; d <= daysInMonth; d++) {
        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
        const secs = window.dailyMap ? (window.dailyMap[dateStr] || 0) : 0;

        const dayDiv = document.createElement('div');
        dayDiv.className = 'calendar-day';
        if (secs > 0) dayDiv.classList.add('active');
        if (d === 20 && month === 1 && year === 2026) dayDiv.classList.add('today-highlight');

        dayDiv.textContent = d;

        const tip = document.createElement('div');
        tip.className = 'cal-tooltip';
        tip.textContent = `${dateStr} → ${formatHHMMSS_long(secs)}`;
        dayDiv.appendChild(tip);

        grid.appendChild(dayDiv);
    }
}

function formatHHMMSS_long(s) {
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = s % 60;
    return `${String(h).padStart(2, '0')}h ${String(m).padStart(2, '0')}m ${String(sec).padStart(2, '0')}s`;
}

window.toggleTheme = toggleTheme;
window.openCalendarModal = openCalendarModal;
window.closeCalendarModal = closeCalendarModal;
window.initTheme = initTheme;
