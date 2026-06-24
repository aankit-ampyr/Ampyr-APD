"""
Tinte Solar KPI Dashboard.

Renders the full 35-KPI Solar universe for the **Ampyr Tinte** PV plant
(9.8 MW AC / 12.6 MWp DC, Netherlands), using the April-2026 SCADA export +
monthly technical report. KPIs are grouped into sections by **how many of the
three survey reviewers selected each KPI** (3/3, 2/3, 1/3, 0/3).

Every KPI renders a graph. Where Tinte has the data (generation / availability /
curtailment) the graph is real; where it doesn't (financials, market prices) a
placeholder graph is shown with an explicit note of what data is missing — the
Tinte feed is technical-only.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

try:  # shared solar-KPI data layer (KPI universe + survey tally)
    from data_cleaning.solar_kpi import load_responses, build_tally, KPI_BY_ID, CATEGORIES
except ImportError:  # pragma: no cover
    from src.data_cleaning.solar_kpi import load_responses, build_tally, KPI_BY_ID, CATEGORIES

try:
    from data_cleaning.process_tinte import (
        read_daily, read_inverter_daily, read_meta, REPORT_APR26,
    )
except ImportError:  # pragma: no cover
    from src.data_cleaning.process_tinte import (
        read_daily, read_inverter_daily, read_meta, REPORT_APR26,
    )

try:
    from data_cleaning.solar_data_requirements import SOLAR_DATA_REQUIREMENTS, MODO_FINDING
except ImportError:  # pragma: no cover
    from src.data_cleaning.solar_data_requirements import SOLAR_DATA_REQUIREMENTS, MODO_FINDING

ORANGE = "#F4A300"
BLUE = "#2C7FB8"
GREY = "#9aa0a6"


# ─────────────────────────────────────────────────────────────
# Real / partial KPI graphs (Tinte data available)
# ─────────────────────────────────────────────────────────────
def _fig_revenue_waterfall(ctx):
    wf = ctx["report"]["energy_waterfall"]
    labels = [w[0] for w in wf] + ["Actual generation"]
    measure = ["absolute"] + ["relative"] * (len(wf) - 1) + ["total"]
    values = [wf[0][1]] + [w[1] for w in wf[1:]] + [None]
    fig = go.Figure(go.Waterfall(
        orientation="v", measure=measure, x=labels, y=values,
        decreasing={"marker": {"color": "#d62728"}},
        increasing={"marker": {"color": "#2ca02c"}},
        totals={"marker": {"color": ORANGE}},
        connector={"line": {"color": GREY}},
    ))
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=60),
                      title="Energy waterfall — theoretical → actual (MWh, Apr-26)",
                      yaxis_title="MWh")
    return fig


def _fig_epi(ctx):
    d = ctx["daily"].dropna(subset=["energy_mwh"])
    bud_daily = ctx["report"]["budget_gen_mwh"] / max(len(d), 1)
    fig = go.Figure()
    fig.add_bar(x=list(d.index), y=d["energy_mwh"], name="Actual", marker_color=ORANGE)
    fig.add_hline(y=bud_daily, line_dash="dash", line_color=BLUE,
                  annotation_text=f"Budget pace {bud_daily:.0f} MWh/day", annotation_position="top left")
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10),
                      title="Daily generation vs budget pace (MWh)", yaxis_title="MWh")
    return fig


def _fig_bepi(ctx):
    d = ctx["daily"].dropna(subset=["energy_mwh"]).copy()
    d["cum_actual"] = d["energy_mwh"].cumsum()
    bud_daily = ctx["report"]["budget_gen_mwh"] / max(len(d), 1)
    d["cum_budget"] = np.arange(1, len(d) + 1) * bud_daily
    fig = go.Figure()
    fig.add_scatter(x=list(d.index), y=d["cum_budget"], name="Budget", line=dict(color=BLUE, dash="dash"))
    fig.add_scatter(x=list(d.index), y=d["cum_actual"], name="Actual", line=dict(color=ORANGE, width=3))
    pct = ctx["report"]["pct_of_budget"]
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10),
                      title=f"Cumulative actual vs budget — {pct}% of budget", yaxis_title="MWh")
    return fig


def _fig_yield_dev(ctx):
    d = ctx["daily"].dropna(subset=["energy_mwh"]).copy()
    bud_daily = ctx["report"]["budget_gen_mwh"] / max(len(d), 1)
    dev = (d["energy_mwh"].cumsum() - np.arange(1, len(d) + 1) * bud_daily)
    fig = go.Figure()
    fig.add_scatter(x=list(d.index), y=dev, fill="tozeroy",
                    line=dict(color="#d62728"), name="Cum. deviation")
    fig.add_hline(y=0, line_color=GREY)
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10),
                      title="Cumulative yield deviation vs budget (MWh)", yaxis_title="MWh")
    return fig


def _fig_availability(ctx):
    d = ctx["daily"]
    fig = go.Figure()
    if "uptime_proxy_pct" in d.columns:
        fig.add_scatter(x=list(d.index), y=d["uptime_proxy_pct"], name="Daylight uptime proxy",
                        line=dict(color=BLUE, width=2))
    s = ctx["report"]["strings"]
    fig.add_annotation(text=f"Strings: {s['normal']}/{s['total']} normal · {s['faulty']} faulty · {s['severe']} severe",
                       showarrow=False, xref="paper", yref="paper", x=0.5, y=-0.18, font=dict(size=10, color=GREY))
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=40),
                      title="Plant uptime proxy (% of daylight intervals producing)",
                      yaxis_title="%", yaxis_range=[0, 105])
    return fig


def _fig_curtailment(ctx):
    d = ctx["daily"]
    fig = go.Figure()
    fig.add_bar(x=list(d.index), y=d.get("curtail_intervals", pd.Series(dtype=float)),
                marker_color="#d62728", name="Curtailed 15-min intervals")
    fig.add_annotation(text="Report: Grid + curtailment loss −148 MWh (combined, tentative)",
                       showarrow=False, xref="paper", yref="paper", x=0.5, y=1.08, font=dict(size=10, color=GREY))
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10),
                      title="Curtailment events per day (setpoint < 100%)", yaxis_title="15-min intervals")
    return fig


def _fig_degradation(ctx):
    s = ctx["report"]["strings"]
    cats = ["Normal", "Underperforming\n(Z<-1)", "Faulty\n(Z<-2)", "Severe\n(Z<-3)"]
    vals = [s["normal"], s["underperforming"], s["faulty"], s["severe"]]
    colors = ["#2ca02c", "#fdae61", "#d62728", "#7f0000"]
    fig = go.Figure(go.Bar(x=cats, y=vals, marker_color=colors, text=vals, textposition="auto"))
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=30, b=10),
                      title=f"String health proxy — {s['total']} strings (worst 1.18.DC4 −21.5%)",
                      yaxis_title="# strings")
    return fig


RENDERERS = {
    "revenue-waterfall": _fig_revenue_waterfall,
    "epi": _fig_epi,
    "epi-budget": _fig_bepi,
    "cumulative-yield-deviation": _fig_yield_dev,
    "availability": _fig_availability,
    "curtailment-rate": _fig_curtailment,
    "degradation-warranty": _fig_degradation,
}

# Per-KPI data-status note. Anything not listed → category default (missing).
NOTES = {
    "revenue-waterfall": ("partial", "Showing the **energy** waterfall (MWh) from the technical report. "
                          "A £-revenue waterfall needs a price/revenue feed — not in the Tinte export."),
    "epi": ("partial", "Daily generation vs budget pace. A true EPI needs the weather-corrected "
            "model-expected yield per day (PVsyst) — only the monthly budget (1,410 MWh) is available."),
    "epi-budget": ("available", "Actual 1,343 MWh vs budget 1,410 MWh = 95.2% (monthly report)."),
    "cumulative-yield-deviation": ("available", "Deviation measured vs the report **budget**; a P50 curve "
                                   "is not available in this feed."),
    "availability": ("partial", "Plant-uptime proxy + string health. True availability % / inverter-status "
                     "flags are not in the feed (report gives plant-breakdown loss −90 MWh)."),
    "curtailment-rate": ("partial", "Setpoint-based curtailment events. The report combines grid + curtailment "
                         "(−148 MWh) and flags the split as tentative."),
    "degradation-warranty": ("partial", "Multi-year degradation vs warranty is not available (one month). "
                             "Shown: the report's string Z-score health as a related proxy."),
}
NOTE_BY_CAT = {
    "revenue": "Needs a revenue / financial feed (£). The Tinte export is technical (SCADA) only.",
    "cash": "Needs cash-flow / treasury data. Not in the Tinte technical export.",
    "debt": "Needs the project-finance / debt model. Not in the Tinte technical export.",
    "contracting": "Needs PPA / offtake contract data. Not in the Tinte technical export.",
    "market": "Generation volume is available, but there is **no market price / imbalance** feed for capture KPIs.",
    "cost": "Needs O&M cost / work-order data. Not in the Tinte technical export.",
    "risk": "Needs financial / counterparty data. Not in the Tinte technical export.",
    "generation": "Not available from this feed.",
}


def _placeholder_fig(short):
    fig = go.Figure()
    fig.update_layout(
        height=300, margin=dict(l=10, r=10, t=30, b=10), plot_bgcolor="#fafbfc",
        xaxis=dict(visible=False, range=[0, 1]), yaxis=dict(visible=False, range=[0, 1]),
        title="No Tinte data",
    )
    fig.add_shape(type="rect", x0=0.02, y0=0.05, x1=0.98, y1=0.95, line=dict(color="#e3e6ea", dash="dot"))
    fig.add_annotation(text="📉 Data not available", showarrow=False, x=0.5, y=0.6,
                       font=dict(size=15, color="#9aa0a6"))
    fig.add_annotation(text=short, showarrow=False, x=0.5, y=0.38, font=dict(size=10, color="#bbb"))
    return fig


# ─────────────────────────────────────────────────────────────
# Page
# ─────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────
# Data-requirements master list — dedupe per-KPI source documents
# into canonical feed/document buckets (first keyword match wins).
# ─────────────────────────────────────────────────────────────
CANONICAL_SOURCES = [
    {"label": "SCADA / PPC historian + grid meter", "provider": "SCADA system + DSO meter", "have": True,
     "keywords": ["scada", "ppc", "historian", "grid main-meter", "grid meter", "data/tinte", "metered export", "meter (export"]},
    {"label": "Monthly Technical Performance Report", "provider": "Asset manager / IE", "have": True,
     "keywords": ["technical performance report", "energy-loss waterfall", "energy loss waterfall", "string health"]},
    {"label": "P50 yield / energy-assessment + degradation report", "provider": "Independent engineer", "have": False,
     "keywords": ["p50", "yield assessment", "energy assessment", "degradation", "warranty", "pvsyst"]},
    {"label": "Signed PPA / offtake agreement", "provider": "Offtaker / commercial", "have": False,
     "keywords": ["ppa", "offtake"]},
    {"label": "Revenue & settlement statements", "provider": "Offtaker / route-to-market trader", "have": False,
     "keywords": ["settlement statement", "revenue / settlement", "revenue/settlement", "settlement statements", "route-to-market", "revenue statement"]},
    {"label": "EPEX / ENTSO-E NL day-ahead price", "provider": "Market-data vendor (EPEX/ENTSO-E)", "have": False,
     "keywords": ["epex", "day-ahead", "day ahead", "wholesale price", "entso", "spot price", "spot clearing"]},
    {"label": "TenneT imbalance settlement", "provider": "TSO (TenneT)", "have": False,
     "keywords": ["tennet", "imbalance"]},
    {"label": "GvO certificates (CertiQ / Vertogas)", "provider": "CertiQ / Vertogas", "have": False,
     "keywords": ["gvo", "certiq", "vertogas", "guarantee of origin", "certificate"]},
    {"label": "SDE++ subsidy award & RVO correction prices", "provider": "RVO", "have": False,
     "keywords": ["sde++", "sde+", "rvo", "subsidy"]},
    {"label": "Merchant price curve (Aurora / Baringa)", "provider": "Market-data vendor", "have": False,
     "keywords": ["merchant price", "aurora", "baringa", "forward curve", "price curve", "price-curve"]},
    {"label": "Project-finance model / annual budget", "provider": "Asset manager / investment", "have": False,
     "keywords": ["project-finance model", "project finance model", "business plan model", "annual budget", "financial model", "the model"]},
    {"label": "Senior facility agreement & debt schedule", "provider": "Lender / agent bank", "have": False,
     "keywords": ["facility agreement", "debt amortis", "debt schedule", "senior debt", "dscr", "llcr", "plcr", "hedge", "gearing", "interest schedule", "covenant", "lender"]},
    {"label": "Shareholder loan agreement", "provider": "Shareholders", "have": False,
     "keywords": ["shareholder loan", "shl", "shareholder agreement"]},
    {"label": "Management accounts / statutory P&L", "provider": "Finance / accounting", "have": False,
     "keywords": ["management accounts", "trial balance", "statutory", "p&l", "audited", "income statement"]},
    {"label": "Fixed-asset register & depreciation policy", "provider": "Finance team", "have": False,
     "keywords": ["fixed-asset", "fixed asset", "depreciation", "asset register", "capex", "capitalised"]},
    {"label": "Dutch corporate-tax computation", "provider": "Tax advisor / finance", "have": False,
     "keywords": ["tax comput", "cit", "vennootschap", "tax provision", "tax workpaper", "corporate income tax", "tax computation"]},
    {"label": "O&M contract & CMMS work-order log", "provider": "O&M contractor", "have": False,
     "keywords": ["o&m", "cmms", "work-order", "work order", "maintenance"]},
    {"label": "Asset-mgmt agreement, insurance, land lease", "provider": "Asset manager", "have": False,
     "keywords": ["asset management agreement", "insurance", "lease", "grond"]},
    {"label": "Network / DSO & energy-tax invoices", "provider": "DSO / tax authority", "have": False,
     "keywords": ["dso", "network charge", "grid connection", "tariff", "ode", "transport charge"]},
    {"label": "Counterparty credit & receivables ledger", "provider": "Finance / credit", "have": False,
     "keywords": ["receivable", "aged", "credit rating", "counterparty credit", "ar ledger", "ageing", "collections", "credit report"]},
    {"label": "Treasury: bank statements & reserve accounts", "provider": "Finance / treasury", "have": False,
     "keywords": ["bank statement", "reserve account", "dsra", "treasury", "liquidity", "cash flow statement"]},
]


def build_master_sources(reqs):
    """Dedupe every KPI's source_documents into canonical feed/document buckets."""
    agg = {s["label"]: {**s, "kpis": set()} for s in CANONICAL_SOURCES}
    other = {"label": "Other / miscellaneous", "provider": "various", "have": False, "kpis": set()}

    def match(doc):
        dl = doc.lower()
        for s in CANONICAL_SOURCES:
            if any(kw in dl for kw in s["keywords"]):
                return s["label"]
        return None

    for cat in reqs:
        for k in cat["kpis"]:
            for doc in k.get("source_documents", []):
                lbl = match(doc)
                (agg[lbl] if lbl else other)["kpis"].add(k["name"])

    rows = [agg[s["label"]] for s in CANONICAL_SOURCES if agg[s["label"]]["kpis"]]
    if other["kpis"]:
        rows.append(other)
    out = []
    for e in rows:
        kl = sorted(e["kpis"])
        out.append({
            "Source / document": e["label"], "Provider": e["provider"],
            "Status": "🟢 in feed" if e["have"] else "⚪ to collect",
            "KPIs unlocked": len(kl),
            "Example KPIs": ", ".join(kl[:4]) + ("…" if len(kl) > 4 else ""),
        })
    out.sort(key=lambda r: (r["Status"].startswith("🟢"), -r["KPIs unlocked"]))
    return out


def _status_badge(status):
    return {"available": "🟢 live data", "partial": "🟡 partial — see note",
            "missing": "⚪ data missing"}[status]


def show_tinte_solar_dashboard():
    meta = read_meta()
    daily = read_daily()
    report = REPORT_APR26

    st.title("☀️ Tinte — Solar KPI Dashboard")
    st.markdown(
        "<style>div[data-testid='stMetricValue']{font-size:1.4rem;}"
        "div[data-testid='stMetricLabel']{font-size:0.78rem;}"
        "div[data-testid='stMetricDelta']{font-size:0.72rem;}</style>",
        unsafe_allow_html=True,
    )
    if not meta or daily.empty:
        st.error("Tinte data not found. Run `python -m src.data_cleaning.process_tinte` first "
                 "(reads raw/Tinte/Tinte.xlsx).")
        return

    st.markdown(
        f"**{meta['asset']}** · {meta['type']} · {meta['country']} · "
        f"**{meta['capacity_ac_mw']} MW AC / {meta['capacity_dc_kwp']/1000:.1f} MWp DC** · "
        f"period **{meta['period_start']} → {meta['period_end']}**. "
        "Solar KPIs are grouped by how many of the three survey reviewers selected them — "
        "**KPIs nobody selected are hidden as noise**. "
        "Every shown KPI has a graph; where the Tinte technical feed lacks the inputs, a placeholder is "
        "shown with a note of what's missing."
    )

    # ---- Asset headline ----
    c = st.columns(6)
    c[0].metric("Generation (Apr)", f"{report['actual_gen_mwh']:,} MWh", f"{report['pct_of_budget']}% of budget")
    c[1].metric("Budget", f"{report['budget_gen_mwh']:,} MWh")
    c[2].metric("Irradiation", f"{report['actual_radiation_kwh_m2']} kWh/m²", f"vs {report['budget_radiation_kwh_m2']} budget")
    c[3].metric("Peak power", f"{meta['peak_mw']} MW")
    c[4].metric("PR (proxy)", f"{meta['avg_pr']:.2f}")
    c[5].metric("Faulty strings", f"{report['strings']['faulty']}/{report['strings']['total']}")
    st.markdown("---")

    # ---- Survey tally → sections by vote count ----
    responses = load_responses()
    n = len(responses)
    tally = build_tally(responses)
    votes_by_id = dict(zip(tally["id"], tally["Votes"]))
    must_by_id = dict(zip(tally["id"], tally["Must-have"]))

    if n:
        shown_ids = [k for k in KPI_BY_ID if int(votes_by_id.get(k, 0)) >= 1]
        live_ct = sum(1 for k in shown_ids if k in RENDERERS)
        hidden_ct = len(KPI_BY_ID) - len(shown_ids)
        st.caption(f"Showing {len(shown_ids)} KPIs selected by ≥1 reviewer "
                   f"({live_ct} live from Tinte data, {len(shown_ids) - live_ct} placeholder). "
                   f"{hidden_ct} KPIs selected by nobody are hidden as noise.")

    ctx = {"daily": daily, "meta": meta, "report": report}

    def kpi_status(kid):
        if kid in NOTES:
            return NOTES[kid][0], NOTES[kid][1]
        cat = KPI_BY_ID[kid]["category"]
        return "missing", NOTE_BY_CAT.get(cat, "Not available from this feed.")

    def render_card(kid, col, v):
        kpi = KPI_BY_ID[kid]
        status, note = kpi_status(kid)
        must = must_by_id.get(kid, 0)
        parts = [CATEGORIES[kpi["category"]][0]]
        if n:
            parts.append(f"votes {v}/{n}")
        if must:
            parts.append(f"★ must-have ×{must}")
        parts.append(_status_badge(status))
        with col:
            with st.container(border=True):
                st.markdown(f"**{kpi['name']}**  \n"
                            f"<span style='font-size:0.8rem;color:#666'>{' · '.join(parts)}</span>",
                            unsafe_allow_html=True)
                fig = RENDERERS[kid](ctx) if kid in RENDERERS else _placeholder_fig(NOTE_BY_CAT.get(kpi["category"], ""))
                st.plotly_chart(fig, use_container_width=True, key=f"tinte_{kid}")
                icon = {"available": "✅", "partial": "🟡", "missing": "⚪"}[status]
                st.caption(f"{icon} {note}")

    def render_section(title, ids, v):
        ids = sorted(ids, key=lambda k: (k not in RENDERERS, list(CATEGORIES).index(KPI_BY_ID[k]["category"])))
        st.header(f"🗳️ {title}  ·  {len(ids)} KPI{'s' if len(ids) != 1 else ''}")
        cols = st.columns(2)
        for i, kid in enumerate(ids):
            render_card(kid, cols[i % 2], v)

    if n == 0:
        st.info("No survey responses in `survey/responses/` yet — showing **all 35 KPIs**. "
                "Add reviewers' `kpi-selections-*.csv` files to `survey/responses/` to prioritise and "
                "section the KPIs by how many of them selected each one.")
        render_section("All KPIs", list(KPI_BY_ID), 0)
    else:
        groups = {}
        for kid in KPI_BY_ID:
            groups.setdefault(int(votes_by_id.get(kid, 0)), []).append(kid)
        for v in range(n, 0, -1):  # skip the 0-vote group (selected by nobody) — noise
            ids = groups.get(v, [])
            if not ids:
                continue
            label = f"all {n}" if v == n else f"{v} of {n}"
            render_section(f"Selected by {label} reviewers", ids, v)

    # ---- Data & documents required for full coverage ----
    st.markdown("---")
    st.header("📋 Data & documents required for full coverage")
    st.markdown(
        "What it takes to light up **all 35 KPIs** for Tinte. The current feed is technical-only "
        "(SCADA + monthly technical report); below is the deduplicated list of feeds/documents, who "
        "provides each, and how many KPIs it unlocks — with full per-KPI detail underneath."
    )

    mf = MODO_FINDING or {}
    if not mf.get("solar_benchmark_found", False):
        st.warning(
            "🔎 **Modo benchmark search (25 endpoints probed):** no Netherlands-solar benchmark exists in "
            "Modo's API — its accessible data is **GB battery-storage only** (ME-BESS-GB), and a "
            "`technology=solar` filter is silently ignored. For solar capture-price benchmarking use "
            "**EPEX / ENTSO-E NL day-ahead** (generation-weighted) plus a merchant curve (Aurora / Baringa)."
        )
    else:
        st.success("🔎 Modo benchmark found — " + mf.get("finding", ""))

    master = build_master_sources(SOLAR_DATA_REQUIREMENTS)
    to_collect = sum(1 for r in master if r["Status"].startswith("⚪"))
    st.markdown(f"#### 🧾 Documents / data feeds to collect — {to_collect} sources")
    st.dataframe(pd.DataFrame(master), use_container_width=True, hide_index=True)

    st.markdown("#### 🔬 Per-KPI requirements (all 35)")
    _st_icon = {"have": "🟢 have", "partial": "🟡 partial", "missing": "⚪ missing"}
    for cat in SOLAR_DATA_REQUIREMENTS:
        with st.expander(f"{cat['category']} — {len(cat['kpis'])} KPIs"):
            rows = [{
                "KPI": k["name"],
                "Status": _st_icon.get(k["tinte_status"], k["tinte_status"]),
                "Data required": " · ".join(k.get("required_data", [])),
                "Source documents": " · ".join(k.get("source_documents", [])),
                "Provider": k.get("provider", ""),
                "Cadence": k.get("cadence", ""),
            } for k in cat["kpis"]]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with st.expander("ℹ️ Data sources & coverage"):
        st.markdown(
            f"- **Tinte.xlsx** (Apr-2026 SCADA): weather (irradiance/temp), plant + per-inverter AC power, "
            f"PPC setpoint, string DC current, grid meter → `data/tinte/*.parquet`.\n"
            f"- **Monthly technical report** (Apr-26): budget {report['budget_gen_mwh']:,} MWh, "
            f"radiation {report['actual_radiation_kwh_m2']} kWh/m², energy loss waterfall, string health.\n"
            f"- Metered generation **{meta['total_energy_mwh']:,} MWh** matches the report's "
            f"{report['actual_gen_mwh']:,} MWh.\n"
            f"- {report['note']}\n"
            "- **Missing across the board:** revenue/£, market prices, cash flow, debt/covenants, contracts, "
            "O&M cost — the Tinte feed is technical-only, so all financial & market KPIs are placeholders."
        )
