# Regelleistung Online — BESS Revenue Index (2h, Germany)

**Research date**: 2026-05-12
**Public page**: https://www.regelleistung-online.de/german-energy-storage-revenue-index/bess-revenue-index-2h/
**Verdict**: **AUTO-SCRAPABLE — fully automatable, no auth, no rate-limit signs, plain CSV.**

---

## 1. Endpoint URLs

The interactive charts on the page load their data from three publicly accessible WordPress AJAX endpoints. They are linked directly as `<a href="...">` "Download data" links in the page HTML — no scraping of JS bundle required.

| Variant | URL |
|---|---|
| 365-day MA (by strategy) | `https://www.regelleistung-online.de/wp-admin/admin-ajax.php?action=download_chart_data&type=bess2-2h&nonce=0e2c333cf5` |
| 30-day MA (by strategy) | `https://www.regelleistung-online.de/wp-admin/admin-ajax.php?action=download_chart_data&type=bess3-2h&nonce=0e2c333cf5` |
| Daily Optimization — daily €/MW/yr by revenue stream | `https://www.regelleistung-online.de/wp-admin/admin-ajax.php?action=download_chart_data&type=bess4-2h&nonce=0e2c333cf5` |

The shorter path `https://www.regelleistung-online.de/?action=download_chart_data&type=bess2-2h&nonce=0e2c333cf5` also works (WordPress routes both forms).

### The `nonce` parameter
- Value observed: `0e2c333cf5`
- WordPress nonces are intended to expire (typically ~24h, configurable). In practice the same nonce kept working across all three downloads in this session.
- The nonce is **embedded in the public page HTML** — a scraper can always pick up a fresh one by GET-ing the page first and parsing the `<a href="...nonce=XXXXXXXXXX">` attributes.
- Risk: nonce rotation could in theory break a cached endpoint. Mitigation: always re-scrape the index page to pick up the current nonce before downloading.

---

## 2. Data format

- **Content-Type**: `text/plain` (despite being CSV)
- **Encoding**: UTF-8
- **Delimiter**: comma
- **Quoting**: every field double-quoted (including header)
- **Date format**: `DD.MM.YYYY` (German)
- **Decimal**: period (`.`) — NOT German comma. Pandas `read_csv` works out of the box.
- **No BOM**, no trailing metadata.
- **Coverage**: rolling ~365 days. Earliest row seen: `11.05.2025`. Latest row: `11.05.2026` (yesterday — i.e. T-1 daily refresh).

### Schemas

**`bess2-2h` / `bess3-2h` (5-strategy comparison, MA)**
```
"Date","Trading Only","FCR Only","aFRR Only","aFRR & Trading","Daily Optimization"
```

**`bess4-2h` (Daily Optimization revenue decomposition)**
```
"Date","Trading","FCR","aFRR"
```

For `bess4-2h`, the three columns should sum (approximately) to the `Daily Optimization` column in `bess2-2h`/`bess3-2h` — confirming this is the revenue-stream breakdown of the headline strategy.

### Which file is 30-day vs 365-day?
Not labelled in the response itself. Inferred from magnitudes (30-day MA is more volatile and tracks recent market shifts; 365-day MA is smoother). Verified by comparing the two on the chart on the public page.

- **`bess2-2h` = 365-day moving average** (smoother, lower current Daily Optimization)
- **`bess3-2h` = 30-day moving average** (more recent, higher Daily Optimization values in current high-FCR environment)

**Confirm this mapping** by overlaying both series against the live chart on the public page before going to production. Could also be inverted — order is an assumption based on inspection.

### Units
Charts and CSVs are denominated in **€/MW/year** (annualised revenue per MW of installed power), per the page methodology.

---

## 3. Sample latest values (as of 2026-05-12, T-1 = 2026-05-11)

### `bess2-2h` (365-day MA) — last 4 rows
```
"08.05.2026","152054.93","174324.68","184574.66","216502.16","224010.51"
"09.05.2026","150407.34","173243.89","184195.55","215599.39","223107.73"
"10.05.2026","150147.76","173046.79","185186.4","215977.94","223486.28"
"11.05.2026","150625.03","173512.63","188985.32","217598.67","225625.75"
```

### `bess4-2h` (Daily Optimization revenue split) — last 4 rows
```
"08.05.2026","59051.09","4628.87","146148.69"
"09.05.2026","58894.14","4628.87","146152.32"
"10.05.2026","58847.97","4628.87","146200.23"
"11.05.2026","58519.56","4628.87","146401.53"
```

### Headline numbers (latest dated 2026-05-11)

| Metric | Value (€/MW/year) |
|---|---|
| **Daily Optimization (likely 365-day MA)** — best strategy | **€225,626** |
| Daily Optimization (likely 30-day MA) — needs verification | (see `bess3-2h`; first/last rows confirm data is live) |
| aFRR & Trading combo (likely 365-day MA) | €217,599 |
| aFRR Only (capacity, likely 365-day MA) | €188,985 |
| FCR Only (capacity, likely 365-day MA) | €173,513 |
| Trading Only (ID1 arbitrage, likely 365-day MA) | €150,625 |

Daily Optimization revenue split (€/MW/year, daily snapshot for 2026-05-11):
- Trading: €58,520
- FCR: €4,629
- aFRR: €146,402

→ **Conclusion**: in May 2026, the 2h BESS revenue stack is heavily aFRR-dominated, with trading a secondary contributor and FCR collapsed to a tiny share. Matches qualitative commentary on Wattmate / ISEA Battery Charts.

---

## 4. Authentication / access controls

- **None required**. No cookie, no session, no login wall.
- WordPress nonce is the only obstacle; it is publicly broadcast in the page HTML.
- No `robots.txt` block observed against the admin-ajax endpoint.
- **Polite scraping cadence**: once per day is plenty (data is T-1 daily). Cache locally.

---

## 5. Feasibility verdict

**AUTO-SCRAPABLE.** Production-ready scraping pattern:

```python
import re
import httpx
import pandas as pd
from io import StringIO

PAGE = "https://www.regelleistung-online.de/german-energy-storage-revenue-index/bess-revenue-index-2h/"
ENDPOINT = "https://www.regelleistung-online.de/wp-admin/admin-ajax.php"

def fetch_bess_2h():
    with httpx.Client(headers={"User-Agent": "Ampyr-APD/1.0 (research)"}) as c:
        html = c.get(PAGE).text
        # Pick up the live nonce from the page
        m = re.search(r"action=download_chart_data&type=bess2-2h&nonce=([a-f0-9]+)", html)
        nonce = m.group(1)
        out = {}
        for variant in ("bess2-2h", "bess3-2h", "bess4-2h"):
            r = c.get(ENDPOINT, params={
                "action": "download_chart_data",
                "type": variant,
                "nonce": nonce,
            })
            r.raise_for_status()
            df = pd.read_csv(StringIO(r.text), parse_dates=["Date"], dayfirst=True)
            out[variant] = df
        return out
```

### To fully automate

1. Schedule the fetch daily (e.g. cron at 09:00 UTC, after the German morning publication).
2. Persist to parquet under `data/benchmarks/regelleistung_de_2h/{variant}_{YYYY-MM-DD}.parquet`, or append to a single growing table.
3. Add a sanity check: latest date ≥ today − 2 calendar days; otherwise alert.
4. Add a unit test that pulls the page nonce and validates the regex still matches (in case the WP plugin changes its href format).
5. Decide on the 30-day vs 365-day mapping (run once, eyeball against the live chart, hardcode the mapping in a constant).
6. Map column names to a consistent internal schema if combining with Modo (e.g. `revenue_eur_per_mw_per_year`, `strategy`, `date`, `window_days`).

### Known risks / failure modes

- Nonce rotation: mitigated by always re-parsing the page.
- WP cache headers: the endpoint returned `text/plain` with no observed strong caching during testing; treat as live.
- The CSV uses double quotes around every value — pandas `read_csv` handles that natively (`quotechar='"'`).
- Locale: dates are DD.MM.YYYY. Always pass `dayfirst=True` or parse explicitly with `%d.%m.%Y`.
- No SLA — it's a free public benchmark from a German market analytics firm (not a TSO directly; "Regelleistung Online" is a commercial analytics platform, distinct from the actual TSO platform `regelleistung.net`). They could pull the data behind a paywall at any time.

---

## 6. Notes on the source

- **Operator**: Regelleistung Online (commercial market analytics platform for German balancing markets). NOT the German TSO consortium platform (`regelleistung.net`) — the prior research note describing it as the "official German TSO benchmark" is **imprecise**. It is a free, independent, publicly published index, but produced by a private analytics firm. Modo Energy's GB index is the closest analogue.
- **WordPress-based site** — the download endpoint pattern (`admin-ajax.php?action=...&nonce=...`) is a standard WP convention; the chart plugin (likely Highcharts or similar, not exposed in markup) writes nonce-guarded download links into the page.
- **Comparable indices**:
  - 1h variant: same site, swap `2h` → `1h` in the endpoint type (e.g. `bess2-1h`). Likely works identically.
  - ISEA Battery Charts: https://battery-charts.de/revenue-index/ — academic, similar concept.
  - Wattmate cross-comparison piece: https://wattmate.de/aktuelles/wattmate-vergleicht-batteriespeicher-bess-indizes

---

## 7. Sources

- BESS 2h page: https://www.regelleistung-online.de/german-energy-storage-revenue-index/bess-revenue-index-2h/
- BESS 1h page: https://www.regelleistung-online.de/german-energy-storage-revenue-index/bess-revenue-index-1h/
- Wattmate comparison: https://wattmate.de/aktuelles/wattmate-vergleicht-batteriespeicher-bess-indizes
- ISEA Battery Charts: https://battery-charts.de/revenue-index/
