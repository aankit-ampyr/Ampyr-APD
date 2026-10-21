"""
Elsterheide Solar Dashboard.

Slim, meter-only view of the Elsterheide PV site (Saxony, Germany): export energy
per metering group and grid connection, daily profile, ceilings, data gaps and
daylight outages — from the portal's 5-minute Janitza feeder-meter exports
materialised by data_cleaning.process_elsterheide. No irradiance, inverter,
price or settlement data exists yet, so PR, availability and revenue KPIs are
not shown; the "What is missing" expander lists what unlocks them.
"""
from __future__ import annotations

import os
import sys

_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# One module name only — never a `src.`-prefixed fallback (see the note in
# data_cleaning/__init__.py about the Streamlit import deadlock).
from data_cleaning.process_elsterheide import (
    read_daily, read_group_15min, read_meta, GROUPS,
)

# Confidential, local-only contract parameters (git-ignored). Absent on Streamlit
# Cloud — the budget comparison is simply not rendered there.
try:
    from data_cleaning.elsterheide_contract import ELSTERHEIDE_EPC
except ImportError:
    ELSTERHEIDE_EPC = None

COLOUR = {"1&2": "#2C4B78", "3 (TR102)": "#F18805", "4 (TR101)": "#7BC8F6"}
CEILING_TOL = 0.01      # a 15-min interval is "at the ceiling" within 1% of the month's max
DAYLIGHT_FRAC = 0.05    # another group above 5% of its month peak => it is daylight


def _episodes(mask: pd.Series) -> list[tuple]:
    """Runs of consecutive True values -> [(start, end, n)] on a time-indexed mask."""
    out, start, prev, n = [], None, None, 0
    for t, v in mask.items():
        if v and start is None:
            start, n = t, 0
        if v:
            n += 1
            prev = t
        elif start is not None:
            out.append((start, prev, n))
            start = None
    if start is not None:
        out.append((start, prev, n))
    return out


def _events(wide: pd.DataFrame) -> pd.DataFrame:
    """Data gaps and daylight zero-export runs per group, from the 15-min group pivot."""
    rows = []
    peaks = wide.max()
    for g in wide.columns:
        others = [c for c in wide.columns if c != g]
        daylight = (wide[others].gt(peaks[others] * DAYLIGHT_FRAC)).any(axis=1) if others else pd.Series(False, index=wide.index)
        for start, end, n in _episodes(wide[g].isna()):
            rows.append((g, "data gap", start, end, n))
        for start, end, n in _episodes(wide[g].eq(0) & daylight):
            rows.append((g, "zero export in daylight", start, end, n))
    ev = pd.DataFrame(rows, columns=["Group", "Type", "From (label)", "To (label)", "15-min intervals"])
    ev = ev[ev["15-min intervals"] >= 2].sort_values("From (label)").reset_index(drop=True)
    ev["Hours"] = ev["15-min intervals"] / 4.0
    return ev


def show_elsterheide_dashboard():
    meta = read_meta()
    daily = read_daily()
    g15 = read_group_15min()

    st.title("☀️ Elsterheide — Solar Dashboard")
    if not meta or daily.empty or g15.empty:
        st.error("Elsterheide data not found. Run `python -m src.data_cleaning.process_elsterheide` first "
                 "(reads raw/Elsterheide/*.xlsx).")
        return

    parks = meta["epc_parks"]
    st.markdown(
        f"**{meta['asset']}** · {meta['type']} · {meta['location']} · "
        f"park 1+2 **{parks['1+2']['dc_kwp']/1000:.1f} MWp** (UW Neuwiese) + "
        f"park 3+4 **{parks['3+4']['dc_kwp']/1000:.1f} MWp** (UW Bluno) · "
        f"data **{meta['period_start']} → {meta['period_end']}**, 5-min feeder-meter export energy."
    )
    st.caption(
        "Groups **3 (TR102)** and **4 (TR101)** are transformer-feeder groups on the Bluno connection, not the EPC's "
        "ELST 3 / ELST 4 fields — per-group kWp is unknown, so yields are shown per EPC park only. "
        "Flagged assumptions: interval labels are period-end; the two 1&2 meters (H01 + H02) are additive; "
        "timestamps are plant-local time. Blanks in the export are missing data, never zero."
    )

    # ---- month selector ----
    daily["date"] = pd.to_datetime(daily["date"])
    g15["time"] = pd.to_datetime(g15["time"])
    months = sorted(daily["date"].dt.to_period("M").unique())
    sel = st.selectbox("Month", [str(m) for m in months], index=len(months) - 1)
    period = pd.Period(sel, "M")
    d = daily[daily["date"].dt.to_period("M") == period]
    g = g15[(g15["time"] - pd.Timedelta(minutes=15)).dt.to_period("M") == period]
    wide = g.pivot(index="time", columns="group", values="power_mw").reindex(columns=[c for c in GROUPS if c in g["group"].unique()])

    # ---- headline metrics per group ----
    energy = d.groupby("group")["energy_mwh"].sum()
    present = d.groupby("group")["n_present"].sum() / d.groupby("group")["n_rows"].sum() * 100
    peak = wide.max()
    at_ceiling = {c: int((wide[c] >= peak[c] * (1 - CEILING_TOL)).sum()) for c in wide.columns}
    cols = st.columns(len(wide.columns) + 1)
    for col, grp in zip(cols, wide.columns):
        with col:
            st.markdown(f"**{grp}** · {meta['groups'][grp]['connection'].split(' (')[0]}")
            st.metric("Export", f"{energy[grp]:,.0f} MWh",
                      None if present[grp] >= 99.95 else f"-{100 - present[grp]:.1f}% data missing")
            st.metric("Peak (15-min)", f"{peak[grp]:.2f} MW")
            st.metric("At ceiling (±1%)", f"{at_ceiling[grp] / 4:.2f} h")
    with cols[-1]:
        st.markdown("**Site**")
        st.metric("Export", f"{energy.sum():,.0f} MWh")
        site = wide.dropna().sum(axis=1)
        st.metric("Peak (15-min)", f"{site.max():.2f} MW" if len(site) else "n/a")
        st.metric("Days", f"{d['date'].nunique()}")

    park_rows = []
    for park, info in parks.items():
        grps = [x for x in info["groups"] if x in energy.index]
        if not grps:
            continue
        mwh = float(energy[grps].sum())
        incomplete = int((~d[d["group"].isin(grps)]["complete"]).sum())
        park_rows.append({
            "EPC park": park, "Groups": ", ".join(grps), "DC capacity (kWp)": f"{info['dc_kwp']:,.2f}",
            "Export (MWh)": f"{mwh:,.1f}", "Specific yield (kWh/kWp)": f"{mwh * 1000 / info['dc_kwp']:.1f}",
            "Group-days with missing data": incomplete,
        })
    st.dataframe(pd.DataFrame(park_rows), use_container_width=True, hide_index=True)
    st.caption("Specific yield is understated on any park with missing intervals — gaps are not filled.")

    # ---- daily energy ----
    st.subheader("Daily export by group")
    fig = go.Figure()
    for grp in wide.columns:
        dd = d[d["group"] == grp]
        fig.add_bar(x=dd["date"], y=dd["energy_mwh"], name=grp, marker_color=COLOUR.get(grp),
                    customdata=dd[["n_present", "n_rows"]].values,
                    hovertemplate="%{x|%d %b}: %{y:,.1f} MWh<br>%{customdata[0]}/%{customdata[1]} intervals present<extra>" + grp + "</extra>")
    fig.update_layout(barmode="stack", height=360, margin=dict(l=10, r=10, t=10, b=10),
                      yaxis_title="MWh", legend_orientation="h")
    st.plotly_chart(fig, use_container_width=True, key="elst_daily")

    # ---- 15-min power + average profile ----
    c1, c2 = st.columns([3, 2])
    with c1:
        st.subheader("15-min average power")
        fig = go.Figure()
        for grp in wide.columns:
            fig.add_scatter(x=wide.index, y=wide[grp], name=grp, mode="lines", line=dict(width=1, color=COLOUR.get(grp)))
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="MW", legend_orientation="h")
        st.plotly_chart(fig, use_container_width=True, key="elst_15min")
        st.caption("Gaps are missing data. Flat tops are export ceilings (1&2 ≈ 51 MW, 3 (TR102) ≈ 38 MW in August 2026) — "
                   "no agreed export limit is documented.")
    with c2:
        st.subheader("Average daily profile")
        prof = wide.groupby(wide.index.time).mean()
        fig = go.Figure()
        for grp in wide.columns:
            fig.add_scatter(x=[t.strftime("%H:%M") for t in prof.index], y=prof[grp], name=grp, mode="lines",
                            line=dict(color=COLOUR.get(grp)))
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="MW", legend_orientation="h",
                          xaxis=dict(nticks=12))
        st.plotly_chart(fig, use_container_width=True, key="elst_profile")

    # ---- budget vs actual (local-only contract module) ----
    if ELSTERHEIDE_EPC:
        st.subheader("Export vs PVsyst budget (EPC, pre-construction)")
        rows = []
        for park, info in parks.items():
            budget = ELSTERHEIDE_EPC[park]["budget_kwh_monthly"][period.month - 1] / 1000.0
            grps = [x for x in info["groups"] if x in energy.index]
            if not grps:
                continue
            actual = float(energy[grps].sum())
            rows.append({"EPC park": park, "Budget (MWh)": f"{budget:,.0f}", "Actual (MWh)": f"{actual:,.1f}",
                         "Actual / budget": f"{actual / budget * 100:.1f}%",
                         "Guaranteed PR (month)": f"{ELSTERHEIDE_EPC[park]['guaranteed_pr_monthly_pct'][period.month - 1]:.2f}%"})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption("Budget = PVsyst monthly energy at the 33 kV plant output from the 2024 EPC annexes, not an as-built "
                   "model. Guaranteed PR needs POA irradiance and module temperature to measure — not in the feed.")

    # ---- events ----
    st.subheader("Data gaps and daylight outages")
    ev = _events(wide)
    if ev.empty:
        st.info("No gaps or daylight zero-export runs of 30 minutes or more.")
    else:
        st.dataframe(ev, use_container_width=True, hide_index=True)
        st.caption("Zero export while another group is producing = outage, grid event or curtailment; the cause is not "
                   "determinable from meter data. Partial reductions (e.g. group 4 at ~80% for much of August 2026) "
                   "are visible in the 15-min chart but not listed here.")

    with st.expander("ℹ️ What is missing, and what it would unlock"):
        st.markdown(
            "- **As-built single-line diagrams + kWp per meter** (ASE / Goldbeck) — confirms H01 + H02 additivity and "
            "lets yields be normalised per group.\n"
            "- **Weather-station data** (POA / GHI, ambient and module temperature; 4 stations per park) — PR against the "
            "guaranteed 80.81% (1+2) / 81.46% (3+4).\n"
            "- **Portal facts** (vendor, interval-label convention, time zone, API) + re-export of 23–25 Aug 2026 — "
            "removes the flagged assumptions and the 1&2 gap.\n"
            "- **DE-LU day-ahead prices** (Ampyr-Epex / SMARD) — capture price and negative-price exposure.\n"
            "- **Curtailment / Redispatch records, inverter and alarm logs, O&M log** — availability, MTTR, event causes.\n"
            "- **Direct-marketing agreement + settlement statements, EEG terms, settlement-meter volumes** — revenue KPIs.\n"
            "- **BESS** (Sungrow, 20.16 MW / 76.5 MWh usable, inside park 1+2): no operating data or EMS signal list yet."
        )
