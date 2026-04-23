import { MONTHS, IAR_PROJECTIONS, COLORS, CAPACITY_MW } from '../constants.js';
import { calculateMonthlyRevenue, calculateAnnualPerMW, calculateCaptureRate, calculateOptimizedRevenue } from '../calculations.js';
import { formatGBP } from '../formatters.js';
import { baseOptions, gbpYAxis, legendBottom, destroyCharts } from './chart-defaults.js';

const charts = {};

export function render(allData) {
  destroyCharts(charts);

  const metrics = [];
  for (const m of MONTHS) {
    const d = allData.get(m.key);
    if (!d) continue;
    const rev = calculateMonthlyRevenue(d.master, m.key);
    const opt = calculateOptimizedRevenue(d.optimized);
    const annPerMW = calculateAnnualPerMW(rev.totalRevenue, m.days, CAPACITY_MW);
    const capture = calculateCaptureRate(rev.gbTotal, opt.multiTotal);
    const iar = IAR_PROJECTIONS[m.key] || 0;
    metrics.push({ ...m, rev, annPerMW, capture, iar });
  }

  // KPIs
  const best = metrics.reduce((a, b) => a.rev.totalRevenue > b.rev.totalRevenue ? a : b);
  const worst = metrics.reduce((a, b) => a.rev.totalRevenue < b.rev.totalRevenue ? a : b);
  const avgCapture = metrics.reduce((s, m) => s + m.capture, 0) / metrics.length;
  const latest = metrics[metrics.length - 1];

  setText('exec-best', best.short);
  setText('exec-best-val', formatGBP(Math.round(best.rev.totalRevenue)) + ' total');
  setText('exec-worst', worst.short);
  setText('exec-worst-val', formatGBP(Math.round(worst.rev.totalRevenue)) + ' total');
  setText('exec-avg-capture', (avgCapture).toFixed(1) + '%');
  setText('exec-annual', formatGBP(Math.round(latest.annPerMW)));

  const labels = metrics.map(m => m.short);

  // IAR vs Actual chart
  charts.iar = new Chart(document.getElementById('iarVsActualChart'), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'Actual Total', data: metrics.map(m => m.rev.totalRevenue), backgroundColor: COLORS.actual, borderRadius: 4 },
        { label: 'IAR Projection', data: metrics.map(m => m.iar), backgroundColor: 'rgba(245,158,11,0.6)', borderRadius: 4 },
      ],
    },
    options: { ...baseOptions, plugins: { legend: legendBottom }, scales: { y: gbpYAxis } },
  });
}

export function destroy() { destroyCharts(charts); }
function setText(id, text) { const el = document.getElementById(id); if (el) el.textContent = text; }
