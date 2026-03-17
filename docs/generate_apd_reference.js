const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
  WidthType, ShadingType, PageNumber, PageBreak, TableOfContents
} = require(path.join(process.env.APPDATA || "", "npm/node_modules/docx"));

// ── Shared styles ──
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 60, bottom: 60, left: 100, right: 100 };
const headerShading = { fill: "1F4E79", type: ShadingType.CLEAR };
const altShading = { fill: "F2F7FB", type: ShadingType.CLEAR };
const TW = 9360; // table width (US Letter with 1" margins)

function hdr(text) {
  return new TextRun({ text, bold: true, color: "FFFFFF", font: "Arial", size: 20 });
}
function cell(text, opts = {}) {
  const runs = Array.isArray(text) ? text : [new TextRun({ text: String(text), font: "Arial", size: 18, ...opts })];
  return new Paragraph({ spacing: { before: 20, after: 20 }, children: runs });
}
function headerCell(text, w) {
  return new TableCell({ borders, width: { size: w, type: WidthType.DXA }, shading: headerShading, margins: cellMargins, verticalAlign: "center", children: [cell("", { text: undefined }), new Paragraph({ children: [hdr(text)] })] });
}
// Simpler headerCell
function hCell(text, w) {
  return new TableCell({
    borders, width: { size: w, type: WidthType.DXA }, shading: headerShading, margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", font: "Arial", size: 20 })] })]
  });
}
function dCell(text, w, shade) {
  const s = shade ? altShading : undefined;
  return new TableCell({
    borders, width: { size: w, type: WidthType.DXA }, shading: s, margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text: String(text), font: "Arial", size: 18 })] })]
  });
}
function bCell(text, w, shade) {
  const s = shade ? altShading : undefined;
  return new TableCell({
    borders, width: { size: w, type: WidthType.DXA }, shading: s, margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text: String(text), font: "Arial", size: 18, bold: true })] })]
  });
}

function h1(text) { return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 200 }, children: [new TextRun({ text, font: "Arial" })] }); }
function h2(text) { return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 160 }, children: [new TextRun({ text, font: "Arial" })] }); }
function h3(text) { return new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 200, after: 120 }, children: [new TextRun({ text, font: "Arial" })] }); }
function p(text, opts = {}) {
  const runs = typeof text === "string"
    ? [new TextRun({ text, font: "Arial", size: 22, ...opts })]
    : text.map(t => typeof t === "string" ? new TextRun({ text: t, font: "Arial", size: 22 }) : new TextRun({ font: "Arial", size: 22, ...t }));
  return new Paragraph({ spacing: { before: 60, after: 60 }, children: runs });
}
function code(text) {
  return new Paragraph({
    spacing: { before: 40, after: 40 },
    indent: { left: 360 },
    children: [new TextRun({ text, font: "Consolas", size: 18, color: "333333" })]
  });
}

function makeTable(headers, rows, colWidths) {
  const tw = colWidths.reduce((a,b) => a+b, 0);
  const tRows = [
    new TableRow({ children: headers.map((h, i) => hCell(h, colWidths[i])) }),
    ...rows.map((row, ri) => new TableRow({
      children: row.map((c, ci) => {
        const shade = ri % 2 === 1;
        return typeof c === "object" && c._bold ? bCell(c.text, colWidths[ci], shade) : dCell(String(c), colWidths[ci], shade);
      })
    }))
  ];
  return new Table({ width: { size: tw, type: WidthType.DXA }, columnWidths: colWidths, rows: tRows });
}

function bold(t) { return { text: t, _bold: true }; }

// ── Build Document ──
const children = [];

// Title page
children.push(
  new Paragraph({ spacing: { before: 3000 }, alignment: AlignmentType.CENTER, children: [] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "AMPYR ENERGY", font: "Arial", size: 36, bold: true, color: "1F4E79" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [new TextRun({ text: "Asset Performance Dashboard (APD)", font: "Arial", size: 52, bold: true, color: "1F4E79" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [new TextRun({ text: "Technical Reference Document", font: "Arial", size: 32, color: "2E75B6" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [new TextRun({ text: "For DoublU Development Team", font: "Arial", size: 28, color: "666666" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Version 1.0 | March 2026", font: "Arial", size: 24, color: "888888" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 }, children: [new TextRun({ text: "Confidential - Project Lazarus", font: "Arial", size: 22, bold: true, color: "CC0000" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 1600 }, children: [new TextRun({ text: "Asset: Northwold Solar Farm BESS (8.4 MWh)", font: "Arial", size: 22, color: "666666" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Aggregator: GridBeyond | DNO: UK Power Networks", font: "Arial", size: 22, color: "666666" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Author: Ankit Agarwal, GM - Product & Technology", font: "Arial", size: 22, color: "666666" })] }),
  new Paragraph({ children: [new PageBreak()] })
);

// TOC
children.push(
  new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "Table of Contents", font: "Arial" })] }),
  new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),
  new Paragraph({ children: [new PageBreak()] })
);

// ════════════════════════════════════════════════
// SECTION 1: SYSTEM OVERVIEW
// ════════════════════════════════════════════════
children.push(
  h1("1. System Overview"),
  p("The Ampyr Asset Performance Dashboard (APD) is a Streamlit-based analytics platform for monitoring and benchmarking BESS (Battery Energy Storage System) performance. The prototype is built for the Northwold Solar Farm 8.4 MWh battery, operated by GridBeyond as the market aggregator."),
  h2("1.1 Architecture Overview"),
  p("The application follows a layered architecture:"),
  makeTable(
    ["Layer", "Technology", "Purpose"],
    [
      ["UI Layer", "Streamlit + Plotly", "Interactive dashboards, charts, tables"],
      ["Business Logic", "Python functions", "Revenue calculations, benchmarking, optimization analysis"],
      ["Data Pipeline", "Pandas + OpenPyXL", "ETL from raw Excel to clean CSV"],
      ["Optimization Engine", "SciPy linprog (HiGHS)", "Linear programming for multi-market dispatch"],
      ["Configuration", "Python module", "Asset parameters, market definitions"],
    ],
    [2000, 2500, 4860]
  ),
  p(""),
  h2("1.2 Data Sources"),
  makeTable(
    ["Source", "Format", "Resolution", "Content"],
    [
      ["GridBeyond", "Excel (.xlsx)", "30-min HH", "Market prices, revenue streams, ancillary services, energy volumes"],
      ["SCADA (Legacy)", "Excel (.xlsx)", "10-min", "Power (kW), SOC (%), Frequency (Hz)"],
      ["SCADA (New)", "Excel (.xlsx, msrc10m sheet)", "10-min", "Power, SOC, SOH, RTE, Cycles, Availability, Import/Export energy"],
      ["EMR Settlement", "CSV (T062) + PDF", "Monthly", "Capacity Market payments, weighting factors"],
      ["Hartree Supply", "PDF invoices", "Monthly", "DUoS charges (Red/Amber/Green GDuos), DNO fixed charges"],
      ["IAR Projections", "Excel (.xlsx)", "Monthly", "Investment Appraisal Report projected revenue by stream"],
      ["Modo Energy", "Manual entry", "Monthly", "GB BESS Index benchmark (GBP/MW/year)"],
    ],
    [1800, 2000, 1400, 4160]
  ),
  p(""),
  h2("1.3 Key File Structure"),
  makeTable(
    ["Path", "Purpose"],
    [
      ["streamlit_dashboard.py", "Main dashboard application (~4,400 lines) - all pages and visualization logic"],
      ["src/config/asset_config.py", "Asset physical and commercial parameters (single source of truth)"],
      ["src/data_cleaning/loader.py", "Data loading: GridBeyond Excel + SCADA Excel (legacy & new formats)"],
      ["src/data_cleaning/transformer.py", "Resampling (10min to 30min), SOC calculation, outlier detection"],
      ["src/data_cleaning/merger.py", "Merge GridBeyond + SCADA into Master CSV, gap detection"],
      ["src/data_cleaning/pipeline.py", "Orchestrates full ETL pipeline (find files, load, resample, merge, report)"],
      ["src/data_cleaning/report.py", "Data quality report generation (missing values, gaps, warnings)"],
      ["src/data_cleaning/invoice_loader.py", "Parse EMR CSVs, Hartree PDFs, Summary Statements, Solar Generation"],
      ["src/data_cleaning/invoice_reconciler.py", "Reconcile energy volumes and revenue across multiple sources"],
      ["src/phase3_multimarket.py", "Multi-market LP optimization engine (EPEX, ISEM, SSP, SBP, DA_HH)"],
      ["src/pages/data_quality.py", "Data import & quality reporting UI page"],
      ["src/pages/invoice_analysis.py", "Invoice reconciliation UI page"],
      ["data/Master_BESS_Analysis_*.csv", "Processed monthly master datasets"],
      ["data/Optimized_Results_*.csv", "Multi-market optimization output per month"],
      ["extra/Northwold BESS Revenue_IAR.xlsx", "IAR projections spreadsheet"],
    ],
    [4000, 5360]
  ),
  new Paragraph({ children: [new PageBreak()] })
);

// ════════════════════════════════════════════════
// SECTION 2: ASSET CONFIGURATION
// ════════════════════════════════════════════════
children.push(
  h1("2. Asset Configuration Parameters"),
  p("All asset parameters are defined in src/config/asset_config.py. These values drive every calculation in the system."),
  h2("2.1 Physical Parameters"),
  makeTable(
    ["Parameter", "Code Name", "Value", "Unit", "Description"],
    [
      ["Max Charge Rate", "P_IMP_MAX_MW", "4.2", "MW", "Maximum import (charging) power"],
      ["Max Discharge Rate", "P_EXP_MAX_MW", "7.5", "MW", "Maximum export (discharging) power - asymmetric"],
      ["Usable Capacity", "CAPACITY_MWH", "8.4", "MWh", "Total usable energy storage"],
      ["Round-Trip Efficiency", "EFF_ROUND_TRIP", "0.87", "fraction", "AC-to-AC efficiency (87%)"],
      ["One-Way Efficiency", "EFF_ONE_WAY", "0.933", "fraction", "Square root of round-trip (93.3%)"],
      ["SOC Minimum", "SOC_MIN_PCT", "0.05", "fraction", "5% floor (safety buffer)"],
      ["SOC Maximum", "SOC_MAX_PCT", "0.95", "fraction", "95% ceiling (safety buffer)"],
      ["SOC Min (absolute)", "SOC_MIN_MWH", "0.42", "MWh", "5% x 8.4 MWh"],
      ["SOC Max (absolute)", "SOC_MAX_MWH", "7.98", "MWh", "95% x 8.4 MWh"],
      ["Time Step", "DT_HOURS", "0.5", "hours", "30-minute settlement periods"],
    ],
    [2000, 1800, 800, 900, 3860]
  ),
  p(""),
  h2("2.2 Commercial & Warranty Parameters"),
  makeTable(
    ["Parameter", "Code Name", "Value", "Unit"],
    [
      ["Warranty Cycles/Day", "CYCLES_PER_DAY", "1.5", "cycles/day"],
      ["Max Daily Throughput", "MAX_DAILY_THROUGHPUT_MWH", "12.6", "MWh"],
      ["Aggregator", "AGGREGATOR_NAME", "GridBeyond", "-"],
      ["Owner Revenue Share", "OWNER_SHARE", "0.95", "fraction (95%)"],
      ["Aggregator Fee", "AGGREGATOR_SHARE", "0.05", "fraction (5%)"],
      ["Annual Degradation", "WARRANTY_DEGRADATION_ANNUAL_PCT", "2.5", "%/year"],
      ["Degradation per Cycle", "(calculated)", "0.00457", "%/cycle"],
    ],
    [2500, 3000, 1500, 2360]
  ),
  p(""),
  p([{ text: "Degradation per Cycle formula: ", bold: true }, { text: "2.5% / (1.5 cycles/day x 365 days) = 0.00457% per cycle" }]),
  new Paragraph({ children: [new PageBreak()] })
);

// ════════════════════════════════════════════════
// SECTION 3: DATA PIPELINE
// ════════════════════════════════════════════════
children.push(
  h1("3. Data Pipeline (ETL)"),
  p("The data pipeline transforms raw Excel exports into analysis-ready Master CSV files. The pipeline is orchestrated by src/data_cleaning/pipeline.py."),
  h2("3.1 Pipeline Steps"),
  p([{ text: "Step 1 - File Detection: ", bold: true }, { text: "find_files() scans folder for GridBeyond (.xlsx with 'Backing Data' or 'Northwold_' prefix) and SCADA files (export-*.xlsx or mon-yy-*.xlsx pattern)." }]),
  p([{ text: "Step 2 - Load GridBeyond: ", bold: true }, { text: "load_gridbeyond() reads Excel, finds timestamp column (case-insensitive), parses dates, cleans column names (removes newlines/spaces), sets Timestamp as index." }]),
  p([{ text: "Step 3 - Load SCADA: ", bold: true }, { text: "load_scada() auto-detects format. Legacy: 5 columns (date, Availability, SOC, Power, Frequency) at 10-min. New: 12 columns from msrc10m sheet with [Northwold] suffix stripped." }]),
  p([{ text: "Step 4 - Resample SCADA: ", bold: true }, { text: "resample_scada() converts 10-min to 30-min using aggregation rules: Power_MW=mean, SOC=last, Frequency=mean, daily cumulatives=last, availability=mean." }]),
  p([{ text: "Step 5 - Fill Missing SOC: ", bold: true }, { text: "calculate_missing_soc() forward-integrates Power with efficiency losses to fill gaps. See formula below." }]),
  p([{ text: "Step 6 - Merge: ", bold: true }, { text: "align_timestamps() trims to common date range, then merge_data() joins on Timestamp index (outer join). SCADA columns prefixed with SCADA_ to avoid conflicts." }]),
  p([{ text: "Step 7 - Quality Report: ", bold: true }, { text: "generate_quality_report() computes missing values, gaps, overlap %, SOC validation, and warnings." }]),
  p([{ text: "Step 8 - Export: ", bold: true }, { text: "Save to data/Master_BESS_Analysis_{Month}_{Year}.csv" }]),
  p(""),
  h2("3.2 SOC Calculation Formula (Missing Value Fill)"),
  p("When SOC values are missing from SCADA, they are reconstructed by integrating Power with efficiency losses:"),
  code("For charging (Power > 0):"),
  code("  delta_SOC = (Power_MW x dt_hours x sqrt(eff_round_trip)) / Capacity_MWh x 100"),
  code("  delta_SOC = (Power_MW x 0.5 x 0.933) / 8.4 x 100"),
  code(""),
  code("For discharging (Power < 0):"),
  code("  delta_SOC = (Power_MW x dt_hours / sqrt(eff_round_trip)) / Capacity_MWh x 100"),
  code("  delta_SOC = (Power_MW x 0.5 / 0.933) / 8.4 x 100"),
  code(""),
  code("New_SOC = Previous_SOC + delta_SOC   (clamped to [0, 100])"),
  p(""),
  p("Forward-fills from left to right, then backward-fills remaining gaps. The SOC_calculated column marks which values were computed vs original."),
  h2("3.3 SCADA Column Mapping (New Format)"),
  makeTable(
    ["Original Column (with [Northwold] suffix)", "Mapped Name", "Aggregation"],
    [
      ["Batteries Power Output Inverters AC (kW)", "Power_MW (converted kW to MW)", "mean"],
      ["BESS Site batteries availability (%)", "Availability", "mean"],
      ["BESS State Of Health (%)", "SOH", "last"],
      ["BESS Cumulative Round Trip Efficiency (POC) (%)", "RTE", "last"],
      ["Batteries Total Cycles (-)", "Daily_Cycles", "last"],
      ["Batteries Total Cycles (to date) (-)", "Cumulative_Cycles", "last"],
      ["BESS Exported Energy Site (daily) (kWh)", "Daily_Export_kWh", "last"],
      ["BESS Imported Energy Site (daily) (kWh)", "Daily_Import_kWh", "last"],
      ["BESS Site inverters availability (%)", "Inverter_Availability", "mean"],
    ],
    [4500, 2800, 2060]
  ),
  new Paragraph({ children: [new PageBreak()] })
);

// ════════════════════════════════════════════════
// SECTION 4: OPTIMIZATION ENGINE
// ════════════════════════════════════════════════
children.push(
  h1("4. Multi-Market Optimization Engine"),
  p("The optimization engine (src/phase3_multimarket.py) uses linear programming to find the revenue-maximizing battery dispatch schedule across 5 wholesale/balancing markets simultaneously."),
  h2("4.1 Markets Modeled"),
  makeTable(
    ["Market", "Column Name in Data", "Type", "Description"],
    [
      ["EPEX", "Day Ahead Price (EPEX)", "Wholesale Day Ahead", "Primary wholesale market, GBP/MWh"],
      ["ISEM", "GB-ISEM Intraday 1 Price", "Intraday Auction", "Intraday cross-border market"],
      ["SSP", "SSP", "System Sell Price", "GB balancing mechanism sell price"],
      ["SBP", "SBP", "System Buy Price", "GB balancing mechanism buy price"],
      ["DA_HH", "DA HH Price", "Day Ahead Half-Hourly", "Half-hourly day-ahead variant"],
    ],
    [1200, 2800, 2000, 3360]
  ),
  p(""),
  h2("4.2 Market Price Selection"),
  p("For each 30-minute period, the optimizer selects the best buy and sell markets:"),
  code("Buy_Price[t]  = min(EPEX[t], ISEM[t], SSP[t], SBP[t], DA_HH[t])"),
  code("Sell_Price[t] = max(EPEX[t], ISEM[t], SSP[t], SBP[t], DA_HH[t])"),
  code("Market_Spread[t] = Sell_Price[t] - Buy_Price[t]"),
  p(""),
  h2("4.3 Linear Programming Formulation"),
  p([{ text: "Decision Variables ", bold: true }, { text: "(3T variables per day, where T = 48 periods):" }]),
  code("x = [Charge_0...Charge_47, Discharge_0...Discharge_47, SoC_0...SoC_47]"),
  p(""),
  p([{ text: "Objective Function (Minimize): ", bold: true }]),
  code("c = [Buy_Price_0 x 0.5, ..., Buy_Price_47 x 0.5,     (charge costs)"),
  code("     -Sell_Price_0 x 0.5, ..., -Sell_Price_47 x 0.5,  (discharge revenue, negated)"),
  code("     0, ..., 0]                                        (SoC: no direct cost)"),
  p(""),
  p([{ text: "Equality Constraints - SoC Physics (48 equations): ", bold: true }]),
  code("SoC[t] = SoC[t-1] + Charge[t] x 0.933 x 0.5 - Discharge[t] / 0.933 x 0.5"),
  code("SoC[0] = start_soc (initial condition, default 4.2 MWh = 50%)"),
  p(""),
  p([{ text: "Inequality Constraint - Daily Throughput Limit (1 equation): ", bold: true }]),
  code("Sum(Discharge[t] x 0.5) <= 12.6 MWh   (= 1.5 cycles x 8.4 MWh capacity)"),
  p(""),
  p([{ text: "Variable Bounds: ", bold: true }]),
  code("Charge[t]:    [0, 4.2 MW]   (or [0, 0] if SFFR-locked)"),
  code("Discharge[t]: [0, 7.5 MW]   (or [0, 0] if SFFR-locked)"),
  code("SoC[t]:       [0.42, 7.98] MWh  (5% to 95% of 8.4 MWh)"),
  p(""),
  p([{ text: "Solver: ", bold: true }, { text: "scipy.optimize.linprog with method='highs' (HiGHS interior-point solver)" }]),
  h2("4.4 Strategy Selection Logic"),
  p("Three independent strategies are computed for each day:"),
  makeTable(
    ["Strategy", "Description", "Output Column Prefix"],
    [
      ["1. EPEX Daily", "Compare full-day SFFR revenue vs EPEX-only LP. Pick higher.", "Optimised_*_Daily"],
      ["2. EPEX EFA Block", "Compare per 4-period (2hr) EFA block: SFFR vs EPEX LP. Allows mixing.", "Optimised_*_EFA"],
      ["3. Multi-Market", "Compare full-day SFFR vs 5-market LP. Pick higher. Best overall.", "Optimised_*_Multi"],
    ],
    [2200, 4860, 2300]
  ),
  p(""),
  p([{ text: "SFFR Revenue formula: ", bold: true }]),
  code("SFFR_Daily = Sum(7.0 MW x SFFR_Price[t] x 0.5 hours)  for all 48 periods"),
  p(""),
  p([{ text: "Final strategy selection: ", bold: true }]),
  code("If SFFR_Daily > Multi_Market_Revenue: choose SFFR (lock battery)"),
  code("Else: choose Multi-Market dispatch"),
  h2("4.5 Revenue Calculation"),
  code("Revenue[t] = (Discharge[t] x Sell_Price[t] - Charge[t] x Buy_Price[t]) x 0.5"),
  code("Total_Daily = Sum(Revenue[t]) for t = 0 to 47"),
  p(""),
  h2("4.6 Output Columns per Timestamp"),
  makeTable(
    ["Column", "Type", "Description"],
    [
      ["Optimised_Net_MWh_Multi", "float", "(Discharge - Charge) x dt for multi-market strategy"],
      ["Optimised_SoC_Multi", "float", "State of charge tracking (MWh)"],
      ["Strategy_Selected_Multi", "string", "'SFFR' or 'Multi-Market'"],
      ["Market_Used_Multi", "string", "'Buy-EPEX', 'Sell-ISEM', 'Idle', etc."],
      ["Optimised_Revenue_Multi", "float", "Revenue for this period (GBP)"],
      ["Best_Buy_Price", "float", "Minimum price across all markets"],
      ["Best_Sell_Price", "float", "Maximum price across all markets"],
      ["Best_Buy_Market", "string", "Market name with lowest price"],
      ["Best_Sell_Market", "string", "Market name with highest price"],
      ["Market_Spread", "float", "Sell_Price - Buy_Price (GBP/MWh)"],
    ],
    [2800, 1000, 5560]
  ),
  new Paragraph({ children: [new PageBreak()] })
);

// ════════════════════════════════════════════════
// SECTION 5: DASHBOARD PAGES
// ════════════════════════════════════════════════
children.push(
  h1("5. Dashboard Pages & Formulas"),
  p("The dashboard has 12 pages organized into general (month-independent) and monthly analysis sections."),
  h2("5.1 Navigation Structure"),
  makeTable(
    ["Page", "Function", "Type", "Description"],
    [
      ["Asset Details", "show_asset_details()", "General", "Physical specs, warranty info, system configuration"],
      ["Data Import", "show_data_quality_page()", "General", "File upload, ETL pipeline execution, quality report"],
      ["Executive Comparison", "show_executive_comparison()", "General", "Multi-month Actual vs Optimal with CM + DUoS"],
      ["Benchmarks", "show_benchmark_comparison()", "General", "Industry comparison, IAR vs Actual, TB spreads"],
      ["Export Reports", "show_pdf_export_page()", "General", "Download text reports and CSV data"],
      ["Invoice Analysis", "show_invoice_analysis()", "General", "Energy and revenue reconciliation across sources"],
      ["Operations Summary", "show_operations_summary()", "Monthly", "Revenue breakdown, SOC, power, market prices"],
      ["Multi-Market Optimization", "show_multimarket_optimization()", "Monthly", "Strategy comparison, market utilization"],
      ["Market Prices", "show_market_price_analysis()", "Monthly", "Price spreads, volatility, hourly patterns"],
      ["Imbalance Analysis", "show_imbalance_deep_dive()", "Monthly", "Imbalance charges, root cause, correlation"],
      ["Ancillary Services", "show_ancillary_services_analysis()", "Monthly", "SFFR/DC/DM/DR revenue and efficiency"],
      ["BESS Health", "show_bess_health()", "Monthly", "Cycle counting, degradation, warranty compliance"],
      ["Performance Report", "show_report_page()", "Monthly", "Executive summary with all KPIs"],
    ],
    [2200, 2800, 1000, 3360]
  ),
  new Paragraph({ children: [new PageBreak()] }),

  // ── 5.2 Revenue Calculations ──
  h2("5.2 Core Revenue Calculations"),
  p("The fundamental revenue calculation used across all pages:"),
  code("Total_Revenue = SFFR + EPEX_DA + IDA1 + IDC + Imbalance_Revenue - Imbalance_Charge"),
  p(""),
  p("Where:"),
  makeTable(
    ["Stream", "Data Column(s)", "Description"],
    [
      ["SFFR", "SFFR revenues", "Static Firm Frequency Response - ancillary service"],
      ["EPEX_DA", "EPEX 30 DA Revenue + EPEX DA Revenues", "Day-ahead wholesale market (two variants summed)"],
      ["IDA1", "IDA1 Revenue", "Intraday auction market"],
      ["IDC", "IDC Revenue", "Intraday continuous market"],
      ["Imbalance Revenue", "Imbalance Revenue", "Positive imbalance settlement"],
      ["Imbalance Charge", "Imbalance Charge", "Penalties for position mismatch (subtracted)"],
    ],
    [2000, 3500, 3860]
  ),
  p(""),
  p([{ text: "With CM and DUoS (full revenue): ", bold: true }]),
  code("Total_All = Total_Revenue + Capacity_Market + DUoS_Credit - DUoS_Fixed_Charges"),
  p(""),
  h2("5.3 Annualized Revenue per MW"),
  code("Annual_per_MW = (Monthly_Revenue / Days_in_Month) x 365 / Capacity_MW"),
  code(""),
  code("Example (Sept 2025):"),
  code("  = (14,457 / 30) x 365 / 4.2 = GBP 41,876/MW/year"),
  p(""),
  h2("5.4 Capture Rate"),
  code("Capture_Rate = (Actual_Revenue / Optimal_Revenue) x 100"),
  code("Revenue_Gap = Optimal_Revenue - Actual_Revenue"),
  p(""),

  // ── 5.5 Cycle Calculations ──
  h2("5.5 Cycle Calculation Methods"),
  p("Three methods are implemented in calculate_cycles():"),
  makeTable(
    ["Method", "Formula", "Description"],
    [
      ["A: Discharge-only", "Sum(P > 0) x dt / Capacity_MWh", "Legacy GridBeyond method. Only counts outbound energy."],
      ["B: Full Equivalent (Industry Standard)", "(Discharge_MWh + Charge_MWh) / 2 / Capacity_MWh", "ISO 62619 standard. One cycle = full charge + discharge."],
      ["C: Throughput-based", "Total_Throughput / (2 x Capacity_MWh)", "Mathematically identical to Method B."],
    ],
    [2500, 3500, 3360]
  ),
  p(""),
  code("Degradation_per_Month = Total_Cycles x 0.00457%"),
  code("Warranty_Status = 'OK' if Avg_Daily_Cycles <= 1.5, else 'WARRANTY VOID'"),
  p(""),

  // ── 5.6 TB Spread ──
  h2("5.6 Top-Bottom Spread Benchmarks"),
  p("TB spreads measure daily arbitrage potential from price volatility:"),
  code("Step 1: Aggregate half-hourly prices to hourly (average of 2 periods)"),
  code("Step 2: Sort 24 hourly prices descending"),
  code(""),
  code("TB1 = max(prices) - min(prices)                    (1-hour battery)"),
  code("TB2 = sum(2 highest) - sum(2 lowest)               (2-hour battery - our benchmark)"),
  code("TB3 = sum(3 highest) - sum(3 lowest)               (3-hour battery)"),
  code(""),
  code("TB2_Max_Revenue = TB2 x 8.4 MWh                    (theoretical max per day)"),
  code("TB2_Capture = (Actual_Arbitrage / TB2_Max) x 100   (can exceed 100% via multi-cycling)"),
  code(""),
  code("Industry benchmark (Modo Energy): 142% TB2 capture"),
  p(""),
  p("Captures above 100% are possible through: multiple daily cycles, intraday market optimization, ancillary service stacking, and balancing mechanism participation."),

  new Paragraph({ children: [new PageBreak()] }),

  // ── 5.7 Executive Comparison ──
  h2("5.7 Executive Comparison Page"),
  p("Compares all available months (Sep 2025 - Jan 2026) side by side."),
  p([{ text: "Data loaded per month: ", bold: true }]),
  code("{ actual: {sffr, epex, ida1, idc, imbalance, total},"),
  code("  optimal: Multi_Market_Revenue_Sum,"),
  code("  cm: Capacity_Market_Payment,"),
  code("  duos_credit: DUoS_Net_Credit,"),
  code("  duos_fixed: DNO_Fixed_Charges,"),
  code("  total_all: actual + cm + duos_credit - duos_fixed }"),
  p(""),
  p("Sections: Key Performance Metrics, Revenue Comparison Bar Chart, Gap Analysis Table (with CM + DUoS), Revenue by Market (pie charts + table), Executive Summary."),

  // ── 5.8 Benchmarks ──
  h2("5.8 Benchmarks Page"),
  p("Four major sections:"),
  p([{ text: "Section 1 - Northwold vs Industry: ", bold: true }, { text: "Compares total revenue (incl. CM + DUoS) converted to GBP/MW/year against Modo Energy benchmarks and industry bands (Low: GBP 36k, Mid: GBP 60k, High: GBP 88k)." }]),
  p([{ text: "Section 2 - IAR vs Actual: ", bold: true }, { text: "Loads IAR projections from Excel (extra/Northwold BESS Revenue_IAR.xlsx). Values are per MW/month, multiplied by 4.2 MW. Shows variance per stream and overall capture vs IAR." }]),
  p([{ text: "Section 3 - Multi-Market vs Actual: ", bold: true }, { text: "Revenue breakdown comparing GridBeyond actual dispatch vs hindsight-optimal LP solution per market." }]),
  p([{ text: "Section 4 - TB Spread Benchmarks: ", bold: true }, { text: "Daily TB2 spread vs actual arbitrage revenue with Modo 142% industry benchmark." }]),
  p(""),
  h2("5.9 IAR Projection Loading"),
  p("IAR data is loaded from Excel at runtime:"),
  code("IAR Excel structure (Sheet1):"),
  code("  Row 3: Date headers (columns E onwards = Mar 2025, F = Apr 2025, ...)"),
  code("  Row 4: Wholesale Day Ahead Battery Revenue (GBP/MW/month)"),
  code("  Row 5: Wholesale Intraday Revenue"),
  code("  Row 6: Balancing Mechanism Revenue"),
  code("  Row 7: Frequency Response Revenues"),
  code("  Row 8: Capacity Market Revenues"),
  code("  Row 9: DUoS Battery Revenues"),
  code("  Row 10: DUoS Fixed Charges"),
  code("  Row 11: TNUoS Revenues"),
  code("  Row 13: MW assumed = 4.2"),
  code(""),
  code("Column mapping: K=Sep25, L=Oct25, M=Nov25, N=Dec25, O=Jan26"),
  code("Actual IAR = value_per_MW x 4.2 MW  (Real terms, no indexation)"),
  new Paragraph({ children: [new PageBreak()] }),

  // ── 5.10 Imbalance ──
  h2("5.10 Imbalance Deep Dive"),
  p("Analyzes settlement imbalance charges:"),
  code("Net_Imbalance = Imbalance_Revenue - Imbalance_Charge"),
  code("Charge_Rate = Periods_With_Charges / Total_Periods x 100"),
  p(""),
  p("Root cause analysis correlates charges with SSP/SBP spread, hourly patterns, and time-of-day distribution."),
  p(""),
  h2("5.11 Market Prices Analysis"),
  p("Six sections analyzing price dynamics:"),
  code("EPEX_Spread = rolling(48).max() - rolling(48).min()    (24-hour rolling window)"),
  code("Hourly_Avg = groupby(hour).mean()                       (24 hourly price curves)"),
  code("Daily_Volatility = groupby(date).std()                  (price standard deviation)"),
  code("High_Vol_Threshold = percentile_75(Daily_Volatility)    (75th percentile)"),
  code(""),
  code("Missed Revenue (conservative estimate):"),
  code("  = idle_periods x 50% capture x 2 MW x spread x 0.5 hours"),
  p(""),
  h2("5.12 Ancillary Services Analysis"),
  p("Tracks 7 ancillary services: SFFR, DCL, DCH, DML, DMH, DRL, DRH"),
  code("Revenue_per_MWh = Total_Revenue / MW_Hours"),
  code("Opportunity_Cost = (Best_Service_Rate - Current_Avg_Rate) x Total_MWh"),
  p(""),
  h2("5.13 Performance Report"),
  p("Comprehensive monthly executive summary with:"),
  code("Actual_Annual_per_MW = (Actual_Total x 12) / Capacity_MW"),
  code("Multi_Annual_per_MW = (Multi_Total x 12) / Capacity_MW"),
  code("Imbalance_Erosion = Net_Imbalance / Total_Revenue x 100"),
  new Paragraph({ children: [new PageBreak()] })
);

// ════════════════════════════════════════════════
// SECTION 6: INVOICE RECONCILIATION
// ════════════════════════════════════════════════
children.push(
  h1("6. Invoice Reconciliation System"),
  p("The invoice module (src/data_cleaning/invoice_loader.py and invoice_reconciler.py) verifies energy volumes and revenue across multiple independent sources."),
  h2("6.1 Data Sources for Reconciliation"),
  makeTable(
    ["Source", "Loader Function", "Key Data"],
    [
      ["Master CSV", "(already loaded)", "Power_MW integrated, Credited Energy Volume"],
      ["EMR Settlement", "load_emr_capacity_market()", "Capacity Market monthly payments, weighting factors"],
      ["Hartree BESS Readings", "load_hartree_bess_readings()", "Daily BESS Import/Export (kWh)"],
      ["Hartree PV Readings", "load_hartree_pv_readings()", "Monthly solar generation, invoiced quantities"],
      ["Summary Statement", "load_summary_statement()", "Half-hourly Import/Export, revenue by stream"],
      ["Solar Generation", "load_solar_generation()", "Allocated quantities (kWh)"],
      ["SCADA Monitoring", "load_scada_monitoring()", "Daily Export/Import from SCADA"],
      ["PDF Invoices", "load_all_pdfs()", "Invoice numbers, dates, totals, line items"],
    ],
    [2200, 3200, 3960]
  ),
  p(""),
  h2("6.2 BESS Energy Reconciliation"),
  p("Compares 4 sources of energy data to verify consistency:"),
  code("Source 1 (Baseline): Master CSV - Credited Energy Volume Battery MWh Output"),
  code("Source 2: Hartree BESS - (Import_kWh + Export_kWh) / 1000 -> MWh"),
  code("Source 3: Summary Statement Detail - Import/Export kWh -> MWh"),
  code("Source 4: SCADA Monitoring - Daily Export/Import kWh (max per day, summed)"),
  code(""),
  code("Variance = (Source_N - Baseline) / Baseline x 100"),
  p(""),
  h2("6.3 Revenue Reconciliation"),
  code("Gross_Revenue = Sum of revenue columns from Master CSV"),
  code("Expected_Net = Gross x 0.93  (7% aggregator fee deducted)"),
  code("Reported_Net = Sum from Summary Statement"),
  code("Variance = Reported_Net - Expected_Net"),
  code(""),
  code("Status thresholds: < 1% = OK, 1-5% = Warning, > 5% = Error"),
  p(""),
  h2("6.4 Capacity Market Payment Verification"),
  code("Expected_Payment = Obligation_MW x Price_per_MW x CPI_Ratio x Monthly_Weighting"),
  code("Where CPI_Ratio = CM_CPI / CM_Base_CPI  (or 1.0 if base = 0)"),
  code("Match = |Expected - Actual| < 0.01"),
  p(""),
  h2("6.5 Actual Capacity Market Payments (from EMR)"),
  makeTable(
    ["Month", "Payment (GBP)", "Obligation (MW)", "Weighting Factor", "Source"],
    [
      ["October 2025", "1,704.17", "1.023", "0.0832929", "EMR T062 #65146"],
      ["November 2025", "1,884.42", "1.023", "0.0921025", "EMR T062 #65960"],
      ["December 2025", "1,994.84", "1.023", "0.0974995", "EMR T062 #66634"],
      ["January 2026", "2,113.87", "1.023", "0.1033173", "EMR T062 #67339"],
    ],
    [2000, 1500, 1500, 1800, 2560]
  ),
  p(""),
  p("Contract: CAN-2025-NSFL01-001, Auction: T-1-2025, Capacity Price: GBP 20,000/MW/year"),
  h2("6.6 DUoS Actuals (from Hartree Supply Invoices)"),
  makeTable(
    ["Month", "Red GDuos", "Amber GDuos", "Green GDuos", "DNO Fixed", "Net Credit"],
    [
      ["Sep 2025", "-322.81", "-410.03", "-43.94", "3.58", "-773.20"],
      ["Oct 2025", "-5,500.11", "-268.35", "-42.92", "3.70", "-5,807.68"],
      ["Nov 2025", "-5,379.73", "-106.41", "-42.54", "3.58", "-5,525.10"],
    ],
    [1500, 1400, 1400, 1400, 1260, 2400]
  ),
  p(""),
  p("Negative values = credits (payments TO Northwold for export). DNO: UK Power Networks. MPAN: 1050003297320."),
  new Paragraph({ children: [new PageBreak()] })
);

// ════════════════════════════════════════════════
// SECTION 7: COLOR PALETTE
// ════════════════════════════════════════════════
children.push(
  h1("7. UI Design: Color Palette"),
  p("All colors are colorblind-friendly (deuteranopia/protanopia safe). Defined as global constants in streamlit_dashboard.py."),
  h2("7.1 Revenue Stream Colors"),
  makeTable(
    ["Constant", "Hex", "Usage"],
    [
      ["COLOR_SFFR", "#2C4B78", "Deep Navy - Frequency Response (SFFR)"],
      ["COLOR_EPEX", "#F18805", "Warm Orange - Day Ahead Markets (EPEX)"],
      ["COLOR_IDA1", "#7BC8F6", "Sky Blue - Intraday Auctions (IDA1)"],
      ["COLOR_IDC", "#9467BD", "Purple - Intraday Continuous (IDC)"],
      ["COLOR_IMBALANCE_REV", "#2CA02C", "Forest Green - Imbalance Revenue"],
      ["COLOR_IMBALANCE_COST", "#D62728", "Crimson - Imbalance Penalties"],
    ],
    [2800, 1200, 5360]
  ),
  p(""),
  h2("7.2 Strategy Colors"),
  makeTable(
    ["Constant", "Hex", "Usage"],
    [
      ["COLOR_ACTUAL", "#3498db", "Blue - GridBeyond actual operation"],
      ["COLOR_EPEX_ONLY", "#F18805", "Orange - EPEX-only optimized strategy"],
      ["COLOR_SFFR_ONLY", "#2C4B78", "Navy - SFFR-only strategy"],
      ["COLOR_MULTI_MARKET", "#2CA02C", "Green - Multi-market optimized strategy"],
    ],
    [2800, 1200, 5360]
  ),
  p(""),
  p("The REVENUE_COLOR_MAP dictionary maps market names to colors for consistent pie charts and bar charts across all pages."),
  new Paragraph({ children: [new PageBreak()] })
);

// ════════════════════════════════════════════════
// SECTION 8: GLOSSARY
// ════════════════════════════════════════════════
children.push(
  h1("8. Glossary"),
  makeTable(
    ["Term", "Definition"],
    [
      ["BESS", "Battery Energy Storage System"],
      ["CM", "Capacity Market - UK government scheme paying generators for availability"],
      ["DA", "Day Ahead - wholesale electricity market for next-day delivery"],
      ["DUoS", "Distribution Use of System - charges/credits for using the distribution network"],
      ["EFA Block", "Electricity Forward Agreement block - 4-hour trading period"],
      ["EPEX", "European Power Exchange - wholesale electricity market"],
      ["GDuos", "Generation DUoS - credits paid to generators for exporting, split into Red/Amber/Green time bands"],
      ["GridBeyond", "Market aggregator operating the Northwold BESS"],
      ["HH", "Half-Hourly - 30-minute settlement period in UK electricity market"],
      ["IAR", "Investment Appraisal Report - projected revenue used for investment decisions"],
      ["IDC", "Intraday Continuous - continuous intraday trading market"],
      ["ISEM", "Integrated Single Electricity Market (GB-IE cross-border)"],
      ["LP", "Linear Programming - mathematical optimization technique"],
      ["Modo Energy", "Industry analytics provider publishing GB BESS performance benchmarks"],
      ["MPAN", "Meter Point Administration Number - unique meter identifier"],
      ["RTE", "Round-Trip Efficiency - ratio of energy out to energy in"],
      ["SBP", "System Buy Price - price for being short in balancing mechanism"],
      ["SCADA", "Supervisory Control and Data Acquisition - real-time monitoring system"],
      ["SFFR", "Static Firm Frequency Response - ancillary service for grid frequency support"],
      ["SOC", "State of Charge - current energy level as % of capacity"],
      ["SOH", "State of Health - battery degradation indicator (100% = new)"],
      ["SSP", "System Sell Price - price for being long in balancing mechanism"],
      ["TB2", "Top-Bottom 2 spread - sum of 2 highest minus 2 lowest hourly prices (2hr battery benchmark)"],
      ["TNUoS", "Transmission Network Use of System - National Grid transmission charges"],
    ],
    [1800, 7560]
  ),
  new Paragraph({ children: [new PageBreak()] })
);

// ════════════════════════════════════════════════
// SECTION 9: APPENDIX
// ════════════════════════════════════════════════
children.push(
  h1("9. Appendix: Monthly Data Summary"),
  h2("9.1 Available Months"),
  makeTable(
    ["Month", "Days", "Master CSV", "Optimization CSV", "CM Data", "DUoS Data"],
    [
      ["September 2025", "30", "Master_BESS_Analysis_Sept_2025.csv", "Optimized_Results_Sept_2025.csv", "No", "Yes"],
      ["October 2025", "31", "Master_BESS_Analysis_Oct_2025.csv", "Optimized_Results_Oct_2025.csv", "Yes", "Yes"],
      ["November 2025", "30", "Master_BESS_Analysis_Nov_2025.csv", "Optimized_Results_Nov_2025.csv", "Yes", "Yes"],
      ["December 2025", "31", "Master_BESS_Analysis_Dec_2025.csv", "Optimized_Results_Dec_2025.csv", "Yes", "No"],
      ["January 2026", "31", "Master_BESS_Analysis_Jan_2026.csv", "Optimized_Results_Jan_2026.csv", "Yes", "No"],
    ],
    [1800, 700, 3000, 2660, 600, 600]
  ),
  p(""),
  h2("9.2 Modo Energy Benchmark Values"),
  makeTable(
    ["Month", "Modo GB BESS Index (GBP/MW/year)"],
    [
      ["September 2025", "70,000"],
      ["October 2025", "77,000"],
      ["November 2025", "59,000"],
      ["December 2025", "47,000"],
      ["January 2026", "88,000"],
    ],
    [4680, 4680]
  ),
  p(""),
  p("Source: Modo Energy GB BESS Monthly Index. These represent the average revenue achieved by 1-hour duration GB BESS fleet."),
  p(""),
  h2("9.3 Industry Benchmark Ranges"),
  makeTable(
    ["Metric", "Low", "Mid", "High", "Source"],
    [
      ["Revenue (GBP/MW/year)", "36,000", "60,000", "88,000", "Modo Energy, NREL"],
      ["Daily Cycles", "1.0", "1.5", "3.0", "Industry average"],
      ["Round-Trip Efficiency", "82%", "85%", "90%", "DNV GL Standards"],
      ["Annual Degradation", "4.0%", "7.5%", "11.0%", "NREL Battery Studies"],
      ["Availability (TWCAA)", "90%", "94%", "98%", "National Grid ESO"],
      ["TB2 Capture Rate", "80%", "100%", "142%+", "Modo Energy"],
    ],
    [2200, 1200, 1200, 1200, 3560]
  ),
  p(""),
  p("--- End of Document ---"),
);

// ── Create Document ──
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: "1F4E79" },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: "2E75B6" },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "4A4A4A" },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
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
            new TextRun({ text: "AMPYR APD Technical Reference", font: "Arial", size: 16, color: "888888" }),
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
  const outPath = path.join("C:", "repos", "Ampyr-APD", "docs", "APD_Technical_Reference.docx");
  fs.writeFileSync(outPath, buffer);
  console.log("Document created: " + outPath);
  console.log("Size: " + (buffer.length / 1024).toFixed(1) + " KB");
});
