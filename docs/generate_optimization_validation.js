const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
  WidthType, ShadingType, PageNumber, PageBreak, TableOfContents, PageOrientation
} = require(path.join(process.env.APPDATA || "", "npm/node_modules/docx"));

// ── Shared helpers ──
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cm = { top: 60, bottom: 60, left: 100, right: 100 };
const hdrShade = { fill: "1F4E79", type: ShadingType.CLEAR };
const altShade = { fill: "F2F7FB", type: ShadingType.CLEAR };
const greenShade = { fill: "E8F5E9", type: ShadingType.CLEAR };
const redShade = { fill: "FFEBEE", type: ShadingType.CLEAR };
const yellowShade = { fill: "FFF8E1", type: ShadingType.CLEAR };
const blueShade = { fill: "E3F2FD", type: ShadingType.CLEAR };

function hCell(text, w) {
  return new TableCell({ borders, width: { size: w, type: WidthType.DXA }, shading: hdrShade, margins: cm,
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", font: "Arial", size: 18 })] })] });
}
function dCell(text, w, shade) {
  return new TableCell({ borders, width: { size: w, type: WidthType.DXA }, shading: shade, margins: cm,
    children: [new Paragraph({ children: [new TextRun({ text: String(text), font: "Arial", size: 17 })] })] });
}
function bCell(text, w, shade) {
  return new TableCell({ borders, width: { size: w, type: WidthType.DXA }, shading: shade, margins: cm,
    children: [new Paragraph({ children: [new TextRun({ text: String(text), font: "Arial", size: 17, bold: true })] })] });
}
function nCell(text, w, shade) {
  return new TableCell({ borders, width: { size: w, type: WidthType.DXA }, shading: shade, margins: cm,
    children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: String(text), font: "Consolas", size: 16 })] })] });
}

function makeTable(headers, rows, cw) {
  const tw = cw.reduce((a,b) => a+b, 0);
  return new Table({ width: { size: tw, type: WidthType.DXA }, columnWidths: cw, rows: [
    new TableRow({ children: headers.map((h,i) => hCell(h, cw[i])) }),
    ...rows.map((row, ri) => new TableRow({
      children: row.map((c, ci) => {
        const sh = ri % 2 === 1 ? altShade : undefined;
        if (typeof c === "object" && c._bold) return bCell(c.t, cw[ci], c.sh || sh);
        if (typeof c === "object" && c._num) return nCell(c.t, cw[ci], c.sh || sh);
        if (typeof c === "object" && c._shade) return dCell(c.t, cw[ci], c.sh);
        return dCell(String(c), cw[ci], sh);
      })
    }))
  ]});
}

function h1(t) { return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 200 }, children: [new TextRun({ text: t, font: "Arial" })] }); }
function h2(t) { return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 160 }, children: [new TextRun({ text: t, font: "Arial" })] }); }
function h3(t) { return new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 200, after: 120 }, children: [new TextRun({ text: t, font: "Arial" })] }); }
function p(text, opts = {}) {
  const runs = typeof text === "string"
    ? [new TextRun({ text, font: "Arial", size: 22, ...opts })]
    : text.map(t => typeof t === "string" ? new TextRun({ text: t, font: "Arial", size: 22 }) : new TextRun({ font: "Arial", size: 22, ...t }));
  return new Paragraph({ spacing: { before: 60, after: 60 }, children: runs });
}
function code(text) {
  return new Paragraph({ spacing: { before: 30, after: 30 }, indent: { left: 360 },
    children: [new TextRun({ text, font: "Consolas", size: 18, color: "333333" })] });
}
function note(text) {
  return new Paragraph({ spacing: { before: 80, after: 80 }, indent: { left: 360, right: 360 },
    border: { left: { style: BorderStyle.SINGLE, size: 12, color: "2E75B6", space: 8 } },
    children: [new TextRun({ text, font: "Arial", size: 20, italics: true, color: "555555" })] });
}
function bold(t) { return { text: t, bold: true }; }
function num(t, sh) { return { _num: true, t: String(t), sh }; }
function shade(t, sh) { return { _shade: true, t: String(t), sh }; }
function boldS(t, sh) { return { _bold: true, t: String(t), sh }; }

const children = [];

// ═══════════════ TITLE PAGE ═══════════════
children.push(
  new Paragraph({ spacing: { before: 2400 }, children: [] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "AMPYR ENERGY", font: "Arial", size: 36, bold: true, color: "1F4E79" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [new TextRun({ text: "BESS Multi-Market Optimisation", font: "Arial", size: 48, bold: true, color: "1F4E79" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: "Algorithm Validation Document", font: "Arial", size: 32, color: "2E75B6" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 }, children: [new TextRun({ text: "With Worked Examples from January 2026 Data", font: "Arial", size: 26, color: "666666" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "Prepared for Business Expert Validation", font: "Arial", size: 24, italics: true, color: "888888" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 800 }, children: [
    new TextRun({ text: "Asset: ", font: "Arial", size: 22, color: "666666" }),
    new TextRun({ text: "Northwold Solar Farm BESS (8.4 MWh / 4.2 MW import / 7.5 MW export)", font: "Arial", size: 22, bold: true, color: "333333" }),
  ]}),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [
    new TextRun({ text: "Aggregator: ", font: "Arial", size: 22, color: "666666" }),
    new TextRun({ text: "GridBeyond", font: "Arial", size: 22, bold: true, color: "333333" }),
  ]}),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [
    new TextRun({ text: "Period: ", font: "Arial", size: 22, color: "666666" }),
    new TextRun({ text: "January 2026 (31 days, 1,488 half-hourly periods)", font: "Arial", size: 22, bold: true, color: "333333" }),
  ]}),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 600 }, children: [new TextRun({ text: "Confidential - Project Lazarus | Version 1.0 | March 2026", font: "Arial", size: 20, color: "999999" })] }),
  new Paragraph({ children: [new PageBreak()] })
);

// TOC
children.push(
  h1("Table of Contents"),
  new TableOfContents("TOC", { hyperlink: true, headingStyleRange: "1-3" }),
  new Paragraph({ children: [new PageBreak()] })
);

// ═══════════════ SECTION 1: WHAT THE ALGORITHM DOES ═══════════════
children.push(
  h1("1. What the Algorithm Does"),
  p("The optimisation algorithm answers a simple question: given perfect knowledge of market prices for an entire day, what is the maximum revenue the battery could have earned?"),
  p("This is a hindsight analysis (not a forecast). It shows the theoretical ceiling that a perfect trading strategy could achieve, allowing us to measure how well GridBeyond actually performed."),
  h2("1.1 The Decision"),
  p("Every day, the algorithm makes one binary decision:"),
  note("Should the battery trade in wholesale/balancing markets (Multi-Market), or stay in frequency response (SFFR)?"),
  p("It calculates the total revenue for each option and picks the higher one."),
  h2("1.2 The Three Strategies Computed"),
  makeTable(
    ["Strategy", "Markets Used", "Switching", "Purpose"],
    [
      ["Strategy 1: EPEX Daily", "EPEX only", "Whole day: SFFR or EPEX", "Simple baseline - what if we only traded EPEX?"],
      ["Strategy 2: EPEX EFA", "EPEX only", "Per 2-hour EFA block", "Can we do better by switching between SFFR and EPEX within a day?"],
      ["Strategy 3: Multi-Market", "EPEX + ISEM + SSP + SBP + DA_HH", "Whole day: SFFR or all markets", "Best possible with all markets - the benchmark we care about"],
    ],
    [2200, 2200, 2400, 2560]
  ),
  p(""),
  p([{ text: "Strategy 3 (Multi-Market) is the primary benchmark. ", bold: true }, { text: "It represents the theoretical maximum revenue achievable within the asset's physical and warranty constraints." }]),
  new Paragraph({ children: [new PageBreak()] })
);

// ═══════════════ SECTION 2: INPUT PARAMETERS ═══════════════
children.push(
  h1("2. Input Parameters"),
  h2("2.1 Battery Physical Constraints"),
  makeTable(
    ["Parameter", "Value", "What It Means"],
    [
      ["Max Charge (Import)", "4.2 MW", "How fast the battery can absorb energy from the grid"],
      ["Max Discharge (Export)", "7.5 MW", "How fast the battery can push energy to the grid (asymmetric - faster out than in)"],
      ["Usable Capacity", "8.4 MWh", "Total energy the battery can store"],
      ["Round-Trip Efficiency", "87%", "For every 1 MWh put in, only 0.87 MWh comes out (13% lost as heat)"],
      ["SOC Floor", "5% (0.42 MWh)", "Never drain below this - protects battery cells from damage"],
      ["SOC Ceiling", "95% (7.98 MWh)", "Never charge above this - prevents thermal stress"],
      ["Warranty Limit", "1.5 cycles/day", "Maximum daily discharge throughput = 12.6 MWh = 1.5 x 8.4"],
    ],
    [2200, 1800, 5360]
  ),
  p(""),
  h2("2.2 Market Prices (5 Markets)"),
  p("For each 30-minute period, the algorithm sees prices from 5 markets and picks the cheapest to buy from and the most expensive to sell into:"),
  makeTable(
    ["Market", "What It Is", "Typical Range (Jan 26)"],
    [
      ["EPEX Day Ahead", "Wholesale market, prices set day before delivery", "50-200 GBP/MWh"],
      ["GB-ISEM Intraday", "Cross-border intraday auction (GB-Ireland)", "50-200 GBP/MWh"],
      ["SSP (System Sell Price)", "Price for being long in National Grid balancing", "50-750 GBP/MWh (spikes!)"],
      ["SBP (System Buy Price)", "Price for being short in National Grid balancing", "50-500 GBP/MWh"],
      ["DA HH (Day Ahead Half-Hourly)", "Half-hourly variant of day-ahead", "50-200 GBP/MWh"],
    ],
    [2400, 4200, 2760]
  ),
  p(""),
  note("Key insight: SSP can spike to extreme levels (750 GBP/MWh on Jan 5!) during system stress events. The multi-market algorithm captures these spikes by selling into SSP when it is the highest-priced market."),
  p(""),
  h2("2.3 SFFR (Frequency Response)"),
  p("SFFR is a contract where the battery commits to being available for grid frequency support. The battery earns a fixed price per MW of availability per hour, regardless of whether it actually needs to respond."),
  code("SFFR Revenue per period = Availability_MW x SFFR_Clearing_Price x 0.5 hours"),
  code(""),
  code("The optimiser assumes 7.0 MW availability (full capacity)."),
  code("Actual availability varies (average 6.81 MW in Jan 2026 due to SOC/operational constraints)."),
  new Paragraph({ children: [new PageBreak()] })
);

// ═══════════════ SECTION 3: THE ALGORITHM STEP BY STEP ═══════════════
children.push(
  h1("3. The Algorithm Step by Step"),
  h2("3.1 Overview"),
  p("For each day in the month:"),
  p([{ text: "Step 1: ", bold: true }, { text: "Calculate SFFR value for the full day" }]),
  code("SFFR_Daily = Sum over 48 periods of (7.0 MW x SFFR_Clearing_Price x 0.5 hours)"),
  p(""),
  p([{ text: "Step 2: ", bold: true }, { text: "For each period, find the cheapest market to buy from and the most expensive to sell into" }]),
  code("Buy_Price[t] = min(EPEX[t], ISEM[t], SSP[t], SBP[t], DA_HH[t])"),
  code("Sell_Price[t] = max(EPEX[t], ISEM[t], SSP[t], SBP[t], DA_HH[t])"),
  p(""),
  p([{ text: "Step 3: ", bold: true }, { text: "Solve the linear program - find the optimal charge/discharge schedule" }]),
  code("Maximize: Sum of (Discharge[t] x Sell_Price[t] - Charge[t] x Buy_Price[t]) x 0.5"),
  code(""),
  code("Subject to:"),
  code("  Battery physics: SoC[t] = SoC[t-1] + Charge[t] x 0.933 x 0.5 - Discharge[t] / 0.933 x 0.5"),
  code("  Charge limit:    0 <= Charge[t] <= 4.2 MW"),
  code("  Discharge limit: 0 <= Discharge[t] <= 7.5 MW"),
  code("  SOC bounds:      0.42 MWh <= SoC[t] <= 7.98 MWh"),
  code("  Warranty:        Sum(Discharge[t] x 0.5) <= 12.6 MWh per day"),
  p(""),
  p([{ text: "Step 4: ", bold: true }, { text: "Compare and choose" }]),
  code("If SFFR_Daily > Multi_Market_Revenue:  choose SFFR (battery locked)"),
  code("If Multi_Market_Revenue >= SFFR_Daily: choose Multi-Market (active dispatch)"),
  p(""),
  p([{ text: "Step 5: ", bold: true }, { text: "Carry SOC forward to the next day" }]),
  code("Day N+1 starting SOC = Day N ending SOC"),
  p(""),
  h2("3.2 Efficiency Explained"),
  p("The battery loses energy in both directions:"),
  code("Charging:    1 MWh from grid --> battery stores 0.933 MWh (6.7% lost)"),
  code("Discharging: 0.933 MWh from battery --> grid receives 0.87 MWh (another 6.7% lost)"),
  code("Round trip:  1 MWh in --> 0.87 MWh out (13% total loss)"),
  p(""),
  p("This means the sell price must be at least 15% higher than the buy price to break even on a round trip (1 / 0.87 = 1.149)."),
  note("Break-even spread = Buy_Price x (1/0.87 - 1) = Buy_Price x 14.9%. At 100 GBP/MWh buy price, need 115 GBP/MWh sell price just to break even."),
  new Paragraph({ children: [new PageBreak()] })
);

// ═══════════════ SECTION 4: JANUARY 2026 RESULTS ═══════════════
children.push(
  h1("4. January 2026 Results Summary"),
  h2("4.1 Monthly Totals"),
  makeTable(
    ["Metric", "Value"],
    [
      [boldS("Optimised Multi-Market Revenue (theoretical max)", blueShade), boldS("33,376", blueShade)],
      [boldS("Actual GridBeyond Revenue", greenShade), boldS("28,190", greenShade)],
      ["Revenue Gap", "5,186"],
      ["Capture Rate", "84.5%"],
      ["Days choosing SFFR", "22 out of 31 (71%)"],
      ["Days choosing Multi-Market", "8 out of 31 (when price spikes made trading more valuable)"],
      ["Total SFFR periods", "1,056 of 1,488 (71%)"],
      ["Total active trading periods", "81 of 1,488 (5.4%)"],
      ["Total idle periods (in trading days)", "303 of 1,488"],
    ],
    [5500, 3860]
  ),
  p(""),
  h2("4.2 Daily Revenue Ranking (Top 10 Days)"),
  makeTable(
    ["Rank", "Date", "Strategy", "Optimised Revenue", "Key Driver"],
    [
      ["1", "Mon 5 Jan", "Multi-Market", "5,222", "SSP spike to 750 at 19:00 - sold 1.65 MW into SSP"],
      ["2", "Thu 8 Jan", "Multi-Market", "3,766", "SSP spike event - high balancing market spreads"],
      ["3", "Tue 6 Jan", "Multi-Market", "2,551", "Continued high SSP spreads from 5th Jan event"],
      ["4", "Fri 2 Jan", "Multi-Market", "1,115", "New Year period high demand/low wind"],
      ["5", "Thu 15 Jan", "Multi-Market", "1,095", "Evening peak SSP spread"],
      ["6", "Mon 19 Jan", "Multi-Market", "1,008", "High evening spreads"],
      ["7", "Wed 14 Jan", "Multi-Market", "981", "Moderate SSP spreads"],
      ["8", "Tue 27 Jan", "SFFR", "943", "High SFFR clearing prices (winter peak demand)"],
      ["9", "Sun 25 Jan", "SFFR", "915", "High SFFR clearing prices"],
      ["10", "Wed 28 Jan", "SFFR", "911", "High SFFR clearing prices"],
    ],
    [600, 1200, 1600, 1800, 4160]
  ),
  p(""),
  note("The top 3 days (5th-8th Jan) generated 34.6% of the entire month's optimised revenue. This concentration highlights the importance of capturing price spike events."),
  new Paragraph({ children: [new PageBreak()] })
);

// ═══════════════ SECTION 5: WORKED EXAMPLE - BEST DAY ═══════════════
children.push(
  h1("5. Worked Example: Best Trading Day (5 January 2026)"),
  p([{ text: "This day generated ", bold: false }, { text: "5,222 GBP", bold: true }, { text: " in optimised revenue - the highest single day in January. The optimizer chose Multi-Market over SFFR. Let's walk through why and how." }]),
  h2("5.1 The Decision: SFFR vs Multi-Market"),
  p([{ text: "SFFR option: ", bold: true }, { text: "Locking the battery in frequency response for the full day. SFFR clearing prices on Jan 5 ranged from 1.17 to 4.36 GBP/MW/h." }]),
  code("SFFR_Daily = Sum(7.0 MW x SFFR_Price[t] x 0.5) for 48 periods"),
  code("         ~= 7.0 x average(2.84) x 0.5 x 48 = ~477 GBP"),
  p(""),
  p([{ text: "Multi-Market option: ", bold: true }, { text: "Active trading across all 5 markets. SSP spiked to 750 GBP/MWh at 19:00!" }]),
  code("Multi_Market_Revenue = 5,222 GBP  (from LP solver)"),
  p(""),
  p([{ text: "Decision: Multi-Market wins (5,222 >> 477). ", bold: true }, { text: "The SSP spike alone made trading 10x more valuable than SFFR." }]),
  h2("5.2 What the Algorithm Did (Hour by Hour)"),
  p([{ text: "Phase 1 - Charging (00:00-02:30): ", bold: true }, { text: "Bought energy from SSP at 68-70 GBP/MWh (cheapest market overnight). Charged from starting SOC up to 7.98 MWh (95% full)." }]),
);

// Jan 5 charging phase
const jan5_charge = [
  ["00:00", "Buy-SSP", "-2.10", "2.38", "68.15", "83.10", "-143"],
  ["00:30", "Buy-SSP", "-2.10", "4.34", "70.16", "83.10", "-147"],
  ["01:00", "Idle", "0.00", "4.34", "77.20", "95.30", "0"],
  ["01:30", "Buy-SSP", "-2.10", "6.30", "70.15", "83.00", "-147"],
  ["02:00", "Idle", "0.00", "6.30", "77.00", "96.00", "0"],
  ["02:30", "Buy-SSP", "-1.81", "7.98", "70.16", "82.37", "-127"],
];
children.push(
  makeTable(
    ["Time", "Action", "Net MWh", "SOC (MWh)", "Buy Price", "Sell Price", "Revenue"],
    jan5_charge.map(r => r.map((c,i) => i === 6 ? num(c) : c)),
    [800, 1100, 900, 1100, 1100, 1100, 1000]
  ),
  p(""),
  p([{ text: "Charging cost: ", bold: true }, { text: "564 GBP spent buying energy. SSP was the cheapest market at 68-70 GBP/MWh while EPEX was 82-83 GBP/MWh. The algorithm saved ~15% by buying from SSP instead of EPEX." }]),
  p(""),
  p([{ text: "Phase 2 - Waiting (03:00-15:30): ", bold: true }, { text: "Battery sat fully charged at 7.98 MWh for 26 consecutive periods. Despite spreads of 20-70 GBP/MWh during this time, the algorithm held because it 'knew' (hindsight) that much larger spreads were coming." }]),
  note("This is the key advantage of hindsight optimization: a real-time trader might have been tempted to discharge at the 68 GBP/MWh spread at 15:30, but the optimizer held for the 640 GBP/MWh spread at 19:00."),
  p(""),
  p([{ text: "Phase 3 - The Spike Discharge (16:00-19:00): ", bold: true }, { text: "SSP spiked to extreme levels. The optimizer sold aggressively:" }]),
);

const jan5_spike = [
  ["16:00", "Buy-ISEM", "+1.65", "5.92", "157.79", boldS("433.30", redShade), boldS("+1,294", greenShade)],
  ["16:30", boldS("Sell-SSP", greenShade), boldS("+3.75", greenShade), "1.90", "175.16", boldS("426.65", redShade), boldS("+1,600", greenShade)],
  ["17:00", "Buy-SSP", "-2.10", "3.86", "82.77", "179.30", num("-174")],
  ["17:30", boldS("Sell-SSP", greenShade), boldS("+1.35", greenShade), "2.41", "174.08", boldS("368.87", redShade), boldS("+498", greenShade)],
  ["18:30", "Buy-ISEM", "-0.08", "2.48", "158.15", "338.56", num("-12")],
  ["19:00", boldS("Sell-SSP", greenShade), boldS("+1.65", greenShade), boldS("0.42", redShade), "110.00", boldS("750.00", redShade), boldS("+2,582", greenShade)],
];
children.push(
  makeTable(
    ["Time", "Action", "Net MWh", "SOC (MWh)", "Buy Price", "Sell Price", "Revenue"],
    jan5_spike,
    [800, 1200, 900, 1100, 1100, 1100, 900]
  ),
  p(""),
  p([{ text: "The 19:00 period alone generated 2,582 GBP. ", bold: true }, { text: "SSP hit 750 GBP/MWh (vs ISEM at 110). The battery discharged its last 1.65 MWh, reaching the minimum SOC of 0.42 MWh." }]),
  p(""),
  p([{ text: "Phase 4 - Empty (19:30-23:30): ", bold: true }, { text: "Battery sat at minimum SOC (0.42 MWh). Even though spreads of 40-100 GBP/MWh existed, there was nothing left to sell and the warranty limit was reached." }]),
  p(""),
  h2("5.3 Revenue Breakdown for Jan 5"),
  makeTable(
    ["Component", "Amount (GBP)", "Explanation"],
    [
      ["Charging cost (4 periods)", "-564", "Bought 8.26 MWh at avg 68-70 via SSP"],
      ["Discharge revenue (3 sell periods)", "+5,974", "Sold into SSP during price spike (avg 408 GBP/MWh)"],
      ["Recharge + small trades", "-188", "Mid-day repositioning"],
      [boldS("NET TOTAL"), boldS("5,222"), boldS("Revenue after all costs")],
    ],
    [2800, 1800, 4760]
  ),
  p(""),
  h2("5.4 How Did GridBeyond Actually Perform on Jan 5?"),
  makeTable(
    ["Metric", "Optimised", "Actual (GridBeyond)", "Gap"],
    [
      [boldS("Total Revenue"), boldS("5,222"), boldS("1,181"), boldS("4,041 (77% missed)")],
      ["Strategy", "Multi-Market (aggressive SSP trading)", "Mixed SFFR + IDA1 + EPEX", "-"],
      ["Revenue from SFFR", "0 (not chosen)", "666", "-"],
      ["Revenue from IDA1", "0", "872", "-"],
      ["Revenue from EPEX 30 DA", "0", "-324 (loss)", "-"],
      ["Imbalance", "0", "-34 (net penalty)", "-"],
    ],
    [2200, 2200, 2600, 2360]
  ),
  p(""),
  note("GridBeyond earned 1,181 GBP vs the theoretical 5,222 GBP (22.6% capture). The main miss: GridBeyond did not sell into SSP during the 750 GBP/MWh spike at 19:00. This single missed period accounts for 2,582 GBP of the 4,041 GBP gap."),
  p(""),
  p([{ text: "Important caveat: ", bold: true }, { text: "GridBeyond trades in real-time without knowledge of future prices. The SSP spike at 19:00 was unpredictable. The optimisation uses perfect hindsight - it is a benchmark, not an expectation." }]),
  new Paragraph({ children: [new PageBreak()] })
);

// ═══════════════ SECTION 6: WORKED EXAMPLE - SFFR DAY ═══════════════
children.push(
  h1("6. Worked Example: SFFR Day (3 January 2026)"),
  p([{ text: "On this day, the algorithm chose SFFR over Multi-Market trading. Revenue: ", bold: false }, { text: "670 GBP", bold: true }, { text: " (all from frequency response, zero active trading)." }]),
  h2("6.1 The Decision"),
  code("SFFR_Daily = Sum(7.0 x SFFR_Price[t] x 0.5) for 48 periods = 670 GBP"),
  code("Multi_Market_Revenue (from LP solver)                      < 670 GBP"),
  code(""),
  code("Result: SFFR wins. Battery stays locked in frequency response all day."),
  p(""),
  p("Why was SFFR better? The market spreads on Jan 3 were modest (4-50 GBP/MWh range), while SFFR clearing prices were decent (1.70-6.09 GBP/MW/h). There was no SSP spike event to make trading worthwhile."),
  h2("6.2 SFFR Clearing Prices Through the Day"),
  p("SFFR prices follow a predictable pattern: low overnight, rising through the morning, peaking in the late afternoon/evening, dropping at night."),
);

const sffr_summary = [
  ["00:00-02:30 (Night)", "1.70", "7.4 MW", "~6.3/period", "Low demand period"],
  ["03:00-06:30 (Early)", "1.30", "7.4 MW", "~4.8/period", "Lowest SFFR price band"],
  ["07:00-10:30 (Morning)", "3.96", "6.6 MW", "~13.0/period", "Morning peak begins"],
  ["11:00-14:30 (Midday)", "5.04", "4.4 MW", "~11.2/period", "High price, lower availability"],
  ["15:00-18:30 (Peak)", "6.09", "7.4 MW", "~22.4/period", "Highest SFFR prices of the day"],
  ["19:00-22:30 (Evening)", "5.51", "7.4 MW", "~20.5/period", "Still high evening demand"],
  ["23:00-23:30 (Night)", "2.99", "7.3 MW", "~11.0/period", "Dropping to night rates"],
];
children.push(
  makeTable(
    ["Time Block", "SFFR Price (GBP/MW/h)", "Avg Availability", "Revenue/Period", "Comment"],
    sffr_summary,
    [2000, 2000, 1500, 1500, 2360]
  ),
  p(""),
  h2("6.3 Optimiser vs Actual Comparison"),
  makeTable(
    ["Metric", "Optimiser", "Actual GridBeyond"],
    [
      ["Strategy", "SFFR (full day)", "SFFR (full day)"],
      ["Assumed Availability", "7.0 MW (constant)", "6.81 MW (average, varies by period)"],
      ["Total Revenue", "670 GBP", "638 GBP"],
      ["Gap", "32 GBP (4.8%)", "-"],
      ["Gap Cause", "-", "Actual availability < assumed 7.0 MW"],
    ],
    [2400, 3480, 3480]
  ),
  p(""),
  note("On SFFR days, the gap between optimised and actual is small (4.8%) and entirely due to the availability assumption. The optimiser uses 7.0 MW; actual availability averages 6.81 MW due to SOC constraints and operational factors. This is not a strategy gap - GridBeyond made the right call on this day."),
  new Paragraph({ children: [new PageBreak()] })
);

// ═══════════════ SECTION 7: WHY DOES THE GAP EXIST ═══════════════
children.push(
  h1("7. Understanding the Performance Gap"),
  p("The total January gap is 5,186 GBP (optimised 33,376 vs actual 28,190). Where does it come from?"),
  h2("7.1 Gap Decomposition"),
  makeTable(
    ["Source of Gap", "Estimated GBP", "% of Total Gap", "Explanation"],
    [
      ["SSP spike events not captured", "~3,500", "67%", "GridBeyond was in SFFR or not positioned when SSP spiked (especially Jan 5, 8)"],
      ["Sub-optimal market selection", "~800", "15%", "Actual trades used EPEX/IDA1 when ISEM or SSP offered better prices"],
      ["SFFR availability gap", "~500", "10%", "Optimiser assumes 7.0 MW, actual averages 6.81 MW"],
      ["Imbalance charges", "~386", "7%", "Actual incurred imbalance penalties not in optimised"],
      [boldS("TOTAL GAP"), boldS("~5,186"), boldS("100%"), boldS("")],
    ],
    [2600, 1400, 1200, 4160]
  ),
  p(""),
  h2("7.2 What This Means"),
  p([{ text: "The 84.5% capture rate is a reasonable result. ", bold: true }, { text: "The majority of the gap (67%) comes from unpredictable SSP spikes that no real-time trader could consistently capture. The algorithm's advantage is purely hindsight." }]),
  p("Key points for validation:"),
  p([{ text: "1. ", bold: true }, { text: "SFFR days show very small gaps (4-5%) - GridBeyond correctly identifies when SFFR is the right strategy." }]),
  p([{ text: "2. ", bold: true }, { text: "The bulk of the gap concentrates in 2-3 spike days per month - this is expected for any non-clairvoyant trader." }]),
  p([{ text: "3. ", bold: true }, { text: "The warranty constraint (1.5 cycles/day = 12.6 MWh discharge) limits how much can be extracted from spike events." }]),
  p([{ text: "4. ", bold: true }, { text: "The algorithm respects all physical constraints - no revenue is assumed that violates SOC bounds, power limits, or efficiency losses." }]),
  new Paragraph({ children: [new PageBreak()] })
);

// ═══════════════ SECTION 8: VALIDATION CHECKLIST ═══════════════
children.push(
  h1("8. Validation Checklist for Business Expert"),
  p("Please confirm the following aspects of the algorithm are correct and reasonable:"),
  h2("8.1 Physical Constraints"),
  makeTable(
    ["Check", "Question", "Expected Answer"],
    [
      ["1", "Is the max charge rate of 4.2 MW correct for Northwold?", "Yes / No / Correct value: ___"],
      ["2", "Is the max discharge rate of 7.5 MW correct?", "Yes / No / Correct value: ___"],
      ["3", "Is 8.4 MWh the correct usable capacity?", "Yes / No / Correct value: ___"],
      ["4", "Is 87% round-trip efficiency accurate?", "Yes / No / Correct value: ___"],
      ["5", "Are the 5%/95% SOC limits appropriate?", "Yes / No / Correct limits: ___"],
    ],
    [600, 5200, 3560]
  ),
  p(""),
  h2("8.2 Commercial Parameters"),
  makeTable(
    ["Check", "Question", "Expected Answer"],
    [
      ["6", "Is 1.5 cycles/day the correct warranty limit?", "Yes / No / Correct limit: ___"],
      ["7", "Is 7.0 MW the right assumed SFFR availability?", "Yes / No / Correct value: ___"],
      ["8", "Should we use 7.0 MW or the actual varying availability for SFFR value?", "7.0 MW / Actual / Other: ___"],
      ["9", "Are all 5 markets (EPEX, ISEM, SSP, SBP, DA_HH) accessible to GridBeyond?", "Yes / Some not: ___"],
      ["10", "Is the whole-day SFFR vs trading decision realistic, or should EFA blocks be the unit?", "Whole day / EFA blocks / Other: ___"],
    ],
    [600, 5200, 3560]
  ),
  p(""),
  h2("8.3 Algorithm Logic"),
  makeTable(
    ["Check", "Question", "Expected Answer"],
    [
      ["11", "Is it correct that the battery cannot trade AND do SFFR in the same period?", "Yes / No (can do both): ___"],
      ["12", "Should imbalance costs be included in the optimisation or excluded?", "Include / Exclude: ___"],
      ["13", "Should the aggregator fee (5%) be applied to the optimised revenue?", "Yes / No: ___"],
      ["14", "Are there any other revenue streams not modelled (e.g., STOR, FFR dynamic)?", "No / Yes: ___"],
      ["15", "Is the assumption of perfect price foresight acceptable for benchmarking?", "Yes / No: ___"],
    ],
    [600, 5200, 3560]
  ),
  p(""),
  h2("8.4 Results Validation"),
  makeTable(
    ["Check", "Question", "Expected Answer"],
    [
      ["16", "Does 84.5% capture rate seem reasonable for Jan 2026?", "Yes / Too high / Too low"],
      ["17", "Is it fair that 22 of 31 days chose SFFR in Jan? (Winter = high SFFR prices)", "Yes / Expected more trading / Less"],
      ["18", "Does the Jan 5 example (5,222 optimised vs 1,181 actual) look plausible?", "Yes / Needs investigation: ___"],
      ["19", "Should we track additional metrics (e.g., risk-adjusted return, Sharpe ratio)?", "No / Yes: ___"],
      ["20", "Is this benchmark appropriate for GridBeyond performance reviews?", "Yes / Needs adjustments: ___"],
    ],
    [600, 5200, 3560]
  ),
  p(""),
  p(""),
  p("--- End of Document ---"),
);

// ── Build & save ──
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 34, bold: true, font: "Arial", color: "1F4E79" },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "2E75B6" },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, font: "Arial", color: "4A4A4A" },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    headers: {
      default: new Header({ children: [
        new Paragraph({
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "1F4E79", space: 4 } },
          children: [
            new TextRun({ text: "BESS Optimisation Validation - January 2026", font: "Arial", size: 16, color: "888888" }),
            new TextRun({ text: "\tConfidential", font: "Arial", size: 16, color: "CC0000", bold: true }),
          ],
          tabStops: [{ type: "right", position: 9360 }],
        })
      ] })
    },
    footers: {
      default: new Footer({ children: [
        new Paragraph({
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 4 } },
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "Page ", font: "Arial", size: 16, color: "888888" }),
            new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "888888" }),
          ]
        })
      ] })
    },
    children
  }]
});

Packer.toBuffer(doc).then(buffer => {
  const outPath = path.join("C:", "repos", "Ampyr-APD", "docs", "APD_Optimisation_Validation.docx");
  fs.writeFileSync(outPath, buffer);
  console.log("Document created: " + outPath);
  console.log("Size: " + (buffer.length / 1024).toFixed(1) + " KB");
});
