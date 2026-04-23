// ============================================================
// CHART.JS GLOBAL DEFAULTS — Dark theme
// ============================================================
import { COLORS } from '../constants.js';
import { gbpTickCallback, pctTickCallback } from '../formatters.js';

export function initChartDefaults() {
  Chart.defaults.color = COLORS.textSecondary;
  Chart.defaults.borderColor = COLORS.borderSubtle;
  Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
  Chart.defaults.font.size = 12;
  Chart.defaults.plugins.legend.display = false;

  // Tooltip
  Chart.defaults.plugins.tooltip.backgroundColor = '#1A1F2E';
  Chart.defaults.plugins.tooltip.borderColor = 'rgba(255,255,255,0.1)';
  Chart.defaults.plugins.tooltip.borderWidth = 1;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
  Chart.defaults.plugins.tooltip.padding = 12;
  Chart.defaults.plugins.tooltip.titleFont = { weight: '600' };
  Chart.defaults.plugins.tooltip.bodyFont = { family: "'JetBrains Mono', monospace", size: 12 };

  // Grid
  Chart.defaults.scale.grid = { color: COLORS.gridLine };
}

// Shared option presets
export const baseOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 400 },
};

export const gbpYAxis = {
  ticks: { callback: gbpTickCallback },
};

export const pctYAxis = {
  ticks: { callback: pctTickCallback },
};

export const legendBottom = {
  display: true,
  position: 'bottom',
  labels: { usePointStyle: true, pointStyle: 'circle', padding: 16, font: { size: 11 } },
};

// Destroy all chart instances in an object
export function destroyCharts(instances) {
  for (const key of Object.keys(instances)) {
    if (instances[key]) {
      instances[key].destroy();
      instances[key] = null;
    }
  }
}
