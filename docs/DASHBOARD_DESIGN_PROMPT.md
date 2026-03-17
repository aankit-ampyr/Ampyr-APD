# BESS Dashboard Design Prompt

## CONTEXT

This is the main dashboard of "Northwold BESS Dashboard," a battery energy storage system performance analysis web application for energy asset owners, BESS operations teams, and financial analysts (typically working at or alongside aggregators like GridBeyond) who need a clear, consolidated view of their battery asset's trading performance. Users have already imported their GridBeyond market data and SCADA telemetry files. The dashboard is the first screen they see after loading the application. The product is used to evaluate aggregator trading performance, compare it against optimized hindsight benchmarks, and prepare for trading strategy review meetings.

The primary asset is an 8.4 MWh / 7.5 MW discharge / 4.2 MW charge BESS at Northwold Solar Farm (Hall Farm) in the UK, operated by the aggregator GridBeyond. All monetary values are in GBP.

## DESCRIPTION

This screen serves as the BESS performance command center — a single application where users can assess their battery asset's financial and operational health across multiple views without switching between spreadsheets or external tools. It should answer five questions at a glance:

1. How much revenue did my battery earn this month? (Total net revenue and breakdown by market stream)
2. How does actual performance compare to projections? (IAR vs. actual capture rate)
3. How much revenue am I leaving on the table? (Multi-market optimization gap)
4. Is my battery healthy? (Cycling rate vs. warranty limit, degradation tracking)
5. Are things improving or getting worse? (Month-over-month trend comparison)

The dashboard should feel professional and data-dense but not cluttered. Prioritize clarity of key financial KPIs at the top of each view, with supporting charts and tables below for users who want to drill deeper. Users should be able to scan the summary metrics in 10 seconds and know whether the asset is performing well.

The application uses a sidebar for navigation across 12 distinct views: 5 general (Asset Details, Data Import, Executive Comparison, Benchmarks, Export Reports) and 7 monthly analysis pages (Operations Summary, Multi-Market Optimization, Market Prices, Imbalance Analysis, Ancillary Services, BESS Health, Performance Report). A month selector in the sidebar (September 2025 / October 2025) updates all monthly views simultaneously. All monetary values should use realistic sample data in GBP with proper formatting (£14,457.00).

## PLATFORM

Desktop-first web application built with Streamlit (Python) using wide layout mode.

- Primary viewport: Full browser width (`layout="wide"`)
- The layout should use Streamlit's built-in left sidebar (approximately 300px) for navigation and a scrollable main content area
- Content area should use Streamlit's column system (`st.columns`) with common ratios: `[2, 1]` for main-plus-sidebar card rows, `[1, 1, 1]` or `[1, 1, 1, 1]` for equal metric cards
- Column layouts naturally stack on narrow viewports via Streamlit's responsive grid
- The design is optimized for desktop/tablet use; no explicit mobile breakpoints

## VISUAL STYLE

- Color palette: Light-themed interface with a white background (`#FFFFFF`) and card/widget surfaces in light gray (`#F0F2F5`). Use amber/orange (`#F0A202`) as the primary brand accent for buttons, sliders, and CTAs. Use teal/green (`#2ecc71`) for positive values, optimized results, and upward trends. Use dark red (`#D95D39`) for actual shortfalls, losses, and negative imbalance. Use coral/red (`#e74c3c`) for alerts, warranty exceedances, and overspending. Use bright blue (`#3498db`) for actual/current operations data. Use dark navy (`#2C4B78`) for ancillary/frequency response revenue. Near-black (`#262730`) for primary text. Muted gray for secondary labels.
- Typography: System sans-serif (Streamlit default). Page titles via `st.title()`. Section headers via `st.header()` and `st.subheader()`. Key financial figures displayed at prominent size using `st.metric()` with delta indicators. Body text and labels at Streamlit default sizing.
- Spacing: Streamlit default spacing between elements. Use `st.columns` with consistent gap ratios. Use `st.divider()` or `st.markdown("---")` to separate major sections.
- Mood: Professional, analytical, and trustworthy — like a Bloomberg terminal meets an energy trading desk. Data-dense but well-organized. Use semantic callout boxes (`st.success`, `st.warning`, `st.error`, `st.info`) for status indicators. Emoji icons (sparingly) in section headers for quick visual scanning. Avoid playful illustrations or decorative elements.

## UI COMPONENTS

### 1. Left Sidebar Navigation

- Application title "Northwold BESS Dashboard" at top with battery emoji icon
- **General Pages section** (month-independent): 5 buttons arranged vertically
  - Asset Details, Data Import, Executive Comparison, Benchmarks, Export Reports
- **Monthly Analysis section**: month selector dropdown (`st.selectbox` — September 2025, October 2025) followed by a radio button list of 7 monthly pages:
  - Operations Summary, Multi-Market Optimization, Market Prices, Imbalance Analysis, Ancillary Services, BESS Health, Performance Report
- **Asset Info Card** at sidebar bottom: collapsible section showing system name, location, capacity (8.4 MWh), max discharge (7.5 MW), max charge (4.2 MW), aggregator (GridBeyond)
- **Glossary Expander** at very bottom: collapsible definitions of key terms (SFFR, EPEX, IDA1, IDC, SSP, SBP, SOC, EFA)

### 2. Operations Summary Page (default monthly view)

- Page title "Operations Summary — [Month] 2025"
- **Revenue Metrics Row** (4 equal columns of `st.metric` cards):
  - Total Net Revenue (£14,457 for Sept / £38,344 for Oct) with delta vs. previous month
  - SFFR Revenue (£17,164 / £28,382)
  - Wholesale Trading Revenue (EPEX + IDA1 + IDC net)
  - Imbalance Cost (-£8,257 / -£816) displayed with negative delta in red
- **Two-tab layout** below metrics: "Trading Analysis" | "Visualizations"
  - Trading Analysis tab: styled dataframe table showing revenue by stream (SFFR, EPEX DA, EPEX 30 DA, IDA1, IDC, Imbalance) with columns for Volume (MWh), Revenue (£), and % of Total. Bold total row at bottom.
  - Visualizations tab: revenue breakdown pie chart (Plotly `px.pie`) on the left two-thirds, daily revenue bar chart on the right one-third

### 3. Net Worth / Revenue Summary Card (Executive Comparison page, full width)

- Large combined revenue figure with green/red percentage change badge vs. previous month
- Below it: a horizontal row of mini cards showing individual market stream revenues:
  - SFFR Revenue (£28,382 — anchor revenue)
  - EPEX DA Revenue (£1,880 — wholesale)
  - IDA1 Revenue (£13,283 — intraday)
  - Imbalance Net (-£816 — displayed in coral/red)
- Each mini card shows: market icon emoji, stream name, revenue value, and month-over-month delta

### 4. IAR vs Actual Comparison Table (Benchmarks page)

- Styled dataframe comparing Internal Appraisal Report projections against actual GridBeyond figures
- Columns: Revenue Stream | IAR Projected (£) | Actual (£) | Variance (%) | Status
- Rows: Frequency Response, Wholesale Day Ahead, Wholesale Intraday, Total
- Variance cells color-coded: green for outperformance, red for underperformance
- Bold total row with light blue background (`#e6f3ff`)
- Capture Rate KPI displayed as large `st.metric` above the table (e.g., "Capture Rate: 166%" with delta)

### 5. Multi-Market Optimization Card (dedicated page, full width)

- **Strategy Selector** dropdown at top: Multi-Market / EPEX-only (Daily) / EPEX-only (EFA) / Actual
- **Metrics Row** (3 columns):
  - Optimized Revenue (£39,196 for selected strategy)
  - Actual Revenue (£14,457)
  - Revenue Gap (£24,739 — displayed in amber as opportunity cost)
- **Market Utilization Donut Chart** (left two-thirds): Plotly pie chart with hole showing % of volume and revenue per market (EPEX, ISEM, SSP, SBP, DA HH). Colored dot legend beside chart.
- **Strategy Comparison Table** (right one-third): dataframe showing each strategy's total revenue, average daily revenue, and capture rate vs. actual
- **Cumulative Revenue Line Chart** (full width below): Plotly scatter/line showing actual vs. optimized cumulative revenue over the month, with the growing gap shaded between the two lines

### 6. Budget Progress / Spending Breakdown Equivalent — Market Price Analysis Card (dedicated page)

- **Price Metrics Row** (4 columns):
  - EPEX DA Average (£72.00/MWh)
  - SSP Max (£92.80/MWh)
  - Best Buy Hour (Hour 4, £18.50/MWh)
  - Best Sell Hour (Hour 18, £98.20/MWh)
- **Hourly Price Pattern Area Chart** (left two-thirds): Plotly area chart showing average EPEX price by hour of day with fill, highlighting optimal buy/sell windows in teal/coral
- **Price Correlation Heatmap** (right one-third): Plotly `imshow` with `RdBu_r` colorscale showing correlation matrix between EPEX DA, Intraday, SSP, and SBP prices
- **Spread Distribution Histogram** (full width below): daily top-bottom spread histogram with vertical reference line for average spread

### 7. BESS Health Card (dedicated page)

- **Health Metrics Row** (4 columns):
  - Warranty Limit (1.5 cycles/day — static reference)
  - Average Daily Cycles (0.95 for Oct)
  - Projected Annual Degradation (%)
  - Estimated Years to 80% SOH
- **Cycle Method Selector**: horizontal radio buttons — Method A (Discharge-only) / Method B (Full Equivalent — industry standard) / Method C (Throughput-based)
- **Daily Cycling Bar Chart** (full width): Plotly bar chart showing daily cycles for each strategy, with a red dashed horizontal reference line at 1.5 cycles/day warranty limit
- **Warranty Exceedance Table** (full width below): styled dataframe with gradient heatmap on "Over Limit" column using Reds colorscale. Columns: Date | Cycles (Actual) | Cycles (Optimized) | Over Limit | Strategy
- **SOC Distribution Histogram** (left half): Plotly histogram of battery SOC values across the month
- **Battery Power Time Series** (right half): Plotly line chart showing charge/discharge power (MW) over time with zero-line reference

### 8. Monthly Cash Flow / Executive Comparison Card (dedicated page, full width)

- **Side-by-side month comparison** (two equal columns):
  - Left column: September 2025 summary (total revenue, capture rate, market mix donut)
  - Right column: October 2025 summary (total revenue, capture rate, market mix donut)
- **Improvement Metrics Row** (3 columns):
  - Revenue Change (+£23,887 in green)
  - Capture Rate Change (+165% improvement)
  - Imbalance Cost Change (-£7,441 reduction in green)
- **Stacked Bar Chart** (full width): monthly revenue breakdown by stream (SFFR vs. EPEX vs. IDA1 vs. Imbalance) for Sept and Oct side by side, income bars in teal/blue, imbalance penalty bars in muted coral
- **Performance Gap Analysis Table** (full width): dataframe with columns for Metric | September | October | Change | Trend (arrow emoji indicators)

### 9. Ancillary Services Card (dedicated page)

- **Service Revenue Metrics Row** (4 columns): SFFR, DCL/DCH, DML/DMH, DRL/DRH revenues
- **Revenue by Service Bar Chart** (left two-thirds): Plotly grouped bar showing revenue per ancillary service, bars in dark navy (`#2C4B78`)
- **Service Pricing Table** (right one-third): dataframe with Service | Avg Clearing Price (£/MW/h) | Avg Availability (%) | Revenue (£)
- **Utilization Donut Chart** (full width below): ancillary service utilization by volume and revenue percentage

### 10. Imbalance Analysis Card (dedicated page)

- **Imbalance Metrics Row** (3 columns):
  - Total Imbalance Cost (-£816 for Oct)
  - Worst Day Cost (date and amount)
  - Average Daily Imbalance (£)
- **Daily Imbalance Bar Chart** (full width): daily imbalance revenue/cost bars, positive in teal, negative in coral
- **Worst Days Table** (left half): top 5 worst imbalance days with date, cost, SSP/SBP spread, and root cause indicator
- **Hourly Penalty Distribution** (right half): bar chart showing imbalance penalty by hour of day

### 11. Recent Transactions Equivalent — Data Import Page

- **Three-tab layout**: "GridBeyond Data" | "SCADA Data" | "Data Preview"
- GridBeyond tab: `st.file_uploader` for Excel file, process button, quality report output
- SCADA tab: `st.file_uploader` for Excel file with SCADA telemetry
- Data Preview tab: `st.dataframe` showing merged dataset with column multi-selector, download button for processed CSV
- Data quality callout boxes (`st.success`/`st.warning`/`st.error`) showing missing value counts, timestamp overlap statistics, SOC range validation

### 12. Export Reports Page

- **Report Format Selector**: radio buttons — "Text Summary" / "CSV Data Export"
- **Report Month Selector**: dropdown matching main month selector
- **Generate Report Button** (`type="primary"`): triggers report generation with `st.spinner` loading state
- **Report Preview**: text area showing generated report content
- **Download Buttons**: `st.download_button` for text report (.txt) and CSV exports

## INTERACTIONS

- All Plotly charts should use `hovermode='x unified'` with vertical crosshair tooltips showing all series values at the cursor position
- The month selector in the sidebar updates all 7 monthly analysis pages simultaneously
- Strategy selector dropdown on Multi-Market Optimization page updates pie charts, statistics, and comparison tables
- Cycle method radio buttons on BESS Health page recalculate all cycling metrics and charts
- Clicking sidebar navigation buttons switches the main content area to the selected view
- File uploaders on Data Import trigger processing pipeline with spinner feedback and quality report output
- Generate Report button produces downloadable text/CSV with loading indicator
- Expander sections throughout (Glossary, Calculation Methodology) toggle open/closed
- Semantic callout boxes (`st.success`, `st.warning`, `st.error`, `st.info`) provide contextual status at the top of relevant sections — e.g., green success box when capture rate exceeds 100%, red error box when warranty limit exceeded
- All dataframes support Streamlit's built-in column sorting and search
