// ============================================================
// DISPLAY FORMATTING UTILITIES
// ============================================================

export function formatGBP(value, decimals = 0) {
  if (value == null || isNaN(value)) return '—';
  const abs = Math.abs(value);
  const formatted = abs.toLocaleString('en-GB', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
  return value < 0 ? `-£${formatted}` : `£${formatted}`;
}

export function formatGBPk(value) {
  if (value == null || isNaN(value)) return '—';
  const abs = Math.abs(value);
  const k = abs / 1000;
  const formatted = k >= 100 ? `${Math.round(k)}k` : `${k.toFixed(1)}k`;
  return value < 0 ? `-£${formatted}` : `£${formatted}`;
}

export function formatPct(value, decimals = 1) {
  if (value == null || isNaN(value)) return '—';
  return `${value.toFixed(decimals)}%`;
}

export function formatNumber(value, decimals = 0) {
  if (value == null || isNaN(value)) return '—';
  return value.toLocaleString('en-GB', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function formatDelta(value, type = 'pct') {
  if (value == null || isNaN(value)) return { text: '—', cls: 'neutral' };
  const prefix = value > 0 ? '+' : '';
  const text = type === 'pct'
    ? `${prefix}${value.toFixed(1)}%`
    : `${prefix}${formatGBP(value)}`;
  const cls = value > 0 ? 'positive' : value < 0 ? 'negative' : 'neutral';
  return { text, cls };
}

// Chart.js tick formatter for GBP axis
export function gbpTickCallback(value) {
  if (Math.abs(value) >= 1000) return '£' + (value / 1000).toFixed(0) + 'k';
  return '£' + value;
}

// Chart.js tick formatter for percentage axis
export function pctTickCallback(value) {
  return value + '%';
}
