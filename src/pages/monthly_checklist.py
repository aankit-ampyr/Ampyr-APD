"""
Monthly Analysis & Checklist Page

Per-month consolidated view bringing together:
- SCADA operational metrics (RTE, SOH, cycles, availability)
- Benchmark comparison (Modo Energy, annualised revenue)
- IAR variance analysis (projected vs actual per stream)
- Invoice status (EMR capacity market, Hartree, GridBeyond summary)
- Items to check and consider for each month
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import os
import sys
import openpyxl

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_cleaning.invoice_loader import (
    load_emr_capacity_market,
    load_summary_statement,
    load_hartree_bess_readings,
    load_hartree_pv_readings,
    load_scada_monitoring,
)

# Paths
RAW_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'raw', 'New')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
IAR_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'extra', 'Northwold BESS Revenue_IAR.xlsx')

# Colors
COLOR_OK = '#27AE60'
COLOR_WARNING = '#F39C12'
COLOR_ERROR = '#E74C3C'
COLOR_ACTUAL = '#3498db'
COLOR_IAR = '#9467BD'
COLOR_MODO = '#F18805'
COLOR_SFFR = '#2C4B78'

# Asset specs
CAPACITY_MWH = 8.4
CAPACITY_MW = 4.2
WARRANTY_DAILY_CYCLES = 1.5

# Month configurations
MONTH_CONFIG = [
    ('Sep 25', 'September 2025', 30, 'Master_BESS_Analysis_Sept_2025.csv', 'Optimized_Results_Sept_2025.csv'),
    ('Oct 25', 'October 2025', 31, 'Master_BESS_Analysis_Oct_2025.csv', 'Optimized_Results_Oct_2025.csv'),
    ('Nov 25', 'November 2025', 30, 'Master_BESS_Analysis_Nov_2025.csv', 'Optimized_Results_Nov_2025.csv'),
    ('Dec 25', 'December 2025', 31, 'Master_BESS_Analysis_Dec_2025.csv', 'Optimized_Results_Dec_2025.csv'),
    ('Jan 26', 'January 2026', 31, 'Master_BESS_Analysis_Jan_2026.csv', 'Optimized_Results_Jan_2026.csv'),
]

# Modo Energy monthly benchmark (£/MW/year)
MODO_BENCHMARKS = {
    'Sep 25': 70000, 'Oct 25': 77000, 'Nov 25': 59000,
    'Dec 25': 47000, 'Jan 26': 88000,
}

# CM actuals from EMR Settlement
CM_ACTUALS = {
    'Oct 25': 1704.17, 'Nov 25': 1884.42,
    'Dec 25': 1994.84, 'Jan 26': 2113.87,
}

# DUoS actuals from Hartree Partners invoices
DUOS_ACTUALS = {
    'Sep 25': {'red': -322.81, 'amber': -410.03, 'green': -43.94,
               'fixed': 3.58, 'net_credit': 773.20},
    'Oct 25': {'red': -5500.11, 'amber': -268.35, 'green': -42.92,
               'fixed': 3.70, 'net_credit': 5807.68},
    'Nov 25': {'red': -5379.73, 'amber': -106.41, 'green': -42.54,
               'fixed': 3.58, 'net_credit': 5525.10},
}

# IAR stream names
IAR_STREAMS = [
    'Wholesale Day Ahead', 'Wholesale Intraday', 'Balancing Mechanism',
    'Frequency Response', 'Capacity Market', 'DUoS Battery',
    'DUoS Fixed Charges', 'TNUoS', 'Imbalance Revenue', 'Imbalance Charge',
    'TOTAL (excl. BM, TNUoS)', 'TOTAL (all streams)',
]


# ─────────────────────────────────────────────────────────────
# Data Loading
# ─────────────────────────────────────────────────────────────

def _safe_sum(df, col):
    if col in df.columns:
        return pd.to_numeric(df[col], errors='coerce').fillna(0).sum()
    return 0.0


@st.cache_data
def _load_master(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return None
    return pd.read_csv(filepath)


@st.cache_data
def _load_optimized(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return None
    return pd.read_csv(filepath)


@st.cache_data
def _load_iar_projections():
    """Load IAR projections from Excel."""
    try:
        wb = openpyxl.load_workbook(IAR_FILE, data_only=True)
        ws = wb['Sheet1']
        iar_mw = 4.2

        col_map = {11: 'Sep 25', 12: 'Oct 25', 13: 'Nov 25', 14: 'Dec 25', 15: 'Jan 26'}
        stream_rows = [4, 5, 6, 7, 8, 9, 10, 11]

        result = {}
        for col_idx, short in col_map.items():
            vals = []
            for row in stream_rows:
                raw = ws.cell(row=row, column=col_idx).value or 0
                vals.append(round(raw * iar_mw))
            vals.extend([0, 0])  # Imbalance Revenue, Imbalance Charge
            total_excl = vals[0] + vals[1] + vals[3] + vals[4] + vals[5] + vals[6]
            total_all = sum(vals[:8])
            vals.extend([total_excl, total_all])
            result[short] = vals
        wb.close()
        return result
    except Exception:
        return {
            'Sep 25': [14343, 4246, 1863, 1383, 4438, 9188, -6462, 835, 0, 0, 27136, 29834],
            'Oct 25': [17178, 4918, 4237, 1038, 4586, 10088, -6678, 863, 0, 0, 31130, 36230],
        }


@st.cache_data
def _load_emr():
    return load_emr_capacity_market(RAW_DIR)


@st.cache_data
def _load_scada():
    return load_scada_monitoring(RAW_DIR)


@st.cache_data
def _load_summary():
    raw_path = Path(RAW_DIR)
    candidates = list(raw_path.glob("Northwold - *.xlsx"))
    if candidates:
        return load_summary_statement(str(candidates[0]))
    return None


def _calculate_revenue(df):
    """Calculate total GridBeyond revenue for a month."""
    sffr = _safe_sum(df, 'SFFR revenues')
    epex = _safe_sum(df, 'EPEX 30 DA Revenue') + _safe_sum(df, 'EPEX DA Revenues')
    ida1 = _safe_sum(df, 'IDA1 Revenue')
    idc = _safe_sum(df, 'IDC Revenue')
    imb_rev = _safe_sum(df, 'Imbalance Revenue')
    imb_charge = _safe_sum(df, 'Imbalance Charge')
    return {
        'sffr': sffr, 'epex': epex, 'ida1': ida1, 'idc': idc,
        'imb_rev': imb_rev, 'imb_charge': imb_charge,
        'gb_total': sffr + epex + ida1 + idc + imb_rev - imb_charge,
    }


def _calculate_cycles(df, capacity_mwh=CAPACITY_MWH, dt_hours=0.5):
    """Calculate cycles using industry standard method (Method B)."""
    for col in ['Physical_Power_MW', 'Power_MW']:
        if col in df.columns:
            power = pd.to_numeric(df[col], errors='coerce').fillna(0)
            energy = power * dt_hours
            discharge = energy[energy > 0].sum()
            charge = abs(energy[energy < 0].sum())
            return (discharge + charge) / 2 / capacity_mwh
    # Fallback: energy volume column
    for col in df.columns:
        if 'Battery MWh' in col:
            energy = pd.to_numeric(df[col], errors='coerce').fillna(0)
            discharge = energy[energy > 0].sum()
            charge = abs(energy[energy < 0].sum())
            return (discharge + charge) / 2 / capacity_mwh
    return None


def _get_scada_metrics(df):
    """Extract SCADA health metrics from Master CSV."""
    metrics = {}
    if 'SCADA_RTE' in df.columns:
        rte = pd.to_numeric(df['SCADA_RTE'], errors='coerce').dropna()
        metrics['rte'] = rte.iloc[-1] if len(rte) > 0 else None
    if 'SCADA_SOH' in df.columns:
        soh = pd.to_numeric(df['SCADA_SOH'], errors='coerce').dropna()
        metrics['soh'] = soh.iloc[-1] if len(soh) > 0 else None
    if 'SCADA_Availability' in df.columns:
        avail = pd.to_numeric(df['SCADA_Availability'], errors='coerce').dropna()
        metrics['availability'] = avail.mean() if len(avail) > 0 else None
    if 'SCADA_Inverter_Availability' in df.columns:
        inv_avail = pd.to_numeric(df['SCADA_Inverter_Availability'], errors='coerce').dropna()
        metrics['inverter_availability'] = inv_avail.mean() if len(inv_avail) > 0 else None
    if 'SCADA_Cumulative_Cycles' in df.columns:
        cum = pd.to_numeric(df['SCADA_Cumulative_Cycles'], errors='coerce').dropna()
        metrics['cumulative_cycles'] = cum.iloc[-1] if len(cum) > 0 else None
    return metrics


# ─────────────────────────────────────────────────────────────
# Main Page
# ─────────────────────────────────────────────────────────────

def show_monthly_checklist():
    """Display per-month analysis and checklist page."""
    st.title("Monthly Analysis & Checklist")
    st.markdown("Per-month consolidated view: SCADA health, benchmarks, IAR variance, invoice status, and items to check")

    # Month selector
    month_options = [(short, full) for short, full, *_ in MONTH_CONFIG]
    selected_idx = st.selectbox(
        "Select Month",
        range(len(month_options)),
        format_func=lambda i: month_options[i][1],
        index=len(month_options) - 1,
    )

    short, full_name, days, master_file, opt_file = MONTH_CONFIG[selected_idx]

    # Load data
    master_df = _load_master(master_file)
    opt_df = _load_optimized(opt_file)
    iar_proj = _load_iar_projections()
    emr = _load_emr()
    scada_monitoring = _load_scada()
    summary = _load_summary()

    if master_df is None:
        st.error(f"Master CSV not found for {full_name}. Expected: data/{master_file}")
        return

    # ─── Compute all metrics ───
    revenue = _calculate_revenue(master_df)
    cycles = _calculate_cycles(master_df)
    scada = _get_scada_metrics(master_df)

    n_days = days
    if 'Timestamp' in master_df.columns:
        master_df['Timestamp'] = pd.to_datetime(master_df['Timestamp'], errors='coerce')
        n_days = master_df['Timestamp'].dt.date.nunique()

    daily_cycles = cycles / n_days if cycles else None
    annual_per_mw = (revenue['gb_total'] / days) * 365 / CAPACITY_MW

    cm = CM_ACTUALS.get(short, 0)
    duos = DUOS_ACTUALS.get(short)
    duos_credit = duos['net_credit'] if duos else 0
    duos_fixed = duos['fixed'] if duos else 0
    total_revenue = revenue['gb_total'] + cm + duos_credit - duos_fixed
    total_annual_per_mw = (total_revenue / days) * 365 / CAPACITY_MW

    modo = MODO_BENCHMARKS.get(short)

    # ─── Layout ───
    _show_header_metrics(short, full_name, revenue, total_revenue, annual_per_mw,
                         total_annual_per_mw, modo, daily_cycles, scada)

    st.divider()

    col_left, col_right = st.columns([3, 2])

    with col_left:
        _show_scada_section(short, full_name, master_df, scada, daily_cycles, cycles, n_days)
        st.divider()
        _show_iar_section(short, full_name, revenue, cm, duos_credit, duos_fixed, iar_proj)

    with col_right:
        _show_benchmark_section(short, full_name, total_annual_per_mw, modo, revenue)
        st.divider()
        _show_invoice_section(short, full_name, emr, summary, duos)

    st.divider()
    _show_checklist(short, full_name, revenue, scada, daily_cycles, modo,
                    total_annual_per_mw, cm, duos, iar_proj, emr, summary)


# ─────────────────────────────────────────────────────────────
# Header Metrics
# ─────────────────────────────────────────────────────────────

def _show_header_metrics(short, full_name, revenue, total_revenue, annual_per_mw,
                          total_annual_per_mw, modo, daily_cycles, scada):
    """Top-level KPI row."""
    cols = st.columns(6)
    cols[0].metric("Total Revenue", f"£{total_revenue:,.0f}",
                   help="GridBeyond + CM + DUoS")
    cols[1].metric("£/MW/year", f"£{total_annual_per_mw:,.0f}",
                   delta=f"{'Above' if modo and total_annual_per_mw > modo else 'Below'} Modo"
                         if modo else None)
    cols[2].metric("Modo Benchmark", f"£{modo:,.0f}" if modo else "N/A")

    if daily_cycles is not None:
        delta = f"{daily_cycles - WARRANTY_DAILY_CYCLES:+.2f} vs limit"
        cols[3].metric("Daily Cycles", f"{daily_cycles:.2f}",
                       delta=delta,
                       delta_color="inverse" if daily_cycles > WARRANTY_DAILY_CYCLES else "normal")
    else:
        cols[3].metric("Daily Cycles", "N/A")

    rte = scada.get('rte')
    cols[4].metric("RTE", f"{rte:.1f}%" if rte else "N/A")

    soh = scada.get('soh')
    cols[5].metric("SOH", f"{soh:.2f}%" if soh else "N/A")


# ─────────────────────────────────────────────────────────────
# SCADA Section
# ─────────────────────────────────────────────────────────────

def _show_scada_section(short, full_name, master_df, scada, daily_cycles, total_cycles, n_days):
    """SCADA operational health metrics."""
    st.subheader("SCADA Operational Health")

    # Metrics grid
    col1, col2, col3, col4 = st.columns(4)

    avail = scada.get('availability')
    col1.metric("Battery Availability",
                f"{avail:.1f}%" if avail else "N/A",
                delta="OK" if avail and avail > 98 else "Low" if avail else None,
                delta_color="normal" if avail and avail > 98 else "inverse")

    inv_avail = scada.get('inverter_availability')
    col2.metric("Inverter Availability",
                f"{inv_avail:.1f}%" if inv_avail else "N/A")

    cum_cycles = scada.get('cumulative_cycles')
    col3.metric("Cumulative Cycles",
                f"{cum_cycles:.1f}" if cum_cycles else "N/A",
                help="Total full equivalent cycles since commissioning")

    col4.metric("Total Cycles (Month)",
                f"{total_cycles:.1f}" if total_cycles else "N/A",
                help=f"Full equivalent cycles in {full_name}")

    # Daily cycles chart
    if 'Timestamp' in master_df.columns and daily_cycles is not None:
        _show_daily_cycles_chart(master_df, n_days)


def _show_daily_cycles_chart(master_df, n_days):
    """Show daily cycling pattern with warranty limit."""
    power_col = None
    for col in ['Physical_Power_MW', 'Power_MW']:
        if col in master_df.columns:
            power_col = col
            break
    if not power_col:
        return

    df = master_df.copy()
    df['date'] = df['Timestamp'].dt.date
    power = pd.to_numeric(df[power_col], errors='coerce').fillna(0)
    energy = power * 0.5
    df['discharge'] = energy.clip(lower=0)
    df['charge'] = energy.clip(upper=0).abs()

    daily = df.groupby('date').agg({'discharge': 'sum', 'charge': 'sum'})
    daily['cycles'] = (daily['discharge'] + daily['charge']) / 2 / CAPACITY_MWH

    fig = go.Figure()
    colors = [COLOR_OK if c <= WARRANTY_DAILY_CYCLES else COLOR_ERROR for c in daily['cycles']]
    fig.add_trace(go.Bar(
        x=daily.index, y=daily['cycles'],
        marker_color=colors, name='Daily Cycles',
    ))
    fig.add_hline(y=WARRANTY_DAILY_CYCLES, line_dash='dash', line_color=COLOR_ERROR,
                  annotation_text=f"Warranty Limit ({WARRANTY_DAILY_CYCLES})")
    fig.update_layout(
        title='Daily Cycling Pattern',
        yaxis_title='Full Equivalent Cycles',
        height=280, margin=dict(t=40, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# Benchmark Section
# ─────────────────────────────────────────────────────────────

def _show_benchmark_section(short, full_name, total_annual_per_mw, modo, revenue):
    """Benchmark comparison gauge and context."""
    st.subheader("Benchmark Position")

    # Industry thresholds
    MODO_LOW = 36000
    MODO_MID = 60000
    MODO_HIGH = 88000

    if modo:
        pct_of_modo = total_annual_per_mw / modo * 100

        # Gauge-style indicator
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=total_annual_per_mw,
            delta={'reference': modo, 'relative': False, 'valueformat': ',.0f', 'prefix': '£'},
            title={'text': '£/MW/year'},
            gauge={
                'axis': {'range': [0, max(MODO_HIGH * 1.5, total_annual_per_mw * 1.2)]},
                'bar': {'color': COLOR_ACTUAL},
                'steps': [
                    {'range': [0, MODO_LOW], 'color': '#FFE0E0'},
                    {'range': [MODO_LOW, MODO_MID], 'color': '#FFF3CD'},
                    {'range': [MODO_MID, MODO_HIGH], 'color': '#D4EDDA'},
                    {'range': [MODO_HIGH, MODO_HIGH * 1.5], 'color': '#CCE5FF'},
                ],
                'threshold': {
                    'line': {'color': COLOR_MODO, 'width': 3},
                    'thickness': 0.75,
                    'value': modo,
                },
            },
        ))
        fig.update_layout(height=250, margin=dict(t=40, b=10, l=30, r=30))
        st.plotly_chart(fig, use_container_width=True)

        if total_annual_per_mw >= modo:
            st.success(f"**{pct_of_modo:.0f}%** of Modo benchmark — outperforming industry")
        elif total_annual_per_mw >= modo * 0.8:
            st.warning(f"**{pct_of_modo:.0f}%** of Modo benchmark — within 20% of industry")
        else:
            st.error(f"**{pct_of_modo:.0f}%** of Modo benchmark — significantly below industry")
    else:
        st.info("Modo benchmark not available for this month")

    # Revenue mix
    rev_items = {
        'SFFR': revenue['sffr'],
        'EPEX': revenue['epex'],
        'IDA1': revenue['ida1'],
        'IDC': revenue['idc'],
        'Imbalance': revenue['imb_rev'] - revenue['imb_charge'],
    }
    positive = {k: v for k, v in rev_items.items() if v > 0}
    if positive:
        fig = go.Figure(go.Pie(
            labels=list(positive.keys()),
            values=list(positive.values()),
            hole=0.4,
            marker_colors=[COLOR_SFFR, COLOR_MODO, '#7BC8F6', '#9467BD', '#2CA02C'],
        ))
        fig.update_layout(title='Revenue Mix', height=250, margin=dict(t=40, b=10))
        st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# IAR Section
# ─────────────────────────────────────────────────────────────

def _show_iar_section(short, full_name, revenue, cm, duos_credit, duos_fixed, iar_data):
    """IAR vs Actual per-stream comparison."""
    st.subheader("IAR Variance Analysis")

    iar_vals = iar_data.get(short)
    if not iar_vals:
        st.info(f"No IAR projections available for {full_name}")
        return

    # Build actuals in IAR stream order
    actuals = [
        revenue['epex'],                              # DA
        revenue['ida1'] + revenue['idc'],             # ID (combined)
        None,                                          # BM (not tracked)
        revenue['sffr'],                               # FR
        cm if cm else None,                            # CM
        duos_credit if duos_credit else None,          # DUoS Battery
        -duos_fixed if duos_fixed else None,           # DUoS Fixed
        None,                                          # TNUoS
        revenue['imb_rev'] if revenue['imb_rev'] else None,   # Imbalance Rev
        -revenue['imb_charge'] if revenue['imb_charge'] else None,  # Imbalance Charge
        None,  # TOTAL excl (calculated below)
        None,  # TOTAL all (calculated below)
    ]

    # Calculate totals
    gb_total = revenue['gb_total']
    full_total = gb_total + (cm or 0) + (duos_credit or 0) - (duos_fixed or 0)
    actuals[-2] = gb_total + (cm or 0) + (duos_credit or 0) + (-duos_fixed if duos_fixed else 0)
    actuals[-1] = full_total

    # Build comparison table
    rows = []
    for i, stream in enumerate(IAR_STREAMS):
        iar_val = iar_vals[i] if isinstance(iar_vals[i], (int, float)) else 0
        actual = actuals[i]
        if actual is not None and iar_val != 0:
            var_pct = ((actual - iar_val) / abs(iar_val)) * 100
        else:
            var_pct = None
        rows.append({
            'Stream': stream,
            'IAR (£)': iar_val,
            'Actual (£)': actual,
            'Variance %': var_pct,
        })

    iar_df = pd.DataFrame(rows)

    # Highlight key variances
    significant = iar_df[(iar_df['Variance %'].notna()) & (iar_df['Variance %'].abs() > 20)
                         & (~iar_df['Stream'].str.startswith('TOTAL'))]

    if not significant.empty:
        for _, row in significant.iterrows():
            var = row['Variance %']
            icon = "🟢" if var > 0 else "🔴"
            st.markdown(f"{icon} **{row['Stream']}**: {var:+.0f}% vs IAR "
                        f"(£{row['Actual (£)']:,.0f} actual vs £{row['IAR (£)']:,.0f} projected)")

    # Bar chart: IAR vs Actual
    display_streams = [s for s in IAR_STREAMS if s not in ('Imbalance Revenue', 'Imbalance Charge',
                                                            'Balancing Mechanism', 'TNUoS')]
    display_idx = [i for i, s in enumerate(IAR_STREAMS) if s in display_streams]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='IAR Projection',
        x=[IAR_STREAMS[i] for i in display_idx],
        y=[iar_vals[i] for i in display_idx],
        marker_color=COLOR_IAR,
        opacity=0.7,
    ))
    fig.add_trace(go.Bar(
        name='Actual',
        x=[IAR_STREAMS[i] for i in display_idx],
        y=[actuals[i] if actuals[i] is not None else 0 for i in display_idx],
        marker_color=COLOR_ACTUAL,
    ))
    fig.update_layout(
        barmode='group', height=350, margin=dict(t=20, b=20),
        yaxis_title='Revenue (£)',
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Detailed table
    with st.expander("IAR Detailed Comparison"):
        display = iar_df.copy()
        display['IAR (£)'] = display['IAR (£)'].apply(lambda x: f"£{x:,.0f}")
        display['Actual (£)'] = display['Actual (£)'].apply(
            lambda x: f"£{x:,.0f}" if x is not None else '-')
        display['Variance %'] = display['Variance %'].apply(
            lambda x: f"{x:+.0f}%" if x is not None else '-')
        st.dataframe(display, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────
# Invoice Section
# ─────────────────────────────────────────────────────────────

def _show_invoice_section(short, full_name, emr, summary, duos):
    """Invoice status and reconciliation summary."""
    st.subheader("Invoice Status")

    # EMR Capacity Market
    if not emr.empty:
        month_emr = emr[emr['cm_month_label'] == full_name]
        if not month_emr.empty:
            row = month_emr.iloc[0]
            st.markdown(f"**EMR Capacity Market**")
            col1, col2 = st.columns(2)
            col1.metric("Invoice #", f"{int(row['invoice_number'])}")
            col2.metric("Amount", f"£{abs(row['invoice_total']):,.2f}")
            st.caption(f"Invoice Date: {row['invoice_date'].strftime('%d %b %Y')} | "
                       f"Payment Date: {row['payment_date'].strftime('%d %b %Y')} | "
                       f"Weighting: {row['weighting_factor']:.4f}")
        else:
            st.markdown("**EMR Capacity Market**: No invoice for this month")
    else:
        st.markdown("**EMR Capacity Market**: No data available")

    st.markdown("---")

    # DUoS
    if duos:
        st.markdown("**DUoS (Hartree Partners)**")
        col1, col2, col3 = st.columns(3)
        col1.metric("Net Credit", f"£{duos['net_credit']:,.2f}")
        col2.metric("Fixed Charges", f"£{duos['fixed']:,.2f}")
        col3.metric("Red Band", f"£{abs(duos['red']):,.2f}")
    else:
        st.markdown("**DUoS**: Not available for this month")

    st.markdown("---")

    # Summary Statement
    if summary and full_name == 'January 2026':
        st.markdown("**GridBeyond Summary Statement**")
        energy_total = summary['summary']['energy_revenue'].get('_total', 0)
        ancillary_total = summary['summary']['ancillary_revenue'].get('_total', 0)
        sub_total = summary['summary']['energy_revenue'].get('_sub_total', 0)
        col1, col2 = st.columns(2)
        col1.metric("Energy Revenue (Net 93%)", f"£{energy_total:,.2f}")
        col2.metric("Ancillary Revenue (Net 93%)", f"£{ancillary_total:,.2f}")
        st.metric("Sub Total", f"£{sub_total:,.2f}")
    else:
        st.markdown(f"**GridBeyond Summary Statement**: "
                    f"{'Only available for January 2026' if full_name != 'January 2026' else 'Not found'}")


# ─────────────────────────────────────────────────────────────
# Checklist
# ─────────────────────────────────────────────────────────────

def _show_checklist(short, full_name, revenue, scada, daily_cycles, modo,
                     total_annual_per_mw, cm, duos, iar_data, emr, summary):
    """Generate automated checklist items based on data analysis."""
    st.subheader(f"Items to Check — {full_name}")

    checks = []

    # ── SCADA Checks ──
    rte = scada.get('rte')
    if rte is not None:
        if rte < 80:
            checks.append(('error', 'SCADA',
                           f"RTE is {rte:.1f}% — significantly below expected 87%. "
                           "Investigate battery degradation, thermal management, or metering issues."))
        elif rte < 85:
            checks.append(('warning', 'SCADA',
                           f"RTE is {rte:.1f}% — below design spec of 87%. "
                           "Monitor for trend. Check if auxiliary consumption is increasing."))
        else:
            checks.append(('ok', 'SCADA', f"RTE at {rte:.1f}% — within normal range."))

    soh = scada.get('soh')
    if soh is not None:
        if soh < 97:
            checks.append(('warning', 'SCADA',
                           f"SOH at {soh:.2f}% — accelerated degradation detected. "
                           "Review cycling patterns and temperature data."))
        else:
            checks.append(('ok', 'SCADA', f"SOH at {soh:.2f}% — healthy."))

    avail = scada.get('availability')
    if avail is not None:
        if avail < 95:
            checks.append(('error', 'SCADA',
                           f"Battery availability {avail:.1f}% — significant downtime. "
                           "Check for outage events, fault logs, maintenance windows."))
        elif avail < 99:
            checks.append(('warning', 'SCADA',
                           f"Battery availability {avail:.1f}% — some downtime detected. "
                           "Verify planned vs unplanned outages."))
        else:
            checks.append(('ok', 'SCADA', f"Battery availability {avail:.1f}% — excellent."))

    # ── Cycling Checks ──
    if daily_cycles is not None:
        if daily_cycles > WARRANTY_DAILY_CYCLES:
            checks.append(('error', 'Cycling',
                           f"Daily cycles {daily_cycles:.2f} exceed warranty limit of {WARRANTY_DAILY_CYCLES}. "
                           "This will void warranty coverage. Adjust dispatch strategy immediately."))
        elif daily_cycles > WARRANTY_DAILY_CYCLES * 0.8:
            checks.append(('warning', 'Cycling',
                           f"Daily cycles {daily_cycles:.2f} approaching warranty limit ({WARRANTY_DAILY_CYCLES}). "
                           "Consider reducing cycling to maintain headroom."))
        elif daily_cycles < 0.3:
            checks.append(('warning', 'Cycling',
                           f"Daily cycles very low at {daily_cycles:.2f}. "
                           "Asset may be underutilised. Review dispatch strategy for revenue optimisation."))
        else:
            checks.append(('ok', 'Cycling',
                           f"Daily cycles {daily_cycles:.2f} — within warranty limits with good headroom."))

    # ── Benchmark Checks ──
    if modo:
        pct = total_annual_per_mw / modo * 100
        if pct < 60:
            checks.append(('error', 'Benchmark',
                           f"Revenue {pct:.0f}% of Modo benchmark (£{total_annual_per_mw:,.0f} vs £{modo:,.0f}/MW/yr). "
                           "Significantly underperforming. Review market strategy and aggregator performance."))
        elif pct < 80:
            checks.append(('warning', 'Benchmark',
                           f"Revenue {pct:.0f}% of Modo benchmark. "
                           "Below industry average. Compare strategy mix with top-performing assets."))
        elif pct > 120:
            checks.append(('ok', 'Benchmark',
                           f"Revenue {pct:.0f}% of Modo benchmark — outperforming industry by {pct-100:.0f}%."))
        else:
            checks.append(('ok', 'Benchmark',
                           f"Revenue {pct:.0f}% of Modo benchmark — in line with industry."))

    # ── IAR Checks ──
    iar_vals = iar_data.get(short)
    if iar_vals:
        iar_total = iar_vals[-1]  # TOTAL (all streams)
        gb_total = revenue['gb_total']
        full_total = gb_total + cm + (duos['net_credit'] if duos else 0) - (duos['fixed'] if duos else 0)
        if iar_total != 0:
            iar_var = ((full_total - iar_total) / abs(iar_total)) * 100
            if iar_var < -30:
                checks.append(('error', 'IAR',
                               f"Total revenue {iar_var:+.0f}% vs IAR projection. "
                               "Significant underperformance vs investment case. "
                               "Prepare variance explanation for stakeholders."))
            elif iar_var < -10:
                checks.append(('warning', 'IAR',
                               f"Total revenue {iar_var:+.0f}% vs IAR projection. "
                               "Below investment case. Monitor trend."))
            elif iar_var > 20:
                checks.append(('ok', 'IAR',
                               f"Total revenue {iar_var:+.0f}% vs IAR — outperforming investment case."))
            else:
                checks.append(('ok', 'IAR',
                               f"Total revenue {iar_var:+.0f}% vs IAR — tracking investment case."))

        # Check specific streams with large variance
        stream_actuals = {
            'Wholesale Day Ahead': revenue['epex'],
            'Frequency Response': revenue['sffr'],
            'Capacity Market': cm,
        }
        for stream, actual in stream_actuals.items():
            idx = IAR_STREAMS.index(stream)
            iar_stream_val = iar_vals[idx]
            if iar_stream_val != 0 and actual:
                var = ((actual - iar_stream_val) / abs(iar_stream_val)) * 100
                if abs(var) > 50:
                    direction = "above" if var > 0 else "below"
                    checks.append(('warning', 'IAR',
                                   f"**{stream}** is {abs(var):.0f}% {direction} IAR "
                                   f"(£{actual:,.0f} vs £{iar_stream_val:,.0f}). "
                                   "Investigate market conditions or strategy changes."))

    # ── Invoice Checks ──
    if not emr.empty:
        month_emr = emr[emr['cm_month_label'] == full_name]
        if month_emr.empty and short in CM_ACTUALS:
            checks.append(('warning', 'Invoice',
                           "CM payment expected but no EMR invoice found for this month. "
                           "Check if invoice has been received."))
        elif not month_emr.empty:
            checks.append(('ok', 'Invoice',
                           f"EMR Invoice #{int(month_emr.iloc[0]['invoice_number'])} received "
                           f"(£{abs(month_emr.iloc[0]['invoice_total']):,.2f})."))

    if duos:
        checks.append(('ok', 'Invoice', f"DUoS data available — net credit £{duos['net_credit']:,.2f}."))
    elif short in ('Sep 25', 'Oct 25', 'Nov 25'):
        checks.append(('warning', 'Invoice',
                       "DUoS invoice expected but not available. Chase Hartree Partners."))

    if summary and full_name == 'January 2026':
        checks.append(('ok', 'Invoice', "GridBeyond Summary Statement received and parsed."))
    elif full_name in ('November 2025', 'December 2025', 'January 2026'):
        if not summary or full_name != 'January 2026':
            checks.append(('warning', 'Invoice',
                           f"No GridBeyond Summary Statement for {full_name}. "
                           "Request from GridBeyond for revenue reconciliation."))

    # ── Revenue Mix Checks ──
    if revenue['gb_total'] != 0:
        sffr_pct = revenue['sffr'] / revenue['gb_total'] * 100 if revenue['gb_total'] > 0 else 0
        if sffr_pct > 80:
            checks.append(('warning', 'Revenue',
                           f"SFFR concentration at {sffr_pct:.0f}% of total revenue. "
                           "High dependency on a single ancillary service. "
                           "Monitor SFFR clearing prices and consider diversification."))
        if revenue['imb_charge'] > revenue['imb_rev'] * 1.5 and revenue['imb_charge'] > 500:
            checks.append(('warning', 'Revenue',
                           f"Imbalance charges (£{revenue['imb_charge']:,.0f}) significantly exceed "
                           f"imbalance revenue (£{revenue['imb_rev']:,.0f}). "
                           "Review dispatch accuracy and position management."))
        if revenue['epex'] < 0 and abs(revenue['epex']) > 1000:
            checks.append(('warning', 'Revenue',
                           f"Negative EPEX revenue (£{revenue['epex']:,.0f}). "
                           "Buying at higher prices than selling. Review day-ahead strategy."))

    # ── Display Checks ──
    if not checks:
        st.success("No issues identified for this month.")
        return

    # Sort: errors first, then warnings, then ok
    priority = {'error': 0, 'warning': 1, 'ok': 2}
    checks.sort(key=lambda x: (priority[x[0]], x[1]))

    icons = {'error': '🔴', 'warning': '🟡', 'ok': '🟢'}
    error_count = sum(1 for c in checks if c[0] == 'error')
    warning_count = sum(1 for c in checks if c[0] == 'warning')
    ok_count = sum(1 for c in checks if c[0] == 'ok')

    st.caption(f"**{error_count}** issues | **{warning_count}** warnings | **{ok_count}** OK")

    # Show errors and warnings prominently
    for status, category, message in checks:
        if status == 'error':
            st.error(f"{icons[status]} **[{category}]** {message}")
        elif status == 'warning':
            st.warning(f"{icons[status]} **[{category}]** {message}")

    # Show OK items in an expander
    ok_items = [c for c in checks if c[0] == 'ok']
    if ok_items:
        with st.expander(f"Show {len(ok_items)} passed checks"):
            for status, category, message in ok_items:
                st.markdown(f"{icons[status]} **[{category}]** {message}")
