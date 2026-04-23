# APD External Data Sources Reference

**Purpose**: Complete reference of all external data sources used in the Asset Performance Dashboard.
For developers building the production application — covers every variable, its source, extraction method, and update frequency.

**Asset**: Northwold Solar Farm BESS (4.2 MW / 8.4 MWh)
**Last Updated**: 30 March 2026

---

## 1. Modo Energy — GB BESS Revenue Benchmarks

| Field | Details |
|-------|---------|
| **Source** | Modo Energy GB BESS Index (monthly research reports) |
| **Access** | Free research articles on modoenergy.com (login required for full data platform) |
| **Update Frequency** | Monthly (published ~2nd week of following month) |
| **Extraction Method** | Manual — read monthly benchmark article, extract headline £/MW/year figure |

### Variables Used

| Variable | Code Location | Type | Unit | Description | How to Extract |
|----------|---------------|------|------|-------------|----------------|
| `MODO_BENCHMARKS[month]` | `streamlit_dashboard.py:3241` | Dict (month → value) | £/MW/year | Annualised monthly revenue benchmark across all GB BESS assets | Read from headline figure in each monthly Modo benchmark article. Modo calculates this as: (total revenue for all tracked GB batteries in the month ÷ total MW capacity) × (365 ÷ days in month) |

### Current Values

| Month | Value (£/MW/yr) | Source |
|-------|-----------------|--------|
| Sep 25 | 70,000 | [Sep 2025 article headline](https://modoenergy.com/research/en/battery-energy-storage-revenues-gb-september-2025-balancing-mechanism-frequency-response) |
| Oct 25 | 77,000 | [Oct 2025 article headline](https://modoenergy.com/research/en/battery-energy-storage-revenues-gb-october-2025-record-balancing-mechanism-dispatch-rates) |
| Nov 25 | 59,000 | [Nov 2025 article headline](https://modoenergy.com/research/en/me-bess-gb-battery-energy-storage-revenues-november-2025-balancing-mechanism-gas-wind) |
| Dec 25 | 47,000 | [Dec 2025 article headline](https://modoenergy.com/research/en/me-bess-gb-battery-energy-storage-revenues-december-2025-low-demand-christmas) |
| Jan 26 | 52,000 | [Jan 2026 article headline](https://modoenergy.com/research/en/me-bess-gb-revenues-january-2026-balancing-mechanism-wholesale-prices-gas-carbon) — prior value of 88,000 was incorrectly sourced from Modo's Jan **2025** roundup and has been corrected |
| Feb 26 | 41,000 | [Feb 2026 article headline](https://modoenergy.com/research/en/me-bess-gb-revenues-february-2026-wholesale-battery-energy-storage-balancing-mechanism) |
| Mar 26 | 65,000 | Modo API (`/pub/v1/gb/modo/benchmarking/monthly-index-live`, `market=total`, `duration=*`) — article not yet published, annualised from `revenue_permw` × 365/31 |

### Industry Range (used in benchmark chart)

| Variable | Value | Unit | Description |
|----------|-------|------|-------------|
| Industry Low | 36,000 | £/MW/year | Lowest monthly benchmark observed (2024–2025) |
| Industry High | 88,000 | £/MW/year | Highest monthly benchmark observed (2024–2025) |

### Source Links (saved in `docs/external_sources/`)

| Report | URL | Local File | Key Data Point |
|--------|-----|------------|----------------|
| 2024 Year in Review | https://modoenergy.com/research/gb-battery-energy-storage-markets-2024-year-in-review-great-britain-wholesale-balancing-mechanism-frequency-response-reserve | `Modo_2024_Year_in_Review.html` | Annual revenue stack trends, market evolution |
| December 2024 Benchmark | https://modoenergy.com/research/battery-energy-storage-revenues-december-benchmark-gb-2024-quick-reserve | `Modo_Dec2024_Benchmark.html` | £84k/MW/year — highest since Jan 2023 |
| January 2025 Roundup | https://modoenergy.com/research/gb-research-roundup-january-2025-battery-energy-storage-great-britain-revenues-markets-wholesale-capacity-market-balancing-mechanism | `Modo_Jan2025_Roundup.html` | £88k/MW/year benchmark |
| June 2025 Benchmark | https://modoenergy.com/research/battery-energy-storage-revenues-gb-benchmark-june-2025-negative-prices | `Modo_Jun2025_Benchmark.html` | £76k/MW/year; 66 hours negative pricing |
| TB Spread Benchmark | https://modoenergy.com/research/top-bottom-spread-revenue-benchmark-battery-energy-storage-sytems-gb-europe-spain-germany-solar-2025 | `Modo_TB_Spread_Benchmark.html` | 142% TB2 capture rate for 2-hr batteries |

> **Note**: Modo Energy pages are JavaScript-rendered (Next.js). The saved HTML files contain the page source but require a browser to render content. For production, either manually extract values monthly or explore Modo's paid API/data platform.

---

## 2. Modo Energy — TB Spread Benchmark (142%)

| Field | Details |
|-------|---------|
| **Source** | Modo Energy research: "Benchmarking European battery revenue with TB spreads" |
| **Access** | Free research article |
| **Update Frequency** | One-off study (referenced as industry standard) |
| **Extraction Method** | Manual — single benchmark value from the article |

### Variables Used

| Variable | Code Location | Type | Unit | Description | How to Extract |
|----------|---------------|------|------|-------------|----------------|
| TB2 Capture Benchmark | `streamlit_dashboard.py:3969` | Constant | % | Industry benchmark: well-operated 2-hr batteries capture ~142% of TB2 spread | From Modo article — Modo analysed revenues from GB BESS assets and found 2-hr batteries typically earn ~142% of the TB2 theoretical max |
| TB1 | `streamlit_dashboard.py:344-406` | Calculated | £/MWh | Highest hourly price − lowest hourly price per day | Calculated internally from EPEX DA prices |
| TB2 | `streamlit_dashboard.py:344-406` | Calculated | £/MWh | Sum of 2 highest − sum of 2 lowest hourly prices per day | Calculated internally from EPEX DA prices |
| TB3 | `streamlit_dashboard.py:344-406` | Calculated | £/MWh | Sum of 3 highest − sum of 3 lowest hourly prices per day | Calculated internally from EPEX DA prices |

### How TB Capture > 100% Is Possible
Batteries earn more than TB spread alone because of:
1. Intraday optimisation — capturing price spikes in real-time markets (IDA1, IDC)
2. Multiple cycles per day — cycling more than once when spreads allow
3. Ancillary services — stacking SFFR frequency response revenue on top of arbitrage

### Dashboard Interpretation
- **≥142%**: At or above industry benchmark (excellent)
- **100–142%**: Capturing spread but below benchmark (room for improvement)
- **60–80%**: Significant room for improvement in market participation
- **<60%**: Major underperformance

---

## 3. Capacity Market — EMR Settlement (T062)

| Field | Details |
|-------|---------|
| **Source** | Electricity Settlements Company (ESC) — EMR Settlement system |
| **Access** | T062 settlement CSV files (emailed to registered parties or via EMR portal) |
| **Update Frequency** | Monthly (settlement runs ~3 months in arrears for final settlement) |
| **Extraction Method** | Download T062 CSV → filter by contract `CAN-2025-NSFL01-001` → sum monthly payment |

### Variables Used

| Variable | Code Location | Type | Unit | Description | How to Extract |
|----------|---------------|------|------|-------------|----------------|
| `CM_ACTUALS[month]` | `streamlit_dashboard.py:3248` | Dict (month → £) | £ | Monthly Capacity Market payment | From T062 CSV: filter for contract CAN-2025-NSFL01-001, sum `Payment Amount` column for the month |

### Contract Details
- **Contract ID**: CAN-2025-NSFL01-001
- **Asset**: Northwold Solar Farm Ltd
- **Capacity Obligation**: 1.023 MW
- **Auction Price**: ~£20,000/MW/year
- **Payment**: Monthly with seasonal weighting (winter months higher)

### Current Values

| Month | CM Payment (£) | Source File |
|-------|----------------|-------------|
| Oct 25 | 1,704.17 | `NORTHWO_*_T062.csv` |
| Nov 25 | 1,884.42 | `NORTHWO_*_T062.csv` |
| Dec 25 | 1,994.84 | `NORTHWO_*_T062.csv` |
| Jan 26 | 2,113.87 | `NORTHWO_*_T062.csv` |

### Raw Files
- Location: `raw/New/` directory
- Pattern: `NORTHWO_*_T062.csv`
- Key columns: Contract ID, Settlement Period, Payment Amount, Obligation MW

---

## 4. DUoS — Distribution Use of System (Hartree Partners)

| Field | Details |
|-------|---------|
| **Source** | Hartree Partners Supply (UK) — generator invoices (passthrough credits from UKPN) |
| **Access** | PDF invoices emailed from Hartree Partners |
| **Update Frequency** | Monthly (invoices arrive ~6–8 weeks after delivery month) |
| **Extraction Method** | Manual — open Hartree Gen_Inv PDF, extract Red/Amber/Green GDuos credit line items and DNO fixed charges |

### Variables Used

| Variable | Code Location | Type | Unit | Description | How to Extract |
|----------|---------------|------|------|-------------|----------------|
| `DUOS_ACTUALS[month]['red']` | `streamlit_dashboard.py:3256` | Float | £ | Red band GDuos export credit (highest value, winter peak) | From Hartree invoice: "GDuos Red" line item (shown as negative = credit to generator) |
| `DUOS_ACTUALS[month]['amber']` | `streamlit_dashboard.py:3256` | Float | £ | Amber band GDuos export credit | From Hartree invoice: "GDuos Amber" line item |
| `DUOS_ACTUALS[month]['green']` | `streamlit_dashboard.py:3256` | Float | £ | Green band GDuos export credit | From Hartree invoice: "GDuos Green" line item |
| `DUOS_ACTUALS[month]['fixed']` | `streamlit_dashboard.py:3256` | Float | £ | DNO fixed network charges (cost) | From Hartree invoice: "Fixed Charges" or "DNO Standing Charge" |
| `DUOS_ACTUALS[month]['net_credit']` | `streamlit_dashboard.py:3256` | Float | £ | Net DUoS = |Red| + |Amber| + |Green| (absolute sum of credits) | Calculated: abs(red) + abs(amber) + abs(green) |

### Current Values

| Month | Red (£) | Amber (£) | Green (£) | Fixed (£) | Net Credit (£) |
|-------|---------|-----------|-----------|-----------|----------------|
| Sep 25 | -322.81 | -410.03 | -43.94 | 3.58 | 773.20 |
| Oct 25 | -5,500.11 | -268.35 | -42.92 | 3.70 | 5,807.68 |
| Nov 25 | -5,379.73 | -106.41 | -42.54 | 3.58 | 5,525.10 |

### Raw Files
- Location: `raw/New/OneDrive_3*/` and `raw/New/OneDrive_4*/`
- Pattern: `NWOSFL_Hartree*_Gen_Inv_*.pdf`
- **Note**: Values in invoices shown as negative = credit to generator. The code stores them as negatives and uses `net_credit` as the positive total.

---

## 5. IAR — Investment Appraisal Report

| Field | Details |
|-------|---------|
| **Source** | Internal financial model (Ampyr) |
| **Access** | `extra/Northwold BESS Revenue_IAR.xlsx` |
| **Update Frequency** | Static (set at investment decision, not updated) |
| **Extraction Method** | Read Excel Sheet1, rows 4–11, columns 11–15 (Sep–Jan), multiply by 4.2 MW |

### Variables Used

| Variable | Code Location | Type | Unit | Description | How to Extract |
|----------|---------------|------|------|-------------|----------------|
| IAR DA projection | `streamlit_dashboard.py:3564` Row 4 | Float | £/MW/month | Day Ahead projected revenue per MW | Excel Sheet1, Row 4 × 4.2 MW |
| IAR ID projection | Row 5 | Float | £/MW/month | Intraday projected revenue per MW | Excel Sheet1, Row 5 × 4.2 MW |
| IAR BM projection | Row 6 | Float | £/MW/month | Balancing Mechanism projected revenue per MW | Excel Sheet1, Row 6 × 4.2 MW |
| IAR FR projection | Row 7 | Float | £/MW/month | Frequency Response projected revenue per MW | Excel Sheet1, Row 7 × 4.2 MW |
| IAR CM projection | Row 8 | Float | £/MW/month | Capacity Market projected revenue per MW | Excel Sheet1, Row 8 × 4.2 MW |
| IAR DUoS Battery | Row 9 | Float | £/MW/month | DUoS battery credit projection per MW | Excel Sheet1, Row 9 × 4.2 MW |
| IAR DUoS Fixed | Row 10 | Float | £/MW/month | DUoS fixed charges projection per MW | Excel Sheet1, Row 10 × 4.2 MW |
| IAR TNUoS | Row 11 | Float | £/MW/month | Transmission Use of System projection per MW | Excel Sheet1, Row 11 × 4.2 MW |

### Column Mapping (Excel columns → months)
| Excel Column | Month |
|--------------|-------|
| 11 | Sep 25 |
| 12 | Oct 25 |
| 13 | Nov 25 |
| 14 | Dec 25 |
| 15 | Jan 26 |

### Scaling
- IAR values are **per MW per month**
- Multiplied by **4.2 MW** (Northwold capacity) to get total £ values
- Indexation factor: **1.073** applied in the IAR model

---

## 6. NREL — Battery Degradation Benchmarks

| Field | Details |
|-------|---------|
| **Source** | NREL (National Renewable Energy Laboratory) |
| **Document** | "Grid-Scale Battery Storage: Frequently Asked Questions" (2022) |
| **Access** | Public PDF: https://www.nrel.gov/docs/fy22osti/80688.pdf |
| **Update Frequency** | Static reference document |
| **Extraction Method** | Manual — degradation ranges from Table/Section on cycle life |
| **Local File** | `docs/external_sources/NREL_Battery_Degradation_fy22osti-80688.pdf` (downloaded) |

### Variables Used

| Variable | Code Location | Value | Unit | Description |
|----------|---------------|-------|------|-------------|
| Degradation Low | `streamlit_dashboard.py:3490` | 4.0% | %/year | High-quality cells, conservative operation |
| Degradation Mid | `streamlit_dashboard.py:3491` | 4.4% | %/year | Typical lithium-ion |
| Degradation High | `streamlit_dashboard.py:3492` | 11.0% | %/year | Aggressive cycling, poor thermal management |
| `WARRANTY_DEGRADATION_ANNUAL_PCT` | `streamlit_dashboard.py:1044` | 2.5% | %/year | Annual degradation at warranty cycle limit |
| 80% SOH threshold | `streamlit_dashboard.py:1340` | 80% | % | End-of-life threshold (years to reach calculated) |

### How Used in Dashboard
- Degradation per cycle = `WARRANTY_DEGRADATION_ANNUAL_PCT / 365` (derived)
- Annual degradation = actual annual cycles × degradation per cycle
- Years to 80% SOH = 20% ÷ annual degradation rate

---

## 7. National Grid ESO — Availability Benchmarks (TWCAA)

| Field | Details |
|-------|---------|
| **Source** | National Grid ESO — Transmission Performance Reports |
| **Access** | https://www.nationalgrideso.com/research-and-publications/transmission-performance-reports (403 — may require direct navigation) |
| **Update Frequency** | Quarterly |
| **Extraction Method** | Manual — read quarterly reports for BESS availability metrics |

### Variables Used

| Variable | Code Location | Value | Unit | Description |
|----------|---------------|-------|------|-------------|
| Availability Low | `streamlit_dashboard.py:3510` | 90% | % | Significant downtime |
| Availability Mid | `streamlit_dashboard.py:3511` | 94.4% | % | Typical BESS performance |
| Availability High | `streamlit_dashboard.py:3512` | 98% | % | Excellent availability |

> **Status**: Northwold TWCAA data TBD — requires ESO reporting data.

---

## 8. DNV GL — Round-Trip Efficiency Benchmarks

| Field | Details |
|-------|---------|
| **Source** | DNV GL — Energy Storage Performance Standards |
| **Access** | Industry standard reference (no single public URL — from DNV technical publications) |
| **Update Frequency** | Static industry reference |
| **Extraction Method** | Manual — from DNV energy storage performance standards documentation |

### Variables Used

| Variable | Code Location | Value | Unit | Description |
|----------|---------------|-------|------|-------------|
| RTE Low | `streamlit_dashboard.py:3530` | 82% | % | Older systems, poor conditions |
| RTE Mid | `streamlit_dashboard.py:3531` | 85% | % | Typical Li-ion NMC/LFP |
| RTE High | `streamlit_dashboard.py:3532` | 90% | % | Optimised operation |
| `EFF_ROUND_TRIP` | `src/config/asset_config.py:21` | 87% | % | Northwold design RTE (used in optimisation) |

---

## 9. OEM Warranty — Cycle Limits

| Field | Details |
|-------|---------|
| **Source** | Northwold Storage Asset Optimisation Agreement (contract) |
| **Access** | Internal contract document |
| **Update Frequency** | Static (contractual) |
| **Extraction Method** | From contract terms |

### Variables Used

| Variable | Code Location | Value | Unit | Description |
|----------|---------------|-------|------|-------------|
| `CYCLES_PER_DAY` | `src/config/asset_config.py:31` | 1.5 | cycles/day | Maximum daily cycles under warranty |
| `MAX_DAILY_THROUGHPUT_MWH` | `src/config/asset_config.py:32` | 12.6 | MWh | = 8.4 MWh × 1.5 cycles |
| Annual cycle limit (derived) | `streamlit_dashboard.py:1066` | 547 | cycles/year | = 1.5 × 365 |

---

## 10. Asset Physical Parameters (from Optimisation Agreement)

| Variable | Code Location | Value | Unit | Source |
|----------|---------------|-------|------|--------|
| `P_IMP_MAX_MW` | `src/config/asset_config.py:14` | 4.2 | MW | Max charge rate |
| `P_EXP_MAX_MW` | `src/config/asset_config.py:15` | 7.5 | MW | Max discharge rate |
| `CAPACITY_MWH` | `src/config/asset_config.py:18` | 8.4 | MWh | Usable energy capacity |
| `EFF_ROUND_TRIP` | `src/config/asset_config.py:21` | 0.87 | ratio | Round-trip efficiency |
| `SOC_MIN_PCT` | `src/config/asset_config.py:24` | 5% | % | Min state of charge |
| `SOC_MAX_PCT` | `src/config/asset_config.py:25` | 95% | % | Max state of charge |
| `OWNER_SHARE` | `src/config/asset_config.py:39` | 95% | % | Owner revenue share |
| `AGGREGATOR_SHARE` | `src/config/asset_config.py:40` | 5% | % | GridBeyond revenue share |

---

## Summary: Data Update Workflow for Production

| Source | Frequency | Method | Automation Potential |
|--------|-----------|--------|---------------------|
| **Modo Energy Benchmark** | Monthly | Manual — read article, extract £/MW/yr | Low (JS-rendered site, no public API). Explore Modo paid data platform for API access |
| **CM (EMR T062)** | Monthly | Download CSV from EMR portal, filter by contract | Medium — could automate CSV download + parsing |
| **DUoS (Hartree)** | Monthly | Read PDF invoice, extract line items | Medium — PDF parsing with OCR/tabula possible |
| **IAR Projections** | Static | One-time Excel read | High — already automated in code |
| **GridBeyond Revenue** | Monthly | Process backing data spreadsheet | High — structured Excel → CSV pipeline exists |
| **NREL Degradation** | Static | Reference values | N/A — hardcoded constants |
| **National Grid ESO** | Quarterly | Read performance report | Low — manual quarterly review |
| **DNV GL RTE** | Static | Reference values | N/A — hardcoded constants |
| **OEM Warranty** | Static | Contract terms | N/A — hardcoded constants |

---

## Downloaded Files Index

| File | Source | Size | Format |
|------|--------|------|--------|
| `NREL_Battery_Degradation_fy22osti-80688.pdf` | NREL | 3.6 MB | PDF |
| `Modo_2024_Year_in_Review.html` | Modo Energy | 647 KB | HTML (JS-rendered) |
| `Modo_Dec2024_Benchmark.html` | Modo Energy | 648 KB | HTML (JS-rendered) |
| `Modo_Jan2025_Roundup.html` | Modo Energy | 659 KB | HTML (JS-rendered) |
| `Modo_Jun2025_Benchmark.html` | Modo Energy | 654 KB | HTML (JS-rendered) |
| `Modo_TB_Spread_Benchmark.html` | Modo Energy | 640 KB | HTML (JS-rendered) |

> **Note on Modo HTML files**: These are page source snapshots. The actual article content is rendered by JavaScript and not visible in the raw HTML. Developers should visit the URLs directly in a browser. For production ingestion, contact Modo Energy about their data platform/API access.
