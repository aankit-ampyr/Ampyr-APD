// ============================================================
// CSV DATA LOADING, PARSING & NORMALIZATION
// ============================================================
import { MONTHS } from './constants.js';

const DATA_BASE = '../data';
const cache = new Map();

function num(v) {
  if (v == null || v === '') return 0;
  const n = Number(v);
  return isNaN(n) ? 0 : n;
}

function parseTimestamp(v) {
  if (!v) return null;
  // Handle multiple formats
  const d = new Date(v);
  if (!isNaN(d)) return d;
  // Try DD/MM/YYYY HH:MM:SS
  const parts = v.match(/(\d{2})\/(\d{2})\/(\d{4})\s+(\d{2}):(\d{2}):(\d{2})/);
  if (parts) return new Date(parts[3], parts[2] - 1, parts[1], parts[4], parts[5], parts[6]);
  return null;
}

function normalizeMasterRow(row, isLegacy) {
  // Sept legacy format: unnamed first col (index 0) is timestamp, Physical_Power_MW, Physical_SoC
  // Oct+ format: Timestamp, Power_MW, SOC
  const timestamp = isLegacy
    ? parseTimestamp(row[''] || row[Object.keys(row)[0]])
    : parseTimestamp(row['Timestamp']);

  const powerMW = num(isLegacy ? row['Physical_Power_MW'] : row['Power_MW']);
  const soc = num(isLegacy ? row['Physical_SoC'] : row['SOC']);

  return {
    timestamp,
    date: timestamp ? timestamp.toISOString().slice(0, 10) : null,
    hour: timestamp ? timestamp.getHours() : 0,
    powerMW,
    soc,
    // Prices
    epexDA: num(row['Day Ahead Price (EPEX)']),
    isemPrice: num(row['GB-ISEM Intraday 1 Price']),
    daHHPrice: num(row['DA HH Price']),
    ssp: num(row['SSP']),
    sbp: num(row['SBP']),
    idcPrice: num(row['IDC Price']),
    // Revenues
    imbalanceRev: num(row['Imbalance Revenue']),
    imbalanceCharge: num(row['Imbalance Charge']),
    daMW: num(row['DA MW']),
    epexDARev: num(row['EPEX DA Revenues']),
    epex30DAMW: num(row['EPEX 30 DA MW']),
    epex30DARev: num(row['EPEX 30 DA Revenue']),
    ida1MW: num(row['IDA1 MW']),
    ida1Rev: num(row['IDA1 Revenue']),
    idcMW: num(row['IDC MW']),
    idcRev: num(row['IDC Revenue']),
    // Ancillary
    sffrAvail: num(row['SFFR Availability']),
    sffrPrice: num(row['SFFR Clearing Price']),
    sffrRev: num(row['SFFR revenues']),
    dclRev: num(row['DCL revenues']),
    dchRev: num(row['DCH revenues']),
    dmlRev: num(row['DML revenues']),
    dmhRev: num(row['DMH revenues']),
    drlRev: num(row['DRL revenues']),
    drhRev: num(row['DRH revenues']),
  };
}

function normalizeOptRow(row) {
  return {
    timestamp: parseTimestamp(row['Timestamp']),
    date: parseTimestamp(row['Timestamp'])?.toISOString().slice(0, 10) || null,
    // Daily strategy
    netMWhDaily: num(row['Optimised_Net_MWh_Daily']),
    socDaily: num(row['Optimised_SoC_Daily']),
    strategyDaily: row['Strategy_Selected_Daily'] || '',
    revDaily: num(row['Optimised_Revenue_Daily']),
    // EFA strategy
    netMWhEFA: num(row['Optimised_Net_MWh_EFA']),
    revEFA: num(row['Optimised_Revenue_EFA']),
    // Multi-market strategy
    netMWhMulti: num(row['Optimised_Net_MWh_Multi']),
    socMulti: num(row['Optimised_SoC_Multi']),
    strategyMulti: row['Strategy_Selected_Multi'] || '',
    marketUsedMulti: row['Market_Used_Multi'] || 'Idle',
    revMulti: num(row['Optimised_Revenue_Multi']),
    // Spread info
    marketSpread: num(row['Market_Spread']),
    bestBuyPrice: num(row['Best_Buy_Price']),
    bestSellPrice: num(row['Best_Sell_Price']),
    bestBuyMarket: row['Best_Buy_Market'] || '',
    bestSellMarket: row['Best_Sell_Market'] || '',
  };
}

function parseCsvAsync(url) {
  return new Promise((resolve, reject) => {
    Papa.parse(url, {
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: (results) => resolve(results.data),
      error: (err) => reject(err),
    });
  });
}

async function loadMonthData(monthCfg) {
  const masterUrl = `${DATA_BASE}/${monthCfg.masterFile}`;
  const optUrl = `${DATA_BASE}/${monthCfg.optFile}`;

  const [masterRaw, optRaw] = await Promise.all([
    parseCsvAsync(masterUrl),
    parseCsvAsync(optUrl),
  ]);

  const master = masterRaw
    .map(r => normalizeMasterRow(r, monthCfg.legacy))
    .filter(r => r.timestamp !== null);

  const optimized = optRaw
    .map(r => normalizeOptRow(r))
    .filter(r => r.timestamp !== null);

  return {
    master,
    optimized,
    meta: { key: monthCfg.key, label: monthCfg.label, short: monthCfg.short, days: monthCfg.days },
  };
}

export async function loadAllMonths() {
  const results = await Promise.all(MONTHS.map(m => loadMonthData(m)));
  results.forEach(r => cache.set(r.meta.key, r));
  return cache;
}

export function getMonthData(key) {
  return cache.get(key) || null;
}

export function getAllData() {
  return cache;
}

export function isLoaded() {
  return cache.size === MONTHS.length;
}
