# Dashboard Metrics Documentation Plan

**Date**: 28 November 2025
**Purpose**: Add clear explanations/tooltips to all metrics and charts

---

## Priority 1: Critical Missing Explanations

### Executive Comparison Page

| Section | Metric/Chart | Issue | Suggested Help Text |
|---------|-------------|-------|---------------------|
| 1. Key Metrics | "Captured %" | No explanation of what's being captured | `Capture Rate = Actual Revenue / Optimal Simulated Revenue × 100. Shows what % of theoretically achievable revenue was actually earned.` |
| 1. Key Metrics | "Gap: £X" | No baseline explained | `Revenue Gap = Optimal Revenue - Actual Revenue. The optimal is calculated using multi-market arbitrage simulation with perfect foresight.` |
| 3. Gap Analysis | "Revenue Gap" | No calculation method | `Gap = Simulated Optimal - Actual. Optimal uses hindsight-based multi-market optimization across EPEX, Intraday, SSP/SBP.` |
| 3. Gap Analysis | "Capture Rate" | No denominator explained | `Capture Rate = (Actual Revenue / Optimal Revenue) × 100%` |
| 3. Gap Analysis | "Imbalance Cost" | Unclear if net or gross | `Net Imbalance = Imbalance Revenue - Imbalance Charges. Negative means net penalty.` |
| 3. Gap Analysis | "Trend" column | "pp" not explained | `pp = percentage points (absolute change in %). Example: 50% to 60% = +10pp improvement.` |

### BESS Health Page

| Section | Metric/Chart | Issue | Suggested Help Text |
|---------|-------------|-------|---------------------|
| Cycling Table | "Total Cycles" | Calculation unclear | `Cycles = Total Discharge Energy (MWh) / Battery Capacity (8.4 MWh). Only counts discharge, not charge.` |
| Cycling Table | "Daily Cycles" | Averaging method unclear | `Daily Cycles = Total Cycles / Number of Days in period` |
| Cycling Table | "Est. Degradation (%)" | Formula not shown | `Degradation = Cycles × 0.0046%. Based on 2.5% annual degradation at 1.5 cycles/day warranty limit.` |
| Daily Cycles Chart | Warranty Limit | Why 1.5? | `Warranty allows 1.5 cycles/day (547 cycles/year). Exceeding this may void warranty coverage.` |
| Exceedance Table | "Over Limit By" | What does it mean? | `Excess cycles above 1.5/day warranty limit. High values indicate aggressive operation.` |

### Market Price Analysis Page

| Section | Metric/Chart | Issue | Suggested Help Text |
|---------|-------------|-------|---------------------|
| 2. Spread Analysis | "EPEX Spread" | Window unclear | `Daily Spread = Max EPEX Price - Min EPEX Price for each day. Higher spreads = better arbitrage opportunity.` |
| 2. Spread Analysis | "SSP/SBP Spread" | Relationship unclear | `SSP = System Sell Price (grid pays you), SBP = System Buy Price (you pay grid). Spread = SBP - SSP.` |
| 3. Hourly Patterns | "Best Buy/Sell Hour" | Based on what? | `Average price across all days at each hour. Buy when prices low, sell when high.` |
| 4. Volatility | "High Volatility Days" | Threshold unclear | `Days where price standard deviation > 75th percentile. High volatility = more trading opportunity.` |
| 5. Missed Opportunities | "Idle During High Spread" | Thresholds? | `Periods where battery power < 0.1 MW AND price spread > 75th percentile. Conservative: assumes 50% capture, 2MW power.` |
| 6. Correlation | Matrix values | Interpretation? | `+1 = perfect positive correlation, -1 = perfect negative, 0 = no correlation. Low correlation = arbitrage potential.` |

### Imbalance Deep Dive Page

| Section | Metric/Chart | Issue | Suggested Help Text |
|---------|-------------|-------|---------------------|
| 1. Summary | "Net Imbalance" | Direction unclear | `Net = Revenue - Charges. Positive = profit from imbalance, Negative = penalty/loss.` |
| 1. Summary | "% Periods with Charges" | What's a period? | `Each period = 30 minutes. Shows % of half-hour slots that incurred imbalance charges.` |
| 4. Correlation | "Charge-Spread Correlation" | What does it mean? | `How much charges relate to SSP/SBP spread. High correlation = charges during volatile periods.` |
| 5. Root Cause | Time categories | Why these hours? | `Morning: 6-12, Afternoon: 12-18, Evening: 18-22, Night: 22-6. Aligned with market dynamics.` |

### Ancillary Services Page

| Section | Metric/Chart | Issue | Suggested Help Text |
|---------|-------------|-------|---------------------|
| 1. Summary | Service codes | Acronyms unexplained | `SFFR=Static Firm Frequency Response, DC=Dynamic Containment, DM=Dynamic Moderation, DR=Dynamic Regulation. L=Low, H=High.` |
| 2. Revenue | "Periods Active" | What's a period? | `Number of 30-minute settlement periods where the service was available/used.` |
| 4. Efficiency | "Revenue per MW-Hour" | Calculation? | `Total Revenue / (Availability MW × Hours). Higher = more £ earned per unit of capacity committed.` |
| 5. Opportunity Cost | "Optimal Revenue" | How calculated? | `Theoretical: if all MW-hours went to most efficient service. Ignores market constraints.` |

### Multi-Market Optimization Page

| Section | Metric/Chart | Issue | Suggested Help Text |
|---------|-------------|-------|---------------------|
| Summary | "EPEX-Only (Daily)" | Strategy unclear | `Optimization using only EPEX prices, strategy fixed for entire day.` |
| Summary | "EPEX-Only (EFA)" | What's EFA? | `EFA = Electricity Forward Agreement blocks (4-hour periods). Strategy can change each EFA block.` |
| Summary | "Multi-Market" | What markets? | `Optimizes across EPEX, Intraday (IDA1), IDC, and SSP/SBP imbalance markets.` |
| Market Usage | Percentages | What do they represent? | `% of 30-min periods where each market/strategy was selected as optimal.` |

### Operations Summary Page

| Section | Metric/Chart | Issue | Suggested Help Text |
|---------|-------------|-------|---------------------|
| BESS Metrics | "Effective Cycles" | Same issue as above | `Cycles = Total Discharge / 8.4 MWh capacity. Does not account for partial cycles or DoD.` |
| Revenue | "Net Revenue" | Components unclear | `SFFR + EPEX + IDA1 + IDC + Imbalance Revenue - Imbalance Charges` |

### Performance Report Page

| Section | Metric/Chart | Issue | Suggested Help Text |
|---------|-------------|-------|---------------------|
| 4. Degradation | "Est. Monthly Degradation" | Magic number 0.0046% | `0.0046% per cycle based on 2.5% annual degradation at 547 cycles/year warranty limit.` |

---

## Priority 2: Methodology Fixes Needed

### Cycle Calculation (BESS Health)
**Current**: Only counts discharge energy
**Should be**: Full equivalent cycle = (Discharge + Charge) / 2 / Capacity
**Impact**: May undercount cycles if charge ≠ discharge

### Optimal Revenue Calculation
**Current**: Uses perfect foresight (hindsight optimization)
**Should clarify**: This is theoretical maximum, not achievable in practice
**Add disclaimer**: "Optimal is calculated with perfect price knowledge - real-world would be lower"

---

## Implementation Approach

### Option A: Tooltips (Streamlit help parameter)
```python
st.metric("Capture Rate", f"{rate:.1f}%",
          help="Capture Rate = Actual/Optimal × 100. Shows efficiency vs theoretical maximum.")
```

### Option B: Expander sections
```python
with st.expander("ℹ️ How is this calculated?"):
    st.markdown("**Capture Rate** = Actual Revenue / Optimal Revenue × 100%...")
```

### Option C: Info boxes per section
```python
st.info("**Methodology**: Gap = Optimal - Actual. Optimal uses multi-market simulation with hindsight.")
```

**Recommendation**: Use Option A (tooltips) for metrics, Option C (info boxes) for complex sections.

---

## Files to Modify

| File | Sections to Update |
|------|-------------------|
| `streamlit_dashboard.py` | All pages listed above |

---

## Next Steps

1. [x] Fix cycle calculation methodology - Phase 5 now supports 3 methods (Discharge-only, Full Equivalent, Throughput)
2. [x] Add tooltips to all st.metric() calls - Implemented with help parameter
3. [x] Add methodology info boxes to each major section - Added st.info() explanations
4. [x] Add glossary of acronyms (SFFR, EFA, SSP, SBP, etc.) - Added comprehensive glossary section
5. [x] Review and test all help text - Completed

## Completed Features (28 Nov 2025)

### Benchmarks Page (New)

| Section | Feature | Status |
|---------|---------|--------|
| 1. Performance Summary | Industry benchmarks table | Done |
| 2. IAR vs Actual | Revenue comparison table (11 rows) | Done |
| 2. IAR vs Actual | Variance calculations | Done |
| 2. IAR vs Actual | Capture rate metrics (Sept 72%, Oct 166%) | Done |
| 2. IAR vs Actual | Styled Total row (bold) | Done |

### Tooltips Added

- All st.metric() calls now include help parameter with explanations
- Key metrics documented: Capture Rate, Revenue Gap, Cycles, Degradation

### Glossary Added

- SFFR, DCL, DCH, DML, DMH, DRL, DRH (Ancillary Services)
- SSP, SBP, EPEX, IDA1, IDC (Markets)
- EFA, pp, DoD, SoC (Technical Terms)
- IAR (Internal Appraisal Report)
