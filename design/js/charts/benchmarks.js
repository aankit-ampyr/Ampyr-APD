import { MONTHS, MODO_BENCHMARKS, COLORS, CAPACITY_MW, TB2_BENCHMARK_PCT, CAPACITY_MWH } from '../constants.js';
import { calculateMonthlyRevenue, calculateAnnualPerMW, calculateTBSpreads, calculateDailyArbitrage } from '../calculations.js';
import { formatGBP } from '../formatters.js';
import { baseOptions, gbpYAxis, pctYAxis, legendBottom, destroyCharts } from './chart-defaults.js';

const charts = {};

export function render(allData) {
  destroyCharts(charts);

  const metrics = [];
  for (const m of MONTHS) {
    const d = allData.get(m.key);
    if (!d) continue;
    const rev = calculateMonthlyRevenue(d.master, m.key);
    const annPerMW = calculateAnnualPerMW(rev.totalRevenue, m.days, CAPACITY_MW);
    const tb = calculateTBSpreads(d.master, 'epexDA');
    const arb = calculateDailyArbitrage(d.master);
    const arbMap = new Map(arb.map(a => [a.date, a.arbitrageRevenue]));

    let tb2CaptureSum = 0, tb2Count = 0;
    for (const t of tb) {
      const arbRev = arbMap.get(t.date) || 0;
      const tb2Max = t.tb2 * CAPACITY_MWH;
      if (tb2Max > 0) { tb2CaptureSum += (arbRev / tb2Max) * 100; tb2Count++; }
    }
    const avgTB2Capture = tb2Count > 0 ? tb2CaptureSum / tb2Count : 0;

    metrics.push({ ...m, annPerMW, modo: MODO_BENCHMARKS[m.key] || 0, avgTB2Capture });
  }

  const labels = metrics.map(m => m.short);

  // Chart 1: £/MW/yr vs Modo
  charts.benchmark = new Chart(document.getElementById('benchmarkChart'), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'Northwold £/MW/yr', data: metrics.map(m => m.annPerMW), backgroundColor: COLORS.actual, borderRadius: 4 },
        { label: 'Modo Benchmark', data: metrics.map(m => m.modo), backgroundColor: 'rgba(245,158,11,0.5)', borderRadius: 4 },
      ],
    },
    options: { ...baseOptions, plugins: { legend: legendBottom }, scales: { y: gbpYAxis } },
  });

  // Chart 2: TB2 Capture
  charts.tb2 = new Chart(document.getElementById('tb2CaptureChart'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'TB2 Capture %',
        data: metrics.map(m => m.avgTB2Capture),
        backgroundColor: metrics.map(m => m.avgTB2Capture >= TB2_BENCHMARK_PCT ? COLORS.success : m.avgTB2Capture >= 100 ? COLORS.warning : COLORS.actual),
        borderRadius: 4,
      }],
    },
    options: { ...baseOptions, scales: { y: pctYAxis } },
  });

  // Update table
  const tbody = document.getElementById('benchmark-table-body');
  if (tbody) {
    const avgAnn = metrics.reduce((s, m) => s + m.annPerMW, 0) / metrics.length;
    const ratingTag = avgAnn >= 88000 ? ['Above High', 'tag-success'] : avgAnn >= 60000 ? ['Above Mid', 'tag-success'] : ['Below Mid', 'tag-warning'];
    tbody.innerHTML = `
      <tr><td>Revenue (£/MW/yr)</td><td class="cell-bold">${formatGBP(Math.round(avgAnn))}</td><td>£36,000</td><td>£60,000</td><td>£88,000</td><td><span class="tag ${ratingTag[1]}">${ratingTag[0]}</span></td></tr>
      <tr><td>Daily Cycles</td><td class="cell-bold">0.64</td><td>1.0</td><td>1.5</td><td>3.0</td><td><span class="tag tag-success">Within Warranty</span></td></tr>
      <tr><td>Round-Trip Efficiency</td><td class="cell-bold">~85%</td><td>82%</td><td>85%</td><td>90%</td><td><span class="tag tag-info">At Mid</span></td></tr>
    `;
  }
}

export function destroy() { destroyCharts(charts); }
