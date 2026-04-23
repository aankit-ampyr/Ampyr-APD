import { COLORS } from '../constants.js';
import { calculateDailyImbalance, calculateMonthlyRevenue } from '../calculations.js';
import { formatGBP } from '../formatters.js';
import { baseOptions, legendBottom, destroyCharts } from './chart-defaults.js';

const charts = {};

export function render(monthData, monthKey) {
  destroyCharts(charts);
  const { master, meta } = monthData;
  const daily = calculateDailyImbalance(master);
  const rev = calculateMonthlyRevenue(master, monthKey);
  const spikeCount = daily.filter(d => Math.abs(d.net) > 300).length;

  setText('imb-rev', formatGBP(Math.round(rev.imbalanceRev)));
  setText('imb-charge', formatGBP(Math.round(-rev.imbalanceCharge)));
  setText('imb-net', formatGBP(Math.round(rev.imbalanceRev - rev.imbalanceCharge)));
  setText('imb-spikes', String(spikeCount));
  setText('imb-subtitle', `${meta.label} — SSP/SBP settlement analysis`);

  charts.imbalance = new Chart(document.getElementById('imbalanceChart'), {
    type: 'bar',
    data: {
      labels: daily.map(d => d.date.slice(8)),
      datasets: [
        { label: 'Revenue', data: daily.map(d => d.revenue), backgroundColor: COLORS.imbalanceRev, borderRadius: 2 },
        { label: 'Charges', data: daily.map(d => -d.charge), backgroundColor: COLORS.imbalanceCost, borderRadius: 2 },
      ],
    },
    options: {
      ...baseOptions,
      plugins: { legend: legendBottom },
      scales: {
        x: { stacked: true, ticks: { font: { size: 10 } } },
        y: { stacked: true, ticks: { callback: v => '£' + v } },
      },
    },
  });
}

export function destroy() { destroyCharts(charts); }
function setText(id, text) { const el = document.getElementById(id); if (el) el.textContent = text; }
