import { COLORS, CYCLES_PER_DAY, CAPACITY_MWH } from '../constants.js';
import { calculateCycles, calculateDailyCycles, calculateSOCDistribution } from '../calculations.js';
import { formatNumber, formatPct } from '../formatters.js';
import { baseOptions, destroyCharts } from './chart-defaults.js';

const charts = {};

export function render(monthData, monthKey) {
  destroyCharts(charts);
  const { master, meta } = monthData;
  const cycleData = calculateCycles(master);
  const dailyCycles = calculateDailyCycles(master);
  const socDist = calculateSOCDistribution(master);
  const avgDailyCycles = dailyCycles.length > 0
    ? dailyCycles.reduce((s, d) => s + d.cycles, 0) / dailyCycles.length : 0;

  setText('health-daily-cycles', avgDailyCycles.toFixed(2));
  setText('health-total-cycles', cycleData.cyclesFull.toFixed(1));
  setText('health-degradation', '~4.4%');
  setText('health-rte', '85%');
  setText('health-subtitle', `${meta.label} — Cycling analysis, degradation tracking, and warranty compliance`);

  // Warranty progress bar
  const bar = document.getElementById('health-warranty-bar');
  if (bar) {
    const pct = Math.min((avgDailyCycles / CYCLES_PER_DAY) * 100, 100);
    bar.style.width = pct + '%';
    bar.style.background = pct > 100 ? 'var(--danger)' : 'var(--success)';
  }

  // Chart 1: Daily Cycling
  charts.cycling = new Chart(document.getElementById('cyclingChart'), {
    type: 'bar',
    data: {
      labels: dailyCycles.map(d => d.date.slice(8)),
      datasets: [{
        label: 'Daily Cycles',
        data: dailyCycles.map(d => d.cycles),
        backgroundColor: dailyCycles.map(d => d.cycles > 1.5 ? COLORS.danger : d.cycles > 1.0 ? COLORS.warning : COLORS.actual),
        borderRadius: 2,
      }],
    },
    options: { ...baseOptions, scales: { y: { max: 2.0 }, x: { ticks: { font: { size: 10 } } } } },
  });

  // Chart 2: SOC Distribution
  charts.soc = new Chart(document.getElementById('socChart'), {
    type: 'bar',
    data: {
      labels: socDist.map(b => b.label),
      datasets: [{
        label: 'Time at SOC (%)',
        data: socDist.map(b => b.pctTime),
        backgroundColor: socDist.map((_, i) => `rgba(59, 130, 246, ${0.3 + (i / 9) * 0.7})`),
        borderRadius: 2,
      }],
    },
    options: { ...baseOptions, scales: { y: { ticks: { callback: v => v + '%' } }, x: { ticks: { font: { size: 10 } } } } },
  });
}

export function destroy() { destroyCharts(charts); }
function setText(id, text) { const el = document.getElementById(id); if (el) el.textContent = text; }
