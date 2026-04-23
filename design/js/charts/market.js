import { COLORS, CAPACITY_MWH, TB2_BENCHMARK_PCT } from '../constants.js';
import { calculateTBSpreads, calculateDailyArbitrage, calculateMarketPriceStats } from '../calculations.js';
import { formatGBP, formatNumber } from '../formatters.js';
import { baseOptions, legendBottom, destroyCharts } from './chart-defaults.js';

const charts = {};

export function render(monthData, monthKey) {
  destroyCharts(charts);
  const { master, meta } = monthData;
  const tbSpreads = calculateTBSpreads(master, 'epexDA');
  const dailyArb = calculateDailyArbitrage(master);
  const priceStats = calculateMarketPriceStats(master);

  // Merge TB and arb by date
  const arbMap = new Map(dailyArb.map(d => [d.date, d.arbitrageRevenue]));
  const avgTB2 = tbSpreads.length > 0 ? tbSpreads.reduce((s, d) => s + d.tb2, 0) / tbSpreads.length : 0;

  setText('mkt-avg-epex', '£' + priceStats.avgEpexDA.toFixed(1));
  setText('mkt-max-ssp', '£' + Math.round(priceStats.maxSSP));
  setText('mkt-avg-tb2', '£' + avgTB2.toFixed(1));
  setText('mkt-volatility', '£' + priceStats.priceVolatility.toFixed(1));
  setText('mkt-subtitle', `${meta.label} — Price spreads, volatility patterns, and arbitrage opportunities`);

  const labels = tbSpreads.map(d => d.date.slice(5));
  const tb2Max = tbSpreads.map(d => d.tb2 * CAPACITY_MWH);
  const actualArb = tbSpreads.map(d => arbMap.get(d.date) || 0);
  const benchmark = tb2Max.map(v => v * TB2_BENCHMARK_PCT / 100);

  charts.spread = new Chart(document.getElementById('priceSpreadChart'), {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'TB2 Theoretical Max (£)', data: tb2Max, borderColor: 'rgba(59,130,246,0.4)',
          backgroundColor: 'rgba(59,130,246,0.08)', fill: true, pointRadius: 0, borderWidth: 1.5 },
        { label: 'Actual Arbitrage (£)', data: actualArb, borderColor: COLORS.actual,
          pointRadius: 2, pointBackgroundColor: COLORS.actual, borderWidth: 2 },
        { label: '142% Benchmark', data: benchmark, borderColor: COLORS.modo,
          borderDash: [5, 5], borderWidth: 1.5, pointRadius: 0 },
      ],
    },
    options: {
      ...baseOptions,
      scales: { x: { ticks: { maxRotation: 45, font: { size: 10 } } }, y: { ticks: { callback: v => '£' + v.toFixed(0) } } },
      plugins: { legend: legendBottom },
    },
  });
}

export function destroy() { destroyCharts(charts); }
function setText(id, text) { const el = document.getElementById(id); if (el) el.textContent = text; }
