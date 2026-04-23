import { COLORS } from '../constants.js';
import { calculateMonthlyRevenue, calculateOptimizedRevenue, calculateSFFROnlyRevenue, calculateCaptureRate, calculateRevenueGap } from '../calculations.js';
import { formatGBP, formatPct } from '../formatters.js';
import { baseOptions, gbpYAxis, destroyCharts } from './chart-defaults.js';

const charts = {};

export function render(monthData, monthKey) {
  destroyCharts(charts);
  const { master, optimized, meta } = monthData;
  const rev = calculateMonthlyRevenue(master, monthKey);
  const opt = calculateOptimizedRevenue(optimized);
  const sffrOnly = calculateSFFROnlyRevenue(master);
  const epexOnlyTotal = opt.dailyTotal;
  const capture = calculateCaptureRate(rev.gbTotal, opt.multiTotal);
  const gap = calculateRevenueGap(rev.gbTotal, opt.multiTotal);

  setText('opt-actual', formatGBP(Math.round(rev.gbTotal)));
  setText('opt-optimal', formatGBP(Math.round(opt.multiTotal)));
  setText('opt-gap', formatGBP(Math.round(gap)));
  setText('opt-capture', formatPct(capture, 1));
  setText('opt-subtitle', `${meta.label} — Hindsight-based LP optimization across EPEX, ISEM, SSP, SBP, and DA HH markets`);

  const strategies = [
    { label: 'Actual (GridBeyond)', value: rev.gbTotal, color: COLORS.actual },
    { label: 'EPEX-Only', value: epexOnlyTotal, color: COLORS.epexOnly },
    { label: 'SFFR-Only', value: sffrOnly, color: COLORS.sffrOnly },
    { label: 'Multi-Market Optimal', value: opt.multiTotal, color: COLORS.optimal },
  ];

  charts.strategy = new Chart(document.getElementById('strategyCompChart'), {
    type: 'bar',
    data: {
      labels: strategies.map(s => s.label),
      datasets: [{ data: strategies.map(s => s.value), backgroundColor: strategies.map(s => s.color), borderRadius: 6 }],
    },
    options: { ...baseOptions, scales: { y: gbpYAxis } },
  });
}

export function destroy() { destroyCharts(charts); }
function setText(id, text) { const el = document.getElementById(id); if (el) el.textContent = text; }
