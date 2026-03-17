# BESS Revenue Tool - Data Requirements & Subscription Costs

**Asset:** Northwold Solar Farm (Hall Farm) - 8.4 MWh / 7.5 MW BESS
**Aggregator:** GridBeyond
**Prepared:** February 2026
**Purpose:** Define all data inputs required for the BESS Revenue Analysis Dashboard, including sources, frequency, and exact subscription costs

---

## Executive Summary

The BESS Revenue Analysis Dashboard requires **77 data fields** from **6 sources** across **3 frequency tiers** (half-hourly, daily, and static). This document catalogues every data point, its source, and the exact cost of obtaining it via live API.

**Key finding:** The majority of UK electricity market data is available **free** through Elexon (BMRS) and NESO public APIs. Paid subscriptions are needed only for exchange-direct price feeds (EPEX SPOT, Nord Pool) and premium analytics (Modo Energy).

| Cost Tier | Annual Cost | What You Get |
|-----------|-------------|--------------|
| **Free** | **£0** | Elexon system prices + NESO ancillary data + GridBeyond contract data |
| **Standard** | **~£1,000-£5,500** | Add Nord Pool N2EX day-ahead + intraday prices via API |
| **Professional** | **~£15,000-£45,000** | Add Modo Energy analytics + benchmarking platform |

---

## 1. Elexon (BMRS / Insights Solution)

**What it provides:** GB system prices (SSP, SBP), market index prices, settlement data, system warnings, generation mix, balancing mechanism data

**Website:** https://bmrs.elexon.co.uk / https://developer.data.elexon.co.uk

### Pricing

| Item | Cost | Notes |
|------|------|-------|
| **API Access** | **FREE** | All Elexon Insights Solution APIs are public and free |
| **Authentication** | **None required** | No API key needed for any endpoint |
| **Rate Limit** | **5,000 requests/min** | Per user; certain endpoints have additional endpoint-specific limits. Exceeding returns HTTP 429 |
| **Paid Tier** | **Does not exist** | Elexon does not offer premium/paid API tiers |

### Data Available (relevant to BESS dashboard)

| Data Point | Frequency | Endpoint | Cost |
|------------|-----------|----------|------|
| SSP (System Sell Price) | Half-hourly | `/balancing/pricing/system-sell-price` | FREE |
| SBP (System Buy Price) | Half-hourly | `/balancing/pricing/system-buy-price` | FREE |
| Market Index Prices (DA reference) | Half-hourly | `/balancing/pricing/market-index` | FREE |
| Imbalance volumes | Half-hourly | `/balancing/settlement/system-prices` | FREE |
| Generation mix by fuel | Half-hourly | `/generation/outturn/summary` | FREE |
| Balancing Mechanism data | Half-hourly | `/balancing/` endpoints | FREE |

### Verdict

**Use for:** SSP, SBP, DA HH reference prices, imbalance settlement data
**Total cost: £0/year**

---

## 2. EPEX SPOT (via EEX Group Webshop)

**What it provides:** Official EPEX day-ahead auction prices, intraday auction (IDA) prices, intraday continuous prices, volumes for GB market

**Website:** https://webshop.eex-group.com / https://www.epexspot.com/en/marketdataservices

### Pricing Structure

EPEX SPOT does **not publish fixed public prices**. Their pricing model works as follows:

- Prices are displayed per month in the EEX Group Webshop
- All products are invoiced **annually**
- Prices vary by **data usage** (internal vs external/redistribution)
- During ordering, a usage questionnaire determines final pricing
- **EPEX SPOT trading members** get their own active market data free + 20% discount on other data
- External usage (website display, redistribution) requires a **custom quote** from the market data team

### Available Products (GB-specific)

| Product | Delivery | Pricing |
|---------|----------|---------|
| GB Day-Ahead Auction Prices & Volumes (End-of-Day) | sFTP daily file | **Quote required** - contact marketdata@epexspot.com |
| GB Day-Ahead Auction Prices & Volumes (Real-Time) | API | **Quote required** |
| GB Intraday Auction Results | sFTP / API | **Quote required** |
| GB Intraday Continuous Trades | API | **Quote required** |
| GB Intraday Continuous Order Book | API (real-time) | **Quote required** |

### Alternative: Via Licensed Data Vendors

EPEX SPOT authorises third-party vendors to redistribute real-time data. Licensed vendors include:

| Vendor | Product | Estimated Cost |
|--------|---------|----------------|
| **Montel** | Real-time EPEX SPOT power prices + API | **Quote required** (2-week free trial available) |
| **Refinitiv (LSEG)** | Eikon/Workspace with EPEX data | ~£12,000-£22,000/user/year (enterprise platform) |
| **ICIS** | Power price dashboard | **Quote required** |
| **Modo Energy** (see Section 5) | EPEX prices included in platform | Included in subscription |

### Verdict

**Challenge:** EPEX SPOT does not publish transparent pricing. You must request a formal quote.
**Workaround:** EPEX DA reference prices are published on Elexon BMRS (free). Full EPEX prices are included in GridBeyond monthly report (no extra cost). For live API access, Nord Pool (Section 3) is a more transparent alternative for GB day-ahead prices.
**Action needed:** Contact marketdata@epexspot.com for a formal quote if live EPEX API is required.

---

## 3. Nord Pool (N2EX) - Day-Ahead & Intraday Data

**What it provides:** N2EX day-ahead auction prices for GB, intraday continuous trades and order books, historical data back to 2012+

**Website:** https://www.nordpoolgroup.com/en/services/power-market-data-services/

### Exact Pricing (from Nord Pool published fee schedule)

#### Day-Ahead Market Data

| Product | Price | Includes |
|---------|-------|----------|
| **UK Day-Ahead Package** | **€1,200/year** | Day-ahead price only + 1 API account + last 8 days history |
| Nordics & Baltics Full Package | €1,250/year | DA + Operating Data + Regulating Market + 1 API |
| Central & Western Europe Full Package | €4,100/year | DA + Operating Data + Regulating Market + 1 API |
| Germany-Luxembourg Package | €1,250/year | DA + 1 API |
| Baltics Only | €430/year | DA + 1 API |
| France/Netherlands/Austria/Belgium | €1,700-€3,300/year | Varies by country |

#### Intraday Market Data

| Product | Price | Includes |
|---------|-------|----------|
| **Intraday Trades Only** | **€5,000/year** | Pricing, volumes, hub-to-hub, ATC capacities, contracts |
| Intraday Trades & Orderbooks (Full) | €36,000/year | Real-time trades + lifecycle of individual orders |
| Regional Trades & Orderbooks | €10,000/year | Same as above but regional |
| Country-Level Orders & Trades (Delayed 20 min) | €4,400/year | History from 2012+ (trades), 2018+ (orders) |
| Orders Only (Delayed) | €3,700-€27,000/year | Depends on region |

#### Additional Costs

| Item | Price |
|------|-------|
| **Additional API account** | **€350/year per account** |
| Redistribution license | €3,000-€7,000/year |
| Aggregated Bidding Curves (Nordics) | €1,650/year |
| SMS Price Notifications (GB) | €200/line/year |
| Tailored Reports | €2,000/hour |

#### Recommended Package for Northwold Dashboard

| Item | Cost |
|------|------|
| UK Day-Ahead Package (N2EX prices) | €1,200/year |
| Intraday Trades Only | €5,000/year |
| Additional API account (if needed) | €350/year |
| **Total** | **€6,200-€6,550/year (~£5,300-£5,600)** |

### Verdict

**Best option for transparent, exact pricing** on GB day-ahead and intraday data.
**Total cost for GB DA + Intraday: ~€6,200/year (~£5,300/year)**

---

## 4. NESO (National Energy System Operator) Data Portal

**What it provides:** Ancillary services procurement results (SFFR, DC, DM, DR), frequency response tender outcomes, system requirements, ESO performance data

**Website:** https://data.nationalgrideso.com

### Pricing

| Item | Cost | Notes |
|------|------|-------|
| **All datasets** | **FREE** | Open data under UK Government open data licence |
| **API Access** | **FREE** | RESTful API, no authentication required |
| **Rate Limit** | Generous | Suitable for dashboard refresh rates |
| **Paid Tier** | **Does not exist** | All NESO data is freely available |

### Data Available (relevant to BESS dashboard)

| Data Point | Frequency | Cost |
|------------|-----------|------|
| SFFR tender results & clearing prices | Per EFA block (daily) | FREE |
| DC (Low/High) tender results | Per EFA block (daily) | FREE |
| DM (Low/High) tender results | Per EFA block (daily) | FREE |
| DR (Low/High) tender results | Per EFA block (daily) | FREE |
| Service requirements (MW) per block | Per EFA block (daily) | FREE |
| System frequency data | Real-time / 1-second | FREE |
| Capacity Market register | Annual | FREE |
| TWCAA availability reports | Quarterly | FREE |

### Verdict

**Use for:** All ancillary services data (SFFR, DC, DM, DR clearing prices, availability, tender results)
**Total cost: £0/year**

---

## 5. Modo Energy (Benchmarking & Analytics Platform)

**What it provides:** BESS revenue benchmarks (ME BESS GB Index), TB spread analysis, revenue forecasts, asset-level performance analytics, research library, API access

**Website:** https://modoenergy.com/pricing

### Subscription Tiers

Modo Energy offers **4 tiers**. All subscriptions include **unlimited users** at no extra cost. Minimum contract term is **36 months** (paid annually).

| Tier | Target User | Key Features | Pricing |
|------|-------------|-------------|---------|
| **Free** | Individuals entering the industry | Limited AI Analyst, global research access, global market data, BESS performance benchmarks (headline only) | **£0** |
| **Plus** | Individual professionals | Extended data access, more AI Analyst usage, research library | **Not publicly listed** - contact Modo for quote |
| **Pro** | Professionals with active portfolios | Full benchmarking, forecast creation (usage-based credits), API access | **Not publicly listed** - contact Modo for quote |
| **Business** | Teams with operational assets, development projects, multi-market coverage | Extended AI Analyst limits, licence to use Modo benchmarks in contracts and external publications, all Pro features | **Not publicly listed** - contact Modo for quote |
| **Enterprise** | Utilities, large-scale operators | Everything in Business + unlimited credits (no usage-based charges), shared context, dedicated account manager, quarterly analyst workshops | **Not publicly listed** - contact Modo for quote |

### Usage-Based Pricing (Pro & Business tiers)

- Pro and Business plans charge per-credit for **creating new forecasts**
- Enterprise plan includes **unlimited credits** (fixed annual fee)
- Exact credit costs are not publicly listed

### What Each Tier Includes

| Feature | Free | Plus | Pro | Business | Enterprise |
|---------|------|------|-----|----------|------------|
| ME BESS GB Index (headline) | Yes | Yes | Yes | Yes | Yes |
| AI Analyst | Limited | Extended | Extended | Extended | Extended + pooled |
| Global research library | Yes | Yes | Yes | Yes | Yes |
| Global market data | Yes | Yes | Yes | Yes | Yes |
| BESS performance benchmarks | Headline | Full | Full | Full | Full |
| Forecast creation | No | No | Usage-based | Usage-based | Unlimited |
| API access | No | No | Yes | Yes | Yes |
| Benchmark licence (contracts/publications) | No | No | No | Yes | Yes |
| Dedicated account manager | No | No | No | No | Yes |
| Quarterly analyst workshops | No | No | No | No | Yes |
| Unlimited users | Yes | Yes | Yes | Yes | Yes |

### Add-On Modules (available on Pro/Business/Enterprise)

| Add-On | Description |
|--------|-------------|
| GB Benchmarking | Granular revenue benchmarking for GB BESS assets |
| GB Research | Full access to GB-specific research reports |
| GB Forecasted Power Prices | Forward price curves and world view |

### Estimated Pricing (industry estimates - not confirmed by Modo)

Based on comparable energy analytics SaaS platforms and industry feedback:

| Tier | Estimated Annual Cost | Basis for Estimate |
|------|----------------------|--------------------|
| Free | £0 | Confirmed free |
| Plus | ~£2,000-£5,000/year | Entry-level SaaS analytics |
| Pro | ~£8,000-£15,000/year | Professional energy analytics platforms |
| Business | ~£15,000-£30,000/year | Multi-user team licences with publication rights |
| Enterprise | ~£30,000-£60,000+/year | Unlimited credits + dedicated support |

**These are estimates only.** Modo Energy does not publicly list prices.

### Verdict

**Action needed:** Contact Modo Energy directly at https://modoenergy.com/pricing for a formal quote.
**Recommended tier for Northwold:** Business (for benchmark licence needed in investor/GridBeyond reporting)
**Estimated cost: £15,000-£30,000/year** (requires 36-month commitment)

---

## 6. GridBeyond (Aggregator Operational Data)

**What it provides:** All dispatch volumes, revenue by market, ancillary service commitments, imbalance positions - the core 36 operational fields used by the dashboard

**Delivery:** Monthly Excel workbook

### Pricing

| Item | Cost | Notes |
|------|------|-------|
| Monthly operational report | **£0 (included in contract)** | Covered by 5% aggregator revenue share |
| Data covers | 36+ fields per settlement period | Dispatch MW, revenues, prices, ancillary availability |
| Live API access | **Not available** | GridBeyond does not provide real-time API access to asset owners |

### Verdict

**Total cost: £0/year** - contractual obligation
**Limitation:** Data arrives monthly with ~2 week lag. No real-time API.

---

## 7. SCADA / Battery Management System

**What it provides:** Physical battery measurements - power, SOC, frequency, availability

### Pricing

| Item | Cost | Notes |
|------|------|-------|
| SCADA data export | **£0** | Existing infrastructure at Northwold |
| Data historian (if upgrade needed) | ~£0-£5,000/year | Tag-based licensing; existing system may suffice |

### Verdict

**Total cost: £0/year** (existing infrastructure)

---

## Consolidated Cost Summary

### Exact & Verified Prices

| Source | Product | Exact Annual Cost | Confidence |
|--------|---------|-------------------|------------|
| **Elexon BMRS** | Full API (SSP, SBP, DA HH, settlement) | **FREE** | Confirmed - public API, no key required |
| **NESO Data Portal** | All ancillary services data | **FREE** | Confirmed - open data |
| **GridBeyond** | Monthly operational report | **£0** | Confirmed - contractual |
| **SCADA** | Existing data export | **£0** | Confirmed - existing infrastructure |
| **Nord Pool** | UK Day-Ahead (N2EX) | **€1,200/year** | Confirmed - published price list |
| **Nord Pool** | Intraday Trades Only | **€5,000/year** | Confirmed - published price list |
| **Nord Pool** | Additional API account | **€350/year** | Confirmed - published price list |
| **Nord Pool** | GB SMS price alerts | **€200/line/year** | Confirmed - published price list |

### Quote-Required (prices not publicly listed)

| Source | Product | Estimated Annual Cost | Action |
|--------|---------|----------------------|--------|
| **EPEX SPOT** (EEX Webshop) | GB DA + Intraday + IDC via API | Unknown - **quote required** | Email marketdata@epexspot.com |
| **Modo Energy** | Pro subscription + GB add-ons | ~£8,000-£15,000/year (estimate) | Visit modoenergy.com/pricing |
| **Modo Energy** | Business subscription + GB add-ons | ~£15,000-£30,000/year (estimate) | Visit modoenergy.com/pricing |
| **Modo Energy** | Enterprise subscription | ~£30,000-£60,000+/year (estimate) | Visit modoenergy.com/pricing |
| **Montel** | Real-time EPEX prices via API | Unknown - **quote required** | 2-week free trial available |
| **Refinitiv (LSEG)** | Eikon with EPEX/power data | ~£12,000-£22,000/user/year (estimate) | Contact LSEG sales |

---

## Recommended Packages

### Option A: Minimum Viable (Free Only)

| Source | Cost |
|--------|------|
| Elexon BMRS API (SSP, SBP, DA HH) | FREE |
| NESO Data Portal (ancillary services) | FREE |
| GridBeyond monthly report | FREE (contract) |
| SCADA export | FREE (existing) |
| Modo Energy Free tier (headline index) | FREE |
| **TOTAL** | **£0/year** |

**Trade-off:** No live EPEX/N2EX prices (rely on Elexon reference + GridBeyond monthly). Benchmarking limited to headline ME BESS GB index.

---

### Option B: Standard (Add Nord Pool Live Prices)

| Source | Cost |
|--------|------|
| Everything in Option A | FREE |
| Nord Pool UK Day-Ahead (N2EX) | €1,200/year |
| Nord Pool Intraday Trades | €5,000/year |
| Additional API account | €350/year |
| **TOTAL** | **€6,550/year (~£5,600/year)** |

**Benefit:** Live N2EX day-ahead and intraday prices via API. Enables real-time price tracking and same-day analysis.

---

### Option C: Professional (Add Modo Analytics)

| Source | Cost |
|--------|------|
| Everything in Option B | ~£5,600/year |
| Modo Energy Pro/Business subscription | ~£15,000-£30,000/year (estimate) |
| **TOTAL** | **~£20,600-£35,600/year** |

**Benefit:** Full BESS benchmarking, revenue forecasts, TB spread analytics, publication-licensed benchmarks for investor reporting.

---

### Option D: Enterprise (Maximum Coverage)

| Source | Cost |
|--------|------|
| Everything in Option C | ~£20,600-£35,600/year |
| EPEX SPOT direct feed (quote required) | TBD |
| Modo Energy Enterprise upgrade | ~£30,000-£60,000/year (estimate) |
| **TOTAL** | **~£35,600-£65,600+/year** |

**Benefit:** Maximum data coverage with unlimited analytics credits and dedicated support.

---

## Next Steps

| Priority | Action | Contact |
|----------|--------|---------|
| 1 (Immediate) | Register for Elexon API (free) | https://developer.data.elexon.co.uk |
| 2 (Immediate) | Register for NESO Data Portal (free) | https://data.nationalgrideso.com |
| 3 (This week) | Request Nord Pool UK DA + Intraday quote | https://www.nordpoolgroup.com/en/services/power-market-data-services/ |
| 4 (This week) | Request Modo Energy pricing (Pro/Business) | https://modoenergy.com/pricing |
| 5 (If needed) | Request EPEX SPOT direct data quote | marketdata@epexspot.com |
| 6 (If needed) | Request Montel trial (2-week free) | https://montel.energy |
| 7 (Ongoing) | Request GridBeyond to provide data as CSV/API | Existing contract contact |

---

## Appendix: All 77 Data Fields by Source

### A. SCADA (4 fields, half-hourly, FREE)

| # | Field | Unit |
|---|-------|------|
| 1 | Physical_Power_MW | MW |
| 2 | Physical_SoC | % |
| 3 | Frequency | Hz |
| 4 | Availability | Flag |

### B. Elexon BMRS (6 fields, half-hourly, FREE)

| # | Field | Unit |
|---|-------|------|
| 5 | SSP (System Sell Price) | GBP/MWh |
| 6 | SBP (System Buy Price) | GBP/MWh |
| 7 | DA HH Price (Market Index) | GBP/MWh |
| 8 | Imbalance Volume | MWh |
| 9 | Net Imbalance Volume | MWh |
| 10 | System warnings | Flag |

### C. GridBeyond Report (32 fields, half-hourly, FREE via contract)

| # | Field | Unit |
|---|-------|------|
| 11 | Day Ahead Price (EPEX) | GBP/MWh |
| 12 | GB-ISEM Intraday 1 Price | GBP/MWh |
| 13 | IDC Price | GBP/MWh |
| 14 | DA MW | MW |
| 15 | EPEX 30 DA MW | MW |
| 16 | IDA1 MW | MW |
| 17 | IDC MW | MW |
| 18 | Credited Energy Volume (Battery MWh Output) | MWh |
| 19 | EPEX DA Revenues | GBP |
| 20 | EPEX 30 DA Revenue | GBP |
| 21 | IDA1 Revenue | GBP |
| 22 | IDC Revenue | GBP |
| 23 | Imbalance Revenue | GBP |
| 24 | Imbalance Charge | GBP |
| 25 | SFFR Availability | MW |
| 26 | SFFR Clearing Price | GBP/MW/h |
| 27 | SFFR revenues | GBP |
| 28 | DCL Availability | MW |
| 29 | DCL Clearing Price | GBP/MW/h |
| 30 | DCL revenues | GBP |
| 31 | DCH Availability | MW |
| 32 | DCH Clearing Price | GBP/MW/h |
| 33 | DCH revenues | GBP |
| 34 | DML Availability | MW |
| 35 | DML Clearing Price | GBP/MW/h |
| 36 | DML revenues | GBP |
| 37 | DMH Availability | MW |
| 38 | DMH Clearing Price | GBP/MW/h |
| 39 | DMH revenues | GBP |
| 40 | DRL Availability | MW |
| 41 | DRL Clearing Price | GBP/MW/h |
| 42 | DRL revenues | GBP |
| 43 | DRH Availability | MW |
| 44 | DRH Clearing Price | GBP/MW/h |
| 45 | DRH revenues | GBP |
| 46 | Battery SoC | % |

### D. Nord Pool / EPEX (6 fields, half-hourly, PAID)

| # | Field | Unit | Source |
|---|-------|------|--------|
| 47 | N2EX Day-Ahead Auction Price | GBP/MWh | Nord Pool (€1,200/yr) |
| 48 | EPEX DA Auction Price | GBP/MWh | EPEX (quote) or via GridBeyond |
| 49 | Intraday Continuous Price | GBP/MWh | Nord Pool (€5,000/yr) or EPEX (quote) |
| 50 | Intraday Auction (IDA1) Price | GBP/MWh | EPEX (quote) or via GridBeyond |
| 51 | Intraday Trade Volumes | MWh | Nord Pool (included in intraday sub) |
| 52 | DA Auction Volumes | MWh | Nord Pool (included in DA sub) |

### E. NESO (10 fields, per EFA block, FREE)

| # | Field | Unit |
|---|-------|------|
| 53 | SFFR tender clearing price | GBP/MW/h |
| 54 | DCL tender clearing price | GBP/MW/h |
| 55 | DCH tender clearing price | GBP/MW/h |
| 56 | DML tender clearing price | GBP/MW/h |
| 57 | DMH tender clearing price | GBP/MW/h |
| 58 | DRL tender clearing price | GBP/MW/h |
| 59 | DRH tender clearing price | GBP/MW/h |
| 60 | Service requirement (MW procured) | MW |
| 61 | System frequency | Hz |
| 62 | Capacity Market register | Various |

### F. Modo Energy (7 fields, monthly/daily, PAID or FREE headline)

| # | Field | Unit |
|---|-------|------|
| 63 | ME BESS GB 2H Index | GBP/MW/year |
| 64 | Revenue range (Low/Mid/High) | GBP/MW/year |
| 65 | TB1/TB2/TB3 spread benchmarks | GBP/MWh |
| 66 | TB2 Capture Rate benchmark | % |
| 67 | Degradation benchmarks | %/year |
| 68 | Availability (TWCAA) benchmarks | % |
| 69 | Round-trip efficiency benchmarks | % |

### G. IAR & Configuration (8 + 10 = 18 fields, static)

| # | Field | Unit |
|---|-------|------|
| 70-77 | IAR monthly projections (8 revenue streams) | GBP/month |

| # | Parameter | Value |
|---|-----------|-------|
| 78 | P_IMP_MAX_MW | 4.2 MW |
| 79 | P_EXP_MAX_MW | 7.5 MW |
| 80 | CAPACITY_MWH | 8.4 MWh |
| 81 | EFF_ROUND_TRIP | 87% |
| 82 | SOC_MIN_PCT | 5% |
| 83 | SOC_MAX_PCT | 95% |
| 84 | CYCLES_PER_DAY | 1.5 |
| 85 | MAX_DAILY_THROUGHPUT_MWH | 12.6 MWh |
| 86 | OWNER_SHARE | 95% |
| 87 | AGGREGATOR_SHARE | 5% |

---

## Sources

- **Elexon BMRS API:** https://bmrs.elexon.co.uk/api-documentation
- **Elexon Developer Portal:** https://developer.data.elexon.co.uk
- **NESO Data Portal:** https://data.nationalgrideso.com
- **Nord Pool Data Services (DA pricing):** https://www.nordpoolgroup.com/en/services/power-market-data-services/day-ahead-market-data/
- **Nord Pool Data Services (Intraday pricing):** https://www.nordpoolgroup.com/en/services/power-market-data-services/intraday-market-data/
- **EPEX SPOT Market Data Services:** https://www.epexspot.com/en/marketdataservices
- **EEX Group Webshop:** https://webshop.eex-group.com
- **Modo Energy Pricing:** https://modoenergy.com/pricing
- **Modo Energy Help - Subscriptions:** https://help.modo.energy/en/collections/6039772-subscriptions-pricing
- **Montel (EPEX data vendor):** https://montel.energy/products/prices/power-market-prices
