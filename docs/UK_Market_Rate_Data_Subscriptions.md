# UK Market Rate Data Subscriptions

**Asset:** Northwold Solar Farm (Hall Farm) — 8.4 MWh / 7.5 MW BESS
**Aggregator:** GridBeyond
**Prepared:** February 2026

---

## 1. Wholesale Electricity Market Prices

### 1.1 EPEX Day-Ahead Auction Price
- **What:** Next-day electricity price set via daily auction on EPEX SPOT exchange
- **Why needed:** Primary benchmark for arbitrage strategy — determines when to charge (low price) and discharge (high price)
- **Frequency:** Half-hourly (48 values per day)
- **Unit:** £/MWh
- **Current delivery:** Included in GridBeyond monthly report
- **Direct source:** EPEX SPOT Market Data Services
- **Direct cost:** Quote required (contact marketdata@epexspot.com)
- **Free alternative:** Elexon BMRS Market Index Data (DA HH reference price)

### 1.2 EPEX 30-Minute Day-Ahead Price
- **What:** EPEX SPOT 30-minute ahead product price — a shorter-horizon variant of the DA auction
- **Why needed:** Captures intra-day price movements closer to delivery; used for short-term dispatch decisions
- **Frequency:** Half-hourly
- **Unit:** £/MWh
- **Current delivery:** Included in GridBeyond monthly report
- **Direct source:** EPEX SPOT
- **Direct cost:** Quote required

### 1.3 GB-ISEM Intraday Auction 1 (IDA1) Price
- **What:** Same-day auction price on the GB-ISEM (Integrated Single Electricity Market) intraday market
- **Why needed:** Second arbitrage opportunity — prices may differ from day-ahead, offering improved trading margins
- **Frequency:** Half-hourly
- **Unit:** £/MWh
- **Current delivery:** Included in GridBeyond monthly report
- **Direct source:** EPEX SPOT / SEMOpx
- **Direct cost:** Bundled with EPEX subscription

### 1.4 Intraday Continuous (IDC) Price
- **What:** Continuous electronic trading price on EPEX intraday market — trades executed up to gate closure
- **Why needed:** Captures real-time price spikes and short-notice trading opportunities
- **Frequency:** Half-hourly (aggregated from continuous trades)
- **Unit:** £/MWh
- **Current delivery:** Included in GridBeyond monthly report
- **Direct source:** EPEX SPOT / Nord Pool
- **Direct cost:** Nord Pool Intraday: ~€5,000/year; EPEX: quote required

### 1.5 Day-Ahead Half-Hourly Reference Price (DA HH)
- **What:** Elexon's official day-ahead reference price — market index used in settlement
- **Why needed:** Independent benchmark for validating EPEX prices and used in optimization engine
- **Frequency:** Half-hourly
- **Unit:** £/MWh
- **Current delivery:** Included in GridBeyond monthly report
- **Direct source:** Elexon BMRS API
- **Direct cost:** FREE (no authentication required)
- **API endpoint:** `https://data.elexon.co.uk/bmrs/api/v1/balancing/pricing/market-index`

### 1.6 System Sell Price (SSP)
- **What:** Price the grid pays generators/batteries when the system is long (excess supply)
- **Why needed:** Determines revenue for unplanned exports; key input for imbalance analysis
- **Frequency:** Half-hourly
- **Unit:** £/MWh
- **Current delivery:** Included in GridBeyond monthly report
- **Direct source:** Elexon BMRS API
- **Direct cost:** FREE
- **API endpoint:** `https://data.elexon.co.uk/bmrs/api/v1/balancing/pricing/system-sell-price`

### 1.7 System Buy Price (SBP)
- **What:** Price batteries/generators pay when the system is short (deficit supply)
- **Why needed:** Determines cost of unplanned imports; critical for imbalance risk management
- **Frequency:** Half-hourly
- **Unit:** £/MWh
- **Current delivery:** Included in GridBeyond monthly report
- **Direct source:** Elexon BMRS API
- **Direct cost:** FREE
- **API endpoint:** `https://data.elexon.co.uk/bmrs/api/v1/balancing/pricing/system-buy-price`

---

## 2. Ancillary Services Clearing Prices

> All ancillary services below are procured by NESO (National Energy System Operator) via competitive tenders. Clearing prices determine the revenue rate per MW of availability provided.

### 2.1 Static Firm Frequency Response (SFFR) Clearing Price
- **What:** Auction clearing price for providing continuous frequency support to the grid
- **Why needed:** SFFR is currently the largest single revenue stream for the asset — essential for strategy comparison (hold SFFR vs. trade wholesale)
- **Frequency:** Per EFA block (6 blocks × 4 hours = 24 hours)
- **Unit:** £/MW/h
- **Current delivery:** Included in GridBeyond monthly report
- **Direct source:** NESO Data Portal
- **Direct cost:** FREE
- **URL:** `https://data.nationalgrideso.com`

### 2.2 Dynamic Containment Low (DCL) Clearing Price
- **What:** Price for providing low-frequency containment response (grid frequency drops below 49.5 Hz)
- **Why needed:** DCL is a key revenue alternative to wholesale trading; pricing trends indicate market saturation
- **Frequency:** Per EFA block
- **Unit:** £/MW/h
- **Current delivery:** Included in GridBeyond monthly report
- **Direct source:** NESO Data Portal
- **Direct cost:** FREE

### 2.3 Dynamic Containment High (DCH) Clearing Price
- **What:** Price for providing high-frequency containment response (grid frequency rises above 50.5 Hz)
- **Why needed:** Paired with DCL — both needed to evaluate full DC revenue potential
- **Frequency:** Per EFA block
- **Unit:** £/MW/h
- **Current delivery:** Included in GridBeyond monthly report
- **Direct source:** NESO Data Portal
- **Direct cost:** FREE

### 2.4 Dynamic Modulation Low (DML) Clearing Price
- **What:** Price for enhanced frequency response at moderate deviations (below 49.75 Hz)
- **Why needed:** Newer product — tracks evolving ancillary services market and revenue diversification options
- **Frequency:** Per EFA block
- **Unit:** £/MW/h
- **Current delivery:** Included in GridBeyond monthly report
- **Direct source:** NESO Data Portal
- **Direct cost:** FREE

### 2.5 Dynamic Modulation High (DMH) Clearing Price
- **What:** Price for enhanced frequency response at moderate deviations (above 50.25 Hz)
- **Why needed:** Paired with DML for full DM evaluation
- **Frequency:** Per EFA block
- **Unit:** £/MW/h
- **Current delivery:** Included in GridBeyond monthly report
- **Direct source:** NESO Data Portal
- **Direct cost:** FREE

### 2.6 Dynamic Regulation Low (DRL) Clearing Price
- **What:** Price for providing continuous active power regulation for low-frequency events
- **Why needed:** Completes the frequency response product suite — needed for comprehensive ancillary revenue analysis
- **Frequency:** Per EFA block
- **Unit:** £/MW/h
- **Current delivery:** Included in GridBeyond monthly report
- **Direct source:** NESO Data Portal
- **Direct cost:** FREE

### 2.7 Dynamic Regulation High (DRH) Clearing Price
- **What:** Price for providing continuous active power regulation for high-frequency events
- **Why needed:** Paired with DRL for full DR evaluation
- **Frequency:** Per EFA block
- **Unit:** £/MW/h
- **Current delivery:** Included in GridBeyond monthly report
- **Direct source:** NESO Data Portal
- **Direct cost:** FREE

---

## 3. Imbalance & Settlement Data

### 3.1 Imbalance Settlement Prices
- **What:** Half-hourly settlement prices applied to any energy volume that deviates from contracted position
- **Why needed:** Imbalance charges are a significant cost line — understanding exposure is critical for risk management
- **Frequency:** Half-hourly
- **Unit:** £/MWh
- **Current delivery:** Revenue and charges included in GridBeyond monthly report
- **Direct source:** Elexon BMRS API (System Price data)
- **Direct cost:** FREE
- **API endpoint:** `https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices`

---

## 4. Benchmarking & Analytics Subscriptions

### 4.1 Modo Energy — BESS Revenue Benchmarks
- **What:** Third-party analytics platform providing GB BESS market indices, revenue benchmarks, and asset-level performance data
- **Why needed:** Enables comparison of Northwold performance against industry peers; provides TB spread indices (TB1, TB2, TB3) and revenue forecasts
- **Frequency:** Daily / Monthly reports
- **Current status:** Referenced in dashboard benchmarks; not a live integration
- **Cost tiers:**
  - Free tier: Limited market overview
  - Plus: Basic analytics
  - Pro: ~£8,000–£15,000/year — full revenue indices and benchmarks
  - Business: ~£15,000–£30,000/year — asset-level analytics
  - Enterprise: ~£30,000–£60,000/year — full platform access
- **URL:** `https://modoenergy.com`

### 4.2 Nord Pool — UK Day-Ahead & Intraday Market Data
- **What:** Alternative market data provider for GB day-ahead (N2EX) and intraday trading data
- **Why needed:** Potential direct feed if moving away from reliance on GridBeyond report; provides real-time and historical price data
- **Frequency:** Real-time / daily
- **Cost:** ~€1,200/year (UK Day-Ahead) + ~€5,000/year (Intraday Trades) = ~€6,200/year (~£5,300/year)
- **Current status:** Not currently subscribed — data comes via GridBeyond
- **URL:** `https://www.nordpoolgroup.com`

---

## 5. Cost Summary

| Data Source | Annual Cost | Status |
|-------------|-------------|--------|
| GridBeyond Monthly Report (all wholesale + ancillary data) | £0 (included in 5% revenue share) | **Active** |
| Elexon BMRS API (SSP, SBP, DA HH, settlement) | £0 (free public API) | **Available** |
| NESO Data Portal (all ancillary clearing prices) | £0 (free public data) | **Available** |
| Nord Pool (UK DA + Intraday direct feed) | ~£5,300/year | Optional |
| EPEX SPOT (direct market data feed) | Quote required | Optional |
| Modo Energy (BESS benchmarking — Pro tier) | ~£8,000–£15,000/year | Optional |
| **Total (current operating cost)** | **£0/year** | |
| **Total (with benchmarking + direct feeds)** | **£13,300–£20,300+/year** | |

---

## 6. Notes

1. **GridBeyond is the primary data delivery mechanism** — all 7 wholesale prices and 7 ancillary clearing prices arrive bundled in their monthly Excel report at no additional cost (covered by the 5% aggregator revenue share).

2. **Direct subscriptions become relevant if:**
   - Moving to real-time or near-real-time dashboard updates
   - Reducing dependency on GridBeyond for data accuracy/timeliness
   - Implementing live trading decision support
   - GridBeyond contract changes or aggregator switch

3. **Elexon BMRS and NESO are always free** — these are public UK energy data platforms with open APIs, suitable for independent verification of GridBeyond data.

4. **Data lag consideration:** GridBeyond reports arrive ~2 weeks after month-end. Direct API subscriptions would reduce this to near-real-time.
