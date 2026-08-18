# CLAUDE.md — Ampyr-APD (Asset Performance Dashboard, Streamlit prototype)

> Rebuilt 2026-07-10 as an APD-only project file (the previous version was a stale 30-Apr snapshot of the master `C:\repos\CLAUDE.md`). Org context, contracts, conventions, and the cross-project index live in the master file — this file is the **authoritative status doc for APD** and holds only APD content. Keep status here dated; update it as work lands.

## What this is

Ankit's Streamlit prototype of the **Asset Performance Dashboard (APD)** — monitoring and analysing Ampyr's energy assets (BESS, solar, solar+BESS) against optimized baselines, IAR projections, and market benchmarks. Doublu is building the production version (React + FastAPI) under Project Lazarus; this prototype leads it and is actively developed in parallel.

**Assets onboarded**: Northwold BESS (8.4 MWh, UK) + **Tinte solar** (Ampyr Tinte, 9.8 MW AC / 12.6 MWp DC PV, Netherlands — added 24 Jun 2026). More Germany solar expected Jul–Aug 2026, more NL Sep–Oct 2026.

## Stack & key files

- **Stack**: Python 3.11, Streamlit, Pandas, NumPy, Plotly, Matplotlib, SciPy (LP), OpenPyXL
- `streamlit_dashboard.py` — main app (~270KB)
- `src/pages/` — `monthly_checklist.py`, `invoice_analysis.py`, `tinte_solar_dashboard.py`, `data_quality.py`
- `src/data_cleaning/` — ETL modules (`process_invoices`, Tinte ETL) + `read_*` accessors
- `data/` — materialised outputs: `Master_BESS_Analysis_<Mon>_<YYYY>.csv` + `Optimized_Results_*.csv` (Sept 2025 → May 2026), `invoices/*.parquet`, `tinte/*.parquet`, `benchmarks/`
- `raw/` — input drop-zone only: month folders `Oct 2025/` … `May 2026/`, `OneDrive_*/` (multi-month Hartree batches), `Tinte/` (solar workbook)
- `docs/` — incl. `Tinte_Data_Collection_Request.md` (uncommitted)

## Data pipeline rules (load-bearing)

- **Pages NEVER read `raw/` at runtime.** `raw/` is a starting point; every page reads materialised `data/` outputs via `data_cleaning.read_*`. This ETL boundary is an architectural rule — do not bypass it.
- **ETL**: `python -m src.data_cleaning.process_invoices` materialises `data/invoices/*.parquet`; `python -m src.data_cleaning.process_tinte` materialises `raw/Tinte/Tinte.xlsx` → `data/tinte/*.parquet` (+ `meta.json`). Run the relevant ETL whenever new files land in `raw/`.
- **Any data refactor must verify bit-for-bit** (`assert_frame_equal(..., check_exact=True)`) against the pre-refactor outputs; surface deltas before proceeding.

## Status as of 2026-07-10 (portfolio refresh + Tarun strategic update)

The 10 Jul Tarun meeting produced three decisions that materially reshape APD: no SCADA integration (asset-performance data now from an ASE-built/managed internal DB), cloud shifts to Azure (not AWS), and Doublu Phase 2 is paused ~2 months+ while Phase-1 feedback is gathered and improvements are made in-house first. On delivery, the Doublu production build is ~90–95% complete after Sprint 8 (demoed 26 Jun) with handover to the in-house team underway (Doublu to provide L3/L4 support post-handover). The prototype is targeting a V1 (Tinte + Northwold first) around 15 Jul.

- **No SCADA integration (10 Jul):** all asset-performance data now comes from ASE's internal database, which ASE will build and manage. **Supersedes the ~4-month SCADA-delivery blocker** — the new dependency is ASE internal-DB readiness. (SCADA items under "API integrations" and in the Phase 2 roadmap annotated as superseded below.)
- **Cloud = Azure, not AWS (10 Jul):** both Ampyr Solar Europe and AGP run on Azure, and AGP supplies the M365 + Claude + Codex subscriptions for Ampyr GTC. Supersedes the 30 Jun "AWS non-base tier" decision.
- **Doublu Phase 2 paused ~2 months+ (10 Jul):** Phase 2 dev (aggregator management + SOLR analytics) and the SOW countersignature are deferred while Phase-1 feedback is actioned in-house — **kickoff is no longer 13 Jul.**
- **Production (Doublu):** Sprint 8 demoed 26 Jun, ~5–10% of features remain. Modules shown: battery-health daily-cycle analytics (1.5 cycles/day warranty line + exceedance table), Executive Analysis (stream-wise SFFR / EPEX / IDA1 / IDC revenue + capture), EMR invoice PDF extraction. **30 Jun decision:** per-asset aggregator on/off toggle (Northwold uses an aggregator; Germany/NL assets don't). **Persist KPI results to DB** to stop recalculating each load — flagged critical for cloud cost + future AI.
- **Prototype (Ankit):** Tinte NL solar onboarded 24 Jun (9.8 MW AC / 12.6 MWp), 35-KPI solar dashboard shipped but blocked on financial/market data; May 2026 BESS + Modo May benchmark integrated (May capture 83% — £24,578 net of 5% GridBeyond fee vs £29,534 optimal); template-upload workflow in progress (Ishita uploads docs → system auto-processes future same-format uploads).

## Current status (as of 2026-07-10)

- **July 2026 integrated (18 Aug):** `Master_BESS_Analysis_Jul_2026.csv` (1,487 rows, 1 Jul 00:30 → 31 Jul 23:30) + `Optimized_Results_Jul_2026.csv` (1,440 rows, multi-market LP £37,521 optimal). July actual **£15,714 net = 44% capture**; IAR 51%. **July is SFFR-only — zero EPEX DAM/IDA1/IDC revenue** (self-bill: SFFR £17,196.07, imbalance −£1,620.97, net £15,226.10) — first such month since Aug 25; ask GridBeyond whether trading was switched off. Master reconciles to the self-bill to the penny except SFFR −£11.06 = the 1 Jul 00:00 half-hour trimmed by `align_timestamps` because the SCADA export starts 00:10 (same as May). July backing data has no `Battery SoC` column — a non-issue, that column has been empty since Oct 25 and nothing consumes it. **SCADA detection fix**: ASE's third filename convention (`monthly-<stamp>.xlsx`) is now caught by the `YYYYMMDDTHHMMSS` export-stamp rule in both `loader.find_files` and `invoice_loader.load_scada_monitoring` (June + optimizer regressions bit-identical). Modo Jul 26 pulled: ALL 64,588 / 1H 51,177 / 2H 71,036 (Jun restated to 70,565 / 54,698 / 78,529 by the live index; both dashboards updated). `monthly_checklist.py` was a month behind (no June, stale `market=total×12` Modo series, IAR col_map to May) — brought in step. Pending: July CM + DUoS actuals (arrive with future EMR/Hartree invoices); new Tinte workbooks (Feb/Mar/Jun-26) landed via GitHub — `process_tinte` not yet re-run. Known pre-existing quirk: dashboard subtracts 0.95×`Imbalance Charge` where the self-bill adds it signed (June +26.35 / July −157.56) — worth a sign check.
- **Invoice Analysis → Revenue Reconciliation now cross-month (18 Aug):** was pinned to the single Jan-26 Summary Statement; now a month selector over every GridBeyond statement on file (self-bills Aug 25 → Jul 26 parsed from `pdf_invoices.parquet` `raw_text` via `invoice_reconciler.parse_gridbeyond_self_bill`, same dict shape as the Summary Statement — no ETL change). Shows master gross ×0.95 vs the bill's Sub Total per stream, then a below-the-line table (DUoS benefit, Imbalance Cost vs master `Imbalance Charge`, one-offs, NET). Findings: **Oct 25 Imbalance Cost £448.53 on the bill vs £488.53 in the master (£40 gap)**; Sep/Oct bills list a DUoS "GB Share" line GridBeyond did not apply to NET; Aug 25 carries a −£5,000 "Setup Fee — GridBeyond Hardware" one-off. Missing self-bills: Dec 25, Jan 26 (Summary Statement instead), Apr 26.
- **Last commits (24 Jun)**: May 2026 monthly data integrated + Modo May benchmark refresh (`21a0a22`); **Tinte solar KPI dashboard shipped** (`c666706`) — 35-KPI solar universe, per-KPI data-requirements, standalone survey page removed.
- **Uncommitted working tree (modified ~6 Jul)**: `src/pages/tinte_solar_dashboard.py` (+50 lines) + `streamlit_dashboard.py` + `.gitignore`, plus new `docs/Tinte_Data_Collection_Request.md` — the request lists what's needed to populate all 35 Tinte KPIs beyond the technical feed (PPA/offtake terms, revenue & settlement statements, GvO/SDE++ lines; note: **no Modo benchmark exists for NL solar** — market/capture KPIs need EPEX/ENTSO-E NL day-ahead + a merchant curve from Aurora/Baringa). Also untracked: `.understand-anything/` + `Raw Files APD.zip` (neither ignored). Commit, ignore, or discard deliberately.
- **May 2026 BESS data**: `Master_BESS_Analysis_May_2026.csv` (1,487 rows) + `Optimized_Results_May_2026.csv` (1,440 rows, multi-market LP); May actual £24,578 net of the 5% GridBeyond fee = 83% capture vs optimal £29,534. Monthly Checklist current through May (Modo aligned to API, CM +Mar, DUoS +Apr, IAR +Apr/May). Pending: May CM + DUoS actuals arrive with future invoices (~July); Modo Terminal percentile extract is a separate manual scrape.
- **Benchmarks**: Modo ME-BESS-GB monthly-index-live API (FCA-regulated) is the authoritative source; May pulled at £39k/MW/yr (ALL 39,023 / 1H 28,168 / 2H 45,126), historical months restated to live-index values. Active 3-benchmark stack: Northwold Actual + Modo all-durations + ME-BESS-GB 2h. Grid fees >5% subtracted across all views. Northwold 1.25–1.5h duration caveat vs Modo brackets documented.

## API integrations (status as of 2026-07-09)

- **EPEX** (primary price feed, replaces GridBeyond) — BLOCKED on Tom Reed departure; Cyrus recruiting a replacement, est. 1–2 months delay
- **Aurora** (benchmark) — BLOCKED on MPA Solar Europe email provisioning (reminder sent 26 May, no response)
- **Modo** — live + integrated
- **SCADA API** — stuck with the EPC company. **SUPERSEDED 2026-07-10**: no SCADA integration — asset-performance data now sourced from ASE's internal DB (see "Status as of 2026-07-10" above); new dependency is ASE internal-DB readiness, not the EPC's SCADA delivery.
- **Aggregator APIs — do not exist; CSV-only ingestion is the standing assumption** (directly constrains the Phase 2 "aggregator API ingestion" roadmap item below)
- **Management-user access** (view-only on view-analysis tab) — owed by Doublu; Rohan's 12 May test via the `*-management@` email format has no recorded outcome — confirm and close

## Production build (Doublu) — APD track

- **Sprint history**: Sprint 1 (auth, user management, platform assignment, audit logs — 12 stories) ✓. Sprint 2 (demoed 6 Apr, 25% milestone: asset onboarding wizard, aggregator + SCADA validation, 50-col data merging, SOC logic) ✓. Subsequent sprint demos 20 Apr → 12 May: DG generator config (binary/variable, F0/F1 fuel curve), first hosted production-env demo (21 Apr), asset details returning-user view + upload history, benchmark settings (Modo monthly auto-pull, green/yellow/red), intraday vs day-ahead price series + battery power graph, n-simulations per project with search/filter/resume/discard. Sprint user stories: `Ampyr-PRDs\Dev Work updates\` (Sprints 1–4, 6).
- **Launch timeline (per 2 Jun meeting — outcomes UNRECORDED, refresh on next Doublu sync)**: launch targeted 1st/2nd week of July; final approval target was 20 Jun; delivery estimate 11 Jul. Whether approval happened and delivery held is not recorded anywhere on disk as of 2026-07-10 — **establish and record the actual launch state.**
- **Production tabs locked (2 Jun)**: Executive Comparison + Benchmarks + Invoice Analysis + Battery Health. Benchmark Comparison demoted to explainer (not in production). Multi-market optimization v2 deployed for testing.
- **Open Doublu items**: dot-based viz replacing heat-map (actual + IAR + Modo on one chart); 5% revenue-share deduction verification across all formulas (Aditya, flagged 12 May); management-user access (above); Sprint-2 item "send Nov–Feb aggregator files to Anil/Arijit" — likely completed (later sprints demoed 50-col aggregator merging) but closure never recorded, confirm.
- **Phase 2**: costed SOW drafts received — **AMP/LZ/002** Dev + **AMP/LZ/003** AI (the AI SOW includes a USD 15,000 APD implementation line). Terms in the master `C:\repos\CLAUDE.md`; review/negotiation state tracked in `Ampyr-PRDs\Phase 2\`, not here.

### APD Roadmap (Doublu)

| Phase | Weeks | Scope |
|-------|-------|-------|
| **Phase 1A** | 1–8 | Initial working system: single asset/org, manual upload, basic validation, core metrics, single benchmark (Modo), basic dashboards, inline annotations |
| **Phase 1B** | 9–17 | Full Phase 1: auth + RBAC, multi-org/asset management, full ingestion pipeline, complete analytics + benchmarking, automated digests + reporting, exports, admin/audit/governance |
| **Phase 2** | 14–28 | Additional benchmark sources, aggregator API ingestion (constrained: aggregator APIs don't exist — CSV-only), SCADA API ingestion (**superseded 2026-07-10** — data now from ASE internal DB, not SCADA), multi-region/country, enhanced visualisations |
| **Support** | 29–40 | Post-implementation support |

## End-of-session checklist (APD)

1. Record status changes **in this file** (dated) — this is APD's authoritative status doc per the master index.
2. If the change affects the portfolio level (timeline, scope, % complete), update the tracker artifacts per the master file's Weekly Refresh procedure.
3. Touch the master `C:\repos\CLAUDE.md` only for index-level changes (paths, ownership, durable facts).
