# BESS Dashboard Improvement Plan

**Date**: 27 November 2025
**Project**: Northwold Solar Farm BESS Analysis Dashboard

## Project Overview

**Project**: Battery Energy Storage System (BESS) Analysis Dashboard for Northwold Solar Farm
**Location**: UK
**Aggregator**: GridBeyond (95%/5% profit sharing - owner gets 95%)
**Current State**: Streamlit dashboard analyzing September 2025 battery trading data
**Key Finding**: Multi-market optimization shows 172% revenue improvement potential (£14,376 → £39,196)

## Data Sources

| Source | File | Content |
|--------|------|---------|
| GridBeyond (Excel) | Northwold_Sep_2025_converted.csv | Market prices, revenues, ancillary services |
| EPC Dashboard | BESS_Sept_2025_converted.csv | Physical battery data (SOC, Power, Frequency) |

**GridBeyond Data Fields:**

- Market prices: EPEX Day Ahead, GB-ISEM Intraday 1, DA HH, SSP, SBP, IDC
- Revenue streams: SFFR, EPEX 30 DA, IDA1, IDC, Imbalance Revenue/Charge
- Ancillary: SFFR, DCL, DCH, DML, DMH, DRL, DRH (availability, price, revenue)

**EPC Data Fields:**

- SOC (%), Power (MW), Frequency (Hz) at 30-min intervals

## Business Context & Purpose

### Primary Purpose 1: Analyze GridBeyond Reports

- Import and analyze monthly Excel reports from GridBeyond
- Track actual revenues across all markets
- Identify issues like the £8,337 imbalance penalty in September
- Verify GridBeyond is operating the asset optimally

### Primary Purpose 2: Compare to Market Optimal

- Simulate optimized BESS dispatch using actual market prices
- Compare GridBeyond's actual vs theoretical optimal
- Quantify "revenue left on table" (currently £24,820/month gap)
- Build evidence base for performance discussions

---

## PRIORITY 1: Analysis & Market Comparison Improvements

### 1.1 Enhanced Market Price Analysis

**Current Gap**: Dashboard shows prices but lacks deep analysis

**Improvements:**

- **Price Spread Analysis**: Show best buy/sell opportunities each day
- **Missed Opportunity Tracker**: Highlight periods where better prices existed
- **Market Volatility Metrics**: Identify high-value trading windows
- **Price Correlation**: Show relationships between EPEX, SSP, SBP, Intraday

**Implementation:**

- Add new analysis section in `streamlit_dashboard.py`
- Calculate daily/hourly spreads: `max(sell_prices) - min(buy_prices)`
- Visualize with heatmaps showing price patterns by hour/day

### 1.2 GridBeyond vs Optimal Comparison Dashboard

**Current Gap**: Comparison exists but needs clearer presentation

**Improvements:**

- **Side-by-side revenue breakdown**: GridBeyond actual vs simulated optimal
- **Period-by-period comparison**: Where did GridBeyond miss opportunities?
- **Strategy attribution**: How much from SFFR vs arbitrage vs imbalance?
- **Daily performance chart**: Cumulative gap visualization

**Key Metrics to Show:**

```text
GridBeyond Actual:     £14,376
- SFFR Revenue:        £17,163
- EPEX/Intraday:       £5,550
- Imbalance Penalty:  -£8,337

Optimal Simulation:    £39,196
- Multi-Market Arb:    £39,196
- Imbalance:           £0 (avoided)

Revenue Gap:           £24,820 (172% improvement possible)
```

### 1.3 Imbalance Deep Dive Analysis

**Current Gap**: Imbalance shown as single number, no root cause

**Improvements:**

- **Imbalance breakdown by period**: When did penalties occur?
- **Correlation with market conditions**: Was it price spikes or forecast errors?
- **Comparison with SSP/SBP**: Show the spread during imbalance periods
- **Actionable insights**: "£5,000 of imbalance occurred during X periods"

### 1.4 Ancillary Services Analysis

**Current Gap**: 7 services shown but underutilized in analysis

**Improvements:**

- **Service utilization comparison**: SFFR vs DC vs DM vs DR
- **Revenue per MW comparison**: Which service is most profitable?
- **Opportunity cost**: "If GridBeyond used DCH instead of SFFR, revenue = £X"
- **Availability patterns**: When is each service available?

---

## PRIORITY 2: Multi-Month & Data Import

### 2.1 Excel Import Tool for GridBeyond Reports

**Implementation:**

- Add file uploader in Streamlit sidebar
- Parse GridBeyond Excel format (detect sheet structure)
- Validate required columns exist
- Store in standardized CSV format for analysis

```python
# Add to streamlit_dashboard.py
uploaded_file = st.sidebar.file_uploader("Upload GridBeyond Report", type=['xlsx', 'xls'])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    # Validate and process...
```

### 2.2 Multi-Month Comparison View

**Implementation:**

- Support loading multiple months' data
- Month-over-month trend charts
- Rolling averages for revenue, imbalance, cycling
- Seasonal pattern identification

### 2.3 Export & Reporting

**Implementation:**

- PDF export of analysis summary
- Excel export with all calculated metrics
- One-page executive summary for GridBeyond meetings

---

## Critical Files to Modify

| File | Changes |
|------|---------|
| `streamlit_dashboard.py` | Add market analysis, comparison views, import tool |
| `src/phase3_multimarket.py` | Enhance optimization to match GridBeyond's markets |
| `phase1.py` | Support multi-month data loading |

---

## Implementation Order

1. **Market Price Analysis** - Add spread analysis, missed opportunities ✅ DONE
2. **GridBeyond vs Optimal View** - Enhanced comparison dashboard ✅ DONE
3. **Imbalance Deep Dive** - Root cause analysis for penalties ✅ DONE
4. **Excel Import** - Easy monthly report upload ✅ DONE
5. **Multi-Month Tracking** - Trend analysis over time ✅ DONE (Sept + Oct)
6. **Export/Reports** - PDF/Excel for GridBeyond meetings
7. **Benchmarks Page** - IAR vs Actual comparison ✅ DONE (28 Nov 2025)

---

## Lower Priority (Code Quality - Do Later)

### Category 1: Code Quality & Architecture

| Issue | Impact | Effort |
|-------|--------|--------|
| Monolithic dashboard (1,322 lines) | High | Medium |
| Duplicate config (phase2.py = digital_twin_config.py) | Medium | Low |
| No error handling/validation | Medium | Medium |
| No unit tests | High | Medium |
| Hardcoded values scattered | Medium | Low |

### Category 2: Logic & Algorithm Accuracy

| Issue | Impact | Effort |
|-------|--------|--------|
| Linear degradation model (oversimplified) | High | Medium |
| Fixed 87% efficiency (doesn't vary with power/SoC) | Medium | High |
| Deterministic optimization (no uncertainty) | Medium | High |
| Only 3 optimization strategies | Medium | Medium |
| Fixed cycle limit (no dynamic allocation) | Medium | Medium |

### Category 3: Feature Gaps

| Issue | Impact | Effort |
|-------|--------|--------|
| Static analysis only (September 2025 hardcoded) | High | Medium |
| No date range selector | High | Low |
| No data export functionality | High | Low |
| No what-if scenario analysis | High | Medium |
| No alerting/threshold monitoring | Medium | Medium |

---

## Future Phases (Code Quality & Algorithm Improvements)

### Phase 1: Quick Wins

- Delete `phase2.py` (duplicate of `src/digital_twin_config.py`)
- Consolidate configuration into single dataclass
- Add data export buttons

### Phase 2: Dashboard Modularization

- Split 1,322-line dashboard into page modules
- Extract data loading and analysis functions
- Add error handling and validation

### Phase 3: Algorithm Improvements

- Non-linear degradation model with DoD weighting
- Variable efficiency based on power level
- Additional optimization strategies (intraday reopt, ancillary stacking)

### Phase 4: Feature Enhancements

- What-if scenario builder
- Alerting & threshold monitoring
- Price/revenue forecasting

---

## Critical Files Reference

| File | Lines | Purpose | Changes Needed |
|------|-------|---------|----------------|
| `streamlit_dashboard.py` | 1,322 | Main UI | Modularize, add features |
| `src/digital_twin_config.py` | 34 | Asset config | Make single source of truth |
| `phase2.py` | 34 | Duplicate config | DELETE |
| `phase3.py` | ~150 | Daily optimization | Extract to module |
| `src/phase3_multimarket.py` | 332 | Multi-market optimization | Add strategies |
| `src/phase5.py` | ~100 | Degradation analysis | Improve model |
| `phase1.py` | ~80 | Data harmonization | Support date ranges |

---

## Notes

- All changes maintain backward compatibility with existing CSV format
- Streamlit Cloud deployment remains supported
- No database migration required (CSV-based storage continues)
- Focus first on analysis features, then code quality

---

## Completed Work Log

### 28 November 2025

**Benchmarks Page Added:**

- Renamed "Industry Benchmarks" → "Benchmarks"
- Section 1: Industry Performance Summary table
- Section 2: IAR vs Actual Revenue comparison
  - 11 revenue streams from IAR Excel data
  - Variance calculations (Sept -28%, Oct +66%)
  - Capture rate metrics
  - Styled Total row with bold formatting
- Data source: `extra/Northwold BESS Revenue_IAR.xlsx`

**Documentation Updated:**

- README.md - Added Benchmarks page, Oct 2025 data, version 1.1.0
- dashboard_README.md - Added Benchmarks section, Oct revenue data
- metrics_documentation_plan.md - Marked all items complete
- project_plan_27_nov.md - This file

**Key Metrics:**

- Sept 2025: IAR £19,973 → Actual £14,457 (72% capture, -28%)
- Oct 2025: IAR £23,134 → Actual £38,344 (166% capture, +66%)
- Frequency Response: Significantly outperformed IAR (20x+ in Oct)
