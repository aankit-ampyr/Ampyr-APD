// ============================================================
// ASSET CONFIGURATION — Northwold Solar Farm (Hall Farm)
// ============================================================
export const ASSET_NAME = 'Northwold Solar Farm (Hall Farm)';
export const P_IMP_MAX_MW = 4.2;
export const P_EXP_MAX_MW = 7.5;
export const CAPACITY_MWH = 8.4;
export const CAPACITY_MW = 4.2;
export const EFF_ROUND_TRIP = 0.87;
export const EFF_ONE_WAY = Math.sqrt(0.87); // ~0.933
export const SOC_MIN_PCT = 0.05;
export const SOC_MAX_PCT = 0.95;
export const SOC_MIN_MWH = 0.42;
export const SOC_MAX_MWH = 7.98;
export const CYCLES_PER_DAY = 1.5;
export const MAX_DAILY_THROUGHPUT_MWH = 12.6;
export const DT_HOURS = 0.5;
export const AGGREGATOR_NAME = 'GridBeyond';
export const OWNER_SHARE = 0.95;

// ============================================================
// MONTH DEFINITIONS — file mappings
// ============================================================
export const MONTHS = [
  { key: 'Sep25', label: 'September 2025', short: 'Sep 25', days: 30,
    masterFile: 'Master_BESS_Analysis_Sept_2025.csv',
    optFile: 'Optimized_Results_Sept_2025.csv', legacy: true },
  { key: 'Oct25', label: 'October 2025', short: 'Oct 25', days: 31,
    masterFile: 'Master_BESS_Analysis_Oct_2025.csv',
    optFile: 'Optimized_Results_Oct_2025.csv', legacy: false },
  { key: 'Nov25', label: 'November 2025', short: 'Nov 25', days: 30,
    masterFile: 'Master_BESS_Analysis_Nov_2025.csv',
    optFile: 'Optimized_Results_Nov_2025.csv', legacy: false },
  { key: 'Dec25', label: 'December 2025', short: 'Dec 25', days: 31,
    masterFile: 'Master_BESS_Analysis_Dec_2025.csv',
    optFile: 'Optimized_Results_Dec_2025.csv', legacy: false },
  { key: 'Jan26', label: 'January 2026', short: 'Jan 26', days: 31,
    masterFile: 'Master_BESS_Analysis_Jan_2026.csv',
    optFile: 'Optimized_Results_Jan_2026.csv', legacy: false },
];

export const DEFAULT_MONTH = 'Jan26';

// ============================================================
// MODO ENERGY BENCHMARKS — £/MW/year (GB BESS Index)
// ============================================================
export const MODO_BENCHMARKS = {
  Sep25: 70000, Oct25: 77000, Nov25: 59000, Dec25: 47000,
  Jan26: 52000, Feb26: 41000, Mar26: 65000,
};

// Industry range
export const INDUSTRY_LOW = 36000;
export const INDUSTRY_MID = 60000;
export const INDUSTRY_HIGH = 88000;

// TB2 benchmark
export const TB2_BENCHMARK_PCT = 142;

// ============================================================
// CAPACITY MARKET — EMR Settlement T062
// ============================================================
export const CM_ACTUALS = {
  Sep25: 0, Oct25: 1704.17, Nov25: 1884.42, Dec25: 1994.84, Jan26: 2113.87,
};

// ============================================================
// DUoS — Hartree Partners passthrough
// ============================================================
export const DUOS_ACTUALS = {
  Sep25: { red: -322.81, amber: -410.03, green: -43.94, fixed: 3.58, net_credit: 773.20 },
  Oct25: { red: -5500.11, amber: -268.35, green: -42.92, fixed: 3.70, net_credit: 5807.68 },
  Nov25: { red: -5379.73, amber: -106.41, green: -42.54, fixed: 3.58, net_credit: 5525.10 },
  Dec25: null,
  Jan26: null,
};

// ============================================================
// IAR PROJECTIONS — Total £ per month (4.2 MW basis)
// ============================================================
export const IAR_PROJECTIONS = {
  Sep25: 26880, Oct25: 27300, Nov25: 26460, Dec25: 27300, Jan26: 27300,
};

// ============================================================
// COLOR PALETTE — Colorblind-friendly
// ============================================================
export const COLORS = {
  // Revenue streams
  sffr:           '#3B82F6',
  epex:           '#F59E0B',
  ida1:           '#8B5CF6',
  idc:            '#EC4899',
  imbalanceRev:   '#10B981',
  imbalanceCost:  '#EF4444',

  // Non-GB streams
  cm:             '#06B6D4',
  duos:           '#14B8A6',

  // Strategies
  actual:         '#3B82F6',
  epexOnly:       '#F59E0B',
  sffrOnly:       '#8B5CF6',
  optimal:        '#10B981',

  // Benchmarks
  modo:           '#F59E0B',
  industryRange:  'rgba(148,163,184,0.2)',

  // Semantic
  success:        '#10B981',
  warning:        '#F59E0B',
  danger:         '#EF4444',
  info:           '#3B82F6',

  // Chart helpers
  gridLine:       'rgba(255,255,255,0.04)',
  borderSubtle:   'rgba(255,255,255,0.06)',
  textSecondary:  '#94A3B8',
  textMuted:      '#64748B',
  bgCard:         '#1A1F2E',
};
