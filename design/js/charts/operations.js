import { COLORS } from '../constants.js';
import { calculateMonthlyRevenue, calculateDailyRevenue } from '../calculations.js';
import { formatGBP } from '../formatters.js';
import { baseOptions, gbpYAxis, destroyCharts } from './chart-defaults.js';

const charts = {};

export function render(monthData, monthKey) {
  destroyCharts(charts);
  const { master, meta } = monthData;
  const rev = calculateMonthlyRevenue(master, monthKey);
  const daily = calculateDailyRevenue(master);

  // KPIs
  setText('ops-sffr', formatGBP(Math.round(rev.sffr)));
  setText('ops-epex', formatGBP(Math.round(rev.epex30DA + rev.epexDA)));
  setText('ops-ida1', formatGBP(Math.round(rev.ida1)));
  setText('ops-imb', formatGBP(Math.round(rev.imbalanceRev - rev.imbalanceCharge)));
  setText('ops-subtitle', `${meta.label} — Revenue breakdown, market participation, and trading performance`);

  // Chart 1: Daily Revenue
  charts.daily = new Chart(document.getElementById('dailyRevenueChart'), {
    type: 'bar',
    data: {
      labels: daily.map(d => d.date.slice(8)),
      datasets: [{
        label: 'Daily Revenue (£)',
        data: daily.map(d => d.total),
        backgroundColor: daily.map(d => d.total > 2000 ? COLORS.epex : COLORS.actual),
        borderRadius: 2,
      }],
    },
    options: { ...baseOptions, scales: { x: { ticks: { font: { size: 10 } } }, y: gbpYAxis } },
  });

  // Chart 2: Market Stream (horizontal)
  const streams = [
    { label: 'SFFR', value: rev.sffr, color: COLORS.sffr },
    { label: 'EPEX DA', value: rev.epex30DA + rev.epexDA, color: COLORS.epex },
    { label: 'IDA1', value: rev.ida1, color: COLORS.ida1 },
    { label: 'IDC', value: rev.idc, color: COLORS.idc },
    { label: 'Imbalance Rev', value: rev.imbalanceRev, color: COLORS.imbalanceRev },
    { label: 'Imbalance Cost', value: -rev.imbalanceCharge, color: COLORS.imbalanceCost },
  ];

  charts.stream = new Chart(document.getElementById('marketStreamChart'), {
    type: 'bar',
    data: {
      labels: streams.map(s => s.label),
      datasets: [{ data: streams.map(s => s.value), backgroundColor: streams.map(s => s.color), borderRadius: 4 }],
    },
    options: { indexAxis: 'y', ...baseOptions, scales: { x: { ticks: { callback: v => '£' + v.toLocaleString() } } } },
  });
}

export function destroy() { destroyCharts(charts); }
function setText(id, text) { const el = document.getElementById(id); if (el) el.textContent = text; }
