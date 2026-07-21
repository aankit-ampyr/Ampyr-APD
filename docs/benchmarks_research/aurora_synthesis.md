# Aurora Energy Research — Synthesis for APD Benchmark Stack

**Date:** 2026-06-01
**Token tested:** Aurora Origin production token (EOS-issued)
**Question:** Does this token unlock anything genuinely useful for Northwold BESS benchmarking, beyond what Modo ME-BESS-GB already provides?

**Headline:** **Skip Aurora for V1.** This specific token is recognised but entitled to nothing. Even if entitlements were unblocked via the Cyrus / MPA Solar Europe route, the only product likely to come with the free tier is Origin — a forward-looking decadal scenario platform — which does NOT solve APD's need for historical battery revenue benchmarks. The product that would actually help (Chronos / GB Battery Index / Flexplorer) is a paid subscription, not exposed via any public SDK, and its headline values are already available for free as manual extracts from Aurora Insights articles.

---

## 1. What this token actually unlocks (right now)

**Nothing.** Concretely:

| Endpoint | Token state | Result |
|---|---|---|
| `api.auroraer.com/scenarioExplr/v1/graphql` (Origin prod) | Recognised | HTTP 403, `errorCode:1002 "Access Denied"` on every read query incl. `{ __typename }` |
| `api.auroraer.com/modelInputs/v1/graphql` (Origin prod) | Recognised | HTTP 403, same error |
| `api-staging.auroraer.com/*` | Not recognised | HTTP 401 "Unauthorized" |

The application-level `errorCode:1002` (vs gateway-level bare `"Forbidden"`) is diagnostic: Aurora's auth layer parsed the token, identified the principal, and refused it. Per the SDK's own error handler, this is the documented signal for *"token valid, principal has zero permissions."* Likely cancelled / expired / wrong product line / issued without Origin provisioning.

This matches the worktree note:
> *"Aurora benchmark: free with MPA Solar Europe email (Cyrus to provision)"*

Entitlement needs to come via that route. No amount of additional probing will change this.

---

## 2. What Origin WOULD unlock if entitled (post-provisioning)

If/when Cyrus successfully provisions the MPA Solar Europe free tier, the token would activate the **Origin** product surface — and only Origin. This is what that looks like:

### Architecture
- **Origin = forward-looking scenario engine.** Decadal market-model runs (typically 2025/2030/2040/2050 horizons) over GB (`gbr`), Germany (`deu`), Pan-European Germany (`peu_deu`), Australia (`aus`), ERCOT (`erc`), etc.
- **One generic data method**: `Scenario.get_scenario_data_csv(region, download_type, granularity, year, currency, node, sub_type)` returning two-header-row CSV.
- **Documented download_types**: `system`, `technology`, `interconnector`, `nodal`.
- **Documented granularities**: `1y`, `1m`, `1h`.
- **Canonical pattern**: `get_aurora_scenarios(region='gbr')` → filter name contains "central" → sort by `publicationDate` desc → grab latest → download by region/type/granularity.

### What's NOT in the SDK source
**Zero source-code mentions** across the entire SDK of: `battery`, `BESS`, `storage`, `TB`, `spread`, `capture`, `ancillary`, `balancing`, `BMU`, `day-ahead`, `intraday`.

The only "historic" reference is an internal-only `AdvancedScenarioSettings.isHistoricRun` flag — explicitly marked internal, not user-facing.

### Implication
If GB-battery-relevant outputs exist in Origin at all, they would be encoded as opaque `download_type` / `sub_type` strings inside the per-scenario `dataDefinitions` manifest — discoverable only by calling `Scenario.get_download_types('gbr')` against an entitled GB scenario. The SDK gives no static guarantee they exist.

---

## 3. What the Origin token does NOT unlock (the products we'd actually want)

Aurora operates a **single-token-many-products** model. One `AURORA_API_KEY` from EOS, but each product is gated by a separate subscription tier.

| Product | What it gives | API/SDK? | Subscription | Relevance to APD |
|---|---|---|---|---|
| **Origin** | Decadal forecast scenarios | Public Python SDK | Power & Renewables (or free MPA tier) | Low — wrong direction (forecast vs historical) |
| **Chronos** | BESS dispatch/valuation engine (2h, GB+DE+NL+BE+IT+Iberia+AUS+CAISO+JP) | Marketed as having an API, **no public SDK** | Flexible Energy Service (paid) | **High — but inaccessible** |
| **Flexplorer** | EOS-internal UI hub showing GB Battery Index + national equivalents, backcasting, asset comparison | **UI only, no API** | Flexible Energy Service (paid) | **High — but UI-only, paid** |
| **GB Battery Index** | Theoretical-optimiser 2h BESS revenue series (perfect-foresight via Chronos) | **No API endpoint**, headlines free via Insights articles | Free article / paid for interactive | Useful, but only via manual article scraping |
| **Lumus** (PPA valuation) | PPA contract structuring | UI only | Separate | Not BESS-relevant |
| **Amun** (wind valuation) | Wind project valuation | Public SDK | Separate | Not BESS-relevant |
| **Nodal Explorer** | Nodal pricing for siting | Not API-documented | Grid Service | Tangential |

### The critical gap
**The data APD would actually want from Aurora — the GB Battery Index — is not an API product.** It is published as:
1. Free headline numbers inside Aurora Insights articles (same channel as Modo Energy's free articles).
2. Free analyst commentary on LinkedIn.
3. Interactive series + decomposition inside Flexplorer (paid Flexible Energy Service subscription, UI-only).

There is no public API endpoint for the GB Battery Index. Even with a fully-entitled Origin token, you would not get it via the SDK.

---

## 4. Does Aurora add anything Modo doesn't already give APD?

APD's current Modo stack:
- Headline + 1H + 2H monthly £/MW/yr (Sep 25 → Mar 26)
- 13 GB regional cuts with P10/P50/P90
- TB1–TB4 GB DA/ID theoretical ceilings
- In-house LP optimiser as Northwold-specific theoretical ceiling

### Honest assessment

| Comparison axis | Modo ME-BESS-GB | Aurora GB Battery Index | Aurora Origin (if entitled) |
|---|---|---|---|
| **Methodology** | Empirical — actual GB fleet revenues | Theoretical — perfect-foresight 2h optimiser | Forecast scenario — decadal price curves |
| **Time direction** | Historical actuals | Historical reconstruction | Forward-looking (2030/2040/2050) |
| **Duration granularity** | Headline + 1H + 2H | 2h standardised only | Generally not battery-specific |
| **Geographic granularity** | 13 GB regional cuts + national | National GB | National GB + nodal |
| **Distribution shape** | P10/P50/P90 percentiles | Single theoretical value | Single scenario value |
| **Northwold fit** | Strong (1.4h, asymmetric — closest to Modo 1H slice) | Approximate (2h standardised — Northwold-shorter caveat needed) | Poor (not asset-level historical) |
| **Already in APD?** | Yes, deeply integrated | No | No |

### Where Aurora COULD add value
- **GB Battery Index as a third theoretical benchmark.** APD already has its own LP optimiser (Northwold-specific) and Modo's TB1–TB4 (GB DA/ID generic). Aurora's index would be a *fourth* theoretical line: 2h perfect-foresight via Chronos. Methodology disclosure — Aurora's theoretical-2h-fleet vs Modo's empirical-fleet vs Ampyr's Northwold-specific-LP — would be transparency win.
- **Cross-validation against Modo headline.** Two independent methodologies on the same period would either reinforce trust (correlated) or surface measurement risk (divergent — e.g. Aurora reportedly captured the +126% Feb–Mar 2026 GB BESS revenue spike).

### Where Aurora does NOT add value
- **Origin forecasts**, even if entitled, do not benchmark Northwold's *historical* revenue against peers. That is the wrong direction. Origin is a PSP/PFA-shaped tool, not an APD-shaped tool.
- **Regional granularity**: Modo's 13 GB cuts already exceed what Aurora's national index provides.
- **Duration match**: Modo's 1H slice is closer to Northwold's ~1.4h than Aurora's standardised 2h.

---

## 5. Accessible vs irrelevant vs relevant-but-inaccessible

Mapping cleanly along the matrix the task asked for:

### Accessible AND relevant (with this token, today)
**None.** Token is entitled to nothing.

### Accessible but irrelevant (post-Cyrus provisioning, free MPA tier)
- **Origin GB long-term forecast scenarios** — useful for PSP investment sizing or PFA project-level price assumptions, but wrong tool for APD benchmark comparison.
- **Origin Germany / Netherlands scenarios** — useful for the co-located projects coming live (Germany Aug 2026, Netherlands Sep–Oct 2026) — but again, this is PSP/PFA territory, not APD.
- **Origin's project/scenario CRUD + custom-scenario authoring** — irrelevant for benchmarking.

### Relevant but inaccessible (paid subscription required)
- **GB Battery Index via API** — there is no API. Even paying for Flexible Energy Service unlocks Flexplorer UI, not an API.
- **Chronos BESS dispatch engine** — marketed as having an API, no public SDK, paid Flexible Energy Service subscription.
- **National Battery Indices for DE / NL** (when those projects go live) — same channel as GB Battery Index.

### Relevant AND accessible via OTHER channel (the realistic V1 path)
- **GB Battery Index headline values from Aurora Insights articles** — published for free, manually extractable as monthly £/MW/yr headlines. Same ingestion pattern as Modo's free articles. This is the realistic Aurora integration for APD.

---

## 6. Recommendation: **Skip Aurora API integration for V1. Build manual article-extract pipeline instead.**

### Decision: SKIP the Aurora API

Reasoning:
1. **Token is dead** until Cyrus completes MPA provisioning. Unknown ETA.
2. **Even when alive**, the entitled product (Origin) is wrong-direction for APD (forecast vs historical).
3. **Right product (Chronos / GB Battery Index)** has no public API at any subscription tier — it's UI-only inside Flexplorer.
4. **Engineering effort** to build SDK integration → discover what's accessible → realise it's wrong → unwind, is not justified vs the easier alternative below.

### Build: Manual GB Battery Index article-extract pipeline

This is the realistic V1 Aurora integration:

| Step | Detail |
|---|---|
| **Source** | Aurora Insights articles (publicly free) — same model as Modo's free articles, which APD already ingests. |
| **Cadence** | Monthly (aligned with Modo cadence and Northwold reporting). |
| **What to extract** | GB Battery Index headline £/MW/yr per month, methodology footnotes (perfect-foresight, 2h standardised), any decomposition Aurora publishes in the article body. |
| **Storage** | `data/aurora_gb_battery_index.parquet`, columns matching the existing `data/modo_*` pattern. |
| **Display** | Add as a third theoretical line on the Benchmark Comparison page — alongside Modo TB1–TB4 and Ampyr's in-house LP. Label methodology clearly (Aurora 2h theoretical vs Modo TB DA/ID vs Ampyr Northwold-specific). |
| **Caveat to display** | Aurora is 2h standardised; Northwold is ~1.4h asymmetric. Same duration-mismatch caveat already documented for Modo. |
| **Effort** | Low — fits existing benchmark scraping/ingestion pattern in the worktree (already running scrapers for Aurora, Montel, GB Battery Index, Inspired, Enveris per CLAUDE.md). |

### Park for Later

If Cyrus eventually delivers a working Origin token via the MPA route:
- 30-minute spike: notebook calling `OriginSession().get_aurora_scenarios(region='gbr')` → for latest scenario, call `Scenario.get_download_types('gbr')` → log the full list to disk.
- If `battery` / `storage` / TB-spread-shaped `sub_type` strings appear, reassess.
- If not (most likely outcome based on SDK source absence), keep using the article-extract approach. Origin then becomes a PSP/PFA candidate, not an APD candidate.

### Do NOT pursue
- Paid Chronos / Flexible Energy Service subscription for V1 — not justified vs free article extraction.
- Building anything against the staging endpoint — independent token namespace, irrelevant.
- Building any speculative `download_type='battery'` calls — there is zero source evidence those exist.

---

## 7. One-line conclusion

The Aurora token in hand is recognised but entitled to nothing, and even fully-entitled Origin is the wrong product (forecast, not historical benchmark) — for APD V1, manually extract GB Battery Index headlines from Aurora's free Insights articles using the existing benchmark-scraping pattern, and park the Origin SDK as a PSP/PFA candidate for later if Cyrus's MPA-tier provisioning eventually lands.
