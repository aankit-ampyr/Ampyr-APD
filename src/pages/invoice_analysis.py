"""
Invoice Comparison & Analysis Page

Provides 5-tab interface for reconciling invoices, energy volumes, and revenues
across multiple data sources for Northwold Solar Farm.

Tabs:
    1. Overview — Cross-month summary
    2. Energy Reconciliation — BESS and Solar PV volume comparison
    3. Revenue Reconciliation — Gross vs net, per-stream comparison
    4. Capacity Market — EMR payment tracking and verification
    5. PDF Invoices — Extracted invoice data browser
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_cleaning.process_invoices import (
    read_emr_capacity_market,
    read_emr_invoice_totals,
    read_summary_statement,
    read_hartree_bess_readings,
    read_hartree_pv_readings,
    read_solar_generation,
    read_scada_monitoring,
    read_pdf_invoices,
)
from data_cleaning.invoice_reconciler import (
    reconcile_bess_energy,
    reconcile_solar_pv,
    reconcile_revenue,
    compute_aggregator_fee_breakdown,
    reconcile_capacity_market,
    build_cross_month_summary,
    variance_status,
)

# Pre-processed invoice data is read from data/invoices/. The raw/ folder is
# only touched by src/data_cleaning/process_invoices.py during ETL.

# Color constants (matching dashboard palette)
COLOR_SFFR = '#2C4B78'
COLOR_EPEX = '#F18805'
COLOR_IDA1 = '#7BC8F6'
COLOR_IDC = '#9467BD'
COLOR_IMBALANCE = '#2CA02C'
COLOR_ACTUAL = '#3498db'
COLOR_MULTI_MARKET = '#2CA02C'
COLOR_WARNING = '#F39C12'
COLOR_ERROR = '#E74C3C'
COLOR_OK = '#27AE60'

SOURCE_COLORS = {
    'Master CSV (GridBeyond)': COLOR_ACTUAL,
    'Hartree BESS Readings': COLOR_EPEX,
    'Summary Statement': COLOR_MULTI_MARKET,
    'SCADA Monitoring': COLOR_IDC,
}

STREAM_COLORS = {
    'EPEX DAM 30': COLOR_EPEX,
    'EPEX DAM 60': '#D4770B',
    'IDA1': COLOR_IDA1,
    'IDC': COLOR_IDC,
    'Imbalance': COLOR_IMBALANCE,
    'SFFR': COLOR_SFFR,
    'DC': '#8C564B',
    'DR': '#AEC7E8',
    'DM': '#17BECF',
}


# ─────────────────────────────────────────────────────────────
# Data Loading (cached)
# ─────────────────────────────────────────────────────────────

@st.cache_data
def _load_emr():
    return read_emr_capacity_market()

@st.cache_data
def _load_emr_txt():
    return read_emr_invoice_totals()

@st.cache_data
def _load_summary():
    return read_summary_statement()

@st.cache_data
def _load_hartree_bess():
    return read_hartree_bess_readings()

@st.cache_data
def _load_hartree_pv():
    return read_hartree_pv_readings()

@st.cache_data
def _load_solar_gen():
    return read_solar_generation()

@st.cache_data
def _load_scada():
    return read_scada_monitoring()

@st.cache_data
def _load_pdfs():
    return read_pdf_invoices()


@st.cache_data
def _load_month_master(month: str):
    """Load Master CSV data for a given month directly."""
    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    # Map month names to file patterns
    month_map = {
        'September 2025': 'Master_BESS_Analysis_Sep_2025.csv',
        'October 2025': 'Master_BESS_Analysis_Oct_2025.csv',
        'November 2025': 'Master_BESS_Analysis_Nov_2025.csv',
        'December 2025': 'Master_BESS_Analysis_Dec_2025.csv',
        'January 2026': 'Master_BESS_Analysis_Jan_2026.csv',
        'February 2026': 'Master_BESS_Analysis_Feb_2026.csv',
        'March 2026': 'Master_BESS_Analysis_Mar_2026.csv',
    }
    filename = month_map.get(month)
    if not filename:
        return None
    filepath = os.path.join(data_dir, filename)
    if not os.path.exists(filepath):
        return None
    try:
        return pd.read_csv(filepath)
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
# Main Page Function
# ─────────────────────────────────────────────────────────────

def show_invoice_analysis():
    """Display the Invoice Comparison & Analysis page."""
    st.title("Invoice Comparison & Analysis")
    st.markdown("Reconcile invoices, energy volumes, and revenues across all data sources")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview",
        "Energy Reconciliation",
        "Revenue Reconciliation",
        "Capacity Market",
        "PDF Invoices",
    ])

    with tab1:
        _show_overview_tab()
    with tab2:
        _show_energy_tab()
    with tab3:
        _show_revenue_tab()
    with tab4:
        _show_capacity_market_tab()
    with tab5:
        _show_pdf_invoices_tab()


# ─────────────────────────────────────────────────────────────
# Tab 1: Overview
# ─────────────────────────────────────────────────────────────

def _show_overview_tab():
    """Cross-month summary dashboard."""
    emr = _load_emr()
    summary = _load_summary()

    if emr.empty:
        st.warning("No EMR capacity market data found. Run "
                   "`python -m src.data_cleaning.process_invoices` to ingest raw files.")
        return

    # Key metrics
    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    total_capacity_payments = abs(emr['invoice_total'].sum())
    col1.metric("Capacity Payments", f"£{total_capacity_payments:,.2f}",
                help="Total EMR capacity market payments (Oct'25–Jan'26)")

    num_invoices = len(emr)
    col2.metric("EMR Invoices", f"{num_invoices}",
                help="Number of capacity market invoices")

    if summary:
        sub_total = summary['summary'].get('energy_revenue', {}).get('_sub_total', 0)
        col3.metric("Reported Net Revenue (Jan)", f"£{sub_total:,.2f}",
                    help="Summary Statement sub-total (net 95%, after 5% GridBeyond fee)")
    else:
        col3.metric("Summary Statement", "Not Available")

    avg_payment = total_capacity_payments / num_invoices if num_invoices else 0
    col4.metric("Avg Monthly Payment", f"£{avg_payment:,.2f}")

    # EMR Payments Table
    st.subheader("Capacity Market Payments")
    display_df = emr[['cm_month_label', 'invoice_number', 'invoice_date',
                       'payment_date', 'invoice_total', 'weighting_factor']].copy()
    display_df.columns = ['CM Month', 'Invoice #', 'Invoice Date', 'Payment Date',
                          'Amount (£)', 'Weighting Factor']
    display_df['Invoice Date'] = display_df['Invoice Date'].dt.strftime('%d %b %Y')
    display_df['Payment Date'] = display_df['Payment Date'].dt.strftime('%d %b %Y')
    display_df['Amount (£)'] = display_df['Amount (£)'].apply(lambda x: f"£{x:,.2f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Payment Trend Chart
    st.subheader("Payment Trend")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=emr['cm_month_label'],
        y=abs(emr['invoice_total']),
        name='Monthly Payment',
        marker_color=COLOR_ACTUAL,
        text=[f"£{abs(v):,.2f}" for v in emr['invoice_total']],
        textposition='outside',
    ))
    fig.add_trace(go.Scatter(
        x=emr['cm_month_label'],
        y=abs(emr['invoice_total']).cumsum(),
        name='Cumulative',
        mode='lines+markers',
        yaxis='y2',
        line=dict(color=COLOR_SFFR, width=2),
        marker=dict(size=8),
    ))
    fig.update_layout(
        yaxis=dict(title='Monthly Payment (£)', side='left'),
        yaxis2=dict(title='Cumulative (£)', overlaying='y', side='right'),
        height=400,
        margin=dict(t=20),
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Summary Statement Revenue Breakdown (if available)
    if summary:
        st.subheader("Revenue Breakdown (January 2026 — Summary Statement)")
        energy_rev = summary['summary'].get('energy_revenue', {})
        ancillary_rev = summary['summary'].get('ancillary_revenue', {})

        # Combine all streams (exclude _total, _sub_total)
        streams = {}
        for k, v in energy_rev.items():
            if not k.startswith('_') and v != 0:
                streams[k] = v
        for k, v in ancillary_rev.items():
            if not k.startswith('_') and v != 0:
                streams[k] = v

        if streams:
            col1, col2 = st.columns(2)

            with col1:
                fig = go.Figure(go.Bar(
                    x=list(streams.keys()),
                    y=list(streams.values()),
                    marker_color=[STREAM_COLORS.get(k, COLOR_ACTUAL) for k in streams.keys()],
                    text=[f"£{v:,.2f}" for v in streams.values()],
                    textposition='outside',
                ))
                fig.update_layout(
                    title='Revenue by Stream (Net 95%)',
                    yaxis_title='Revenue (£)',
                    height=350,
                    margin=dict(t=40),
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Only positive values for pie chart
                positive = {k: v for k, v in streams.items() if v > 0}
                if positive:
                    fig = go.Figure(go.Pie(
                        labels=list(positive.keys()),
                        values=list(positive.values()),
                        marker_colors=[STREAM_COLORS.get(k, COLOR_ACTUAL) for k in positive.keys()],
                        textinfo='label+percent',
                        hole=0.4,
                    ))
                    fig.update_layout(
                        title='Revenue Share (Positive Streams)',
                        height=350,
                        margin=dict(t=40),
                    )
                    st.plotly_chart(fig, use_container_width=True)

        # Market Commentary
        if summary.get('commentary'):
            st.subheader("Market Commentary")
            st.info(summary['commentary'])


# ─────────────────────────────────────────────────────────────
# Tab 2: Energy Reconciliation
# ─────────────────────────────────────────────────────────────

def _show_energy_tab():
    """BESS and Solar PV energy volume reconciliation."""
    st.subheader("BESS Energy Volume Reconciliation")

    # Month selector
    available_months = ['November 2025', 'December 2025', 'January 2026']
    selected_month = st.selectbox("Select Month", available_months, key='energy_month')

    # Load all sources
    hartree_bess = _load_hartree_bess()
    scada = _load_scada()
    summary = _load_summary()

    # Load master data for the selected month
    master_df = _load_month_master(selected_month)

    # Summary statement detail (only for January)
    summary_detail = None
    if summary and 'January' in selected_month:
        summary_detail = summary.get('detail')

    # Run BESS reconciliation
    bess_recon = reconcile_bess_energy(
        master_df=master_df,
        hartree_bess=hartree_bess,
        summary_detail=summary_detail,
        scada_df=scada,
        month_label=selected_month,
    )

    if bess_recon.empty:
        st.warning(f"No BESS energy data available for {selected_month}")
    else:
        # Metric cards
        cols = st.columns(len(bess_recon))
        for i, (_, row) in enumerate(bess_recon.iterrows()):
            with cols[i]:
                delta = None
                if i > 0 and 'export_variance_pct' in bess_recon.columns:
                    var_pct = row.get('export_variance_pct', 0)
                    delta = f"{var_pct:+.2f}% vs baseline"
                st.metric(
                    row['source'],
                    f"{row['export_mwh']:.1f} MWh (export)",
                    delta=delta,
                )

        # Comparison bar chart
        fig = go.Figure()
        for _, row in bess_recon.iterrows():
            color = SOURCE_COLORS.get(row['source'], COLOR_ACTUAL)
            fig.add_trace(go.Bar(
                name=row['source'],
                x=['Import', 'Export'],
                y=[row['import_mwh'], row['export_mwh']],
                marker_color=color,
                text=[f"{row['import_mwh']:.1f}", f"{row['export_mwh']:.1f}"],
                textposition='outside',
            ))
        fig.update_layout(
            title=f'BESS Energy Volumes — {selected_month}',
            yaxis_title='Energy (MWh)',
            barmode='group',
            height=400,
            margin=dict(t=40),
            legend=dict(orientation='h', yanchor='bottom', y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Detailed table with export
        with st.expander("Detailed Comparison Table"):
            st.dataframe(bess_recon.round(3), use_container_width=True, hide_index=True)
            st.download_button(
                "Download as CSV",
                bess_recon.round(3).to_csv(index=False),
                f"bess_energy_recon_{selected_month.replace(' ', '_')}.csv",
                "text/csv",
            )

    # Solar PV Section
    st.divider()
    st.subheader("Solar PV Generation Reconciliation")

    hartree_pv = _load_hartree_pv()
    solar_gen = _load_solar_gen()

    pv_recon = reconcile_solar_pv(solar_gen, hartree_pv)

    if pv_recon.empty:
        st.warning("No Solar PV reconciliation data available")
    else:
        # Summary metrics
        total_gen = pv_recon['allocated_kwh'].sum()
        total_invoiced = pv_recon['invoiced_kwh'].sum()
        total_under_over = pv_recon['under_over_kwh'].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Generation", f"{total_gen/1000:,.1f} MWh")
        col2.metric("Total Invoiced", f"{total_invoiced/1000:,.1f} MWh")
        col3.metric("Under/(Over) Invoiced", f"{total_under_over/1000:,.1f} MWh",
                     delta=f"£{total_under_over * 0.1:,.2f} at £0.10/kWh")

        # Under/over invoiced bar chart by month
        display = pv_recon[pv_recon['month'] != 'Grand Total'].copy()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=display['month'],
            y=display['under_over_kwh'] / 1000,
            marker_color=[COLOR_OK if v > 0 else COLOR_ERROR for v in display['under_over_kwh']],
            text=[f"{v/1000:.1f}" for v in display['under_over_kwh']],
            textposition='outside',
        ))
        fig.update_layout(
            title='Under/(Over) Invoiced by Month (MWh)',
            yaxis_title='MWh (positive = under-invoiced)',
            height=350,
            margin=dict(t=40),
        )
        fig.add_hline(y=0, line_dash='dash', line_color='gray')
        st.plotly_chart(fig, use_container_width=True)

        # Detailed table
        with st.expander("Solar PV Detailed Table"):
            display_table = pv_recon.copy()
            display_table['allocated_kwh'] = display_table['allocated_kwh'].apply(lambda x: f"{x:,.1f}")
            display_table['invoiced_kwh'] = display_table['invoiced_kwh'].apply(lambda x: f"{x:,.1f}")
            display_table['under_over_kwh'] = display_table['under_over_kwh'].apply(lambda x: f"{x:,.1f}")
            st.dataframe(display_table, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────
# Tab 3: Revenue Reconciliation
# ─────────────────────────────────────────────────────────────

def _show_revenue_tab():
    """Revenue reconciliation: gross vs net, per stream."""
    st.subheader("Revenue Reconciliation")

    summary = _load_summary()

    if not summary:
        st.warning("No Summary Statement found. Revenue reconciliation requires "
                   "a `Northwold - *.xlsx` Summary Statement to be present in raw/New/ "
                   "and the ETL to have been run "
                   "(`python -m src.data_cleaning.process_invoices`).")
        st.info("Currently only January 2026 Summary Statement is available.")
        return

    # Load master data for the summary period
    period = summary.get('period', {})
    month_label = 'January 2026'
    if period.get('from'):
        month_label = period['from'].strftime('%B %Y')

    st.caption(f"Comparing Master CSV (gross) vs Summary Statement (net 95%, after 5% GridBeyond fee) for **{month_label}**")

    master_df = _load_month_master(month_label)

    if master_df is None:
        st.warning(f"Could not load Master CSV data for {month_label}")
        return

    # Revenue reconciliation table
    recon = reconcile_revenue(master_df, summary)

    if recon.empty:
        st.warning("No revenue data to reconcile")
        return

    # Aggregator fee breakdown
    fee_breakdown = compute_aggregator_fee_breakdown(master_df, summary)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Gross Revenue", f"£{fee_breakdown['gross']:,.2f}")
    col2.metric("GridBeyond Fee (5%)", f"£{fee_breakdown['fee']:,.2f}")
    col3.metric("Expected Net (95%)", f"£{fee_breakdown['expected_net']:,.2f}")
    col4.metric("Reported Net", f"£{fee_breakdown['reported_net']:,.2f}")
    variance = fee_breakdown['variance']
    col5.metric("Variance", f"£{variance:,.2f}",
                delta=f"{'Over' if variance > 0 else 'Under'} by £{abs(variance):,.2f}")

    # Waterfall chart
    st.subheader("Revenue Waterfall")
    waterfall_labels = ['Gross Revenue', 'GridBeyond Fee (-5%)', 'Expected Net',
                        'Reported Net', 'Variance']
    waterfall_values = [
        fee_breakdown['gross'],
        -fee_breakdown['fee'],
        0,  # subtotal
        fee_breakdown['reported_net'],
        fee_breakdown['variance'],
    ]
    waterfall_measures = ['relative', 'relative', 'total', 'total', 'relative']

    fig = go.Figure(go.Waterfall(
        x=waterfall_labels,
        y=waterfall_values,
        measure=waterfall_measures,
        connector=dict(line=dict(color='rgba(0,0,0,0)')),
        increasing=dict(marker_color=COLOR_OK),
        decreasing=dict(marker_color=COLOR_ERROR),
        totals=dict(marker_color=COLOR_ACTUAL),
        text=[f"£{abs(v):,.2f}" for v in waterfall_values],
        textposition='outside',
    ))
    fig.update_layout(height=400, margin=dict(t=20), yaxis_title='Revenue (£)')
    st.plotly_chart(fig, use_container_width=True)

    # Per-stream comparison table
    st.subheader("Per-Stream Comparison")
    display_recon = recon.copy()

    # Color-code variance
    def format_variance(row):
        v = row['variance']
        if abs(v) < 1:
            return '✓'
        elif abs(v) < 100:
            return '⚠'
        else:
            return '✗'

    display_recon['status'] = display_recon.apply(format_variance, axis=1)

    # Format for display
    for col in ['gross_revenue', 'expected_net', 'reported_net', 'variance']:
        display_recon[col] = display_recon[col].apply(lambda x: f"£{x:,.2f}")
    display_recon['variance_pct'] = display_recon['variance_pct'].apply(lambda x: f"{x:.1f}%")

    display_recon.columns = ['Stream', 'Gross Revenue', 'Expected Net (×0.93)',
                              'Reported Net', 'Variance (£)', 'Variance %', 'Status']
    st.dataframe(display_recon, use_container_width=True, hide_index=True)
    st.download_button(
        "Download Revenue Reconciliation CSV",
        recon.to_csv(index=False),
        f"revenue_recon_{month_label.replace(' ', '_')}.csv",
        "text/csv",
    )

    # Per-stream bar chart
    st.subheader("Revenue by Stream")
    recon_no_total = recon[recon['stream'] != 'TOTAL']
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Gross Revenue',
        x=recon_no_total['stream'],
        y=recon_no_total['gross_revenue'],
        marker_color=COLOR_ACTUAL,
    ))
    fig.add_trace(go.Bar(
        name='Expected Net (×0.93)',
        x=recon_no_total['stream'],
        y=recon_no_total['expected_net'],
        marker_color=COLOR_EPEX,
    ))
    fig.add_trace(go.Bar(
        name='Reported Net',
        x=recon_no_total['stream'],
        y=recon_no_total['reported_net'],
        marker_color=COLOR_MULTI_MARKET,
    ))
    fig.update_layout(
        barmode='group',
        height=400,
        margin=dict(t=20),
        yaxis_title='Revenue (£)',
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Market Commentary
    if summary.get('commentary'):
        st.subheader("Market Commentary")
        st.info(summary['commentary'])


# ─────────────────────────────────────────────────────────────
# Tab 4: Capacity Market
# ─────────────────────────────────────────────────────────────

def _show_capacity_market_tab():
    """EMR capacity market payment tracking and verification."""
    st.subheader("Capacity Market Payment Analysis")

    emr = _load_emr()
    emr_txt = _load_emr_txt()

    if emr.empty:
        st.warning("No EMR capacity market data found")
        return

    # Reconcile and verify
    verified = reconcile_capacity_market(emr)

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Payments", f"£{abs(verified['invoice_total'].sum()):,.2f}")
    col2.metric("Months Covered", f"{len(verified)}")
    col3.metric("Capacity Price", f"£{verified['capacity_price'].iloc[0]:,.2f}/MW")

    all_match = verified['payment_match'].all()
    col4.metric("Formula Verification", "All Match ✓" if all_match else "Mismatch ✗")

    # Verification table
    st.subheader("Payment Verification")
    st.caption("Formula: Payment = Obligation × Price × CPI_Ratio × Monthly_Weighting")

    verify_display = verified[[
        'cm_month_label', 'invoice_number', 'invoice_total',
        'capacity_obligation', 'weighting_factor', 'calculated_payment', 'payment_match'
    ]].copy()
    verify_display.columns = ['CM Month', 'Invoice #', 'Actual Payment (£)',
                               'Obligation (MW)', 'Weighting', 'Calculated (£)', 'Match']
    verify_display['Actual Payment (£)'] = verify_display['Actual Payment (£)'].apply(lambda x: f"£{x:,.2f}")
    verify_display['Calculated (£)'] = verify_display['Calculated (£)'].apply(lambda x: f"£{x:,.2f}")
    verify_display['Match'] = verify_display['Match'].apply(lambda x: '✓' if x else '✗')
    st.dataframe(verify_display, use_container_width=True, hide_index=True)

    # Weighting factor trend
    st.subheader("Monthly Weighting Factors")
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=verified['cm_month_label'],
            y=verified['weighting_factor'],
            marker_color=COLOR_ACTUAL,
            text=[f"{w:.4f}" for w in verified['weighting_factor']],
            textposition='outside',
        ))
        fig.update_layout(
            title='Monthly Weighting Factor',
            yaxis_title='Weighting Factor',
            height=350,
            margin=dict(t=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=verified['cm_month_label'],
            y=abs(verified['cumulative_payment']),
            mode='lines+markers+text',
            text=[f"£{abs(v):,.0f}" for v in verified['cumulative_payment']],
            textposition='top center',
            line=dict(color=COLOR_SFFR, width=3),
            marker=dict(size=10),
        ))
        fig.update_layout(
            title='Cumulative Capacity Payments',
            yaxis_title='Cumulative (£)',
            height=350,
            margin=dict(t=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Cross-validate with TXT files
    if not emr_txt.empty:
        st.subheader("Cross-Validation: CSV vs TXT Sources")
        merged = emr[['invoice_number', 'invoice_total']].merge(
            emr_txt[['invoice_number', 'invoice_total']],
            on='invoice_number',
            suffixes=('_csv', '_txt'),
            how='outer',
        )
        merged['match'] = abs(merged['invoice_total_csv'] - merged['invoice_total_txt']) < 0.01
        merged.columns = ['Invoice #', 'CSV Amount (£)', 'TXT Amount (£)', 'Match']
        merged['CSV Amount (£)'] = merged['CSV Amount (£)'].apply(lambda x: f"£{x:,.2f}" if pd.notna(x) else 'N/A')
        merged['TXT Amount (£)'] = merged['TXT Amount (£)'].apply(lambda x: f"£{x:,.2f}" if pd.notna(x) else 'N/A')
        merged['Match'] = merged['Match'].apply(lambda x: '✓' if x else '✗')
        st.dataframe(merged, use_container_width=True, hide_index=True)

    # Contract details
    with st.expander("Capacity Agreement Details"):
        st.markdown(f"""
        | Field | Value |
        |-------|-------|
        | **Agreement** | {verified['capacity_agreement'].iloc[0]} |
        | **Capacity Obligation** | {verified['capacity_obligation'].iloc[0]} MW |
        | **Capacity Price** | £{verified['capacity_price'].iloc[0]:,.2f}/MW |
        | **Cleared Price** | £{verified['cleared_price'].iloc[0]:,.2f}/MW |
        | **Auction** | {emr['source_file'].iloc[0].split('_')[0]} |
        | **Suspension Flag** | {verified['suspension_flag'].iloc[0]} |
        """)


# ─────────────────────────────────────────────────────────────
# Tab 5: PDF Invoices
# ─────────────────────────────────────────────────────────────

def _show_pdf_invoices_tab():
    """PDF invoice extraction browser."""
    st.subheader("PDF Invoice Extraction")

    try:
        import pdfplumber
        pdfplumber_available = True
    except ImportError:
        pdfplumber_available = False

    if not pdfplumber_available:
        st.error("**pdfplumber** is not installed. Install it with: `pip install pdfplumber`")
        st.code("pip install pdfplumber", language='bash')
        return

    with st.spinner("Extracting data from PDFs..."):
        pdf_data = _load_pdfs()

    if pdf_data.empty:
        st.warning("No PDF invoices found. Run "
                   "`python -m src.data_cleaning.process_invoices` to ingest raw files.")
        return

    # Summary
    type_counts = pdf_data['type'].value_counts()
    st.caption(f"Found **{len(pdf_data)}** PDF files across **{len(type_counts)}** categories")

    col1, col2, col3, col4 = st.columns(4)
    for i, (pdf_type, count) in enumerate(type_counts.items()):
        [col1, col2, col3, col4][i % 4].metric(pdf_type, f"{count} files")

    # Filter by type
    selected_types = st.multiselect(
        "Filter by Type",
        options=sorted(pdf_data['type'].unique()),
        default=sorted(pdf_data['type'].unique()),
    )

    filtered = pdf_data[pdf_data['type'].isin(selected_types)]

    # Display table
    display = filtered[['source_file', 'subfolder', 'type', 'invoice_number', 'date', 'total']].copy()
    display['date'] = pd.to_datetime(display['date']).dt.strftime('%d %b %Y')
    display['total'] = display['total'].apply(lambda x: f"£{x:,.2f}" if pd.notna(x) else 'Not extracted')
    display.columns = ['File', 'Folder', 'Type', 'Invoice #', 'Date', 'Amount']
    st.dataframe(display, use_container_width=True, hide_index=True)

    # Extraction success rate
    st.subheader("Extraction Quality")
    col1, col2, col3 = st.columns(3)

    total = len(filtered)
    extracted_numbers = filtered['invoice_number'].notna().sum()
    extracted_dates = filtered['date'].notna().sum()
    extracted_totals = filtered['total'].notna().sum()

    col1.metric("Invoice # Extracted", f"{extracted_numbers}/{total}",
                delta=f"{extracted_numbers/total*100:.0f}%" if total else "N/A")
    col2.metric("Dates Extracted", f"{extracted_dates}/{total}",
                delta=f"{extracted_dates/total*100:.0f}%" if total else "N/A")
    col3.metric("Amounts Extracted", f"{extracted_totals}/{total}",
                delta=f"{extracted_totals/total*100:.0f}%" if total else "N/A")

    # Raw text viewer
    st.subheader("Raw Text Preview")
    selected_file = st.selectbox(
        "Select PDF to preview",
        options=filtered['source_file'].tolist(),
    )

    if selected_file:
        row = filtered[filtered['source_file'] == selected_file].iloc[0]
        with st.expander(f"Raw text from {selected_file}", expanded=True):
            st.text(row.get('raw_text', 'No text extracted'))
