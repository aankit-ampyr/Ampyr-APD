# Tinte (NL Solar) — Data Collection Request

**Asset:** Ampyr Tinte — 9.8 MW AC / 12.6 MWp DC solar PV, Netherlands.
**Goal:** populate all 35 KPIs on the Tinte performance dashboard. We currently have only the *technical* feed (SCADA + monthly technical report); the items below are what's needed to add the financial, market, contract and cost KPIs.

**Already in hand (no action):** SCADA/PPC + grid meter (generation, irradiance, power, setpoint, string DC) and the monthly Technical Performance Report (budget vs actual generation/irradiation, loss waterfall, string health).

> Note: there is **no Modo benchmark for NL solar** — for market/capture KPIs we need EPEX/ENTSO-E NL day-ahead prices + a merchant curve (Aurora/Baringa), not Modo.

## 1. Commercial / Offtake & Route-to-Market

### Signed PPA / offtake agreement  _(enables ~17 KPIs)_
- Contracted volume profile and % of generation under contract
- PPA price (EUR/MWh) + indexation / escalation
- Tenor (start–end dates)
- Nomination / settlement & curtailment terms

### Revenue & settlement statements  _(enables ~8 KPIs)_
- Monthly settled volume (MWh) and price by channel (PPA / merchant / imbalance)
- GvO and SDE++ revenue lines
- Route-to-market / trading fee (%)
- Any curtailment compensation

### GvO certificates (CertiQ / Vertogas)  _(enables ~13 KPIs)_
- GvO volume issued (MWh)
- GvO sale price (EUR/GvO) and counterparty

### SDE++ subsidy award & RVO correction prices  _(enables ~6 KPIs)_
- SDE++ award: base price, correction-amount, tenor, annual cap (kWh)
- RVO correction-price publications
- Subsidy amount received per period

## 2. Investment / Asset Management

### P50 yield / energy-assessment + degradation report  _(enables ~7 KPIs)_
- P50 / P90 annual + monthly energy yield (MWh) and specific yield (kWh/kWp)
- Module degradation rate (%/yr) and manufacturer warranty curve
- Assumed availability / soiling losses

### Project-finance model / annual budget  _(enables ~15 KPIs)_
- Monthly budget: revenue, EBITDA, generation (MWh) and price
- CapEx breakdown and capitalised costs
- Lifetime distributable cash flows + equity contributions (timing/amount)
- Discount rate / WACC, inflation/CPI assumptions

### Asset-mgmt agreement, insurance, land lease  _(enables ~1 KPIs)_
- Asset-management fee
- Insurance premium + cover schedule
- Land lease / grondrent amount and indexation

## 3. Finance / Accounting / Treasury

### Senior facility agreement & debt schedule  _(enables ~5 KPIs)_
- Senior debt amount + amortisation schedule
- Interest rate + hedge coverage (%)
- DSCR / LLCR / PLCR covenant definitions + thresholds
- DSRA requirement, gearing

### Shareholder loan agreement  _(enables ~3 KPIs)_
- SHL principal
- Interest rate / accrual
- Repayment terms

### Management accounts / statutory P&L  _(enables ~15 KPIs)_
- Monthly P&L: revenue, all OpEx lines, EBITDA, D&A, interest, PAT
- Trial balance / management accounts

### Fixed-asset register & depreciation policy  _(enables ~1 KPIs)_
- Gross asset cost (CapEx)
- Book depreciation schedule + accumulated depreciation (→ NBV)
- Any impairments / revaluations

### Dutch corporate-tax computation  _(enables ~1 KPIs)_
- CIT computation (25.8%, lower bracket)
- EIA / fiscal depreciation, NOL (loss) pool
- Interest-deduction (earnings-stripping) limitation

### Network / DSO & energy-tax invoices  _(enables ~3 KPIs)_
- DSO grid-connection + transport tariffs
- ODE / energy tax
- Metering & balancing-service fees

### Counterparty credit & receivables ledger  _(enables ~2 KPIs)_
- Aged-receivables / DSO ledger
- Offtaker credit rating
- Revenue concentration by counterparty

### Treasury: bank statements & reserve accounts  _(enables ~5 KPIs)_
- SPV bank balances
- DSRA / reserve-account funding status
- Distributions paid to equity (FCFE)

## 4. O&M Contractor / Engineering

### O&M contract & CMMS work-order log  _(enables ~7 KPIs)_
- O&M fixed + variable (availability-linked) fee
- Availability guarantee + liquidated-damage deductions
- Work-order log: fault start/end times (→ MTTR)
- Spares / planned-maintenance schedule

## 5. Market Data (external vendor / TSO)

### EPEX / ENTSO-E NL day-ahead price  _(enables ~12 KPIs)_
- Hourly EPEX NL day-ahead price (EUR/MWh)
- Intraday price (if traded)

### TenneT imbalance settlement  _(enables ~2 KPIs)_
- Imbalance volumes per ISP
- TenneT imbalance settlement prices (EUR/MWh)

### Merchant price curve (Aurora / Baringa)  _(enables ~3 KPIs)_
- Long-run NL merchant power-price forward curve (EUR/MWh)
- Capture-rate assumptions for solar
