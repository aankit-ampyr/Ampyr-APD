# Solar KPI Survey

Artifacts for the **Solar Asset KPI priority survey**. The reviewers' responses
feed the **🌅 Tinte Solar Dashboard** (KPIs are sectioned by how many reviewers
selected them). The 35-KPI universe + response parsing live in
`src/data_cleaning/solar_kpi.py`.

## Files
- `solar-kpi-selector.html` — the survey Ankit circulated to SMEs (8 categories,
  35 KPIs). Reviewers tick the KPIs they want on a Solar / Solar+BESS dashboard,
  flag some as **must-have**, add a comment, and export their selections as a CSV.
- `responses/` — drop each reviewer's exported CSV here. The page reads every
  `*.csv` in this folder automatically (no code change needed). Filename pattern:
  `kpi-selections-<name>-<YYYY-MM-DD>.csv`.

## Adding a response
1. Save the reviewer's CSV attachment into `responses/`.
2. If the reviewer left the survey name field blank, the export is named
   `...-unknown-...` — rename the `unknown` slug to their name (e.g.
   `kpi-selections-daniel-2026-06-18.csv`) so the page labels it correctly.
3. Reload the page — the new response is included in the comparison + analysis.

## Responses received (18 Jun 2026)
- Daniel Peschel — `kpi-selections-unknown-2026-06-18.csv` (name left blank)
- Lars Maehl — `kpi-selections-lars-2026-06-18.csv`
- Matt van Staden — `kpi-selections-matt-2026-06-18.csv`

**Pending / suggested:** Markos Farag (on the thread, not yet returned); Lars and
Daniel also suggested surveying Dhruv and Shashank.
