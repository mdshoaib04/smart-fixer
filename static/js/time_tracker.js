/**
 * time_tracker.js — UI only. No backend routes modified.
 * Handles: session timer, stats display, Instagram graph, calendar modal with tooltips.
 */

// ─── State ───────────────────────────────────────────────────────────────────
let totalSessionSeconds = 0;
let heartbeatInterval = null;
let isTabActive = true;
let cachedDailyData = {}; // date-string -> seconds (from /api/time-stats daily_breakdown)

// Calendar state
let calCurrentYear = new Date().getFullYear();
let calCurrentMonth = new Date().getMonth(); // 0-indexed

// ─── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  initTheme();
  startSessionTimer();
  startHeartbeat();
  fetchStats();
  wireButtons();
});

// ─── Theme ────────────────────────────────────────────────────────────────────
function initTheme() {
  const saved = localStorage.getItem('ttTheme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon(saved);
}

function toggleTheme() {
  const root = document.documentElement;
  const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  root.setAttribute('data-theme', next);
  localStorage.setItem('ttTheme', next);
  updateThemeIcon(next);
}

function updateThemeIcon(theme) {
  const icon = document.querySelector('#themeToggle i');
  if (!icon) return;
  icon.className = theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
}

// ─── Wire Buttons ─────────────────────────────────────────────────────────────
function wireButtons() {
  const backBtn = document.getElementById('backBtn');
  const themeBtn = document.getElementById('themeToggle');
  const monthBtn = document.getElementById('monthStatsBtn');
  const overlay = document.getElementById('calModalOverlay');
  const closeBtn = document.getElementById('calCloseBtn');
  const prevBtn = document.getElementById('calPrevBtn');
  const nextBtn = document.getElementById('calNextBtn');

  if (backBtn) backBtn.onclick = () => window.history.back();
  if (themeBtn) themeBtn.onclick = toggleTheme;

  // "This Month" → open calendar
  if (monthBtn) monthBtn.onclick = openCalendar;

  // Close calendar by clicking overlay background or X
  if (overlay) overlay.addEventListener('click', function (e) {
    if (e.target === overlay) closeCalendar();
  });
  if (closeBtn) closeBtn.onclick = closeCalendar;

  // Month navigation
  if (prevBtn) prevBtn.onclick = () => { calCurrentMonth--; if (calCurrentMonth < 0) { calCurrentMonth = 11; calCurrentYear--; } renderCalendar(); };
  if (nextBtn) nextBtn.onclick = () => { calCurrentMonth++; if (calCurrentMonth > 11) { calCurrentMonth = 0; calCurrentYear++; } renderCalendar(); };

  // Tab visibility tracking
  document.addEventListener('visibilitychange', () => { isTabActive = !document.hidden; });
}

// ─── Session Timer (synced from server) ──────────────────────────────────────
async function startSessionTimer() {
  // Ask the server how long this session has been running
  try {
    const res = await fetch('/api/session-info');
    const data = await res.json();
    if (data.logged_in && data.elapsed_seconds > 0) {
      totalSessionSeconds = data.elapsed_seconds;
    }
  } catch (e) { /* start from 0 if API fails */ }

  setInterval(() => {
    if (!isTabActive) return; // pause timer when tab is hidden
    totalSessionSeconds++;
    const h = Math.floor(totalSessionSeconds / 3600);
    const m = Math.floor((totalSessionSeconds % 3600) / 60);
    const s = totalSessionSeconds % 60;
    const el = document.getElementById('session-timer-display');
    if (el) el.textContent = [h, m, s].map(v => String(v).padStart(2, '0')).join(':');
  }, 1000);
}

// ─── Heartbeat: sync + refresh stats every 30s ────────────────────────────────
function startHeartbeat() {
  if (heartbeatInterval) clearInterval(heartbeatInterval);
  heartbeatInterval = setInterval(() => {
    if (isTabActive) fetchStats();
  }, 30000);
}

// ─── Fetch stats from existing endpoint (READ-ONLY frontend call) ─────────────
async function fetchStats() {
  try {
    const res = await fetch('/api/time-stats');
    if (!res.ok) return;
    const data = await res.json();
    if (!data.success) return;

    const stats = data.stats;

    // Update stat cards using formatted summary strings from backend
    setEl('today-hrs', stats.today_summary || '0h 0m');
    setEl('week-hrs', stats.week_summary || '0h 0m');
    setEl('month-hrs', stats.month_summary || '0h 0m');

    // Streaks
    setEl('longest-streak', `${stats.longest_streak || 0} days`);
    setEl('current-streak', `${stats.current_streak || 0} days 🔥`);

    // Cache daily_map for calendar tooltips: { 'YYYY-MM-DD': seconds }
    if (data.daily_map) {
      cachedDailyData = data.daily_map;
    }

    // Instagram graph
    if (data.weekly_bars && data.weekly_bars.length) {
      renderInstagramGraph(data.weekly_bars);
    }
  } catch (e) {
    console.warn('fetchStats error:', e);
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
function setEl(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function formatHours(seconds) {
  if (!seconds) return '0.0';
  const h = seconds / 3600;
  return h >= 10 ? h.toFixed(0) : h.toFixed(1);
}

function fmtHM(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return `${h}h ${m.toString().padStart(2, '0')}m`;
}

function fmtDateLabel(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

// ─── Instagram Graph ──────────────────────────────────────────────────────────
function renderInstagramGraph(bars) {
  const container = document.getElementById('instagram-graph-bars');
  const avgEl = document.getElementById('daily-avg-display');
  if (!container) return;
  container.innerHTML = '';

  const maxSec = Math.max(...bars.map(b => b.seconds), 1);

  bars.forEach(bar => {
    const pct = (bar.seconds / maxSec) * 100;

    const wrapper = document.createElement('div');
    wrapper.className = 'ig-bar-wrapper';

    const fill = document.createElement('div');
    fill.className = 'ig-bar-fill' + (bar.is_today ? '' : ' dimmed');
    fill.style.height = Math.max(pct, 2) + '%';

    const label = document.createElement('div');
    label.className = 'ig-bar-label' + (bar.is_today ? ' active' : '');
    label.textContent = bar.is_today ? 'Today' : (bar.label || '').substring(0, 3);

    wrapper.appendChild(fill);
    wrapper.appendChild(label);
    container.appendChild(wrapper);
  });

  if (avgEl && bars.length) {
    const avg = bars.reduce((a, b) => a + b.seconds, 0) / bars.length;
    avgEl.textContent = fmtHM(avg);
  }
}

// ─── Calendar Modal ───────────────────────────────────────────────────────────
function openCalendar() {
  const now = new Date();
  calCurrentYear = now.getFullYear();
  calCurrentMonth = now.getMonth();
  renderCalendar();
  document.getElementById('calModalOverlay').classList.add('open');
}

function closeCalendar() {
  document.getElementById('calModalOverlay').classList.remove('open');
}

function renderCalendar() {
  const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'];

  document.getElementById('calMonthLabel').textContent =
    `${MONTHS[calCurrentMonth]}, ${calCurrentYear}`;

  const grid = document.getElementById('calDaysGrid');
  grid.innerHTML = '';

  const today = new Date();
  const firstDay = new Date(calCurrentYear, calCurrentMonth, 1).getDay(); // 0=Sun
  const daysInMonth = new Date(calCurrentYear, calCurrentMonth + 1, 0).getDate();
  const daysInPrev = new Date(calCurrentYear, calCurrentMonth, 0).getDate();

  // Leading empty cells (greyed previous month days)
  for (let i = 0; i < firstDay; i++) {
    const day = daysInPrev - firstDay + 1 + i;
    const cell = makeDayCell(day, true, false, null, null);
    grid.appendChild(cell);
  }

  // This month's days
  for (let d = 1; d <= daysInMonth; d++) {
    const dateObj = new Date(calCurrentYear, calCurrentMonth, d);
    const iso = dateObj.toISOString().slice(0, 10);
    const isToday = (dateObj.toDateString() === today.toDateString());
    const seconds = cachedDailyData[iso] || 0;
    const cell = makeDayCell(d, false, isToday, iso, seconds);
    grid.appendChild(cell);
  }

  // Trailing empty cells (next month days)
  const totalCells = firstDay + daysInMonth;
  const trailingCount = totalCells % 7 === 0 ? 0 : 7 - (totalCells % 7);
  for (let i = 1; i <= trailingCount; i++) {
    const cell = makeDayCell(i, true, false, null, null);
    grid.appendChild(cell);
  }
}

function makeDayCell(dayNum, outsideMonth, isToday, isoDate, seconds) {
  const cell = document.createElement('div');

  let cls = 'cal-day';
  if (outsideMonth) cls += ' outside-month';
  if (isToday) cls += ' today';
  if (!outsideMonth && seconds > 0) cls += ' has-data';
  cell.className = cls;
  cell.textContent = dayNum;

  // Tooltip: only for days in this month with data
  if (!outsideMonth && isoDate) {
    const tip = document.createElement('div');
    tip.className = 'cal-day-tooltip';
    const dateLabel = fmtDateLabel(isoDate);
    const timeLabel = seconds > 0 ? fmtHM(seconds) : 'No data';
    tip.innerHTML = `<strong>${dateLabel}</strong><br>${timeLabel}`;
    cell.appendChild(tip);
  }

  return cell;
}