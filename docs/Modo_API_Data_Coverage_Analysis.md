# APD Data Requirements vs Modo Energy API Availability

**Date:** 2026-03-31
**Purpose:** Map all data requirements for UK, Germany, and Netherlands against Modo Energy API availability

---

## 1. MARKET DATA REQUIREMENTS

### 1A. Wholesale / Day-Ahead Prices

| # | Data Requirement | UK (GB) | Germany (DE) | Netherlands (NL) | Modo API — GB | Modo API — DE | Modo API — NL | Modo Endpoint Path | Live? | Historical? | History Depth |
|---|-----------------|---------|-------------|-----------------|---------------|---------------|---------------|-------------------|-------|-------------|---------------|
| 1 | **Day-Ahead Hourly Prices** | EPEX GB | EPEX DE | EPEX NL | YES | NO | NO | `/gb/epex/day-ahead/hourly` | ~1hr lag | YES | Est. 2020+ |
| 2 | **Day-Ahead Half-Hourly Prices** | EPEX GB HH | N/A (15-min) | N/A (15-min) | YES | N/A | N/A | `/gb/epex/day-ahead/hh` | ~1hr lag | YES | Est. 2020+ |
| 3 | **Day-Ahead Quarter-Hourly Prices** | N/A | EPEX DE QH | EPEX NL QH | N/A | NO | NO | — | — | — | — |
| 4 | **N2EX Day-Ahead Hourly Prices** | N2EX GB | N/A | N/A | YES | N/A | N/A | `/gb/n2ex/day-ahead-hourly/prices` | ~1hr lag | YES | Est. 2015+ |
| 5 | **N2EX Block Orders** | N2EX GB | N/A | N/A | YES | N/A | N/A | `/gb/n2ex/day-ahead-hourly/block-orders` | ~1hr lag | YES | Est. 2015+ |
| 6 | **N2EX Volumes** | N2EX GB | N/A | N/A | YES | N/A | N/A | `/gb/n2ex/day-ahead-hourly/volumes` | ~1hr lag | YES | Est. 2015+ |
| 7 | **Nord Pool DA Hourly Prices** | Via N2EX | YES (CWE) | YES (CWE) | Via N2EX | PARTIAL | PARTIAL | `/eur/nord-pool/day-ahead-hourly/prices` | ~1hr lag | YES | Unknown |
| 8 | **Nord Pool Block Orders** | Via N2EX | YES (CWE) | YES (CWE) | Via N2EX | PARTIAL | PARTIAL | `/eur/nord-pool/day-ahead-hourly/block-orders` | ~1hr lag | YES | Unknown |
| 9 | **Nord Pool Volumes** | Via N2EX | YES (CWE) | YES (CWE) | Via N2EX | PARTIAL | PARTIAL | `/eur/nord-pool/day-ahead-hourly/volumes` | ~1hr lag | YES | Unknown |

**Notes on Nord Pool DE/NL:** Documented delivery areas show NO, SE, FI. DE/NL coverage via `delivery_area` parameter is **unconfirmed** — needs API testing with `country=DE` or `delivery_area=DE-LU`.

---

### 1B. Intraday / Continuous Market Prices

| # | Data Requirement | UK (GB) | Germany (DE) | Netherlands (NL) | Modo API — GB | Modo API — DE | Modo API — NL | Modo Endpoint Path | Live? | Historical? | History Depth |
|---|-----------------|---------|-------------|-----------------|---------------|---------------|---------------|-------------------|-------|-------------|---------------|
| 10 | **IDA1 (Intraday Auction 1)** | EPEX GB | EPEX DE | EPEX NL | YES | NO | NO | `/gb/epex/intra-day/d1` | Same-day | YES | Est. 2021+ |
| 11 | **IDA2 (Intraday Auction 2)** | EPEX GB | EPEX DE | EPEX NL | YES | NO | NO | `/gb/epex/intra-day/d2` | Same-day | YES | Est. 2021+ |
| 12 | **Intraday Continuous Trades** | EPEX GB IDC | EPEX DE IDC | EPEX NL IDC | YES | NO | NO | `/gb/epex/intra-day/detailed-trades` | Live | YES | Est. 2021+ |
| 13 | **Intraday Continuous OHLC** | EPEX GB | EPEX DE | EPEX NL | YES | NO | NO | `/gb/epex/intra-day/ohlc` | Live | YES | Est. 2021+ |
| 14 | **Intraday Reference Price** | EPEX GB | EPEX DE | EPEX NL | YES | NO | NO | `/gb/epex/intra-day/reference-price` | Live | YES | Est. 2021+ |
| 15 | **Intraday Reference Price (HH)** | EPEX GB | N/A | N/A | YES | N/A | N/A | `/gb/epex/intra-day/reference-price-hh` | Live | YES | Est. 2021+ |
| 16 | **Intraday Reference Price (EOD)** | EPEX GB | EPEX DE | EPEX NL | YES | NO | NO | `/gb/epex/intra-day/reference-price-eod` | Daily | YES | Est. 2021+ |
| 17 | **Intraday Order Book** | EPEX GB | EPEX DE | EPEX NL | YES | NO | NO | `/gb/epex/intra-day/order-book` | Live | YES | Est. 2021+ |
| 18 | **Intraday Public Trade Confirm** | EPEX GB | EPEX DE | EPEX NL | YES | NO | NO | `/gb/epex/intra-day/public-trade-confirmation` | Live | YES | Est. 2021+ |
| 19 | **Intraday Contract Info** | EPEX GB | EPEX DE | EPEX NL | YES | NO | NO | `/gb/epex/intra-day/contract-info` | Live | YES | Est. 2021+ |

---

### 1C. System / Imbalance Prices

| # | Data Requirement | UK (GB) | Germany (DE) | Netherlands (NL) | Modo API — GB | Modo API — DE | Modo API — NL | Modo Endpoint Path | Live? | Historical? | History Depth |
|---|-----------------|---------|-------------|-----------------|---------------|---------------|---------------|-------------------|-------|-------------|---------------|
| 20 | **System Buy Price (SBP)** | Elexon | N/A | N/A | YES | N/A | N/A | `/gb/elexon/settlement/disebsp` | ~30min | YES | Est. 2015+ |
| 21 | **System Sell Price (SSP)** | Elexon | N/A | N/A | YES | N/A | N/A | `/gb/elexon/settlement/disebsp` | ~30min | YES | Est. 2015+ |
| 22 | **Detailed System Price (ISPSTACK)** | Elexon | N/A | N/A | YES | N/A | N/A | `/gb/elexon/settlement/ispstack` | ~30min | YES | Est. 2015+ |
| 23 | **Live System Price** | Elexon | N/A | N/A | YES | N/A | N/A | `/gb/elexon/bm/live-system-price` | Live | NO | Real-time only |
| 24 | **Live Detailed System Price** | Elexon | N/A | N/A | YES | N/A | N/A | `/gb/elexon/bm/live-detailed-system-price` | Live | NO | Real-time only |
| 25 | **Net Imbalance Volume (NIV)** | Elexon | N/A | N/A | YES | N/A | N/A | `/gb/elexon/settlement/disebsp` | ~30min | YES | Est. 2015+ |
| 26 | **Live NIV** | Elexon | N/A | N/A | YES | N/A | N/A | `/gb/elexon/bm/live-niv` | Live | NO | Real-time only |
| 27 | **Market Index Data** | Elexon | N/A | N/A | YES | N/A | N/A | `/gb/elexon/system/mid` | ~30min | YES | Est. 2015+ |
| 28 | **Imbalance Price (reBAP)** | N/A | Netztransparenz | N/A | N/A | NO | N/A | — | — | — | — |
| 29 | **Imbalance Settlement Price** | N/A | N/A | TenneT NL | N/A | N/A | NO | — | — | — | — |

---

### 1D. Balancing Mechanism

| # | Data Requirement | UK (GB) | Germany (DE) | Netherlands (NL) | Modo API — GB | Modo API — DE | Modo API — NL | Modo Endpoint Path | Live? | Historical? |
|---|-----------------|---------|-------------|-----------------|---------------|---------------|---------------|-------------------|-------|-------------|
| 30 | **Bid-Offer Data** | Elexon | N/A | N/A | YES | N/A | N/A | `/gb/elexon/bm/bod` | ~30min | YES |
| 31 | **BOA Levels (Flagged)** | Elexon | N/A | N/A | YES | N/A | N/A | `/gb/elexon/bm/boalf` | ~30min | YES |
| 32 | **Physical Notifications** | Elexon | N/A | N/A | YES | N/A | N/A | `/gb/elexon/bm/pn` | ~30min | YES |
| 33 | **Max Export/Import Limits** | Elexon | N/A | N/A | YES | N/A | N/A | `/gb/elexon/bm/mel` + `/mil` | ~30min | YES |
| 34 | **Dispatch Transparency (DT-BOA)** | NESO | N/A | N/A | YES | N/A | N/A | `/gb/national-grid/bm/dispatch-transparency` | Daily | YES |
| 35 | **Balancing Services Volume** | Elexon | N/A | N/A | YES | N/A | N/A | `/gb/elexon/bm/bsv` | ~30min | YES |
| 36 | **Non-BM STOR** | Elexon | N/A | N/A | YES | N/A | N/A | `/gb/elexon/bm/nonbm-stor` | ~30min | YES |

---

## 2. ANCILLARY SERVICES / FREQUENCY RESPONSE

### 2A. UK Dynamic Services (DC/DM/DR)

| # | Data Requirement | Modo API Available? | Modo Endpoint Path | Live? | Historical? |
|---|-----------------|--------------------|--------------------|-------|-------------|
| 37 | **DC/DM/DR Results Summary** (clearing prices + accepted volumes) | YES | `/gb/national-grid/dx/results-summary` | Daily | YES |
| 38 | **DC/DM/DR Buy Orders** | YES | `/gb/national-grid/dx/buy-orders` | Daily | YES |
| 39 | **DC/DM/DR Sell Orders** | YES | `/gb/national-grid/dx/sell-orders` | Daily | YES |
| 40 | **DC/DM/DR Results by Unit** | YES | `/gb/national-grid/dx/results-by-unit` | Daily | YES |
| 41 | **DC/DM/DR Block Orders** | YES | `/gb/national-grid/dx/block-orders` | Daily | YES |
| 42 | **DC Forecast (4-day ahead)** | YES | `/gb/national-grid/forecasts/dc-4d` | Daily | YES |
| 43 | **Historic DC Data (pre-Sep 2021)** | YES | `/gb/national-grid/dx/historic` | N/A | YES (pre-Sep 2021 only) |

### 2B. UK Weekly FFR (WFFR / SFFR)

| # | Data Requirement | Modo API Available? | Modo Endpoint Path | Live? | Historical? |
|---|-----------------|--------------------|--------------------|-------|-------------|
| 44 | **WFFR Results Summary** | YES | `/gb/national-grid/wffr/results-summary` | Weekly | YES |
| 45 | **WFFR Results by Unit** | YES | `/gb/national-grid/wffr/results-unit` | Weekly | YES |
| 46 | **WFFR Block Orders** | YES | `/gb/national-grid/wffr/block-orders` | Weekly | YES |
| 47 | **WFFR Linear Orders** | YES | `/gb/national-grid/wffr/linear-orders` | Weekly | YES |

### 2C. UK Balancing Reserve (BR)

| # | Data Requirement | Modo API Available? | Modo Endpoint Path | Live? | Historical? |
|---|-----------------|--------------------|--------------------|-------|-------------|
| 48 | **BR Buy Orders** | YES | `/gb/national-grid/br/buy-orders` | Daily | YES |
| 49 | **BR Sell Orders** | YES | `/gb/national-grid/br/sell-orders` | Daily | YES |
| 50 | **BR Results Summary** | YES | `/gb/national-grid/br/results-summary` | Daily | YES |
| 51 | **BR Results by Unit** | YES | `/gb/national-grid/br/results-by-unit` | Daily | YES |

### 2D. Germany & Netherlands Ancillary Services

| # | Data Requirement | Germany (DE) | Netherlands (NL) | Modo API — DE | Modo API — NL | Alternative Source |
|---|-----------------|-------------|-----------------|---------------|---------------|-------------------|
| 52 | **FCR (Frequency Containment Reserve)** — clearing prices, accepted volumes | Regelleistung.net | Regelleistung.net | NO | NO | Regelleistung.net API (free) |
| 53 | **aFRR+ (Auto Freq Restoration — Up)** — capacity prices, energy activation | Regelleistung + PICASSO | Regelleistung + PICASSO | NO | NO | Regelleistung.net + ENTSO-E TP |
| 54 | **aFRR- (Auto Freq Restoration — Down)** | Regelleistung + PICASSO | Regelleistung + PICASSO | NO | NO | Regelleistung.net + ENTSO-E TP |
| 55 | **mFRR+ (Manual Freq Restoration — Up)** | Regelleistung + MARI | Regelleistung + MARI | NO | NO | Regelleistung.net + ENTSO-E TP |
| 56 | **mFRR- (Manual Freq Restoration — Down)** | Regelleistung + MARI | Regelleistung + MARI | NO | NO | Regelleistung.net + ENTSO-E TP |

---

## 3. GRID CHARGES & NETWORK DATA

| # | Data Requirement | UK (GB) | Germany (DE) | Netherlands (NL) | Modo API? | Modo Endpoint Path | Alternative Source |
|---|-----------------|---------|-------------|-----------------|-----------|--------------------|--------------------|
| 57 | **BSUoS (Balancing Services Use of System)** | YES | N/A | N/A | YES | `/gb/national-grid/charges/bsuos-forecast` + `bsuosii` + `bsuosrf` + `bsuossf` | NESO Data Portal (free) |
| 58 | **BSUoS Forecast** | YES | N/A | N/A | YES | `/gb/national-grid/charges/bsuos-forecast` | NESO Data Portal (free) |
| 59 | **DUoS (Distribution Use of System)** | YES | Grid fees | Grid fees | NO | — | DNO tariff sheets (UKPN, WPD, etc.) |
| 60 | **TNUoS (Transmission Use of System)** | YES | Grid fees | Grid fees | NO | — | NESO charging statements |
| 61 | **Capacity Market (CM) Payments** | YES | N/A | N/A | NO | — | EMR Settlement (T062 files) |
| 62 | **Constraints Costs & Volume** | YES | N/A | N/A | YES | `/gb/national-grid/constraints/cost-volume` | NESO Data Portal |
| 63 | **Constraints Day-Ahead** | YES | N/A | N/A | YES | `/gb/national-grid/constraints/day-ahead` | NESO Data Portal |
| 64 | **Constraints Thermal Costs** | YES | N/A | N/A | YES | `/gb/national-grid/constraints/thermal-costs` | NESO Data Portal |

---

## 4. SYSTEM & GENERATION DATA

| # | Data Requirement | UK (GB) | Germany (DE) | Netherlands (NL) | Modo API — GB | Modo API — DE/NL | Modo Endpoint Path |
|---|-----------------|---------|-------------|-----------------|---------------|------------------|-------------------|
| 65 | **System Frequency** | 50Hz (1s res) | 50Hz | 50Hz | YES | NO | `/gb/elexon/system/frequency` |
| 66 | **Generation Outturn by Fuel (HH)** | Elexon | N/A | N/A | YES | NO | `/gb/elexon/generation/hh-outturn-by-fuel` |
| 67 | **Generation Outturn by Fuel (Instant)** | Elexon | N/A | N/A | YES | NO | `/gb/elexon/generation/instantaneous-outturn-by-fuel` |
| 68 | **Output per Generation Unit** | Elexon | N/A | N/A | YES | NO | `/gb/elexon/generation/b1610` |
| 69 | **Solar Generation** | Sheffield Solar | N/A | N/A | YES | NO | `/gb/sheffield-solar/generation` |
| 70 | **Solar PV Regions/GSP List** | Sheffield Solar | N/A | N/A | YES | NO | `/gb/sheffield-solar/regions` |
| 71 | **Wind Generation Forecast** | Elexon | N/A | N/A | YES | NO | `/gb/elexon/forecasts/wind` |
| 72 | **Carbon Intensity Forecast** | NESO | N/A | N/A | YES | NO | `/gb/national-grid/forecasts/carbon` |
| 73 | **Renewables Forecast** | NESO | N/A | N/A | YES | NO | `/gb/national-grid/forecasts/renewables` |
| 74 | **Gas Data** | NESO | N/A | N/A | YES | NO | `/gb/national-grid/gas` |
| 75 | **Inertia Data** | NESO | N/A | N/A | YES | NO | `/gb/national-grid/inertia` |
| 76 | **Interconnector Data (IFA2)** | NESO | N/A | N/A | YES | NO | `/gb/national-grid/interconnectors/ifa2` |

---

## 5. DEMAND FORECASTS

| # | Data Requirement | Modo API? | Modo Endpoint Path |
|---|-----------------|-----------|-------------------|
| 77 | **DA Total Load Forecast (DATL)** | YES | `/gb/elexon/forecasts/datl` |
| 78 | **DA Wind+Solar Forecast (DGWS)** | YES | `/gb/elexon/forecasts/dgws` |
| 79 | **2-14 Day Gen Availability by Fuel** | YES | `/gb/elexon/forecasts/fou2t14d` |
| 80 | **2-156 Week Gen Availability by Fuel** | YES | `/gb/elexon/forecasts/availability-156w-fuel` |
| 81 | **DA Indicated Imbalance** | YES | `/gb/elexon/forecasts/da-imbalance` |
| 82 | **DA Indicated Demand** | YES | `/gb/elexon/forecasts/da-demand` |
| 83 | **DA Indicated Generation** | YES | `/gb/elexon/forecasts/da-generation` |
| 84 | **National Demand Forecast (DA)** | YES | `/gb/elexon/forecasts/national-demand-da` |
| 85 | **Demand 2-14 Days Ahead** | YES | `/gb/elexon/forecasts/demand-2-14d` |
| 86 | **Demand 2-52 Weeks Ahead** | YES | `/gb/elexon/forecasts/demand-2-52w` |
| 87 | **Demand Forecast (NESO 2D)** | YES | `/gb/national-grid/forecasts/demand-2d` |
| 88 | **Demand Forecast (NESO 7D)** | YES | `/gb/national-grid/forecasts/demand-7d` |
| 89 | **Wind Forecast (NESO 14D)** | YES | `/gb/national-grid/forecasts/wind-14d` |
| 90 | **Surplus & Margin Forecasts** | YES | Multiple `/gb/elexon/forecasts/surplus-*` endpoints |
| 91 | **LOLP / De-Rated Margin** | YES | `/gb/elexon/system/lolpdrm` |

---

## 6. BESS ASSET & BENCHMARKING DATA

| # | Data Requirement | UK (GB) | Germany (DE) | Netherlands (NL) | Modo API — GB | Modo API — DE | Modo API — NL | Modo Endpoint Path |
|---|-----------------|---------|-------------|-----------------|---------------|---------------|---------------|-------------------|
| 92 | **BESS Asset Database** | All GB BESS | All DE BESS | All NL BESS | YES | NO | NO | `/gb/modo/asset/database` |
| 93 | **Asset Operations (Live Revenue)** | Per-asset | Per-asset | Per-asset | YES | NO | NO | `/gb/modo/benchmarking/asset-operations-live` |
| 94 | **Monthly Leaderboard** | GB fleet | DE fleet | NL fleet | YES | NO | NO | `/gb/modo/benchmarking/monthly-leaderboard` |
| 95 | **Live Leaderboard** | GB fleet | DE fleet | NL fleet | YES | NO | NO | `/gb/modo/benchmarking/leaderboard-live` |
| 96 | **BESS Owners Database** | GB | DE | NL | YES | NO | NO | `/gb/modo/companies/bess-owners` |
| 97 | **Revenue Forecasts (Pre-populated)** | GB | DE | NL | YES | NO | NO | `/forecasts/gb-forecasts-list/` |
| 98 | **Custom Revenue Forecasts** | GB | DE | NL | YES (any) | YES (any) | YES (any) | `/forecasts/forecasts/` + `/forecasts/run-simulation/` |
| 99 | **Macro Scenario List** | All | All | All | YES | YES | YES | `/forecasts/macro-scenarios/` |

---

## 7. BESS REVENUE INDICES (Modo Proprietary)

| # | Data Requirement | Modo API — GB | Modo API — DE | Modo API — NL | Modo Endpoint Path | Notes |
|---|-----------------|---------------|---------------|---------------|-------------------|-------|
| 100 | **ME BESS GB Index (Daily)** | YES (deprecated) | NO | NO | `/gb/modo/indices/daily` | Use new benchmarking endpoints |
| 101 | **ME BESS GB Index (Monthly)** | YES (deprecated) | NO | NO | `/gb/modo/indices/monthly` | Use new benchmarking endpoints |
| 102 | **BESS Industry Growth GB** | YES (deprecated) | NO | NO | `/gb/modo/indices/industry-growth` | Capacity/count trends |

---

## 8. COVERAGE SUMMARY

### Data Availability Scorecard

| Category | UK (GB) Needed | GB via Modo | DE Needed | DE via Modo | NL Needed | NL via Modo |
|----------|---------------|-------------|-----------|-------------|-----------|-------------|
| **Day-Ahead Prices** | YES | **YES** (EPEX + N2EX) | YES | **PARTIAL** (Nord Pool only, unconfirmed) | YES | **PARTIAL** (Nord Pool only, unconfirmed) |
| **Intraday Prices** | YES | **YES** (IDA1/2 + IDC) | YES | **NO** | YES | **NO** |
| **System/Imbalance Prices** | YES | **YES** (SSP/SBP/NIV) | YES (reBAP) | **NO** | YES (TenneT) | **NO** |
| **Balancing Mechanism** | YES | **YES** (full suite) | N/A | N/A | N/A | N/A |
| **Ancillary — DC/DM/DR** | YES | **YES** (full DX suite) | N/A | N/A | N/A | N/A |
| **Ancillary — FFR/SFFR** | YES | **YES** (full WFFR suite) | N/A | N/A | N/A | N/A |
| **Ancillary — FCR** | N/A | N/A | YES | **NO** | YES | **NO** |
| **Ancillary — aFRR/mFRR** | N/A | N/A | YES | **NO** | YES | **NO** |
| **BSUoS** | YES | **YES** | N/A | N/A | N/A | N/A |
| **DUoS / TNUoS / CM** | YES | **NO** | YES (grid fees) | **NO** | YES (grid fees) | **NO** |
| **System Frequency** | YES | **YES** | YES | **NO** | YES | **NO** |
| **Generation Mix** | YES | **YES** (fuel, solar, wind) | YES | **NO** | YES | **NO** |
| **Demand Forecasts** | YES | **YES** (13+ endpoints) | YES | **NO** | YES | **NO** |
| **BESS Asset Database** | YES | **YES** | YES | **NO** | YES | **NO** |
| **BESS Benchmarking** | YES | **YES** (leaderboard + ops) | YES | **NO** | YES | **NO** |
| **Revenue Forecasts** | YES | **YES** | YES | **PARTIAL** (custom only) | YES | **PARTIAL** (custom only) |
| **Carbon/Renewables Forecast** | Nice-to-have | **YES** | Nice-to-have | **NO** | Nice-to-have | **NO** |

### Coverage Percentage

| Market | Requirements Count | Covered by Modo | Coverage % | Notes |
|--------|-------------------|-----------------|------------|-------|
| **UK (GB)** | ~85 data points | ~75 | **~88%** | Excellent — only DUoS/TNUoS/CM gaps |
| **Germany (DE)** | ~7 data points (EPEX only) | ~2 (Nord Pool DA + forecasts) | **~29%** | Modo DE launching; EPEX direct fills gap |
| **Netherlands (NL)** | ~7 data points (EPEX only) | ~2 (Nord Pool DA + forecasts) | **~29%** | Modo NL launching; EPEX direct fills gap |

**Revised scope note:** Per Feb 26, 2026 meeting decision, DE/NL requirements are limited to EPEX data only (DA + intraday prices + benchmarks). No ancillary services, system data, or grid charges needed for DE/NL.

---

## 9. REVISED SCOPE — DE/NL REQUIREMENTS (Per Feb 26, 2026 Meeting)

**Key decision from Feb 26 Tuesday meeting:**
> DE and NL data requirements are **exactly the same as EPEX data** — we do **not** need other data (no ancillary services like FCR/aFRR/mFRR, no system frequency, no generation mix, no demand forecasts for DE/NL).

This dramatically simplifies the DE/NL scope. The only data needed for DE and NL is:

### Revised DE/NL Data Requirements (EPEX Only)

| # | Data Requirement | Germany (DE) | Netherlands (NL) | Modo API? | Alternative Source |
|---|-----------------|-------------|-----------------|-----------|-------------------|
| 1 | **EPEX Day-Ahead Prices** | DA hourly/QH | DA hourly/QH | NO (GB-only endpoints) | EPEX SPOT direct (paid), ENTSO-E TP (free) |
| 2 | **EPEX Intraday Auction (IDA1/IDA2)** | IDA results | IDA results | NO (GB-only endpoints) | EPEX SPOT direct (paid) |
| 3 | **EPEX Intraday Continuous Trades** | IDC trades | IDC trades | NO (GB-only endpoints) | EPEX SPOT direct (paid) |
| 4 | **EPEX Intraday Reference Price** | IDC ref price | IDC ref price | NO (GB-only endpoints) | EPEX SPOT direct (paid) |
| 5 | **EPEX Intraday OHLC** | IDC OHLC | IDC OHLC | NO (GB-only endpoints) | EPEX SPOT direct (paid) |
| 6 | **Nord Pool DA Prices** | Possibly via CWE | Possibly via CWE | PARTIAL (unconfirmed) | Nord Pool direct, ENTSO-E TP (free) |
| 7 | **BESS Benchmarking** | Modo DE benchmark | Modo NL benchmark | COMING (per Feb meeting, expected end of Mar 2026) | Aurora (alternative) |

### Meeting Context (Feb 26, 2026)
- **Modo started DE & NL service** — expected to be integrated by end of March 2026
- Data currently received via **SFTP** from Modo
- **EPEX intraday license** being purchased (PO in progress as of Mar 24 meeting)
- Modo subscription status and budget allocation still being clarified with Cyrus
- **Aurora** identified as alternative benchmarking provider — comparison pending
- Revenue in DE/NL expected from **July 2026** onward

---

## 10. GAPS — SOURCES TO FILL

### For DE/NL EPEX Data (the only gap that matters)

| Gap | Alternative Source | Cost | API? | Notes |
|-----|-------------------|------|------|-------|
| EPEX DE/NL DA Prices | **EPEX SPOT direct** (existing subscription, adding intraday) | Paid (PO in progress) | SFTP | Tom raising PO, Cyrus approving |
| EPEX DE/NL DA Prices | **ENTSO-E Transparency Platform** | FREE | REST API | Backup/validation source |
| EPEX DE/NL Intraday | **EPEX SPOT direct** (intraday license) | Paid (PO in progress) | SFTP | Key gap — being addressed |
| DE/NL BESS Benchmarks | **Modo Energy** (DE/NL service launching) | Existing subscription | API/SFTP | Expected end of March 2026 |
| DE/NL BESS Benchmarks | **Aurora** (alternative) | Quote needed | Unknown | Comparison with Modo pending |

### For GB (minor gaps only)

| Gap | Source | Cost |
|-----|--------|------|
| DUoS charges | DNO tariff sheets (UKPN Eastern) | FREE |
| TNUoS charges | NESO charging statements | FREE |
| Capacity Market payments | EMR T062 settlement files | FREE |

---

## 11. RECOMMENDATIONS

### Immediate (Now)
1. **Use Modo API for all GB data** — excellent coverage (~88%), single API
2. **Complete EPEX intraday PO** — Tom to raise, Cyrus to approve (per Mar 24 meeting)
3. **Legal review** — Ashley reviewing EPEX T&Cs for data sharing with Ampyr India
4. **Confirm Modo DE/NL readiness** — check if DE/NL data is live on Modo SFTP (was expected end of March)
5. **Test Nord Pool API** with `country=DE` and `country=NL` to confirm CWE coverage

### Before July 2026 (DE/NL Revenue Start)
6. **EPEX DE/NL intraday data flowing** via SFTP or API
7. **Modo DE/NL benchmarks integrated** into dashboard
8. **Compare Aurora vs Modo** for DE/NL benchmarking cost-effectiveness
9. **ENTSO-E TP** as free backup for DA price validation

### Production Platform (Doublu Phase 2)
10. **Build unified EPEX ingestion** — same schema for GB, DE, NL (only settlement period differs: 30min GB vs 15min DE/NL)
11. **Modo API integration** for benchmarking across all 3 markets
12. **Custom revenue forecasts** via Modo `/forecasts/run-simulation/` for all markets
