# Energy Data Requirements — Internal & External

**Asset:** Northwold Solar Farm (Hall Farm) — 8.4 MWh / 7.5 MW BESS
**Aggregator:** GridBeyond
**Prepared:** February 2026

---

## PART A: DATA CURRENTLY USED BY THE DASHBOARD

---

### 1. Battery Physical Data (Internal — SCADA)

> Source: Onsite SCADA system / Battery Management System export
> Delivery: Excel file (manual export)
> Native frequency: 10-minute intervals, resampled to 30-minute for analysis
> Cost: £0 (existing infrastructure)

| # | Data Field | Description | Unit | Why Needed |
|---|-----------|-------------|------|------------|
| 1 | **Power** | Real-time active power output of the battery inverter. Positive = charging, negative = discharging | MW (converted from kW) | Core operational metric — drives all cycle, throughput, and revenue calculations |
| 2 | **State of Charge (SOC)** | Current energy level of the battery as a percentage of total capacity | % (0–100) | Tracks battery utilisation, validates dispatch constraints, and feeds degradation models |
| 3 | **Grid Frequency** | Measured AC frequency at the point of connection | Hz | Needed for frequency response service verification and grid stability analysis |
| 4 | **Availability** | System availability flag from SCADA | Boolean / % | Currently 100% null in available data — not actively used but retained for future use |

---

### 2. Wholesale Market Trading Data (External — GridBeyond)

> Source: GridBeyond aggregator monthly Excel report
> Delivery: Monthly sFTP / email (~2 weeks after month-end)
> Frequency: Half-hourly (48 periods per day)
> Cost: £0 (included in 5% aggregator revenue share)

#### 2.1 Trading Volumes

| # | Data Field | Description | Unit | Why Needed |
|---|-----------|-------------|------|------------|
| 5 | **DA MW** | Day-ahead dispatch volume — energy traded in DA auction | MW | Tracks how much capacity was committed to day-ahead market |
| 6 | **EPEX 30 DA MW** | EPEX 30-minute product dispatch volume | MW | Tracks short-horizon DA trading activity |
| 7 | **IDA1 MW** | Intraday Auction 1 dispatch volume | MW | Measures intraday trading participation |
| 8 | **IDC MW** | Intraday Continuous dispatch volume | MW | Measures continuous intraday trading activity |

#### 2.2 Revenue Streams

| # | Data Field | Description | Unit | Why Needed |
|---|-----------|-------------|------|------------|
| 9 | **EPEX DA Revenue** | Revenue earned from EPEX day-ahead auction trades | £ | Primary wholesale revenue line |
| 10 | **EPEX 30 DA Revenue** | Revenue from EPEX 30-minute ahead product | £ | Secondary wholesale revenue line |
| 11 | **IDA1 Revenue** | Revenue from GB-ISEM Intraday Auction 1 | £ | Tracks intraday auction earnings |
| 12 | **IDC Revenue** | Revenue from Intraday Continuous trading | £ | Tracks continuous market earnings |
| 13 | **Imbalance Revenue** | Revenue received when battery helps balance the grid (system long) | £ | Key profitability line — can be significant during volatile periods |
| 14 | **Imbalance Charge** | Penalties incurred when battery position deviates from contracted | £ | Risk metric — high charges indicate poor dispatch accuracy or forecasting |
| 15 | **Credited Energy Volume** | Net energy volume credited in settlement for the battery | MWh | Validates metered output against traded volumes |

---

### 3. Ancillary Services Data (External — GridBeyond / NESO)

> Source: GridBeyond monthly report (originally from NESO tender results)
> Frequency: Per EFA block (6 blocks × 4 hours) or half-hourly
> Cost: £0

**For each of the 7 services below, three fields are provided:**

| Field Type | Description | Unit |
|-----------|-------------|------|
| Availability | MW of capacity contracted for this service | MW |
| Clearing Price | Auction clearing price awarded | £/MW/h |
| Revenue | Earnings from providing this service | £ |

| # | Service | Description | Why Needed |
|---|---------|-------------|------------|
| 16–18 | **SFFR** (Static Firm Frequency Response) | Continuous frequency support — battery responds to frequency deviations | Currently the largest revenue stream; critical for SFFR-vs-wholesale strategy comparison |
| 19–21 | **DCL** (Dynamic Containment Low) | Fast response to low-frequency events (<49.5 Hz) | Evaluates revenue from newer frequency products |
| 22–24 | **DCH** (Dynamic Containment High) | Fast response to high-frequency events (>50.5 Hz) | Paired with DCL for full containment revenue picture |
| 25–27 | **DML** (Dynamic Modulation Low) | Enhanced response for moderate low-frequency deviations | Tracks emerging ancillary revenue opportunities |
| 28–30 | **DMH** (Dynamic Modulation High) | Enhanced response for moderate high-frequency deviations | Paired with DML |
| 31–33 | **DRL** (Dynamic Regulation Low) | Active power regulation for sustained low-frequency periods | Completes frequency response product suite |
| 34–36 | **DRH** (Dynamic Regulation High) | Active power regulation for sustained high-frequency periods | Paired with DRL |

**Total ancillary data fields: 21** (7 services × 3 fields each)

---

### 4. Asset Configuration Parameters (Internal — Static)

> Source: Asset purchase agreement, warranty documentation, GridBeyond contract
> Frequency: One-time setup, updated only if asset is modified
> Cost: £0

| # | Parameter | Value | Why Needed |
|---|-----------|-------|------------|
| 37 | **Battery Capacity** | 8.4 MWh | Defines the energy storage limits for optimisation and cycle calculations |
| 38 | **Max Charge Rate (Import)** | 4.2 MW | Constrains how fast the battery can absorb energy |
| 39 | **Max Discharge Rate (Export)** | 7.5 MW | Constrains how fast the battery can deliver energy (asymmetric) |
| 40 | **Round-Trip Efficiency** | 87% | Energy loss factor — critical for accurate revenue and degradation modelling |
| 41 | **SOC Safety Minimum** | 5% | Protects battery from deep discharge damage |
| 42 | **SOC Safety Maximum** | 95% | Protects battery from overcharge damage |
| 43 | **Warranty Cycle Limit** | 1.5 cycles/day | Maximum daily cycling to maintain warranty — exceeding voids warranty |
| 44 | **Max Daily Throughput** | 12.6 MWh | Derived from cycle limit × capacity — hard constraint on optimiser |
| 45 | **Owner Revenue Share** | 95% | Portion of gross revenue retained by asset owner |
| 46 | **Aggregator Revenue Share** | 5% | Portion retained by GridBeyond as aggregator fee |
| 47 | **Settlement Period** | 30 minutes | UK electricity market standard half-hourly period |

---

### 5. Derived / Computed Metrics (Internal — Dashboard Calculations)

> These are not data inputs but are calculated from the data above within the dashboard.

| # | Metric | Calculated From | Why Needed |
|---|--------|-----------------|------------|
| 48 | **Battery Cycles** (3 methods) | Power, Capacity, Time step | Warranty compliance monitoring and degradation forecasting |
| 49 | **Degradation Estimate** | Cycles, Warranty parameters | Projects remaining battery life and state of health |
| 50 | **TB Spreads** (TB1, TB2, TB3) | Day-ahead prices | Measures daily arbitrage opportunity in the market |
| 51 | **Net Imbalance** | Imbalance Revenue – Imbalance Charge | Tracks imbalance cost exposure |
| 52 | **Capture Rate** | Actual Revenue ÷ Optimal Revenue | Measures how well the asset captures available market value |
| 53 | **Revenue per MW** | Total Revenue ÷ Export Capacity | Industry-standard benchmarking metric |
| 54 | **Optimised Dispatch Profile** | All prices, asset constraints | Counterfactual — what revenue could have been under optimal strategy |

---

## PART B: DATA NOT CURRENTLY USED — RECOMMENDED ADDITIONS

---

### 6. Battery Management System (BMS) Diagnostics (Internal)

> Source: Battery Management System (onsite, via SCADA or direct BMS API)
> Current status: NOT captured — only high-level Power and SOC are available
> Importance: High — essential for accurate degradation tracking and warranty evidence

| # | Data Field | Description | Unit | Why Recommended |
|---|-----------|-------------|------|-----------------|
| 55 | **Cell Voltages** | Individual cell or module voltage readings | V | Early detection of cell imbalance, degradation hotspots, and safety issues |
| 56 | **Cell Temperatures** | Temperature at cell or module level | °C | Temperature is the primary driver of calendar ageing — critical for accurate degradation |
| 57 | **String Currents** | Current flowing through each battery string | A | Identifies imbalanced loading across strings |
| 58 | **Pack Resistance** | Internal resistance of battery packs (measured or estimated) | mΩ | Rising resistance indicates capacity fade — leading indicator of degradation |
| 59 | **Thermal Management Status** | HVAC/cooling system operating state and power consumption | On/Off, kW | Parasitic load that affects net efficiency and operating cost |
| 60 | **BMS Alarms & Events** | Fault codes, protection trips, mode changes | Event log | Operational reliability tracking and incident investigation |

---

### 7. Weather & Environmental Data (External)

> Source: Met Office, Open-Meteo, or commercial weather API
> Current status: NOT used
> Importance: Medium — useful for solar co-location analysis, temperature-adjusted degradation, and demand forecasting

| # | Data Field | Description | Unit | Why Recommended |
|---|-----------|-------------|------|-----------------|
| 61 | **Ambient Temperature** | Air temperature at site location | °C | Affects battery degradation rate and HVAC energy consumption |
| 62 | **Solar Irradiance** | Solar radiation at site (relevant if solar co-located) | W/m² | Would enable co-optimisation of solar + storage dispatch |
| 63 | **Wind Speed** | Local wind speed | m/s | Affects grid frequency volatility and ancillary service demand |
| 64 | **Weather Forecast** | 24–48 hour ahead temperature and irradiance forecast | Various | Enables predictive dispatch and forward position planning |

---

### 8. Grid & System Data (External — Free)

> Source: Elexon BMRS, NESO Data Portal
> Current status: Partially used (SSP/SBP only)
> Importance: Medium — enables richer market context and forecasting

| # | Data Field | Description | Unit | Why Recommended |
|---|-----------|-------------|------|-----------------|
| 65 | **System Frequency (Live)** | Real-time national grid frequency | Hz | Verify frequency response delivery against contracted obligations |
| 66 | **Generation Mix** | GB generation by fuel type (wind, solar, gas, nuclear) | MW / % | High renewables → more frequency volatility → more ancillary revenue opportunity |
| 67 | **System Demand** | National demand level | GW | Demand patterns correlate with wholesale price levels |
| 68 | **System Warnings / Notices** | NESO operational warnings (margins, constraints) | Text/flags | Early signal for price spikes and high-value trading periods |
| 69 | **Capacity Market Register** | Registered capacity and obligation status | MW | Tracks asset compliance with any Capacity Market commitments |

---

### 9. Metering & Settlement Verification (External)

> Source: Elexon settlement systems, DNO metering
> Current status: NOT directly integrated
> Importance: High — needed for revenue assurance and dispute resolution

| # | Data Field | Description | Unit | Why Recommended |
|---|-----------|-------------|------|-----------------|
| 70 | **Metered Volume (HH Settlement)** | Official half-hourly metered energy at point of connection | MWh | Reconciles SCADA readings against settlement volumes — catches metering errors |
| 71 | **Final Physical Notification (FPN)** | Contracted dispatch position submitted to grid operator | MW | Needed to calculate imbalance exposure accurately |
| 72 | **Bid/Offer Acceptance Data** | Accepted bids/offers in balancing mechanism | MW, £/MWh | Tracks BM participation and revenue |

---

### 10. Financial & Commercial Data (Internal)

> Source: Asset management systems, contracts, accounting
> Current status: Partially used (revenue share only)
> Importance: Medium — enables full P&L tracking

| # | Data Field | Description | Unit | Why Recommended |
|---|-----------|-------------|------|-----------------|
| 73 | **Grid Connection Charges** | TNUoS, BSUoS, DUoS charges | £ | Significant cost line — affects net revenue calculations |
| 74 | **Operational Expenditure** | Maintenance, insurance, site costs | £/month | Enables true net profit calculation |
| 75 | **Warranty Claim History** | Any warranty events or capacity guarantee claims | Event log | Links degradation data to commercial warranty outcomes |
| 76 | **Aggregator Invoice Data** | GridBeyond invoiced amounts and revenue reconciliation | £ | Verifies 95/5 revenue split accuracy |

---

## PART C: SUMMARY

### Data Field Counts

| Category | Currently Used | Recommended Additions | Total |
|----------|---------------|----------------------|-------|
| Battery Physical (SCADA) | 4 | 6 (BMS diagnostics) | 10 |
| Wholesale Trading (volumes + revenues) | 11 | 0 | 11 |
| Ancillary Services | 21 | 0 | 21 |
| Market Prices | 7 | 0 | 7 |
| Imbalance & Settlement | 2 | 3 (metering verification) | 5 |
| Asset Configuration | 11 | 0 | 11 |
| Derived Metrics | 7 | 0 | 7 |
| Weather & Environmental | 0 | 4 | 4 |
| Grid & System Context | 0 | 5 | 5 |
| Financial & Commercial | 0 | 4 | 4 |
| **TOTAL** | **63** | **22** | **85** |

### Source Summary

| Source | Type | Fields | Cost | Data Lag |
|--------|------|--------|------|----------|
| SCADA / BMS | Internal | 4 (current) + 6 (recommended) | £0 | Real-time (10-min export) |
| GridBeyond Report | External | 39 | £0 (5% revenue share) | ~2 weeks |
| Elexon BMRS | External | 5+ (free API) | £0 | Near real-time |
| NESO Data Portal | External | 14+ (free data) | £0 | Daily |
| Asset Documentation | Internal | 11 | £0 | Static |
| Met Office / Weather API | External | 4 (recommended) | £0–£500/year | Hourly |
| DNO / Settlement Agent | External | 3 (recommended) | £0 | 14-day settlement cycle |
| Commercial / Finance | Internal | 4 (recommended) | £0 | Monthly |

### Priority Recommendations

1. **HIGH PRIORITY — BMS Diagnostics (Fields 55–60):** Cell-level temperature and voltage data would dramatically improve degradation modelling accuracy. Current degradation estimates rely on cycle counting alone, which misses the dominant impact of temperature on battery ageing.

2. **HIGH PRIORITY — Metering Verification (Fields 70–72):** Settlement metering data provides revenue assurance. Without it, there is no independent check on GridBeyond-reported volumes and revenues.

3. **MEDIUM PRIORITY — Grid Connection Charges (Field 73):** TNUoS/BSUoS/DUoS charges can represent 5–15% of gross revenue. Including them would enable true net revenue reporting.

4. **MEDIUM PRIORITY — Ambient Temperature (Field 61):** Simple addition via free weather API that would meaningfully improve degradation forecasting.

5. **LOWER PRIORITY — Generation Mix & System Data (Fields 65–69):** Useful for market context and narrative but not critical for operational decisions.
