// ============================================================
// OVERVIEW PAGE — 4 charts + 6 KPIs + revenue table
// ============================================================
import { MONTHS, MODO_BENCHMARKS, COLORS, CAPACITY_MW } from '../constants.js';
import { calculateMonthlyRevenue, calculateAnnualPerMW, calculateOptimizedRevenue, calculateCaptureRate } from '../calculations.js';
import { formatGBP, formatPct } from '../formatters.js';
import { baseOptions, gbpYAxis, pctYAxis, legendBottom, destroyCharts } from './chart-defaults.js';

const charts = {};

export function render(allData, selectedMonth) {
  destroyCharts(charts);

  // Compute all months
  const monthMetrics = [];
  for (const m of MONTHS) {
    const d = allData.get(m.key);
    if (!d) continue;
    const rev = calculateMonthlyRevenue(d.master, m.key);
    const opt = calculateOptimizedRevenue(d.optimized);
    const annPerMW = calculateAnnualPerMW(rev.totalRevenue, m.days, CAPACITY_MW);
    const capture = calculateCaptureRate(rev.gbTotal, opt.multiTotal);
    monthMetrics.push({ ...m, rev, opt, annPerMW, capture });
  }

  const sel = monthMetrics.find(m => m.key === selectedMonth) || monthMetrics[monthMetrics.length - 1];

  // ---- KPI Cards ----
  setText('kpi-total-revenue', formatGBP(sel.rev.totalRevenue));
  setText('kpi-total-revenue-sub', `GB + CM + DUoS — ${sel.short}`);
  setText('kpi-capture-rate', formatPct(sel.capture, 1));
  setText('kpi-annual-mw', formatGBP(Math.round(sel.annPerMW)));
  setText('kpi-sffr', formatGBP(Math.round(sel.rev.sffr)));
  setText('kpi-cm', formatGBP(Math.round(sel.rev.cm)));

  // Prev month delta
  const selIdx = monthMetrics.findIndex(m => m.key === selectedMonth);
  if (selIdx > 0) {
    const prev = monthMetrics[selIdx - 1];
    const momPct = ((sel.rev.totalRevenue - prev.rev.totalRevenue) / prev.rev.totalRevenue * 100);
    setText('kpi-total-revenue-delta', `${momPct >= 0 ? '+' : ''}${momPct.toFixed(1)}% MoM`);
    setClass('kpi-total-revenue-delta', momPct >= 0 ? 'positive' : 'negative');
  }

  // Industry rating
  const rating = sel.annPerMW >= 88000 ? 'Above High' : sel.annPerMW >= 60000 ? 'Above Mid' : sel.annPerMW >= 36000 ? 'Below Mid' : 'Below Low';
  setText('kpi-annual-mw-delta', rating);

  // ---- Chart 1: Revenue Trend (stacked bar + Modo line) ----
  const labels = monthMetrics.map(m => m.short);
  charts.trend = new Chart(document.getElementById('revenueTrendChart'), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'GridBeyond', data: monthMetrics.map(m => m.rev.gbTotal), backgroundColor: COLORS.actual, borderRadius: 4, order: 3 },
        { label: 'Capacity Market', data: monthMetrics.map(m => m.rev.cm), backgroundColor: COLORS.cm, borderRadius: 4, order: 2 },
        { label: 'DUoS Net', data: monthMetrics.map(m => m.rev.duosCredit - m.rev.duosFixed), backgroundColor: COLORS.duos, borderRadius: 4, order: 1 },
        { label: 'Modo (£/mth)', data: monthMetrics.map(m => {
          const modo = MODO_BENCHMARKS[m.key] || 0;
          return (modo * CAPACITY_MW * m.days / 365);
        }), type: 'line', borderColor: COLORS.modo, backgroundColor: 'transparent', borderDash: [6, 4],
          pointRadius: 4, pointBackgroundColor: COLORS.modo, borderWidth: 2, order: 0 }
      ],
    },
    options: { ...baseOptions, plugins: { tooltip: { mode: 'index', intersect: false } }, scales: { x: { stacked: true }, y: { stacked: true, ...gbpYAxis } } },
  });

  // ---- Chart 2: Revenue Mix (donut for selected month) ----
  const mixData = [sel.rev.sffr, sel.rev.epex30DA + sel.rev.epexDA, sel.rev.ida1, sel.rev.idc, sel.rev.imbalanceRev - sel.rev.imbalanceCharge, sel.rev.cm];
  charts.mix = new Chart(document.getElementById('revenueMixChart'), {
    type: 'doughnut',
    data: {
      labels: ['SFFR', 'EPEX DA', 'IDA1', 'IDC', 'Imbalance', 'CM'],
      datasets: [{ data: mixData.map(v => Math.max(v, 0)),
        backgroundColor: [COLORS.sffr, COLORS.epex, COLORS.ida1, COLORS.idc, COLORS.imbalanceRev, COLORS.cm],
        borderColor: COLORS.bgCard, borderWidth: 2 }],
    },
    options: { ...baseOptions, cutout: '65%', plugins: { legend: legendBottom } },
  });

  // ---- Chart 3: Actual vs Optimal ----
  charts.actualVsOpt = new Chart(document.getElementById('actualVsOptimalChart'), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'Actual', data: monthMetrics.map(m => m.rev.gbTotal), backgroundColor: COLORS.actual, borderRadius: 4 },
        { label: 'Optimal', data: monthMetrics.map(m => m.opt.multiTotal), backgroundColor: COLORS.optimal, borderRadius: 4 },
      ],
    },
    options: { ...baseOptions, plugins: { legend: legendBottom }, scales: { y: gbpYAxis } },
  });

  // ---- Chart 4: Capture Rate ----
  charts.capture = new Chart(document.getElementById('captureRateChart'), {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Capture Rate', data: monthMetrics.map(m => m.capture), borderColor: COLORS.actual,
          backgroundColor: 'rgba(59,130,246,0.1)', fill: true, tension: 0.4,
          pointBackgroundColor: COLORS.actual, pointRadius: 5, borderWidth: 2.5 },
        { label: '100% Line', data: labels.map(() => 100), borderColor: 'rgba(239,68,68,0.4)',
          borderDash: [6, 4], borderWidth: 1, pointRadius: 0 },
      ],
    },
    options: { ...baseOptions, scales: { y: { min: 0, max: 120, ...pctYAxis } }, plugins: { legend: legendBottom } },
  });

  // ---- Revenue Table ----
  renderRevenueTable(monthMetrics);
}

function renderRevenueTable(monthMetrics) {
  const tbody = document.getElementById('revenue-table-body');
  if (!tbody) return;

  const rows = [
    { label: 'GridBeyond Revenue', fn: m => m.rev.gbTotal, bold: false },
    { label: 'Capacity Market', fn: m => m.rev.cm || null, bold: false },
    { label: 'DUoS Net Credit', fn: m => m.rev.duosCredit || null, bold: false },
    { label: 'DUoS Fixed Charges', fn: m => m.rev.duosFixed ? -m.rev.duosFixed : null, bold: false },
    { label: 'Total Revenue', fn: m => m.rev.totalRevenue, bold: true },
    { label: '£/MW/year', fn: m => m.annPerMW, bold: false },
    { label: 'Modo Benchmark', fn: m => MODO_BENCHMARKS[m.key] || null, bold: false },
  ];

  let html = '';
  for (const row of rows) {
    const cls = row.bold ? 'style="background:var(--bg-elevated)"' : '';
    html += `<tr ${cls}><td class="${row.bold ? 'cell-bold' : ''}">${row.label}</td>`;
    for (const m of monthMetrics) {
      const val = row.fn(m);
      const cellCls = row.bold ? 'cell-bold' : (row.label === '£/MW/year' && val >= 88000 ? 'cell-positive' : '');
      html += `<td class="${cellCls}">${val == null ? '—' : formatGBP(Math.round(val))}</td>`;
    }
    html += '</tr>';
  }

  // Rating row
  html += '<tr><td>Rating</td>';
  for (const m of monthMetrics) {
    const r = m.annPerMW;
    const [tag, cls] = r >= 88000 ? ['Above High', 'tag-success'] : r >= 60000 ? ['Above Mid', 'tag-success'] : r >= 36000 ? ['Below Mid', 'tag-warning'] : ['Below Low', 'tag-danger'];
    html += `<td><span class="tag ${cls}">${tag}</span></td>`;
  }
  html += '</tr>';

  tbody.innerHTML = html;
}

export function destroy() { destroyCharts(charts); }

// DOM helpers
function setText(id, text) { const el = document.getElementById(id); if (el) el.textContent = text; }
function setClass(id, cls) {
  const el = document.getElementById(id);
  if (el) { el.className = `kpi-delta ${cls}`; }
}
