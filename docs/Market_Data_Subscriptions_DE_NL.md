# Market Rate Data Subscriptions — Germany & Netherlands

**Purpose:** Data requirements for extending the BESS dashboard to German and Dutch assets
**Reference:** See `UK_Market_Rate_Data_Subscriptions.md` for existing UK requirements
**Prepared:** February 2026

---

## KEY STRUCTURAL DIFFERENCES FROM UK

Before listing individual feeds, it's important to understand the fundamental market structure differences:

| Feature | UK (GB) | Germany (DE) | Netherlands (NL) |
|---------|---------|--------------|-------------------|
| **Settlement period** | 30 minutes (48/day) | **15 minutes** (96/day) | **15 minutes** (96/day) |
| **Currency** | GBP | EUR | EUR |
| **TSO(s)** | NESO (1) | 50Hertz, Amprion, TenneT, TransnetBW (4) | TenneT NL (1) |
| **Bidding zone** | GB | DE-LU | NL |
| **Exchange** | EPEX SPOT / Nord Pool | EPEX SPOT | EPEX SPOT |
| **Imbalance pricing** | Dual (SSP / SBP) | Single (reBAP) | Hybrid single/dual |
| **Frequency response products** | SFFR, DC, DM, DR (GB-specific) | FCR, aFRR, mFRR (EU standard) | FCR, aFRR, mFRR (EU standard) |
| **Intraday auctions per day** | 1 (IDA1) | 3 (IDA1, IDA2, IDA3) | 3 (IDA1, IDA2, IDA3) |
| **Intraday gate closure** | 30 min before delivery | **5 min** before delivery | **5 min** before delivery |

**Dashboard implication:** The move from 48 to 96 periods per day doubles the data volume. The ancillary services module needs a complete redesign — DE/NL use FCR/aFRR/mFRR instead of UK's SFFR/DC/DM/DR products.

---

# PART 1: GERMANY (DE)

---

## 1. Wholesale Electricity Prices — Germany

### 1.1 EPEX Day-Ahead Auction Price (DE-LU)
- **What:** Next-day electricity price from the EPEX SPOT day-ahead auction for the Germany-Luxembourg bidding zone
- **Why needed:** Primary benchmark for charge/discharge arbitrage decisions
- **Frequency:** Quarter-hourly (96 values per day, since October 2025 — previously hourly)
- **Unit:** EUR/MWh
- **Current free source:** SMARD (Bundesnetzagentur) — `https://www.smard.de`
- **Alternative free source:** ENTSO-E Transparency Platform
- **Paid direct source:** EPEX SPOT (quote required)
- **Cost:** FREE via SMARD / ENTSO-E; paid via EPEX SPOT (quote)

### 1.2 EPEX Intraday Auction 1 (IDA1) Price — DE
- **What:** First same-day auction result — provides updated pricing after day-ahead
- **Why needed:** Second trading opportunity to refine positions before delivery
- **Frequency:** Quarter-hourly
- **Unit:** EUR/MWh
- **Gate closure:** 15:00 CET on D-1
- **Source:** EPEX SPOT (paid subscription)
- **Free alternative:** Partial data available on SMARD
- **Cost:** Bundled with EPEX SPOT subscription (quote required)

### 1.3 EPEX Intraday Auction 2 (IDA2) Price — DE
- **What:** Second same-day auction — evening auction for full next day
- **Why needed:** Further position refinement; captures late-day forecast changes
- **Frequency:** Quarter-hourly
- **Unit:** EUR/MWh
- **Gate closure:** 22:00 CET on D-1
- **Source:** EPEX SPOT (paid subscription)
- **Cost:** Bundled with EPEX SPOT subscription

### 1.4 EPEX Intraday Auction 3 (IDA3) Price — DE
- **What:** Third intraday auction — morning of delivery day for afternoon/evening periods
- **Why needed:** Captures same-day demand and generation updates
- **Frequency:** Quarter-hourly (covers 12:00–24:00 delivery)
- **Unit:** EUR/MWh
- **Gate closure:** 10:00 CET on delivery day
- **Source:** EPEX SPOT (paid subscription)
- **Cost:** Bundled with EPEX SPOT subscription

### 1.5 Intraday Continuous (IDC) Price — DE
- **What:** Continuous electronic trading price on EPEX intraday market — trades executed up to 5 minutes before delivery
- **Why needed:** Captures real-time price volatility and short-notice opportunities; 5-minute gate closure is much shorter than UK's 30-minute
- **Frequency:** Quarter-hourly (aggregated from continuous trades)
- **Unit:** EUR/MWh
- **Source:** EPEX SPOT (paid subscription for real-time)
- **Free alternative:** Aggregated data on SMARD (delayed)
- **Cost:** Bundled with EPEX SPOT subscription

### 1.6 Imbalance Price (reBAP) — DE
- **What:** The "regelzonenuebergreifender einheitlicher Bilanzausgleichsenergiepreis" — Germany's single, uniform imbalance settlement price
- **Why needed:** Determines cost/revenue of any deviation from contracted position; unlike UK's dual SSP/SBP, Germany uses a single symmetric price
- **Frequency:** Quarter-hourly (per 15-min settlement period)
- **Unit:** EUR/MWh
- **Source:** Netztransparenz.de — `https://www.netztransparenz.de/en/Balancing-Capacity/Imbalance-price`
- **Cost:** FREE (published by all 4 TSOs jointly)
- **Near-real-time estimator available:** `https://www.netztransparenz.de/en/Balancing-Capacity/Imbalance-price/IP-estimator`

---

## 2. Ancillary Services Clearing Prices — Germany

> Germany uses the EU-standard FCR/aFRR/mFRR framework, procured jointly by the 4 TSOs via regelleistung.net. These replace the UK's SFFR/DC/DM/DR products entirely.

### 2.1 FCR Capacity Price (Frequency Containment Reserve)
- **What:** Clearing price for providing primary frequency containment — battery must respond within 30 seconds to frequency deviations
- **Why needed:** FCR is a high-value revenue stream for BESS — historically up to ~EUR 9,400/MW per month in favourable periods
- **Frequency:** Per 4-hour block (6 blocks per day), daily tender
- **Unit:** EUR/MW per 4-hour block
- **Direction:** Symmetric (single bid covers both up and down)
- **Pricing mechanism:** Pay-as-cleared (all accepted bidders get the marginal price)
- **Minimum bid:** 1 MW
- **Source:** Regelleistung.net — `https://www.regelleistung.net/apps/datacenter/tenders/`
- **Cost:** FREE
- **Note:** FCR is procured via the FCR Cooperation — a shared auction across Germany, France, Belgium, Netherlands, Austria, Switzerland, and others

### 2.2 aFRR Positive Capacity Price (Automatic Frequency Restoration Reserve — Up)
- **What:** Price for providing upward secondary frequency response — activated automatically within 5 minutes when grid frequency drops
- **Why needed:** aFRR is a major revenue source for German BESS — positive capacity prices have reached ~EUR 21,500/MW per month
- **Frequency:** Per 4-hour block, daily tender
- **Unit:** EUR/MW per 4-hour block
- **Pricing mechanism:** Pay-as-bid
- **Minimum bid:** 5 MW
- **Source:** Regelleistung.net
- **Cost:** FREE

### 2.3 aFRR Negative Capacity Price (Automatic Frequency Restoration Reserve — Down)
- **What:** Price for providing downward secondary frequency response — activated when grid frequency rises
- **Why needed:** Separate product from positive aFRR — enables full revenue stacking analysis
- **Frequency:** Per 4-hour block, daily tender
- **Unit:** EUR/MW per 4-hour block
- **Pricing mechanism:** Pay-as-bid
- **Source:** Regelleistung.net
- **Cost:** FREE

### 2.4 aFRR Energy Activation Price
- **What:** Price paid when aFRR reserve is actually called upon (dispatched) — separate from the capacity holding payment
- **Why needed:** Determines actual revenue when battery is activated; critical for accurate P&L — Germany pays both capacity AND energy, unlike UK ancillary services which are capacity-only
- **Frequency:** Per activation event / quarter-hourly settlement
- **Unit:** EUR/MWh
- **Pricing mechanism:** Pay-as-bid (merit order activation)
- **Source:** Regelleistung.net / Netztransparenz.de
- **Cost:** FREE

### 2.5 mFRR Positive Capacity Price (Manual Frequency Restoration Reserve — Up)
- **What:** Price for providing upward tertiary reserve — manually activated within 15 minutes for larger imbalances
- **Why needed:** Additional revenue stream, though typically lower value than FCR/aFRR for BESS
- **Frequency:** Per 4-hour block, daily tender
- **Unit:** EUR/MW per 4-hour block
- **Pricing mechanism:** Pay-as-bid
- **Minimum bid:** 5 MW
- **Source:** Regelleistung.net
- **Cost:** FREE

### 2.6 mFRR Negative Capacity Price (Manual Frequency Restoration Reserve — Down)
- **What:** Price for providing downward tertiary reserve
- **Why needed:** Completes the full ancillary service product suite
- **Frequency:** Per 4-hour block, daily tender
- **Unit:** EUR/MW per 4-hour block
- **Source:** Regelleistung.net
- **Cost:** FREE

### 2.7 mFRR Energy Activation Price
- **What:** Price paid when mFRR is dispatched
- **Why needed:** As with aFRR, actual revenue depends on both capacity and energy payments
- **Frequency:** Per activation event
- **Unit:** EUR/MWh
- **Pricing mechanism:** Pay-as-bid
- **Source:** Regelleistung.net / Netztransparenz.de
- **Cost:** FREE

---

## 3. German Data Sources Summary

| Source | What It Provides | Cost | Auth Required |
|--------|-----------------|------|---------------|
| **SMARD** (Bundesnetzagentur) | DA prices, generation mix, consumption, wholesale data | FREE | None |
| **Netztransparenz.de** (4 TSOs) | Imbalance price (reBAP), near-real-time estimator | FREE | None |
| **Regelleistung.net** (4 TSOs) | FCR/aFRR/mFRR tender results, clearing prices, activation data | FREE | None |
| **ENTSO-E Transparency Platform** | Cross-border flows, DA prices, load, generation by type | FREE | API token (email request) |
| **EPEX SPOT** (direct) | Official exchange prices, intraday continuous, order books | Paid (quote required) | Subscription |
| **Nord Pool** (alternative) | DE DA + intraday prices | ~EUR 1,200–5,000/year | Subscription |

---

# PART 2: NETHERLANDS (NL)

---

## 4. Wholesale Electricity Prices — Netherlands

### 4.1 EPEX Day-Ahead Auction Price (NL)
- **What:** Next-day electricity price from the EPEX SPOT auction for the Netherlands bidding zone (formerly operated by APX, now EPEX SPOT since 2015)
- **Why needed:** Primary arbitrage benchmark — determines charge/discharge schedule
- **Frequency:** Quarter-hourly (96 values per day, since October 2025 — previously hourly)
- **Unit:** EUR/MWh
- **Free source:** ENTSO-E Transparency Platform
- **Paid direct source:** EPEX SPOT (quote required)
- **Cost:** FREE via ENTSO-E; paid via EPEX SPOT

### 4.2 EPEX Intraday Auction 1 (IDA1) Price — NL
- **What:** First same-day auction on EPEX SPOT for NL delivery
- **Why needed:** Refines trading position after DA auction; captures updated forecasts
- **Frequency:** Quarter-hourly
- **Unit:** EUR/MWh
- **Gate closure:** 15:00 CET on D-1
- **Source:** EPEX SPOT (paid subscription)
- **Cost:** Bundled with EPEX SPOT subscription

### 4.3 EPEX Intraday Auction 2 (IDA2) Price — NL
- **What:** Second same-day auction — evening update
- **Why needed:** Further position refinement
- **Frequency:** Quarter-hourly
- **Unit:** EUR/MWh
- **Gate closure:** 22:00 CET on D-1
- **Source:** EPEX SPOT (paid subscription)
- **Cost:** Bundled with EPEX SPOT subscription

### 4.4 EPEX Intraday Auction 3 (IDA3) Price — NL
- **What:** Third intraday auction — morning of delivery day
- **Why needed:** Same-day demand and generation adjustments
- **Frequency:** Quarter-hourly (covers 12:00–24:00)
- **Unit:** EUR/MWh
- **Gate closure:** 10:00 CET on delivery day
- **Source:** EPEX SPOT (paid subscription)
- **Cost:** Bundled with EPEX SPOT subscription

### 4.5 Intraday Continuous (IDC) Price — NL
- **What:** Continuous trading price on EPEX intraday — trades up to 5 minutes before delivery
- **Why needed:** Captures real-time volatility and short-notice opportunities
- **Frequency:** Quarter-hourly (aggregated)
- **Unit:** EUR/MWh
- **Source:** EPEX SPOT (paid subscription for real-time)
- **Cost:** Bundled with EPEX SPOT subscription

### 4.6 Imbalance / Settlement Price — NL
- **What:** TenneT's settlement price for balancing energy — determined by the most extreme aFRR activation price in each 15-minute period
- **Why needed:** The Dutch market explicitly rewards "passive balancing" — a BESS that charges when the system is long (or discharges when short) can profit from the imbalance price. This is a distinct revenue stream.
- **Frequency:** Quarter-hourly (per 15-min ISP)
- **Unit:** EUR/MWh
- **Pricing:** Usually single price; dual pricing applies when both up and down balancing is activated in the same period
- **Source:** TenneT API — `https://developer.tennet.eu/specs/v1/settlement-prices`
- **Cost:** FREE (registration required)
- **Note:** TenneT also publishes balance delta (system imbalance direction) in near-real-time — useful for passive balancing signals

---

## 5. Ancillary Services Clearing Prices — Netherlands

> The Netherlands uses the same EU-standard FCR/aFRR/mFRR framework as Germany. Products are procured by TenneT NL, with cross-border sharing via PICASSO and MARI platforms.

### 5.1 FCR Capacity Price — NL
- **What:** Clearing price from the daily FCR Cooperation common auction
- **Why needed:** FCR is a key revenue stream for Dutch BESS — procured via the same pan-European auction as Germany
- **Frequency:** Per 4-hour block (6 blocks per day), daily auction
- **Unit:** EUR/MW per 4-hour block
- **Direction:** Symmetric
- **Pricing mechanism:** Pay-as-cleared
- **Source:** TenneT transparency data / FCR Cooperation results
- **Cost:** FREE
- **Note:** 30% of TenneT's FCR obligation must be sourced from providers physically in the Netherlands; remaining 70% can come from any FCR Cooperation country

### 5.2 aFRR Positive Capacity Price — NL
- **What:** Price for providing upward automatic frequency restoration reserve
- **Why needed:** aFRR is a significant BESS revenue source; energy activation now cross-border via PICASSO platform (since October 2024)
- **Frequency:** Weekly and daily tenders
- **Unit:** EUR/MW per period
- **Source:** TenneT transparency data — `https://www.tennet.eu/nl-en/markets/ancillary-services`
- **Cost:** FREE

### 5.3 aFRR Negative Capacity Price — NL
- **What:** Price for providing downward automatic frequency restoration reserve
- **Why needed:** Separate product — needed for full revenue stacking analysis
- **Frequency:** Weekly and daily tenders
- **Unit:** EUR/MW per period
- **Source:** TenneT transparency data
- **Cost:** FREE

### 5.4 aFRR Energy Activation Price — NL
- **What:** Price paid when aFRR is dispatched via the PICASSO platform
- **Why needed:** Since PICASSO go-live in NL (October 2024), cross-border aFRR sharing has reduced imbalance price volatility but created new energy activation revenue opportunities
- **Frequency:** Per activation / quarter-hourly
- **Unit:** EUR/MWh
- **Source:** TenneT API / PICASSO results
- **Cost:** FREE

### 5.5 mFRR Capacity Price — NL
- **What:** Price for providing manual frequency restoration reserve (historically called "noodvermogen" in Dutch market)
- **Why needed:** Additional revenue stream; NL connected to MARI platform from December 2025, enabling cross-border mFRR energy exchange
- **Frequency:** Per tender period
- **Unit:** EUR/MW per period
- **Source:** TenneT transparency data
- **Cost:** FREE

### 5.6 mFRR Energy Activation Price — NL
- **What:** Price paid when mFRR is dispatched via MARI platform
- **Why needed:** New revenue stream since MARI connection in December 2025
- **Frequency:** Per activation event
- **Unit:** EUR/MWh
- **Source:** TenneT API / MARI results
- **Cost:** FREE

---

## 6. Dutch Data Sources Summary

| Source | What It Provides | Cost | Auth Required |
|--------|-----------------|------|---------------|
| **TenneT API** (developer.tennet.eu) | Settlement prices, imbalance volumes, balance delta, regulation state | FREE | Registration + token |
| **TenneT Transparency Portal** | Ancillary service results, system data, download CSVs | FREE | Token for automation |
| **ENTSO-E Transparency Platform** | DA prices, cross-border flows, generation, load | FREE | API token (email request) |
| **EPEX SPOT** (direct) | Official NL exchange prices, intraday continuous, order books | Paid (quote required) | Subscription |
| **Nord Pool** (alternative) | NL DA + intraday prices | ~EUR 1,700–3,300/year (FR/NL/AT/BE bundle) | Subscription |

---

# PART 3: CROSS-MARKET COMPARISON

---

## 7. Data Feed Count by Market

| Category | UK (GB) | Germany (DE) | Netherlands (NL) |
|----------|---------|--------------|-------------------|
| Wholesale prices | 7 feeds | 6 feeds | 6 feeds |
| Imbalance prices | 2 (SSP + SBP) | 1 (reBAP) | 1 (settlement price) |
| Ancillary capacity prices | 7 (SFFR, DCL/H, DML/H, DRL/H) | 5 (FCR, aFRR+/-, mFRR+/-) | 5 (FCR, aFRR+/-, mFRR+/-) |
| Ancillary energy prices | 0 (capacity-only) | 2 (aFRR + mFRR energy) | 2 (aFRR + mFRR energy) |
| **Total individual feeds** | **16** | **14** | **14** |

---

## 8. Ancillary Services Mapping (UK vs DE/NL)

| UK Product | DE/NL Equivalent | Key Difference |
|-----------|-----------------|----------------|
| SFFR (Static Firm Frequency Response) | **No direct equivalent** | UK-specific product; closest is FCR but architecture differs |
| DC Low / DC High (Dynamic Containment) | **FCR** (Frequency Containment Reserve) | FCR is symmetric (one bid = both directions); DC is split into Low/High. FCR responds in 30s; DC in 1s |
| DM Low / DM High (Dynamic Modulation) | **aFRR** (automatic FRR) | aFRR activates within 5 min; separate positive/negative tenders. DE/NL pay both capacity AND energy; UK pays capacity only |
| DR Low / DR High (Dynamic Regulation) | **mFRR** (manual FRR) | mFRR activates within 15 min; separate positive/negative. Connected to MARI cross-border platform |
| Procured by NESO, EFA blocks | Procured via **Regelleistung.net** (DE) / **TenneT** (NL), 4-hour blocks | DE/NL: pay-as-bid for aFRR/mFRR; UK: mostly pay-as-cleared |

---

## 9. Full Cost Summary — All Three Markets

### Free Data Sources (sufficient for analytical dashboard)

| Market | Source | Data Provided | Cost |
|--------|--------|--------------|------|
| **UK** | Elexon BMRS | SSP, SBP, DA HH reference | FREE |
| **UK** | NESO Data Portal | Ancillary clearing prices (all 7 services) | FREE |
| **UK** | GridBeyond report | All wholesale + ancillary (bundled in aggregator fee) | FREE |
| **DE** | SMARD | DA prices, generation mix, wholesale data | FREE |
| **DE** | Netztransparenz.de | Imbalance price (reBAP) | FREE |
| **DE** | Regelleistung.net | FCR/aFRR/mFRR tender results | FREE |
| **DE** | ENTSO-E | Cross-border flows, load, generation | FREE |
| **NL** | TenneT API | Settlement prices, imbalance data, ancillary results | FREE |
| **NL** | ENTSO-E | DA prices, cross-border flows | FREE |

### Paid Subscriptions (for real-time / direct feeds)

| Subscription | Markets Covered | Annual Cost (approx.) |
|-------------|-----------------|----------------------|
| EPEX SPOT DE data package | Germany DA + Intraday | Quote required |
| EPEX SPOT NL data package | Netherlands DA + Intraday | Quote required |
| Nord Pool DE Day-Ahead | Germany DA prices | ~EUR 1,200/year |
| Nord Pool DE Intraday | Germany intraday trades | ~EUR 5,000/year |
| Nord Pool NL bundle (FR/NL/AT/BE) | Netherlands DA prices | ~EUR 1,700–3,300/year |
| Nord Pool Intraday (per market) | NL intraday trades | ~EUR 5,000/year |
| Modo Energy (benchmarking) | GB, DE, NL analytics | ~EUR 8,000–60,000/year |

### Cost Scenarios

| Scenario | UK Cost | DE Cost | NL Cost | Total |
|----------|---------|---------|---------|-------|
| **Minimum (free sources only)** | £0 | EUR 0 | EUR 0 | **£0 / EUR 0** |
| **Standard (with aggregator)** | £0 (GridBeyond) | Depends on aggregator | Depends on aggregator | Varies |
| **With direct market feeds** | ~£5,300 | ~EUR 6,200 | ~EUR 6,700–8,300 | ~£18,000–20,000 equiv. |
| **Full (feeds + benchmarking)** | ~£20,000 | ~EUR 14,000–66,000 | ~EUR 14,000–68,000 | ~£40,000–150,000 equiv. |

---

## 10. Dashboard Implementation Notes

### Data Model Changes Required
1. **Settlement period:** Must support both 30-min (UK) and 15-min (DE/NL) — 48 vs 96 periods/day
2. **Currency:** GBP for UK, EUR for DE/NL — dashboard needs multi-currency support or conversion
3. **Ancillary module redesign:** UK's 7 frequency response products (SFFR/DC/DM/DR) do not map 1:1 to DE/NL's 5 products (FCR/aFRR/mFRR). The aFRR/mFRR energy activation payment is a concept that does not exist in the UK model
4. **Imbalance module:** UK dual pricing (SSP/SBP) vs DE single pricing (reBAP) vs NL hybrid — different logic per market
5. **Intraday auctions:** UK has 1 IDA; DE/NL have 3 IDAs each

### New Data Fields for DE/NL (not in current UK dashboard)
- aFRR energy activation price (EUR/MWh)
- mFRR energy activation price (EUR/MWh)
- Balance delta / system imbalance direction (for NL passive balancing)
- Cross-border flow data (significant price driver for NL due to high interconnection)
- Grid fees / network charges (significant cost line in NL; less impactful in UK/DE)

### API Integration Priority
1. **SMARD** (DE) — REST API, no auth, well-documented, Python library available
2. **TenneT API** (NL) — REST API, token auth, good documentation
3. **ENTSO-E** (both) — REST API, email for token, covers both markets
4. **Regelleistung.net** (DE) — web data centre, free, no auth
5. **EPEX SPOT** (both) — paid, for real-time feeds only
