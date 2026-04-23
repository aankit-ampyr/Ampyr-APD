// ============================================================
// APP ORCHESTRATOR — Navigation, month switching, initialization
// ============================================================
import { MONTHS, DEFAULT_MONTH } from './constants.js';
import { loadAllMonths, getAllData, getMonthData } from './data.js';
import { initChartDefaults } from './charts/chart-defaults.js';
import * as overview from './charts/overview.js';
import * as executive from './charts/executive.js';
import * as benchmarks from './charts/benchmarks.js';
import * as operations from './charts/operations.js';
import * as optimization from './charts/optimization.js';
import * as market from './charts/market.js';
import * as imbalance from './charts/imbalance.js';
import * as health from './charts/health.js';

let selectedMonth = DEFAULT_MONTH;
let currentPage = 'overview';
const renderedPages = new Set();

// Page module map
const pageModules = {
  overview:     { module: overview,     type: 'multi' },
  executive:    { module: executive,    type: 'multi' },
  benchmarks:   { module: benchmarks,   type: 'multi' },
  operations:   { module: operations,   type: 'single' },
  optimization: { module: optimization, type: 'single' },
  market:       { module: market,       type: 'single' },
  imbalance:    { module: imbalance,    type: 'single' },
  health:       { module: health,       type: 'single' },
};

function renderPage(pageId) {
  const pm = pageModules[pageId];
  if (!pm) return; // static page (invoices, asset)

  const allData = getAllData();
  if (allData.size === 0) return;

  if (pm.type === 'multi') {
    pm.module.render(allData, selectedMonth);
  } else {
    const monthData = getMonthData(selectedMonth);
    if (monthData) pm.module.render(monthData, selectedMonth);
  }
  renderedPages.add(pageId);
}

function navigate(pageId) {
  // Update sidebar
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const navItem = document.querySelector(`.nav-item[data-page="${pageId}"]`);
  if (navItem) navItem.classList.add('active');

  // Toggle pages
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const pageEl = document.getElementById('page-' + pageId);
  if (pageEl) pageEl.classList.add('active');

  currentPage = pageId;

  // Lazy render on first visit
  if (!renderedPages.has(pageId)) {
    renderPage(pageId);
  }
}

function onMonthChange(monthKey) {
  selectedMonth = monthKey;

  // Re-render single-month pages that have been previously rendered
  for (const [pageId, pm] of Object.entries(pageModules)) {
    if (pm.type === 'single' && renderedPages.has(pageId)) {
      renderPage(pageId);
    }
  }

  // Update multi-month pages' selected month highlight (re-render overview donut etc.)
  if (renderedPages.has('overview')) renderPage('overview');
}

function showLoading(show) {
  const el = document.getElementById('loading-overlay');
  if (el) el.style.display = show ? 'flex' : 'none';
}

// ============================================================
// INIT
// ============================================================
document.addEventListener('DOMContentLoaded', async () => {
  initChartDefaults();

  // Navigation
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => navigate(item.dataset.page));
  });

  // Month selector
  const monthSelect = document.getElementById('monthSelector');
  if (monthSelect) {
    monthSelect.addEventListener('change', () => onMonthChange(monthSelect.value));
  }

  // Tab bars (static toggle)
  document.querySelectorAll('.tab-bar').forEach(bar => {
    bar.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        bar.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });
  });

  // Load data
  showLoading(true);
  try {
    await loadAllMonths();
    showLoading(false);
    // Render initial page
    renderPage('overview');
    // Initialize Lucide icons
    if (window.lucide) lucide.createIcons();
  } catch (err) {
    showLoading(false);
    console.error('Failed to load data:', err);
    const el = document.getElementById('loading-overlay');
    if (el) {
      el.style.display = 'flex';
      el.innerHTML = `<div style="text-align:center;color:var(--danger)">
        <p style="font-size:1.25rem;font-weight:600">Failed to load data</p>
        <p style="color:var(--text-secondary);margin-top:8px">${err.message}</p>
        <p style="color:var(--text-muted);margin-top:16px;font-size:0.8rem">
          Make sure you're running a local server from the project root:<br>
          <code style="color:var(--brand-primary)">cd C:\\repos\\Ampyr-APD && python -m http.server 8000</code><br>
          Then open <code>http://localhost:8000/design/index.html</code>
        </p>
      </div>`;
    }
  }
});
