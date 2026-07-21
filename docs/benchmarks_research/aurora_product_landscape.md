# Aurora Energy Research — Product Landscape & Token Access Map

**Investigation scope**: Map Aurora Energy Research's full product line, distinguish each from the others, identify how subscription tiers and API access work, and pinpoint where the **GB Battery Index** sits (free article vs subscription vs API endpoint). Sibling doc `aurora_sdk_use_cases.md` already covers the Origin Python SDK in depth — this doc fills in everything *around* it: Chronos, Flexplorer, Lumus, Amun, EOS, and the GB Battery Index specifically.

**Disambiguation up front**: this is **Aurora Energy Research** (auroraer.com, Oxford-based energy market analytics, founded by Dieter Helm and team, ~1,000 institutional clients) — NOT Aurora Solar (aurorasolar.com, US-based solar design SaaS) and NOT Aurora Solar API at docs.aurorasolar.com. All four returned hits in early searches; all four are different companies.

**Sources fetched**:
- auroraer.com product pages: `/eos`, `/software`, `/software/chronos`, `/software/lumus`, `/products/flexible-energy-service`, `/products/power-renewables-service`, `/who-are-you/developers`, `/analytics/gb-distributed-flexible-energy/`
- GitHub: `github.com/AuroraEnergyResearch` (org), `aurora-origin-python-sdk`, `aurora-amun-python-sdk`
- Live SDK docs: `ghp.auroraer.com/aurora-origin-python-sdk/docs/intro/` and `/common-patterns/`
- Press: Aurora press room (Chronos launch, Flexplorer global launch), solarpowerportal.co.uk, energy-storage.news, pv-magazine.com
- Careers: `careers.auroraer.com/postings/...` Platform Software Engineer posting (confirms sub-team structure)
- GB Battery Index article: `auroraer.com/resources/aurora-insights/articles/introducing-auroras-gb-battery-index` (published 11 Dec 2025 per Google index; body truncated in WebFetch and not publicly cached)
- Battery Benchmark report: `auroraer.com/resources/aurora-insights/market-reports/bridging-the-gap-between-revenue-indices-and-forecasts`

---

## 1. The five software products (one EOS portal)

Aurora's careers page (Platform Software Engineer, Oxford) confirms the **internal product structure** — each of the following is a separate sub-team in their Software Development org, sharing a TypeScript/AWS-Lambda micro-services backend and React micro-frontends:

| Product | Asset focus | Sub-team confirmed in careers? | API surface |
|---|---|---|---|
| **Origin** | Power market scenarios (long-term) | Yes | **Python SDK** + REST + GraphQL underneath |
| **EOS** | Portal / hub | Yes | Token issuer (`eos.auroraer.com/dragonfly/settings`) |
| **Chronos** | BESS dispatch / valuation | Yes | API mentioned in product marketing — **no public SDK on GitHub** |
| **Amun** | Wind project valuation | Yes (implied via SDK existence) | **Python SDK** on GitHub |
| **PPA+ / Lumus** | PPA valuation | Yes (listed as "PPA+" in careers) | Not documented publicly |

The careers post phrasing — "smaller sub-teams of Software Engineers who develop different parts of their software suite: **Origin, EOS, Chronos, PPA+, and Amun**" — is the single best confirmation that these are **architecturally distinct products** that happen to share an identity/token layer (EOS) and an underlying micro-services stack. **Flexplorer** is newer (2026) and is described as integrated *into* EOS rather than as its own sub-team — likely owned by the Chronos team since it surfaces Chronos-engine backcasts.

### EOS = the portal, not a product

EOS is "the central hub for all of Aurora's software and research subscription services." It is the **single sign-on point** and the **token-management UI**. The Amun SDK README explicitly says tokens are created in EOS settings (`https://eos.auroraer.com/dragonfly/settings`) and stored as `AURORA_API_KEY` — and the Origin SDK uses the identically-named env var. So **one EOS token, multiple product APIs** is structurally true; what each token can *do* is gated by the subscriptions tied to that account.

---

## 2. Product-by-product detail

### 2.1 Origin — power market scenarios

- **Purpose**: scenario-based long-term power market modelling. Run Aurora's published "central case" forecasts, or build custom scenarios overriding demand / commodity prices / technology assumptions / interconnectors, then download CSV outputs (annual / monthly / hourly).
- **Geographies (confirmed)**: GBR (Great Britain), AUS (Australia), ERC (ERCOT/Texas), DEU (Germany), PEU groupings (Pan-European), plus a `SimulationMode.EUROPEAN_NETWORK` option. Regions are discovered dynamically — no hard-coded enum.
- **Time horizon**: long, decadal — scenarios carry an explicit `years: List[int]` list (e.g. 2025, 2030, 2040, 2050) and Aurora's standard outlook runs to 2050/2060.
- **BESS coverage**: indirect. SDK has **zero explicit `battery` / `BESS` / `storage` / `GB Battery Index` / `TB spread` / `capture rate` references**. Battery data, if present, lives inside `technology`-type CSV downloads — would need a live API call to confirm.
- **API access**: **Public Python SDK** on GitHub (`aurora-origin-python-sdk`). Token via `AURORA_API_KEY`. Methods: `get_projects`, `get_aurora_scenarios(region=)`, `get_scenario_by_id`, `get_scenario_data_csv`, plus mutations to create projects/scenarios.
- **Subscription**: Origin access is bundled into the "Power & Renewables Service" subscription tier (and other tiers that include Origin). MPA Solar Europe members reportedly get free access (per project memory).

### 2.2 Chronos — BESS dispatch & valuation

- **Purpose**: bankable battery valuations via dispatch optimisation. Site-scanning across multiple sites/locations, portfolio valuation, customisable revenue stacking, degradation analysis.
- **Geographies (confirmed)**: Great Britain, Germany, Netherlands, Belgium, Italy, **Iberia (Spain/Portugal — launched 2026)**, **Australia (launched 2025)**, **US & Canada (July 2025 expansion — CAISO and others)**. Press releases also cite a launch in Japan.
- **Time horizon**: handles both backcasting (historical revenues) and forward valuations. Drives the Aurora battery benchmarks.
- **BESS coverage**: **this IS Aurora's BESS product.** Models storage performance, revenues, degradation, across wholesale + balancing + ancillary markets. Standard benchmark assumption is **2-hour BESS** (confirmed for Germany benchmark and used across the European country benchmarks).
- **API access**: marketing pages explicitly mention "Its API allows for efficient hypothesis testing, fast result validation, and a strong bridge to Origin-based scenario work." However, **no public SDK exists on GitHub for Chronos** (only Origin and Amun have SDKs). The API surface is therefore **either a private/customer-only REST API gated by the EOS token, or accessed via the Chronos web UI inside EOS.** A single Origin-style token *may* unlock Chronos API calls if the underlying subscription includes Chronos — but this is not verifiable without testing the token.
- **Subscription**: Chronos sits inside the **Flexible Energy Service** subscription (the same subscription that bundles Flexplorer). Press release evidence: Aurora announced Flexplorer "available through Aurora's Flexible Energy Service subscription" — Flexplorer is "powered by Chronos engine," so the two are co-licensed.
- **Clients**: 200+ industry leaders trust Chronos for battery transactions and financing. Public names include Sonnedix, Aquila Capital, Centrica, Octopus Energy.

### 2.3 Flexplorer — battery intelligence hub (NEW, launched 2026)

- **Purpose**: an all-in-one battery intelligence hub *inside EOS* that lets users (i) backcast what an asset could have earned, (ii) compare actual asset performance vs similar assets and Aurora benchmarks, (iii) analyse future battery investments.
- **Launch sequence**: GB / Europe first half of 2026 (the March 2026 GB BESS revenue spike was first reported via Flexplorer). Global launch announced via Aurora's Australia LinkedIn channel for the NEM. Italian / Iberian / German rollouts confirmed.
- **Engine**: Flexplorer is **powered by Chronos** — same dispatch simulator under the hood.
- **GB Battery Index relationship**: Flexplorer is **the surface through which Aurora exposes the GB Battery Index** and similar national benchmarks (Germany, France, Italy, Iberia, Australia). The benchmarks themselves are the Chronos-simulated 2h BESS revenue series for each market; Flexplorer is the UI that presents and compares them.
- **API access**: not mentioned in any public material — Flexplorer is described purely as a UI/hub. No reference to a Flexplorer-specific SDK or REST endpoint. Whatever data backs it almost certainly is **accessible internally via the Chronos API** (which is itself not publicly documented).
- **Subscription**: **Flexible Energy Service** (same as Chronos).

### 2.4 Lumus — PPA valuation (formerly "PPA+" in careers post)

- **Purpose**: quantify, configure, and structure PPA contracts using market-aligned pricing and Aurora's long-term forecasts. Granular breakdown of price components, contract structuring from origination through financial close.
- **Geographies**: 15+ markets across EMEA (24 countries including Germany, France, UK, Nordics, Iberia, Poland), APAC (Australia, India, Japan, Korea, Singapore, Malaysia, Philippines), Americas (US/Canada/Mexico/Brazil/Chile).
- **BESS coverage**: not BESS-specific (PPA = power purchase agreement, generally for solar/wind generation).
- **API access**: not publicly documented. Accessed through the EOS Platform UI.
- **Launch**: rolled out in Europe in May 2025 per pv-magazine.

### 2.5 Amun — wind project valuation

- **Purpose**: wind site-specific revenue forecasting, turbine choice optimisation, curtailment assessment using geospatial wind modelling.
- **API access**: **Public Python SDK** on GitHub (`aurora-amun-python-sdk`). Token via `AURORA_API_KEY`, same EOS-issued token. Example call: `session.get_turbines()`.
- **BESS coverage**: none — wind only.

### 2.6 Nodal Explorer

- **Purpose**: grid analysis and asset siting via nodal-pricing visualisation. Listed on Aurora's `/software` page alongside the others.
- **API access**: not publicly documented; presumably accessed via EOS UI.
- **BESS coverage**: indirect — node-level pricing matters for BESS arbitrage but Nodal Explorer itself is about siting decisions, not BESS revenue.

---

## 3. The GB Battery Index — what it is and how to get it

This is the central question of the investigation. Best evidence assembled below:

### 3.1 What it is

- **Named product**: "Aurora's GB Battery Index" — introduced via an Aurora Insights article (`auroraer.com/resources/aurora-insights/articles/introducing-auroras-gb-battery-index`) published **11 December 2025** (date from Google's index of the article).
- **What it tracks**: historical revenues for a **standardised 2-hour BESS** in Great Britain, decomposed across the revenue stack (Wholesale, Balancing Mechanism, Capacity Market, Ancillary Services, Embedded Benefits) — this is consistent with how Aurora's German Battery Benchmark and other national equivalents work, and consistent with the methodology Aurora explicitly cites: "Aurora uses Chronos to simulate the optimised dispatch behaviour based on historical prices for wholesale and balancing markets."
- **Methodology family**: **theoretical optimiser, not empirical fleet**. Aurora explicitly contrasts its approach to Modo's: where Modo measures revenues from the actual operating GB fleet, Aurora simulates the revenues a **perfectly-optimised representative asset** would have earned given historical prices, using Chronos. This is critical for benchmarking — Aurora is a "what a great trader would have earned" benchmark, Modo is "what the fleet actually earned." They are complementary and answer different questions.

### 3.2 Where it lives — three channels

The GB Battery Index is published through **three overlapping channels**:

1. **Aurora Insights articles** (auroraer.com — free, public). The December 2025 launch article is on the public site. Aurora has also published similar free articles for the France Battery Benchmark and reports comparing Germany. These are typically **summary articles with charts**, not raw data downloads, and they are released **periodically** rather than monthly — judging by sibling Battery Benchmark articles which appear quarterly. Solarpowerportal.co.uk's April 2026 piece reporting "+126% February-to-March 2026 GB BESS revenue growth" appears to be based on a free Aurora data point released via Flexplorer's launch coverage, not a paid product.
2. **Flexplorer hub inside EOS** (subscription, Flexible Energy Service). Flexplorer is the **interactive surface** for the GB Battery Index — gives subscribers the ability to drill down month-by-month, compare against their own asset, backcast hypothetical configurations, and view the full revenue-stack decomposition. This is the "paid version" of the same index.
3. **LinkedIn posts from Aurora analysts** (free). Aurora's analysts (e.g. Sophie Martin, Philipp Hesel) post monthly Battery Benchmark snapshots on LinkedIn — these are free secondary research with summary numbers (e.g. "Aurora's Battery Benchmark in June," "Battery Benchmark in Q4 2025"). These postings carry headline figures suitable for benchmarking but not raw data.

### 3.3 Is there a public API endpoint specifically for the GB Battery Index?

**Almost certainly no public API endpoint.** Evidence:

- The **Origin Python SDK contains zero references** to GB Battery Index, BESS, battery, storage, TB spread, or capture rate. It is a generic scenario-fetch client and the GB Battery Index is not in its scope.
- **Chronos has an API** per marketing copy, but **no public SDK or documentation** exists on GitHub or elsewhere — its API is described as an internal/customer integration for "efficient hypothesis testing," not as a benchmark-data feed.
- **Flexplorer** is described purely as a UI hub. No API, no SDK, no programmatic access path mentioned in any public source.

So the index value is **either**: (a) read from the Aurora Insights article (the manual / canonical public path), (b) viewed/exported from Flexplorer inside EOS (subscription, manual export), or (c) pulled via the Chronos API (subscription + technical integration, likely white-glove).

A user **with an Aurora token that happens to come from an Origin/MPA subscription** would have access to:
- Aurora Insights articles (these are public anyway, no token needed)
- The Origin SDK (long-term scenarios — useful but **not** the GB Battery Index)

And would **not** have access to:
- Flexplorer (requires Flexible Energy Service)
- Chronos API (requires Flexible Energy Service)
- Raw GB Battery Index data feed (doesn't exist as a public endpoint)

### 3.4 Confirmed Aurora battery benchmark family

For context, the GB Battery Index is one of a growing family:

| Country | Index name | Methodology | Status |
|---|---|---|---|
| Great Britain | Aurora's GB Battery Index | Chronos sim, 2h BESS | Launched Dec 2025 |
| Germany | Aurora's Battery Benchmark (Germany) | Chronos sim, 2h BESS | Live (2025) |
| France | France Battery Benchmark | Chronos sim | Launched 2025 |
| Iberia | Aurora's Iberia Battery Benchmark | Chronos sim, 2h BESS | Live |
| Italy | Aurora's Italy Battery Benchmark | Chronos sim, 2h BESS | Live |
| Australia (NEM) | NEM Weekly Battery Benchmark | Chronos sim | Weekly, since Wk 49 2025 |

All use the same Chronos engine and 2h standardised asset — making cross-country comparison clean within the Aurora world.

---

## 4. Token-access map — what a single AURORA_API_KEY unlocks

This is the structural answer to "what can this one token do?"

**Single point of issuance**: all Aurora API tokens come from EOS (`eos.auroraer.com/dragonfly/settings`). Both Origin SDK and Amun SDK use the identically-named `AURORA_API_KEY` env var, confirming **one token, many possible products**.

**Capability is gated by subscription**: the token itself is just bearer credentials. What it can authenticate against depends on which subscriptions are attached to the EOS account that minted it:

| Subscription | Token unlocks |
|---|---|
| **Power & Renewables Service** | Origin SDK (scenario downloads for subscribed regions) |
| **Flexible Energy Service** | Chronos API + Flexplorer (+ GB Battery Index data behind it) |
| **Grid Service** | Nodal Explorer (presumed) |
| **Hydrogen Service** | Hydrogen-specific tools (presumed) |
| **MPA Solar Europe membership** | Free tier — Aurora published scenarios via Origin SDK (per Ampyr memory) |

**Practical implication for Ampyr**: an Aurora token sourced via the MPA Solar Europe free route will almost certainly only unlock the **Origin SDK with published scenarios** (the `AURORA_SCENARIO` type, not tenanted custom runs). It will **not** unlock Chronos, Flexplorer, or the underlying GB Battery Index data feed — those require a paid Flexible Energy Service subscription.

For BESS revenue benchmarking specifically (the APD use case), the MPA Aurora token is therefore valuable for **long-term price scenarios** (TB spreads in 2030, capture prices in 2040, etc.) but **not for the GB Battery Index data series**. To get the index series, the options are:

1. Read the index headline values from Aurora Insights articles (public, manual)
2. Subscribe to Flexible Energy Service (paid, gives Flexplorer + Chronos API)
3. Negotiate a one-off data licence with Aurora's commercial team

---

## 5. Summary — direct answers to the brief's questions

| Question | Answer |
|---|---|
| What products exist? | Origin, EOS (portal), Chronos, Flexplorer, Lumus, Amun, Nodal Explorer |
| How do API access tiers work? | Single token issued by EOS; what it unlocks is gated by the subscriptions on the account |
| What does a single token likely unlock? | Whatever sub-products are included in the subscription tied to that EOS account. For an MPA-Solar-Europe-free-tier token: Origin SDK with published Aurora scenarios. **Probably not Chronos / Flexplorer / GB Battery Index data.** |
| Does the GB Battery Index have its own API? | **No public API.** Index headline values are released via free Aurora Insights articles. The interactive series + decomposition is inside Flexplorer (Flexible Energy Service subscription). Chronos has an API but no public docs and is not described as serving the index as a data feed. |
| Methodology of GB Battery Index? | **Theoretical optimiser via Chronos**, simulating a perfectly-optimised 2h BESS against historical wholesale + balancing prices. Contrasts with Modo's empirical-fleet approach. |
| Public number? | Yes, headline values released via Aurora Insights articles and Aurora analyst LinkedIn posts. Raw series is paid. |

---

## 6. Implications for APD's benchmark stack

1. **Aurora GB Battery Index is a Chronos-optimiser benchmark** — analogous to Modo's ME-BESS-GB but with a theoretical-perfect-foresight methodology rather than empirical-fleet. Both have value; including both gives the dashboard a "what a great trader earned" line (Aurora) alongside a "what the GB fleet actually earned" line (Modo). The +126% Feb-to-Mar 2026 spike Aurora cited gives a credible cross-check against Modo's same-period numbers.
2. **No realistic path to a Chronos / Flexplorer API integration without paying for Flexible Energy Service.** The Origin Python SDK reachable through the MPA free tier is the wrong product for BESS revenue benchmarking — its strength is long-term scenarios.
3. **Manual ingestion of GB Battery Index values** (from Aurora Insights articles + LinkedIn snapshots, similar to how Modo's free articles are scraped today) is the **realistic V1 plan**. Treat Aurora as a quarterly headline-value benchmark, not a real-time API feed.
4. **For longer-term BESS forecast work** (e.g. 2030+ TB spreads to support PSP sizing and PFA financial modelling), the Origin SDK + free MPA tier is genuinely useful and should be wired up — but that is a different use case than the current APD historical benchmarking goal.
5. **Watch for Aurora extending the SDK** to cover Chronos. The org's GitHub has only Origin + Amun SDKs today; a future `aurora-chronos-python-sdk` (which would change the procurement calculus completely) is plausible but not announced.

---

## 7. Open questions worth confirming if commercial conversation continues

- Does the MPA Solar Europe free tier include any Chronos / Flexplorer / GB Battery Index access, or is it strictly Origin-scenarios? (Best evidence says strictly Origin.)
- What does Flexible Energy Service cost annually, and is there a battery-only sub-tier?
- Is there a future plan to expose GB Battery Index as a public API? (Worth asking Aurora's commercial team directly — they may release this if there's enough institutional demand.)
- For the **current Northwold benchmark stack**: the Aurora GB Battery Index, if obtainable manually via the Insights articles, would be a strong addition alongside Modo and ME-BESS-GB. Worth tracking the Aurora article cadence over 2-3 months to see how publication frequency works in practice.

