# Clean Horizon Storage Index — Scrape Feasibility Findings

**Researcher**: Claude (investigation only — no code modified)
**Date**: 2026-05-12
**Source**: https://www.cleanhorizon.com/battery-index/

---

## 1. Data Endpoint URL — Search Results

**No public JSON / CSV / AJAX endpoint is exposed by `cleanhorizon.com`.**

Checked the following:

| Probe | Result |
|---|---|
| Full HTML source of `/battery-index/` | No Plotly / Highcharts / D3 / Chart.js / iframe / `data-*` attributes referencing a data file. Page is server-rendered WordPress, no embedded chart payload. |
| WordPress REST API `/wp-json/` | Only stock WP routes (`/wp/v2/posts`, Yoast, Matomo, Akismet, MiniOrange 2FA, WP Statistics, oEmbed, batch). **No custom `/storage-index/` or `/battery/` namespace.** |
| Common paths probed via search / source: `/api/`, `/data/`, `.json`, `.csv` | None found referenced from the public page. |
| `platform.cleanhorizon.com` | Login wall (the interactive index lives here — requires free or paid account). |
| Nord Pool partner distribution (`data.nordpoolgroup.com/power-system/storage-index`) | Paid Market Data API only. Annual "Data Fee" subscription; no free tier. |

**Conclusion**: The interactive chart on `/battery-index/` appears to render on the `platform.cleanhorizon.com` side, behind authentication. The marketing page itself ships no data.

---

## 2. Data Format / How the Chart Loads

- Public marketing page is static WordPress HTML. The chart is **not on this page** — the page describes methodology and links to `platform.cleanhorizon.com/signin/` ("Access the Storage Index").
- The interactive viewer lives on the platform (login required). Free-tier account = monthly granularity; Premium = daily granularity + stack breakdown.
- Nord Pool's partner feed (launched 9 Mar 2026) is a paid Market Data API per bidding zone — daily revenue stack JSON, charged annually.

No client-side JavaScript exposes the underlying dataset. **The chart is not silently fetchable.**

---

## 3. Public €/MW/year Values Found (from monthly blog posts)

Each month Clean Horizon publishes a free news article summarising the latest Storage Index. These articles consistently quote a handful of countries with absolute values, and percentage moves for the rest. The pattern over recent months:

### March 2026 (published 20 Apr 2026)
Source: `cleanhorizon.com/news/storage-index-march-2026/`
2-hour BESS, annualised gross:

| Country | Value (k€/MW/yr) | MoM |
|---|---:|---:|
| Estonia (EE) | 303 | -45% |
| Italy (IT) | 270 | -17% |
| Latvia (LV) | 334 | -46% |
| Lithuania (LT) | 325 | -43% |
| Poland (PL) | ~500 | +34% |
| Romania (RO) | 386 | +19% |
| Belgium (BE) | (not absolute) | +60% |
| Germany (DE) | (not absolute) | "+70% for all durations" |
| France (FR) | (not absolute) | +7% MoM |
| Spain (ES) | (not absolute) | -17% |
| Portugal (PT) | (not absolute) | +72% avg |
| Sweden SE3 | (not absolute) | -27% |
| Finland (FI) | spreads halved to €120/MWh aFRR/mFRR, €46/MWh DA | — |

### February 2026 (published 17 Mar 2026)
Source: `cleanhorizon.com/news/storage-index-february/`
2-hour BESS, annualised:

| Country | Value (k€/MW/yr) | MoM |
|---|---:|---:|
| Estonia (EE) | 548 | +9% |
| Latvia (LV) | 615 | +15% |
| Lithuania (LT) | 575 | +10% |
| Poland (PL) | 370 (down from 605 Jan) | ~-39% |
| Belgium (BE) | (qualitative) | +5% avg |
| France (FR) | (qualitative) — DA spreads +23%, aFRR energy +40% | up |
| Germany (DE) | DA spread fell €90→€73/MWh | — |
| Portugal (PT) | (qualitative) | -35% avg |
| Romania (RO) | (qualitative) | -10% |
| Spain (ES) | (qualitative) | -17% avg |
| Denmark | (qualitative) | -13 to -15% |
| Sweden | FCR cap +30% | — |

### January 2026 (published 18 Feb 2026)
Source: `cleanhorizon.com/news/january-storage-index-is-out/`

| Country | Value (k€/MW/yr, 2h) | MoM |
|---|---:|---:|
| Estonia (EE) | 503 | +87% |
| Latvia (LV) | 533 | ~+100% (nearly doubled) |
| Lithuania (LT) | 519 | +57% |
| Belgium (BE) | (qualitative) | +20% / +50% for 2h / 4h |
| Germany (DE) | (qualitative) | -35% avg across durations |
| Spain (ES) | "more than doubled on average" | — |
| Sweden | 2h index | -27% |

### December 2025 (published 15 Jan 2026)
Source: `cleanhorizon.com/news/decembre-2025-storage-index-is-out/`

| Country | Value | Notes |
|---|---|---|
| Belgium (BE) | 80–100 k€/MW/yr (2h and 4h) | aFRR cap 2–6 €/MW/h |
| Estonia (EE) | -37% MoM | FCR cap €64→€15/MW/h |
| Latvia (LV) | -40% MoM | FCR cap €70→€14/MW/h |
| Lithuania (LT) | -32% MoM | FCR cap €70→€14/MW/h |
| Poland (PL) | DA spread hit €73/MWh (2025 low); 2025 avg ~€150/MWh | — |
| Spain (ES) | -29% avg all durations | — |
| Sweden | ~-50% drop | — |

### Pattern observation
- **Germany and France absolute values are NOT routinely published in the free monthly blog posts** — only percentage moves and underlying price components (DA spreads in €/MWh, aFRR/FCR in €/MW/h).
- Baltic states (EE, LV, LT) and a rotating subset (PL, IT, RO, BE, ES) get absolute figures.
- This is presumably a deliberate gate to drive sign-ups to the free platform account, where the chart shows all 14/15 countries.

### Methodology note (2026 break)
Starting Jan 2026, methodology changed: index now reflects the *average* MW of battery (weighted by installed capacity and actual market volumes), **not** the marginal MW. This makes pre-2026 vs post-2026 values **not directly comparable**.

---

## 4. Feasibility Verdict

| Option | Feasibility |
|---|---|
| **Auto-scrape interactive chart on `/battery-index/`** | NOT possible — page contains no data; chart lives on `platform.cleanhorizon.com` behind login. |
| **Scrape free-tier platform after login** | TECHNICALLY possible (free signup), but: (a) requires creating an account and storing creds, (b) likely breaches their ToS (their value depends on Premium upsell), (c) terms reserve the right to revoke access. **NOT recommended.** |
| **Scrape monthly blog posts** | Feasible — News articles are public, indexed, and follow a predictable URL pattern (`/news/storage-index-<month>-<year>/`). But: only ~3-6 absolute country values per month (rotating subset). Germany and France are usually qualitative only. |
| **Nord Pool partner API** | Paid only. No free tier. Annual data fee. |
| **Manual extract from blog posts each month** | Easiest. Takes ~5 min/month to copy figures into a spreadsheet. Coverage of DE/FR/NL gaps remains a problem — they're rarely quoted in absolute terms. |
| **Sign up for free Clean Horizon platform account, manually screenshot/export monthly** | Within ToS, gets full 14-country monthly coverage. Manual but reliable. |

**Bottom line**: There is **no auto-scrapable JSON/CSV endpoint** for the free monthly index. The free chart is a login-gated SaaS view. The only programmatic access route is the paid Nord Pool feed.

---

## 5. Recommended Next Step (for AMPYR APD benchmarks page)

1. **Short term (free, manual)** — Ankit or analyst signs up for a free `platform.cleanhorizon.com` account. Once a month, log in, screenshot the chart, and manually transcribe the 14-country monthly values into a CSV under `data/benchmarks/clean_horizon/`. Add a simple `read_clean_horizon()` loader to the dashboard. Effort: ~10 min/month.
2. **Medium term (free, semi-automated)** — Add a scraper for the monthly news posts (`/news/storage-index-<month>-<year>/`) for the rotating subset of countries where absolute values *are* published (EE, LV, LT, IT, PL, RO, BE in recent months). Use as a sanity cross-check against the manually-entered values.
3. **Long term (paid)** — If the benchmark becomes load-bearing for investment decisions, evaluate the Nord Pool Market Data API subscription (`data.nordpoolgroup.com/power-system/storage-index`). Get a quote from Nord Pool sales — Clean Horizon's premium covers daily values plus the revenue stack split (DA / ID / FCR / aFRR / mFRR / imbalance / ancillary), which would be far more useful for Northwold benchmarking than just the headline monthly number.
4. **Important caveat to flag on the Benchmarks page** — The Jan 2026 methodology break (marginal-MW → average-MW). Any pre-2026 Clean Horizon values will read systematically higher than post-2026 values for the same underlying market.
5. **No-coverage gap** — Clean Horizon does **not** cover the UK (most relevant to Northwold) or NL. For Northwold the index is at best a sense-check on the EU energy-only stack; the bulk of UK BESS revenue (Dynamic Containment, BM, etc.) is out of scope of this benchmark entirely.

---

## 6. References

- https://www.cleanhorizon.com/battery-index/
- https://www.cleanhorizon.com/news/storage-index-march-2026/
- https://www.cleanhorizon.com/news/storage-index-february/
- https://www.cleanhorizon.com/news/january-storage-index-is-out/
- https://www.cleanhorizon.com/news/decembre-2025-storage-index-is-out/
- https://www.cleanhorizon.com/news/clean-horizon-releases-november-storage-index/
- https://www.cleanhorizon.com/news/storage-index-european-bess-market-update-october-2025/
- https://www.cleanhorizon.com/news/nord-pool-and-clean-horizon-launch-new-european-battery-storage-indices/
- https://www.nordpoolgroup.com/en/services/power-market-data-services/bess-market-clean-horizon-storage-index/
- https://data.nordpoolgroup.com/power-system/storage-index
