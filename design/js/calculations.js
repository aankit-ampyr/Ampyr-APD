// ============================================================
// METRIC CALCULATIONS — Replicates Streamlit logic
// ============================================================
import { CAPACITY_MWH, CAPACITY_MW, DT_HOURS, CM_ACTUALS, DUOS_ACTUALS } from './constants.js';

// ---- helpers ----
function groupBy(arr, keyFn) {
  const map = new Map();
  for (const item of arr) {
    const k = keyFn(item);
    if (k == null) continue;
    if (!map.has(k)) map.set(k, []);
    map.get(k).push(item);
  }
  return map;
}

function sum(arr, fn) {
  let total = 0;
  for (const item of arr) total += fn(item);
  return total;
}

// ============================================================
// REVENUE
// ============================================================
export function calculateMonthlyRevenue(masterRows, monthKey) {
  const sffr = sum(masterRows, r => r.sffrRev);
  const epex30DA = sum(masterRows, r => r.epex30DARev);
  const epexDA = sum(masterRows, r => r.epexDARev);
  const ida1 = sum(masterRows, r => r.ida1Rev);
  const idc = sum(masterRows, r => r.idcRev);
  const imbalanceRev = sum(masterRows, r => r.imbalanceRev);
  const imbalanceCharge = sum(masterRows, r => r.imbalanceCharge);

  const gbTotal = sffr + epex30DA + epexDA + ida1 + idc + imbalanceRev - imbalanceCharge;

  const cm = CM_ACTUALS[monthKey] || 0;
  const duosData = DUOS_ACTUALS[monthKey];
  const duosCredit = duosData ? duosData.net_credit : 0;
  const duosFixed = duosData ? duosData.fixed : 0;
  const totalRevenue = gbTotal + cm + duosCredit - duosFixed;

  return {
    sffr, epex30DA, epexDA, ida1, idc,
    imbalanceRev, imbalanceCharge,
    gbTotal, cm, duosCredit, duosFixed, totalRevenue,
  };
}

export function calculateAnnualPerMW(totalRevenue, days, capacityMW = CAPACITY_MW) {
  return (totalRevenue / days) * 365 / capacityMW;
}

// ============================================================
// DAILY REVENUE BREAKDOWN
// ============================================================
export function calculateDailyRevenue(masterRows) {
  const byDay = groupBy(masterRows, r => r.date);
  const result = [];
  for (const [date, rows] of byDay) {
    result.push({
      date,
      sffr: sum(rows, r => r.sffrRev),
      epex: sum(rows, r => r.epex30DARev + r.epexDARev),
      ida1: sum(rows, r => r.ida1Rev),
      idc: sum(rows, r => r.idcRev),
      imbalanceNet: sum(rows, r => r.imbalanceRev - r.imbalanceCharge),
      total: sum(rows, r => r.sffrRev + r.epex30DARev + r.epexDARev + r.ida1Rev + r.idcRev + r.imbalanceRev - r.imbalanceCharge),
    });
  }
  result.sort((a, b) => a.date.localeCompare(b.date));
  return result;
}

// ============================================================
// TB SPREADS — resample to hourly, compute TB1/TB2/TB3 per day
// ============================================================
export function calculateTBSpreads(masterRows, priceField = 'epexDA') {
  // Group by date + hour, average to hourly
  const hourlyMap = new Map();
  for (const r of masterRows) {
    if (!r.date) continue;
    const key = `${r.date}_${r.hour}`;
    if (!hourlyMap.has(key)) hourlyMap.set(key, { date: r.date, prices: [] });
    const price = r[priceField];
    if (price !== 0 || priceField === 'epexDA') hourlyMap.get(key).prices.push(price);
  }

  // Average to single hourly price
  const hourly = [];
  for (const [, v] of hourlyMap) {
    if (v.prices.length === 0) continue;
    hourly.push({ date: v.date, price: v.prices.reduce((a, b) => a + b, 0) / v.prices.length });
  }

  // Group hourly prices by date
  const byDay = groupBy(hourly, r => r.date);
  const result = [];
  for (const [date, rows] of byDay) {
    const prices = rows.map(r => r.price).sort((a, b) => a - b);
    const n = prices.length;
    if (n < 3) continue;

    const tb1 = prices[n - 1] - prices[0];
    const tb2 = (prices[n - 1] + prices[n - 2]) - (prices[0] + prices[1]);
    const tb3 = n >= 6
      ? (prices[n - 1] + prices[n - 2] + prices[n - 3]) - (prices[0] + prices[1] + prices[2])
      : tb2;

    result.push({ date, tb1, tb2, tb3 });
  }
  result.sort((a, b) => a.date.localeCompare(b.date));
  return result;
}

// ============================================================
// DAILY ARBITRAGE — wholesale trading only (no SFFR)
// ============================================================
export function calculateDailyArbitrage(masterRows) {
  const byDay = groupBy(masterRows, r => r.date);
  const result = [];
  for (const [date, rows] of byDay) {
    const arb = sum(rows, r => r.epex30DARev + r.epexDARev + r.ida1Rev + r.idcRev);
    result.push({ date, arbitrageRevenue: arb });
  }
  result.sort((a, b) => a.date.localeCompare(b.date));
  return result;
}

// ============================================================
// CYCLES — (discharge + charge) / 2 / capacity
// ============================================================
export function calculateCycles(masterRows) {
  let dischargeMWh = 0;
  let chargeMWh = 0;
  for (const r of masterRows) {
    const energy = r.powerMW * DT_HOURS;
    if (energy > 0) dischargeMWh += energy;
    else chargeMWh += Math.abs(energy);
  }
  const cyclesFull = (dischargeMWh + chargeMWh) / 2 / CAPACITY_MWH;
  return { dischargeMWh, chargeMWh, cyclesFull };
}

export function calculateDailyCycles(masterRows) {
  const byDay = groupBy(masterRows, r => r.date);
  const result = [];
  for (const [date, rows] of byDay) {
    let dis = 0, chg = 0;
    for (const r of rows) {
      const e = r.powerMW * DT_HOURS;
      if (e > 0) dis += e; else chg += Math.abs(e);
    }
    result.push({ date, cycles: (dis + chg) / 2 / CAPACITY_MWH });
  }
  result.sort((a, b) => a.date.localeCompare(b.date));
  return result;
}

// ============================================================
// SOC DISTRIBUTION — 10 bins
// ============================================================
export function calculateSOCDistribution(masterRows) {
  const bins = Array(10).fill(0);
  let total = 0;
  for (const r of masterRows) {
    if (r.soc == null || r.soc === 0 && r.powerMW === 0) continue;
    const idx = Math.min(Math.floor(r.soc / 10), 9);
    bins[idx]++;
    total++;
  }
  return bins.map((count, i) => ({
    label: `${i * 10}-${(i + 1) * 10}%`,
    pctTime: total > 0 ? (count / total) * 100 : 0,
  }));
}

// ============================================================
// OPTIMIZED REVENUE
// ============================================================
export function calculateOptimizedRevenue(optRows) {
  const multiTotal = sum(optRows, r => r.revMulti);
  const dailyTotal = sum(optRows, r => r.revDaily);
  const efaTotal = sum(optRows, r => r.revEFA);

  // Market breakdown for multi-market strategy
  const byMarket = groupBy(optRows, r => r.marketUsedMulti);
  const marketBreakdown = {};
  for (const [market, rows] of byMarket) {
    marketBreakdown[market] = sum(rows, r => r.revMulti);
  }

  return { multiTotal, dailyTotal, efaTotal, marketBreakdown };
}

// ============================================================
// SFFR-ONLY REVENUE — what if battery did only SFFR every day
// ============================================================
export function calculateSFFROnlyRevenue(masterRows) {
  return sum(masterRows, r => r.sffrRev);
}

// ============================================================
// CAPTURE RATE & GAP
// ============================================================
export function calculateCaptureRate(actual, optimal) {
  return optimal > 0 ? (actual / optimal) * 100 : 0;
}

export function calculateRevenueGap(actual, optimal) {
  return optimal - actual;
}

// ============================================================
// DAILY IMBALANCE
// ============================================================
export function calculateDailyImbalance(masterRows) {
  const byDay = groupBy(masterRows, r => r.date);
  const result = [];
  for (const [date, rows] of byDay) {
    result.push({
      date,
      revenue: sum(rows, r => r.imbalanceRev),
      charge: sum(rows, r => r.imbalanceCharge),
      net: sum(rows, r => r.imbalanceRev - r.imbalanceCharge),
    });
  }
  result.sort((a, b) => a.date.localeCompare(b.date));
  return result;
}

// ============================================================
// MARKET PRICE STATS
// ============================================================
export function calculateMarketPriceStats(masterRows) {
  const epexPrices = masterRows.map(r => r.epexDA).filter(p => p !== 0);
  const sspPrices = masterRows.map(r => r.ssp).filter(p => p !== 0);

  const avg = arr => arr.length ? arr.reduce((a, b) => a + b, 0) / arr.length : 0;
  const stdDev = arr => {
    if (arr.length < 2) return 0;
    const mean = avg(arr);
    return Math.sqrt(arr.reduce((s, v) => s + (v - mean) ** 2, 0) / arr.length);
  };

  return {
    avgEpexDA: avg(epexPrices),
    maxSSP: sspPrices.length ? Math.max(...sspPrices) : 0,
    priceVolatility: stdDev(epexPrices),
  };
}
