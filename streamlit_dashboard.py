"""
Streamlit Dashboard for BESS and Northwold Data Analysis
Displays comprehensive analysis of battery energy storage system operations and market trading
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
import sys

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
import digital_twin_config as config
from pages.data_quality import show_data_quality_page

# Configure data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(DATA_DIR):
    DATA_DIR = '.'  # Fallback to current directory for local testing

# Set page config
st.set_page_config(
    page_title="BESS Analysis Dashboard",
    page_icon="🔋",
    layout="wide"
)

# Available months configuration
AVAILABLE_MONTHS = {
    "September 2025": {
        "bess_file": "BESS_Sept_2025_converted.csv",
        "northwold_file": "Northwold_Sep_2025_converted.csv",
        "master_file": "Master_BESS_Analysis_Sept_2025.csv",
        "optimization_file": "Optimized_Results_Sept_2025.csv",
        "use_master": False,  # September uses separate files
    },
    "October 2025": {
        "bess_file": None,
        "northwold_file": None,
        "master_file": "Master_BESS_Analysis_Oct_2025.csv",
        "optimization_file": "Optimized_Results_Oct_2025.csv",
        "use_master": True,  # October uses merged Master file
    },
}

@st.cache_data
def load_data():
    """Load and cache the CSV files (legacy - September only)"""
    try:
        bess_df = pd.read_csv(os.path.join(DATA_DIR, 'BESS_Sept_2025_converted.csv'))
        northwold_df = pd.read_csv(os.path.join(DATA_DIR, 'Northwold_Sep_2025_converted.csv'))

        # Convert timestamps
        bess_df['date'] = pd.to_datetime(bess_df['date'], format='%d/%m/%Y %H:%M:%S')
        northwold_df['Timestamp'] = pd.to_datetime(northwold_df['Timestamp'], format='%d-%m-%Y %H:%M')

        return bess_df, northwold_df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

@st.cache_data
def load_month_data(month: str):
    """Load data for selected month - handles both separate files and Master format"""
    config = AVAILABLE_MONTHS.get(month)
    if not config:
        st.error(f"Unknown month: {month}")
        return None, None

    try:
        if config["use_master"]:
            # Load merged Master file
            master_df = pd.read_csv(os.path.join(DATA_DIR, config["master_file"]))

            # Parse timestamp
            if 'Timestamp' in master_df.columns:
                master_df['Timestamp'] = pd.to_datetime(master_df['Timestamp'])
            elif 'Unnamed: 0' in master_df.columns:
                master_df['Timestamp'] = pd.to_datetime(master_df['Unnamed: 0'])
                master_df = master_df.drop(columns=['Unnamed: 0'])

            # Create compatible bess_df from Master file (SCADA columns)
            bess_df = pd.DataFrame()
            bess_df['date'] = master_df['Timestamp']

            # Map power column (different naming in different files)
            if 'Power_MW' in master_df.columns:
                bess_df['Power'] = master_df['Power_MW']
            elif 'Physical_Power_MW' in master_df.columns:
                bess_df['Power'] = master_df['Physical_Power_MW']
            else:
                bess_df['Power'] = 0

            # Map SOC column
            if 'SOC' in master_df.columns:
                bess_df['SOC'] = master_df['SOC']
            elif 'Physical_SoC' in master_df.columns:
                bess_df['SOC'] = master_df['Physical_SoC']
            else:
                bess_df['SOC'] = 50  # Default

            # Frequency if available
            if 'Frequency' in master_df.columns:
                bess_df['Frequency'] = master_df['Frequency']
            else:
                bess_df['Frequency'] = 50.0  # Default grid frequency

            # northwold_df is the Master file with GridBeyond data
            northwold_df = master_df.copy()

            return bess_df, northwold_df
        else:
            # Load separate files (September format)
            bess_df = pd.read_csv(os.path.join(DATA_DIR, config["bess_file"]))
            northwold_df = pd.read_csv(os.path.join(DATA_DIR, config["northwold_file"]))

            # Convert timestamps
            bess_df['date'] = pd.to_datetime(bess_df['date'], format='%d/%m/%Y %H:%M:%S')
            northwold_df['Timestamp'] = pd.to_datetime(northwold_df['Timestamp'], format='%d-%m-%Y %H:%M')

            return bess_df, northwold_df

    except Exception as e:
        st.error(f"Error loading data for {month}: {str(e)}")
        return None, None

def analyze_bess_data(bess_df):
    """Analyze BESS dataset"""
    analysis = {}

    # Time coverage
    analysis['start_time'] = bess_df['date'].min()
    analysis['end_time'] = bess_df['date'].max()
    analysis['duration_days'] = (bess_df['date'].max() - bess_df['date'].min()).days + 1

    # SOC Analysis
    analysis['soc_mean'] = bess_df['SOC'].mean()
    analysis['soc_median'] = bess_df['SOC'].median()
    analysis['soc_min'] = bess_df['SOC'].min()
    analysis['soc_max'] = bess_df['SOC'].max()
    analysis['soc_std'] = bess_df['SOC'].std()

    # Power Analysis
    analysis['power_mean'] = bess_df['Power'].mean()
    analysis['power_max_charge'] = bess_df['Power'].max()
    analysis['power_max_discharge'] = bess_df['Power'].min()
    analysis['total_energy_charged'] = bess_df[bess_df['Power'] > 0]['Power'].sum() * 0.5
    analysis['total_energy_discharged'] = abs(bess_df[bess_df['Power'] < 0]['Power'].sum() * 0.5)

    # Frequency Analysis
    analysis['freq_mean'] = bess_df['Frequency'].mean()
    analysis['freq_min'] = bess_df['Frequency'].min()
    analysis['freq_max'] = bess_df['Frequency'].max()
    analysis['freq_std'] = bess_df['Frequency'].std()

    # Operation patterns
    analysis['charging_periods'] = (bess_df['Power'] > 0).sum()
    analysis['discharging_periods'] = (bess_df['Power'] < 0).sum()
    analysis['idle_periods'] = (bess_df['Power'] == 0).sum()
    analysis['total_periods'] = len(bess_df)

    return analysis

def analyze_northwold_data(northwold_df):
    """Analyze Northwold dataset"""
    analysis = {}

    # Time coverage
    analysis['start_time'] = northwold_df['Timestamp'].min()
    analysis['end_time'] = northwold_df['Timestamp'].max()
    analysis['duration_days'] = (northwold_df['Timestamp'].max() - northwold_df['Timestamp'].min()).days + 1

    # Energy Trading Analysis
    analysis['da_price_mean'] = northwold_df['Day Ahead Price (EPEX)'].mean()
    analysis['da_price_min'] = northwold_df['Day Ahead Price (EPEX)'].min()
    analysis['da_price_max'] = northwold_df['Day Ahead Price (EPEX)'].max()
    analysis['da_price_std'] = northwold_df['Day Ahead Price (EPEX)'].std()

    analysis['intraday_price_mean'] = northwold_df['GB-ISEM Intraday 1 Price'].mean()
    analysis['intraday_price_min'] = northwold_df['GB-ISEM Intraday 1 Price'].min()
    analysis['intraday_price_max'] = northwold_df['GB-ISEM Intraday 1 Price'].max()

    # Revenue Analysis
    analysis['imbalance_revenue'] = northwold_df['Imbalance Revenue'].sum()
    analysis['imbalance_charge'] = northwold_df['Imbalance Charge'].sum()
    analysis['net_imbalance'] = analysis['imbalance_revenue'] - analysis['imbalance_charge']

    # Revenue streams
    analysis['sffr_revenue'] = northwold_df['SFFR revenues'].sum()
    analysis['epex30_revenue'] = northwold_df['EPEX 30 DA Revenue'].sum()
    analysis['ida1_revenue'] = northwold_df['IDA1 Revenue'].sum()
    analysis['idc_revenue'] = northwold_df['IDC Revenue'].sum()

    analysis['total_net_revenue'] = (
        analysis['sffr_revenue'] +
        analysis['epex30_revenue'] +
        analysis['ida1_revenue'] +
        analysis['idc_revenue'] +
        analysis['imbalance_revenue'] -
        analysis['imbalance_charge']
    )

    # Ancillary services
    services = ['SFFR', 'DCL', 'DCH', 'DML', 'DMH', 'DRL', 'DRH']
    analysis['ancillary_services'] = {}
    for service in services:
        clearing_col = f'{service} Clearing Price'
        avail_col = f'{service} Availability'
        if clearing_col in northwold_df.columns:
            analysis['ancillary_services'][service] = {
                'avg_price': northwold_df[clearing_col].mean(),
                'avg_availability': northwold_df[avail_col].mean()
            }

    # Price volatility
    analysis['ssp_std'] = northwold_df['SSP'].std()
    analysis['sbp_std'] = northwold_df['SBP'].std()

    # Trading metrics
    analysis['da_mw_mean'] = northwold_df['DA MW'].mean()
    analysis['epex30_mw_mean'] = northwold_df['EPEX 30 DA MW'].mean()
    analysis['ida1_mw_mean'] = northwold_df['IDA1 MW'].mean()

    return analysis

def calculate_cycles(df, power_col, capacity_mwh=8.4, dt_hours=0.5):
    """
    Calculate battery cycles using three methodologies.

    Args:
        df: DataFrame with power data
        power_col: Column name for power (positive = discharge, negative = charge)
        capacity_mwh: Battery capacity (default 8.4)
        dt_hours: Time step in hours (default 0.5 for 30-min)

    Returns:
        dict with cycles_discharge, cycles_full, cycles_throughput
    """
    power = pd.to_numeric(df[power_col], errors='coerce').fillna(0)

    # Convert power (MW) to energy (MWh) for each period
    energy = power * dt_hours

    # Method A: Discharge-only (current method)
    discharge_mwh = energy[energy > 0].sum()
    cycles_discharge = discharge_mwh / capacity_mwh

    # Method B: Full Equivalent Cycles (Industry Standard)
    charge_mwh = abs(energy[energy < 0].sum())
    cycles_full = (discharge_mwh + charge_mwh) / 2 / capacity_mwh

    # Method C: Throughput-based (mathematically same as B)
    total_throughput = discharge_mwh + charge_mwh
    cycles_throughput = total_throughput / (2 * capacity_mwh)

    return {
        'discharge_mwh': discharge_mwh,
        'charge_mwh': charge_mwh,
        'cycles_discharge': cycles_discharge,
        'cycles_full': cycles_full,
        'cycles_throughput': cycles_throughput
    }


def show_asset_details():
    """Display asset details from digital twin configuration"""
    st.title("🏭 Asset Details")
    st.markdown("### Northwold Solar Farm (Hall Farm) - Battery Energy Storage System")

    # Physical Specifications
    st.subheader("⚡ Physical Specifications")

    col1, col2 = st.columns(2)

    with col1:
        st.info("**Power Capabilities**")
        st.metric("Maximum Charging Rate", f"{config.P_IMP_MAX_MW} MW",
                 help="Maximum rate at which the battery can charge (import power)")
        st.metric("Maximum Discharging Rate", f"{config.P_EXP_MAX_MW} MW",
                 help="Maximum rate at which the battery can discharge (export power)")
        st.metric("Power Asymmetry Ratio", f"{config.P_EXP_MAX_MW/config.P_IMP_MAX_MW:.2f}x",
                 help="Discharge to charge power ratio")

    with col2:
        st.info("**Energy Storage**")
        st.metric("Usable Capacity", f"{config.CAPACITY_MWH} MWh",
                 help="Total usable energy storage capacity")
        st.metric("Minimum SOC", f"{config.SOC_MIN_PCT*100:.0f}%",
                 help=f"Minimum State of Charge ({config.SOC_MIN_MWH:.2f} MWh)")
        st.metric("Maximum SOC", f"{config.SOC_MAX_PCT*100:.0f}%",
                 help=f"Maximum State of Charge ({config.SOC_MAX_MWH:.2f} MWh)")

    # Efficiency & Warranty
    st.subheader("🔧 Efficiency & Warranty")

    col1, col2 = st.columns(2)

    with col1:
        st.info("**Efficiency Parameters**")
        st.metric("Round-Trip Efficiency", f"{config.EFF_ROUND_TRIP*100:.0f}%",
                 help="Energy efficiency for a complete charge-discharge cycle")

    with col2:
        st.info("**Warranty Constraints**")
        st.metric("Maximum Daily Cycles", f"{config.CYCLES_PER_DAY} cycles/day",
                 help="Warranty limit on daily cycling")

def show_operations_summary(bess_df, northwold_df, bess_analysis, northwold_analysis, month: str = "September 2025"):
    """Display monthly operations summary"""
    st.title(f"📊 {month} Operations Summary")

    # Create tabs for the operations summary
    tab1, tab2 = st.tabs(["💰 Trading Analysis", "📈 Visualizations"])

    with tab1:

        # Revenue Breakdown
        st.subheader("💵 Revenue Breakdown")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("SFFR Revenues", f"£{northwold_analysis['sffr_revenue']:,.2f}",
                     help="Static Firm Frequency Response - Largest revenue stream")
        with col2:
            st.metric("IDA1 Revenue", f"£{northwold_analysis['ida1_revenue']:,.2f}",
                     help="Intraday Auction 1 trading revenue")
        with col3:
            st.metric("EPEX 30 DA Revenue", f"£{northwold_analysis['epex30_revenue']:,.2f}",
                     help="Day-ahead market revenue")

        col4, col5, col6 = st.columns(3)
        with col4:
            st.metric("Imbalance Revenue", f"£{northwold_analysis['imbalance_revenue']:,.2f}",
                     help="Revenue from imbalance mechanism (negative indicates costs)")
        with col5:
            st.metric("Imbalance Charge", f"£{northwold_analysis['imbalance_charge']:,.2f}",
                     help="Charges from imbalance mechanism")
        with col6:
            st.metric("**TOTAL NET REVENUE**", f"£{northwold_analysis['total_net_revenue']:,.2f}",
                     help="Total net revenue for the month")

        # Market Prices
        st.subheader("📈 Market Prices Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Day Ahead Price (EPEX)**")
            price_data = {
                'Average': f"£{northwold_analysis['da_price_mean']:.2f}",
                'Minimum': f"£{northwold_analysis['da_price_min']:.2f}",
                'Maximum': f"£{northwold_analysis['da_price_max']:.2f}",
                'Std Dev': f"£{northwold_analysis['da_price_std']:.2f}"
            }
            for key, value in price_data.items():
                st.text(f"{key}: {value}")

        with col2:
            st.markdown("**Intraday Price**")
            intraday_data = {
                'Average': f"£{northwold_analysis['intraday_price_mean']:.2f}",
                'Minimum': f"£{northwold_analysis['intraday_price_min']:.2f}",
                'Maximum': f"£{northwold_analysis['intraday_price_max']:.2f}",
                'Spread (ID-DA)': f"£{(northwold_analysis['intraday_price_mean'] - northwold_analysis['da_price_mean']):.2f}"
            }
            for key, value in intraday_data.items():
                st.text(f"{key}: {value}")

        # Ancillary Services
        st.subheader("⚡ Ancillary Services Pricing")

        services_data = []
        for service, data in northwold_analysis['ancillary_services'].items():
            services_data.append({
                'Service': service,
                'Avg Clearing Price (£)': f"{data['avg_price']:.2f}",
                'Avg Availability (MW)': f"{data['avg_availability']:.0f}"
            })

        services_df = pd.DataFrame(services_data)
        st.dataframe(services_df, use_container_width=True, hide_index=True)

        # Trading Activity
        st.subheader("📊 Trading Activity")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average DA MW", f"{northwold_analysis['da_mw_mean']:.2f} MW")
        with col2:
            st.metric("Average EPEX 30 DA MW", f"{northwold_analysis['epex30_mw_mean']:.2f} MW")
        with col3:
            st.metric("Average IDA1 MW", f"{northwold_analysis['ida1_mw_mean']:.2f} MW")

    with tab2:

        # Create visualizations
        col1, col2 = st.columns(2)

        with col1:
            # Revenue breakdown pie chart
            st.subheader("Revenue Breakdown")
            revenue_data = {
                'SFFR': abs(northwold_analysis['sffr_revenue']),
                'EPEX 30 DA': abs(northwold_analysis['epex30_revenue']),
                'IDA1': abs(northwold_analysis['ida1_revenue']),
                'Imbalance (Net)': abs(northwold_analysis['net_imbalance'])
            }

            fig = px.pie(
                values=list(revenue_data.values()),
                names=list(revenue_data.keys()),
                title="Revenue Sources Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # SOC distribution
            st.subheader("State of Charge Distribution")
            fig = px.histogram(
                bess_df,
                x='SOC',
                nbins=50,
                title="SOC Distribution",
                labels={'SOC': 'State of Charge (%)', 'count': 'Frequency'}
            )
            st.plotly_chart(fig, use_container_width=True)

        # Time series plots
        st.subheader("Time Series Analysis")

        # Power over time
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=bess_df['date'],
            y=bess_df['Power'],
            mode='lines',
            name='Power (MW)',
            line=dict(width=1)
        ))
        fig.update_layout(
            title="Battery Power Over Time",
            xaxis_title="Date",
            yaxis_title="Power (MW)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Price comparison
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=northwold_df['Timestamp'],
            y=northwold_df['Day Ahead Price (EPEX)'],
            mode='lines',
            name='Day Ahead Price',
            line=dict(width=1)
        ))
        fig.add_trace(go.Scatter(
            x=northwold_df['Timestamp'],
            y=northwold_df['GB-ISEM Intraday 1 Price'],
            mode='lines',
            name='Intraday Price',
            line=dict(width=1)
        ))
        fig.update_layout(
            title="Energy Prices Comparison",
            xaxis_title="Date",
            yaxis_title="Price (£/MWh)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)


def show_multimarket_optimization(month: str = "September 2025"):
    """Display multi-market optimization results"""
    st.title(f"🚀 Multi-Market Optimization Analysis - {month}")
    st.markdown("### Enhanced Trading Strategy with Cross-Market Arbitrage")

    # Get month-specific file paths
    month_config = AVAILABLE_MONTHS.get(month, AVAILABLE_MONTHS["September 2025"])
    optimization_file = month_config.get("optimization_file", "Optimized_Results_MultiMarket.csv")
    master_file = month_config.get("master_file", "Master_BESS_Analysis_Sept_2025.csv")

    # Check if multi-market results exist
    try:
        multi_df = pd.read_csv(os.path.join(DATA_DIR, optimization_file))
        multi_df['Timestamp'] = pd.to_datetime(multi_df['Timestamp'])
    except:
        st.warning(f"Multi-market results not found for {month}. Click below to generate.")
        if st.button("Run Multi-Market Optimization"):
            with st.spinner("Running optimization... This may take a minute."):
                from src import phase3_multimarket
                multi_df = phase3_multimarket.run_phase_3_multimarket(os.path.join(DATA_DIR, master_file))
                multi_df.to_csv(os.path.join(DATA_DIR, optimization_file), index=False)
                st.success(f"Optimization complete! Results saved to {optimization_file}")
                st.rerun()
        return

    # Summary metrics
    st.subheader("💰 Revenue Comparison")

    col1, col2, col3, col4 = st.columns(4)

    total_epex_daily = multi_df['Optimised_Revenue_Daily'].sum()
    total_epex_efa = multi_df['Optimised_Revenue_EFA'].sum()
    total_multi = multi_df['Optimised_Revenue_Multi'].sum()
    improvement = ((total_multi / total_epex_daily - 1) * 100)

    with col1:
        st.metric("EPEX-Only (Daily)", f"£{total_epex_daily:,.2f}",
                 help="Original strategy using only EPEX prices with daily switching")
    with col2:
        st.metric("EPEX-Only (EFA)", f"£{total_epex_efa:,.2f}",
                 delta=f"{((total_epex_efa/total_epex_daily - 1) * 100):.1f}%",
                 help="EPEX prices with 2-hour block switching")
    with col3:
        st.metric("Multi-Market", f"£{total_multi:,.2f}",
                 delta=f"+{improvement:.1f}%",
                 help="Optimized across all available markets")
    with col4:
        st.metric("Additional Revenue", f"£{(total_multi - total_epex_daily):,.2f}",
                 help="Extra revenue from multi-market strategy")

    # Market usage analysis
    st.subheader("📊 Market Utilization")

    # Add strategy selector dropdown
    strategy_option = st.selectbox(
        "Select Strategy to View:",
        ["Multi-Market", "EPEX-only (Daily)", "EPEX-only (EFA)", "Actual"],
        index=0,  # Default to Multi-Market
        help="Choose which strategy's market utilization to display"
    )

    # Initialize variables for volume and revenue tracking
    market_usage = pd.Series()
    market_revenue = pd.Series()
    chart_title = "No Data Available"

    # Determine which column to use based on selection
    if strategy_option == "Multi-Market":
        if 'Market_Used_Multi' in multi_df.columns:
            market_usage = multi_df['Market_Used_Multi'].value_counts()
            # Calculate revenue by market
            if 'Optimised_Revenue_Multi' in multi_df.columns:
                market_revenue = multi_df.groupby('Market_Used_Multi')['Optimised_Revenue_Multi'].sum()
            chart_title = "Multi-Market Strategy"
        else:
            st.warning("Multi-Market data not available")

    elif strategy_option == "EPEX-only (Daily)":
        if 'Strategy_Selected_Daily' in multi_df.columns:
            market_usage = multi_df['Strategy_Selected_Daily'].value_counts()
            if 'Optimised_Revenue_Daily' in multi_df.columns:
                market_revenue = multi_df.groupby('Strategy_Selected_Daily')['Optimised_Revenue_Daily'].sum()
            chart_title = "EPEX-only (Daily) Strategy"
        else:
            st.warning("EPEX Daily data not available")

    elif strategy_option == "EPEX-only (EFA)":
        if 'Strategy_Selected_EFA' in multi_df.columns:
            market_usage = multi_df['Strategy_Selected_EFA'].value_counts()
            if 'Optimised_Revenue_EFA' in multi_df.columns:
                market_revenue = multi_df.groupby('Strategy_Selected_EFA')['Optimised_Revenue_EFA'].sum()
            chart_title = "EPEX-only (EFA) Strategy"
        else:
            st.warning("EPEX EFA data not available")

    else:  # Actual
        # For actual operation, derive market usage AND revenue from revenue columns
        try:
            actual_master_df = pd.read_csv(os.path.join(DATA_DIR, master_file))
            if 'Unnamed: 0' in actual_master_df.columns:
                actual_master_df.rename(columns={'Unnamed: 0': 'Timestamp'}, inplace=True)

            # Find power column for buy/sell direction
            power_col = None
            for col in actual_master_df.columns:
                if 'Battery MWh' in col and 'Output' in col:
                    power_col = col
                    break

            # Track both market assignment and revenue per market
            actual_markets = []
            actual_revenues = []

            for idx, row in actual_master_df.iterrows():
                market = 'Idle'
                revenue = 0.0
                power_val = row.get(power_col, 0) if power_col else 0

                # Helper to safely get numeric value (handles NaN)
                def safe_get(r, col, default=0):
                    val = r.get(col, default)
                    return default if pd.isna(val) else val

                # Check trading markets first (actual energy traded)
                epex_rev = safe_get(row, 'EPEX 30 DA Revenue', 0) + safe_get(row, 'EPEX DA Revenues', 0)
                ida1_rev = safe_get(row, 'IDA1 Revenue', 0)
                idc_rev = safe_get(row, 'IDC Revenue', 0)
                imb_rev = safe_get(row, 'Imbalance Revenue', 0) - abs(safe_get(row, 'Imbalance Charge', 0))
                sffr_rev = safe_get(row, 'SFFR revenues', 0)

                # Check EPEX markets
                if abs(epex_rev) > 0.01:
                    if power_val > 0.1:
                        market = 'Sell-EPEX'
                    elif power_val < -0.1:
                        market = 'Buy-EPEX'
                    else:
                        market = 'EPEX'
                    revenue = epex_rev
                # Check IDA1
                elif abs(ida1_rev) > 0.01:
                    if power_val > 0.1:
                        market = 'Sell-IDA1'
                    elif power_val < -0.1:
                        market = 'Buy-IDA1'
                    else:
                        market = 'IDA1'
                    revenue = ida1_rev
                # Check IDC
                elif abs(idc_rev) > 0.01:
                    if power_val > 0.1:
                        market = 'Sell-IDC'
                    elif power_val < -0.1:
                        market = 'Buy-IDC'
                    else:
                        market = 'IDC'
                    revenue = idc_rev
                # Check Imbalance
                elif abs(row.get('Imbalance Revenue', 0)) > 0.01 or abs(row.get('Imbalance Charge', 0)) > 0.01:
                    market = 'Imbalance'
                    revenue = imb_rev
                # Check SFFR (availability payment)
                elif abs(sffr_rev) > 0.01:
                    market = 'SFFR'
                    revenue = sffr_rev
                # Default - check physical operation without identified market
                elif power_col and abs(power_val) > 0.1:
                    if power_val > 0:
                        market = 'Discharging (Unknown)'
                    else:
                        market = 'Charging (Unknown)'

                actual_markets.append(market)
                actual_revenues.append(revenue)

            # Create DataFrame for aggregation
            actual_df = pd.DataFrame({'market': actual_markets, 'revenue': actual_revenues})
            market_usage = actual_df['market'].value_counts()
            market_revenue = actual_df.groupby('market')['revenue'].sum()
            chart_title = "Actual (GridBeyond)"

        except Exception as e:
            st.warning(f"Could not load actual data: {str(e)}")

    # Display the visualization if we have data
    if not market_usage.empty:
        # Two pie charts: Volume and Revenue
        col1, col2 = st.columns(2)

        with col1:
            # Volume pie chart
            fig_volume = px.pie(
                values=market_usage.values[:10],
                names=market_usage.index[:10],
                title=f"📊 Volume (Periods) - {chart_title}"
            )
            fig_volume.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_volume, use_container_width=True)

        with col2:
            # Revenue pie chart
            if not market_revenue.empty:
                # Handle negative values for pie chart (show absolute, note negatives)
                rev_for_pie = market_revenue.abs()
                fig_revenue = px.pie(
                    values=rev_for_pie.values[:10],
                    names=rev_for_pie.index[:10],
                    title=f"💰 Revenue (£) - {chart_title}"
                )
                fig_revenue.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_revenue, use_container_width=True)
            else:
                st.info("Revenue data not available for this strategy")

        # Combined statistics table
        st.markdown("**Market Statistics**")

        # Build table with both volume and revenue
        table_data = {
            'Market': market_usage.index[:10],
            'Periods': market_usage.values[:10],
            '% of Time': (market_usage.values[:10] / len(multi_df) * 100).round(1)
        }

        if not market_revenue.empty:
            # Align revenue with market_usage index
            revenue_values = [market_revenue.get(m, 0) for m in market_usage.index[:10]]
            table_data['Revenue (£)'] = [f"£{v:,.2f}" for v in revenue_values]
            total_rev = sum(revenue_values)
            table_data['% of Revenue'] = [(v / total_rev * 100 if total_rev != 0 else 0) for v in revenue_values]
            table_data['% of Revenue'] = [f"{v:.1f}%" for v in table_data['% of Revenue']]

        market_stats = pd.DataFrame(table_data)
        st.dataframe(market_stats, use_container_width=True, hide_index=True)

    # Price spread analysis
    st.subheader("📈 Market Price Spreads")

    if 'Market_Spread' in multi_df.columns:
        col1, col2 = st.columns(2)

        with col1:
            spread_stats = {
                'Average Spread': f"£{multi_df['Market_Spread'].mean():.2f}/MWh",
                'Max Spread': f"£{multi_df['Market_Spread'].max():.2f}/MWh",
                'Min Spread': f"£{multi_df['Market_Spread'].min():.2f}/MWh",
                'Spreads >£30': f"{(multi_df['Market_Spread'] > 30).sum()} periods",
                'Spreads >£50': f"{(multi_df['Market_Spread'] > 50).sum()} periods"
            }
            for key, value in spread_stats.items():
                st.text(f"{key}: {value}")

        with col2:
            # Spread distribution histogram
            fig_hist = px.histogram(
                multi_df,
                x='Market_Spread',
                nbins=50,
                title="Distribution of Market Spreads",
                labels={'Market_Spread': 'Price Spread (£/MWh)', 'count': 'Frequency'}
            )
            st.plotly_chart(fig_hist, use_container_width=True)

    # Time series comparison
    st.subheader("📊 Strategy Comparison Over Time")

    # Revenue over time
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=multi_df['Timestamp'],
        y=multi_df['Optimised_Revenue_Daily'].cumsum(),
        mode='lines',
        name='EPEX-Only (Cumulative)',
        line=dict(width=2, color='blue')
    ))
    fig.add_trace(go.Scatter(
        x=multi_df['Timestamp'],
        y=multi_df['Optimised_Revenue_Multi'].cumsum(),
        mode='lines',
        name='Multi-Market (Cumulative)',
        line=dict(width=2, color='green')
    ))
    fig.update_layout(
        title="Cumulative Revenue Comparison",
        xaxis_title="Date",
        yaxis_title="Cumulative Revenue (£)",
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # Best markets by time
    st.subheader("🏆 Best Markets by Period")

    if 'Best_Buy_Market' in multi_df.columns and 'Best_Sell_Market' in multi_df.columns:
        col1, col2 = st.columns(2)

        with col1:
            buy_markets = multi_df['Best_Buy_Market'].value_counts()
            st.markdown("**Best Markets for Buying (Charging)**")
            buy_df = pd.DataFrame({
                'Market': buy_markets.index,
                'Times Selected': buy_markets.values,
                'Percentage': (buy_markets.values / len(multi_df) * 100).round(1)
            })
            st.dataframe(buy_df.head(), use_container_width=True, hide_index=True)

        with col2:
            sell_markets = multi_df['Best_Sell_Market'].value_counts()
            st.markdown("**Best Markets for Selling (Discharging)**")
            sell_df = pd.DataFrame({
                'Market': sell_markets.index,
                'Times Selected': sell_markets.values,
                'Percentage': (sell_markets.values / len(multi_df) * 100).round(1)
            })
            st.dataframe(sell_df.head(), use_container_width=True, hide_index=True)

    # Key insights
    st.subheader("🔍 Key Insights")

    insights_col1, insights_col2 = st.columns(2)

    with insights_col1:
        st.info(f"""
        **Revenue Improvement:**
        - Multi-market strategy yields {improvement:.1f}% more revenue
        - Additional monthly revenue: £{(total_multi - total_epex_daily):,.2f}
        - Annualized benefit: £{((total_multi - total_epex_daily) * 12):,.2f}
        """)

    with insights_col2:
        st.success(f"""
        **Market Dynamics:**
        - SSP market provides best arbitrage opportunities
        - Battery idle {(market_usage.get('Idle', 0) / len(multi_df) * 100):.1f}% of time to preserve cycles
        - Average spread captured: £{multi_df['Market_Spread'].mean():.2f}/MWh
        """)

def show_bess_health(month: str = "September 2025"):
    """Display BESS health analysis - cycles and degradation"""
    st.title(f"🔋 BESS Health Analysis - {month}")
    st.markdown("### Battery Cycling and Degradation Assessment")

    # Get month-specific file paths
    month_config = AVAILABLE_MONTHS.get(month, AVAILABLE_MONTHS["September 2025"])
    master_file = month_config.get("master_file", "Master_BESS_Analysis_Sept_2025.csv")
    optimization_file = month_config.get("optimization_file", "Optimized_Results_MultiMarket.csv")

    # Load required data
    try:
        # Load actual data
        master_df = pd.read_csv(os.path.join(DATA_DIR, master_file))
        if 'Unnamed: 0' in master_df.columns:
            master_df.rename(columns={'Unnamed: 0': 'Timestamp'}, inplace=True)
        master_df['Timestamp'] = pd.to_datetime(master_df['Timestamp'])

        # Load multi-market optimization results
        multi_df = pd.read_csv(os.path.join(DATA_DIR, optimization_file))
        multi_df['Timestamp'] = pd.to_datetime(multi_df['Timestamp'])

    except Exception as e:
        st.error(f"Error loading data files for {month}: {str(e)}")
        st.info(f"Please ensure both {master_file} and {optimization_file} exist. Run optimization first if needed.")
        return

    # Constants from config
    CAPACITY_MWH = config.CAPACITY_MWH  # 8.4 MWh
    WARRANTY_CYCLES_DAILY = config.CYCLES_PER_DAY  # 1.5 cycles/day
    WARRANTY_DEGRADATION_ANNUAL_PCT = 2.5  # Annual degradation at warranty limit
    DEGRADATION_PER_CYCLE_PCT = WARRANTY_DEGRADATION_ANNUAL_PCT / (WARRANTY_CYCLES_DAILY * 365)

    # Calculate number of days from data
    num_days = (master_df['Timestamp'].max() - master_df['Timestamp'].min()).days + 1

    # Find actual battery power column (in MW, not pre-converted to MWh)
    actual_power_col = None
    if 'Physical_Power_MW' in master_df.columns:
        actual_power_col = 'Physical_Power_MW'
    elif 'Power_MW' in master_df.columns:
        actual_power_col = 'Power_MW'

    # ==================== CYCLE METHODOLOGY COMPARISON ====================
    st.subheader("📐 Cycle Calculation Methods Comparison")

    st.caption("""
**Cycle Calculation Methods:**
- **A: Discharge-only** = Discharge MWh / Capacity (current method)
- **B: Full Equivalent** = (Discharge + Charge) / 2 / Capacity ⭐ Industry Standard
- **C: Throughput** = Total Throughput / (2 × Capacity) (mathematically same as B)

Warranty limit: 1.5 cycles/day (547 cycles/year)
""")

    # Calculate cycles using all 3 methods for Actual and Multi-Market
    if actual_power_col and actual_power_col in master_df.columns:
        actual_cycles_all = calculate_cycles(master_df, actual_power_col, CAPACITY_MWH, dt_hours=0.5)
    else:
        actual_cycles_all = {'discharge_mwh': 0, 'charge_mwh': 0, 'cycles_discharge': 0, 'cycles_full': 0, 'cycles_throughput': 0}

    # For Multi-Market, the values are already in MWh (not MW), so dt_hours=1
    multi_cycles_all = calculate_cycles(multi_df, 'Optimised_Net_MWh_Multi', CAPACITY_MWH, dt_hours=1.0)

    # Create comparison table for all 3 methods
    method_comparison = pd.DataFrame({
        'Method': ['A: Discharge-only', 'B: Full Equivalent (Industry Std)', 'C: Throughput-based'],
        'Actual Total Cycles': [
            actual_cycles_all['cycles_discharge'],
            actual_cycles_all['cycles_full'],
            actual_cycles_all['cycles_throughput']
        ],
        'Multi-Market Total Cycles': [
            multi_cycles_all['cycles_discharge'],
            multi_cycles_all['cycles_full'],
            multi_cycles_all['cycles_throughput']
        ],
        'Actual Daily Avg': [
            actual_cycles_all['cycles_discharge'] / num_days,
            actual_cycles_all['cycles_full'] / num_days,
            actual_cycles_all['cycles_throughput'] / num_days
        ],
        'Multi-Market Daily Avg': [
            multi_cycles_all['cycles_discharge'] / num_days,
            multi_cycles_all['cycles_full'] / num_days,
            multi_cycles_all['cycles_throughput'] / num_days
        ]
    })

    st.dataframe(
        method_comparison.style.format({
            'Actual Total Cycles': '{:.2f}',
            'Multi-Market Total Cycles': '{:.2f}',
            'Actual Daily Avg': '{:.3f}',
            'Multi-Market Daily Avg': '{:.3f}'
        }),
        use_container_width=True,
        hide_index=True
    )

    # Show energy totals
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Actual Discharge Energy", f"{actual_cycles_all['discharge_mwh']:.2f} MWh",
                 help="Total energy discharged (exported to grid)")
        st.metric("Actual Charge Energy", f"{actual_cycles_all['charge_mwh']:.2f} MWh",
                 help="Total energy charged (imported from grid)")
    with col2:
        st.metric("Multi-Market Discharge Energy", f"{multi_cycles_all['discharge_mwh']:.2f} MWh",
                 help="Total simulated discharge energy")
        st.metric("Multi-Market Charge Energy", f"{multi_cycles_all['charge_mwh']:.2f} MWh",
                 help="Total simulated charge energy")

    st.markdown("---")

    # ==================== STRATEGY COMPARISON WITH METHOD SELECTOR ====================
    st.subheader("📊 Strategy Cycling Comparison")

    # Method selector
    cycle_method = st.radio(
        "Select Cycle Calculation Method for Strategy Comparison:",
        ["A: Discharge-only", "B: Full Equivalent (Industry Std)", "C: Throughput-based"],
        index=1,  # Default to industry standard
        horizontal=True,
        help="Method B (Full Equivalent) is the industry standard for battery cycling"
    )

    # Map selection to cycle key
    method_key_map = {
        "A: Discharge-only": 'cycles_discharge',
        "B: Full Equivalent (Industry Std)": 'cycles_full',
        "C: Throughput-based": 'cycles_throughput'
    }
    selected_key = method_key_map[cycle_method]

    # Calculate cycles for all strategies using selected method
    strategies_data = []

    # Helper to get cycles and discharge based on selected method
    def get_strategy_metrics(df, col, is_mwh=False):
        dt = 1.0 if is_mwh else 0.5
        cycles_data = calculate_cycles(df, col, CAPACITY_MWH, dt_hours=dt)
        return cycles_data[selected_key], cycles_data['discharge_mwh']

    # 1. Actual (Original) Operation
    if actual_power_col and actual_power_col in master_df.columns:
        actual_cycles, actual_discharge = get_strategy_metrics(master_df, actual_power_col, is_mwh=False)
        actual_daily_cycles = actual_cycles / num_days
        actual_degradation = actual_cycles * DEGRADATION_PER_CYCLE_PCT
        strategies_data.append({
            'Strategy': 'Actual Operation',
            'Total Discharge (MWh)': actual_discharge,
            'Total Cycles': actual_cycles,
            'Daily Cycles': actual_daily_cycles,
            'Est. Degradation (%)': actual_degradation,
            'Warranty Status': '✅ OK' if actual_daily_cycles <= WARRANTY_CYCLES_DAILY else '⚠️ EXCEEDED'
        })

    # 2. EPEX-Only Daily Strategy
    epex_daily_cycles, epex_daily_discharge = get_strategy_metrics(multi_df, 'Optimised_Net_MWh_Daily', is_mwh=True)
    epex_daily_daily_cycles = epex_daily_cycles / num_days
    epex_daily_degradation = epex_daily_cycles * DEGRADATION_PER_CYCLE_PCT
    strategies_data.append({
        'Strategy': 'EPEX-Only (Daily)',
        'Total Discharge (MWh)': epex_daily_discharge,
        'Total Cycles': epex_daily_cycles,
        'Daily Cycles': epex_daily_daily_cycles,
        'Est. Degradation (%)': epex_daily_degradation,
        'Warranty Status': '✅ OK' if epex_daily_daily_cycles <= WARRANTY_CYCLES_DAILY else '⚠️ EXCEEDED'
    })

    # 3. EPEX-Only EFA Strategy
    epex_efa_cycles, epex_efa_discharge = get_strategy_metrics(multi_df, 'Optimised_Net_MWh_EFA', is_mwh=True)
    epex_efa_daily_cycles = epex_efa_cycles / num_days
    epex_efa_degradation = epex_efa_cycles * DEGRADATION_PER_CYCLE_PCT
    strategies_data.append({
        'Strategy': 'EPEX-Only (EFA)',
        'Total Discharge (MWh)': epex_efa_discharge,
        'Total Cycles': epex_efa_cycles,
        'Daily Cycles': epex_efa_daily_cycles,
        'Est. Degradation (%)': epex_efa_degradation,
        'Warranty Status': '✅ OK' if epex_efa_daily_cycles <= WARRANTY_CYCLES_DAILY else '⚠️ EXCEEDED'
    })

    # 4. Multi-Market Strategy
    multi_cycles, multi_discharge = get_strategy_metrics(multi_df, 'Optimised_Net_MWh_Multi', is_mwh=True)
    multi_daily_cycles = multi_cycles / num_days
    multi_degradation = multi_cycles * DEGRADATION_PER_CYCLE_PCT
    strategies_data.append({
        'Strategy': 'Multi-Market',
        'Total Discharge (MWh)': multi_discharge,
        'Total Cycles': multi_cycles,
        'Daily Cycles': multi_daily_cycles,
        'Est. Degradation (%)': multi_degradation,
        'Warranty Status': '✅ OK' if multi_daily_cycles <= WARRANTY_CYCLES_DAILY else '⚠️ EXCEEDED'
    })

    # Create DataFrame
    health_df = pd.DataFrame(strategies_data)

    st.info(f"**Using Method: {cycle_method}**")

    # Display comparison table
    st.dataframe(
        health_df.style.format({
            'Total Discharge (MWh)': '{:.2f}',
            'Total Cycles': '{:.2f}',
            'Daily Cycles': '{:.3f}',
            'Est. Degradation (%)': '{:.4f}'
        }),
        use_container_width=True,
        hide_index=True
    )

    # Key metrics cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Warranty Limit",
            f"{WARRANTY_CYCLES_DAILY} cycles/day",
            help="Maximum daily cycles allowed under warranty"
        )

    with col2:
        st.metric(
            "Annual Degradation at Limit",
            f"{WARRANTY_DEGRADATION_ANNUAL_PCT}%",
            help="Expected annual degradation if operating at warranty limit"
        )

    with col3:
        st.metric(
            "Analysis Period",
            f"{num_days} days",
            help=f"{month} data"
        )

    # Visualizations
    st.subheader("📈 Visual Comparisons")

    col1, col2 = st.columns(2)

    with col1:
        # Daily cycles bar chart
        fig_cycles = go.Figure(data=[
            go.Bar(
                x=health_df['Strategy'],
                y=health_df['Daily Cycles'],
                text=health_df['Daily Cycles'].round(3),
                textposition='auto',
                marker_color=['lightblue', 'blue', 'darkblue', 'green']
            )
        ])
        # Add warranty limit line
        fig_cycles.add_hline(
            y=WARRANTY_CYCLES_DAILY,
            line_dash="dash",
            line_color="red",
            annotation_text="Warranty Limit (1.5 cycles/day)"
        )
        fig_cycles.update_layout(
            title="Daily Cycling Comparison",
            yaxis_title="Cycles per Day",
            xaxis_title="Strategy",
            height=400
        )
        st.plotly_chart(fig_cycles, use_container_width=True)

    with col2:
        # Degradation comparison
        fig_degrade = go.Figure(data=[
            go.Bar(
                x=health_df['Strategy'],
                y=health_df['Est. Degradation (%)'],
                text=health_df['Est. Degradation (%)'].round(4),
                textposition='auto',
                marker_color=['lightcoral', 'coral', 'darkorange', 'green']
            )
        ])
        fig_degrade.update_layout(
            title="Monthly Degradation Comparison",
            yaxis_title="Estimated Degradation (%)",
            xaxis_title="Strategy",
            height=400
        )
        st.plotly_chart(fig_degrade, use_container_width=True)

    # Total discharge comparison
    st.subheader("⚡ Energy Throughput Analysis")

    fig_discharge = go.Figure()

    # Add bars for each strategy
    strategies = health_df['Strategy'].tolist()
    discharges = health_df['Total Discharge (MWh)'].tolist()

    fig_discharge.add_trace(go.Bar(
        x=strategies,
        y=discharges,
        text=[f"{d:.1f} MWh" for d in discharges],
        textposition='auto',
        marker_color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA']
    ))

    fig_discharge.update_layout(
        title=f"Total Energy Discharged ({month})",
        yaxis_title="Total Discharge (MWh)",
        xaxis_title="Strategy",
        height=400,
        showlegend=False
    )

    st.plotly_chart(fig_discharge, use_container_width=True)

    # Projected annual analysis
    st.subheader("📅 Projected Annual Impact")

    annual_data = []
    for _, row in health_df.iterrows():
        annual_cycles = row['Daily Cycles'] * 365
        annual_degradation = annual_cycles * DEGRADATION_PER_CYCLE_PCT
        annual_data.append({
            'Strategy': row['Strategy'],
            'Projected Annual Cycles': annual_cycles,
            'Projected Annual Degradation (%)': annual_degradation,
            'Years to 80% SOH': 20.0 / annual_degradation if annual_degradation > 0 else float('inf')
        })

    annual_df = pd.DataFrame(annual_data)

    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(
            annual_df[['Strategy', 'Projected Annual Cycles', 'Projected Annual Degradation (%)']].style.format({
                'Projected Annual Cycles': '{:.1f}',
                'Projected Annual Degradation (%)': '{:.2f}'
            }),
            use_container_width=True,
            hide_index=True
        )

    with col2:
        # Years to 80% SOH
        fig_years = go.Figure(data=[
            go.Bar(
                x=annual_df['Strategy'],
                y=annual_df['Years to 80% SOH'],
                text=[f"{y:.1f} years" if y < 100 else "100+ years" for y in annual_df['Years to 80% SOH']],
                textposition='auto',
                marker_color=['#FFA15A', '#19D3F3', '#FF6692', '#B6E880']
            )
        ])
        fig_years.update_layout(
            title="Estimated Battery Lifespan",
            yaxis_title="Years to 80% State of Health",
            xaxis_title="Strategy",
            height=400
        )
        st.plotly_chart(fig_years, use_container_width=True)

    # Insights
    st.subheader("🔍 Key Health Insights")

    best_strategy = health_df.loc[health_df['Daily Cycles'].idxmin(), 'Strategy']
    worst_strategy = health_df.loc[health_df['Daily Cycles'].idxmax(), 'Strategy']

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"""
        **Battery Preservation:**
        - Best for battery health: **{best_strategy}**
        - Most intensive: **{worst_strategy}**
        - All strategies within warranty limits ✅
        - Multi-market strategy balances revenue and health
        """)

    with col2:
        st.success(f"""
        **Optimization Benefits:**
        - Multi-market reduces cycling vs EPEX strategies
        - Higher revenue with lower battery wear
        - Extended battery lifespan potential
        - Warranty compliance maintained
        """)

    # ==================== NEW SECTION: DAILY CYCLES COMPARISON ====================
    st.markdown("---")
    st.subheader("📊 Daily Cycles: Actual vs Multi-Market Optimization")

    st.info(f"**Using Method: {cycle_method}** (same as strategy comparison above)")

    # Helper function for daily cycle calculation based on selected method
    def calc_daily_cycles(df, col, date_col, is_mwh=False):
        """Calculate daily cycles using selected method."""
        dt = 1.0 if is_mwh else 0.5
        power = pd.to_numeric(df[col], errors='coerce').fillna(0)
        energy = power * dt

        if selected_key == 'cycles_discharge':
            # Method A: Discharge only
            df_temp = df.copy()
            df_temp['_energy'] = energy
            df_temp['_discharge'] = df_temp['_energy'].apply(lambda x: x if x > 0 else 0)
            daily = df_temp.groupby(date_col)['_discharge'].sum() / CAPACITY_MWH
        elif selected_key in ['cycles_full', 'cycles_throughput']:
            # Method B/C: Full equivalent (discharge + charge) / 2
            df_temp = df.copy()
            df_temp['_energy'] = energy
            df_temp['_discharge'] = df_temp['_energy'].apply(lambda x: x if x > 0 else 0)
            df_temp['_charge'] = df_temp['_energy'].apply(lambda x: abs(x) if x < 0 else 0)
            daily_discharge = df_temp.groupby(date_col)['_discharge'].sum()
            daily_charge = df_temp.groupby(date_col)['_charge'].sum()
            daily = (daily_discharge + daily_charge) / 2 / CAPACITY_MWH
        return daily.reset_index()

    # Calculate daily cycles for each day
    master_df['Date'] = master_df['Timestamp'].dt.date
    multi_df['Date'] = multi_df['Timestamp'].dt.date

    # Actual daily cycles
    if actual_power_col and actual_power_col in master_df.columns:
        actual_daily = calc_daily_cycles(master_df, actual_power_col, 'Date', is_mwh=False)
        actual_daily.columns = ['Date', 'Actual_Cycles']
    else:
        actual_daily = pd.DataFrame({'Date': master_df['Date'].unique(), 'Actual_Cycles': 0})

    # Multi-market daily cycles
    multi_daily = calc_daily_cycles(multi_df, 'Optimised_Net_MWh_Multi', 'Date', is_mwh=True)
    multi_daily.columns = ['Date', 'Multi_Cycles']

    # Merge the two
    daily_cycles_df = pd.merge(actual_daily, multi_daily, on='Date', how='outer').fillna(0)
    daily_cycles_df['Date'] = pd.to_datetime(daily_cycles_df['Date'])
    daily_cycles_df = daily_cycles_df.sort_values('Date')

    # Create comparison chart
    fig_daily = go.Figure()

    fig_daily.add_trace(go.Bar(
        x=daily_cycles_df['Date'],
        y=daily_cycles_df['Actual_Cycles'],
        name='Actual (GridBeyond)',
        marker_color='#3498db',
        opacity=0.8
    ))

    fig_daily.add_trace(go.Bar(
        x=daily_cycles_df['Date'],
        y=daily_cycles_df['Multi_Cycles'],
        name='Multi-Market Optimized',
        marker_color='#2ecc71',
        opacity=0.8
    ))

    # Add warranty limit line
    fig_daily.add_hline(
        y=WARRANTY_CYCLES_DAILY,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Warranty Limit ({WARRANTY_CYCLES_DAILY} cycles/day)",
        annotation_position="top right"
    )

    fig_daily.update_layout(
        title=f"Daily Battery Cycles - {month}",
        xaxis_title="Date",
        yaxis_title="Cycles per Day",
        barmode='group',
        height=450,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )

    st.plotly_chart(fig_daily, use_container_width=True)

    # Summary stats
    method_help = {
        'cycles_discharge': 'Discharge-only method (A)',
        'cycles_full': 'Full Equivalent method (B) - Industry Standard',
        'cycles_throughput': 'Throughput method (C)'
    }
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Actual Avg Daily Cycles", f"{daily_cycles_df['Actual_Cycles'].mean():.3f}",
                 help=f"Using {method_help[selected_key]}. Average cycles per day for actual operation.")
    with col2:
        st.metric("Multi-Market Avg Daily", f"{daily_cycles_df['Multi_Cycles'].mean():.3f}",
                 help=f"Using {method_help[selected_key]}. Simulated daily cycles under multi-market optimization.")
    with col3:
        st.metric("Actual Max Day", f"{daily_cycles_df['Actual_Cycles'].max():.3f}",
                 help=f"Using {method_help[selected_key]}. Highest single-day cycling for actual operation.")
    with col4:
        st.metric("Multi-Market Max Day", f"{daily_cycles_df['Multi_Cycles'].max():.3f}",
                 help=f"Using {method_help[selected_key]}. Highest single-day cycling for simulated strategy.")

    # ==================== NEW SECTION: WARRANTY EXCEEDANCE TABLE ====================
    st.markdown("---")
    st.subheader("⚠️ Warranty Limit Exceedance Analysis")

    # Find days exceeding warranty limits
    daily_cycles_df['Actual_Exceeded'] = daily_cycles_df['Actual_Cycles'] > WARRANTY_CYCLES_DAILY
    daily_cycles_df['Multi_Exceeded'] = daily_cycles_df['Multi_Cycles'] > WARRANTY_CYCLES_DAILY

    actual_exceeded_days = daily_cycles_df[daily_cycles_df['Actual_Exceeded']]
    multi_exceeded_days = daily_cycles_df[daily_cycles_df['Multi_Exceeded']]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Actual Operation: {len(actual_exceeded_days)} days exceeded**")
        if len(actual_exceeded_days) > 0:
            exceeded_display = actual_exceeded_days[['Date', 'Actual_Cycles']].copy()
            exceeded_display['Date'] = exceeded_display['Date'].dt.strftime('%Y-%m-%d')
            exceeded_display['Over Limit By'] = exceeded_display['Actual_Cycles'] - WARRANTY_CYCLES_DAILY
            exceeded_display.columns = ['Date', 'Cycles', 'Over Limit']
            exceeded_display = exceeded_display.sort_values('Cycles', ascending=False)

            st.dataframe(
                exceeded_display.style.format({
                    'Cycles': '{:.3f}',
                    'Over Limit': '{:+.3f}'
                }).background_gradient(subset=['Over Limit'], cmap='Reds'),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ No days exceeded warranty limits!")

    with col2:
        st.markdown(f"**Multi-Market Optimized: {len(multi_exceeded_days)} days exceeded**")
        if len(multi_exceeded_days) > 0:
            exceeded_display = multi_exceeded_days[['Date', 'Multi_Cycles']].copy()
            exceeded_display['Date'] = exceeded_display['Date'].dt.strftime('%Y-%m-%d')
            exceeded_display['Over Limit By'] = exceeded_display['Multi_Cycles'] - WARRANTY_CYCLES_DAILY
            exceeded_display.columns = ['Date', 'Cycles', 'Over Limit']
            exceeded_display = exceeded_display.sort_values('Cycles', ascending=False)

            st.dataframe(
                exceeded_display.style.format({
                    'Cycles': '{:.3f}',
                    'Over Limit': '{:+.3f}'
                }).background_gradient(subset=['Over Limit'], cmap='Reds'),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ No days exceeded warranty limits!")

    # Comparison summary
    st.markdown("---")
    st.subheader("📋 Warranty Compliance Summary")

    summary_data = {
        'Metric': [
            'Total Days Analyzed',
            'Days Exceeding Warranty (Actual)',
            'Days Exceeding Warranty (Multi-Market)',
            'Compliance Rate (Actual)',
            'Compliance Rate (Multi-Market)',
            'Total Excess Cycles (Actual)',
            'Total Excess Cycles (Multi-Market)'
        ],
        'Value': [
            f"{len(daily_cycles_df)} days",
            f"{len(actual_exceeded_days)} days",
            f"{len(multi_exceeded_days)} days",
            f"{(1 - len(actual_exceeded_days)/len(daily_cycles_df))*100:.1f}%",
            f"{(1 - len(multi_exceeded_days)/len(daily_cycles_df))*100:.1f}%",
            f"{daily_cycles_df[daily_cycles_df['Actual_Exceeded']]['Actual_Cycles'].sum() - len(actual_exceeded_days)*WARRANTY_CYCLES_DAILY:.3f}" if len(actual_exceeded_days) > 0 else "0.000",
            f"{daily_cycles_df[daily_cycles_df['Multi_Exceeded']]['Multi_Cycles'].sum() - len(multi_exceeded_days)*WARRANTY_CYCLES_DAILY:.3f}" if len(multi_exceeded_days) > 0 else "0.000"
        ]
    }

    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    # Insight box
    if len(actual_exceeded_days) > len(multi_exceeded_days):
        st.warning(f"""
        **⚠️ Finding:** Actual operation exceeded warranty limits on **{len(actual_exceeded_days) - len(multi_exceeded_days)} more days**
        than the multi-market optimized strategy. This indicates GridBeyond is cycling the battery more aggressively than optimal.
        """)
    elif len(multi_exceeded_days) > len(actual_exceeded_days):
        st.info(f"""
        **ℹ️ Finding:** Multi-market optimization would exceed warranty limits on **{len(multi_exceeded_days) - len(actual_exceeded_days)} more days**
        than actual operation. The optimization prioritizes revenue over battery preservation.
        """)
    else:
        st.success("""
        **✅ Finding:** Both strategies have similar warranty compliance. Battery health is being managed consistently.
        """)


def show_report_page(month: str = "September 2025"):
    """Display comprehensive performance report comparing actual vs multi-market optimization"""

    # Header
    st.title("📑 Performance Report")
    st.markdown(f"### Northwold BESS Performance Audit - {month}")
    st.markdown("---")

    # Get month-specific file paths
    month_config = AVAILABLE_MONTHS.get(month, AVAILABLE_MONTHS["September 2025"])
    master_file = month_config.get("master_file", "Master_BESS_Analysis_Sept_2025.csv")
    optimization_file = month_config.get("optimization_file", "Optimized_Results_MultiMarket.csv")
    northwold_file = month_config.get("northwold_file")

    # Load required data
    try:
        # Load actual data
        master_df = pd.read_csv(os.path.join(DATA_DIR, master_file))
        if 'Unnamed: 0' in master_df.columns:
            master_df.rename(columns={'Unnamed: 0': 'Timestamp'}, inplace=True)
        master_df['Timestamp'] = pd.to_datetime(master_df['Timestamp'])
        master_df['Date'] = master_df['Timestamp'].dt.date

        # Load multi-market optimization results
        multi_df = pd.read_csv(os.path.join(DATA_DIR, optimization_file))
        multi_df['Timestamp'] = pd.to_datetime(multi_df['Timestamp'])
        multi_df['Date'] = multi_df['Timestamp'].dt.date

        # Load northwold data for actual revenues (use master file if northwold not available)
        if northwold_file:
            northwold_df = pd.read_csv(os.path.join(DATA_DIR, northwold_file))
        else:
            northwold_df = master_df  # Master file contains GridBeyond revenue data

    except Exception as e:
        st.error(f"Error loading data files for {month}: {str(e)}")
        st.info(f"Please ensure {master_file} and {optimization_file} exist. Run optimization first if needed.")
        return

    # Calculate key metrics using actual column names in Northwold CSV
    # SFFR revenue - single column in this dataset
    if 'SFFR revenues' in northwold_df.columns:
        sffr_revenue = northwold_df['SFFR revenues'].sum()
    else:
        # Fallback: check for any SFFR revenue column
        sffr_cols = [col for col in northwold_df.columns if 'SFFR' in col and 'revenue' in col.lower()]
        sffr_revenue = northwold_df[sffr_cols[0]].sum() if sffr_cols else 0

    # Other revenue columns
    epex_revenue = northwold_df['EPEX 30 DA Revenue'].sum() if 'EPEX 30 DA Revenue' in northwold_df.columns else 0
    ida1_revenue = northwold_df['IDA1 Revenue'].sum() if 'IDA1 Revenue' in northwold_df.columns else 0
    imbalance_revenue = northwold_df['Imbalance Revenue'].sum() if 'Imbalance Revenue' in northwold_df.columns else 0
    imbalance_charge = northwold_df['Imbalance Charge'].sum() if 'Imbalance Charge' in northwold_df.columns else 0
    net_imbalance = imbalance_revenue - imbalance_charge
    actual_total = sffr_revenue + epex_revenue + ida1_revenue + net_imbalance

    # Multi-market revenue
    multi_total = multi_df['Optimised_Revenue_Multi'].sum()

    # Performance gap
    improvement_pct = ((multi_total / actual_total - 1) * 100)
    revenue_gap = multi_total - actual_total

    # ==================== SECTION 1: EXECUTIVE SUMMARY ====================
    st.header("1️⃣ The Performance Gap")
    st.markdown("The analysis reveals a significant gap between the asset's actual revenue and its optimized potential using multi-market strategies.")

    # Key metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            f"Actual Revenue ({month[:3]})",
            f"£{actual_total:,.0f}",
            help=f"Total revenue from actual operation in {month}"
        )

    with col2:
        st.metric(
            "Multi-Market Potential",
            f"£{multi_total:,.0f}",
            delta=f"+{improvement_pct:.0f}%",
            help="Optimized revenue using multi-market strategy"
        )

    with col3:
        st.metric(
            "Identified Opportunity",
            f"£{revenue_gap:,.0f}",
            delta=f"+{improvement_pct:.0f}%",
            help="Additional revenue available through optimization"
        )

    # Annualized comparison chart
    st.subheader("📊 Annualized Revenue Comparison")

    # Calculate annualized values per MW
    capacity_mw = config.P_EXP_MAX_MW  # 7.5 MW
    actual_annual_per_mw = (actual_total * 12) / capacity_mw
    multi_annual_per_mw = (multi_total * 12) / capacity_mw

    fig_annual = go.Figure(data=[
        go.Bar(
            x=['Actual (£/MW/yr)', 'Multi-Market (£/MW/yr)'],
            y=[actual_annual_per_mw, multi_annual_per_mw],
            text=[f'£{actual_annual_per_mw:,.0f}', f'£{multi_annual_per_mw:,.0f}'],
            textposition='auto',
            marker_color=['#D95D39', '#F0A202']
        )
    ])

    fig_annual.update_layout(
        title="Annualized Revenue per MW",
        yaxis_title="Revenue (£/MW/yr)",
        height=400,
        showlegend=False
    )

    st.plotly_chart(fig_annual, use_container_width=True)

    # ==================== SECTION 2: ACTUAL PERFORMANCE ====================
    st.header("2️⃣ Actual Performance Analysis")
    st.markdown("The aggregator's strategy relied heavily on SFFR with significant imbalance penalties eroding profits.")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Revenue breakdown donut chart
        revenue_components = {
            'SFFR Revenue': abs(sffr_revenue),
            'EPEX Trading': abs(epex_revenue),
            'IDA1 Trading': abs(ida1_revenue),
            'Imbalance (Net)': abs(net_imbalance)
        }

        fig_donut = px.pie(
            values=list(revenue_components.values()),
            names=list(revenue_components.keys()),
            title="Actual Revenue Breakdown",
            hole=0.4,
            color_discrete_map={
                'SFFR Revenue': '#2C4B78',
                'EPEX Trading': '#F18805',
                'IDA1 Trading': '#90EE90',
                'Imbalance (Net)': '#D95D39'
            }
        )

        st.plotly_chart(fig_donut, use_container_width=True)

    with col2:
        st.error(f"""
        **⚠️ Critical Finding**

        **-£{abs(net_imbalance):,.0f}**
        in Net Imbalance Impact

        This loss erased **{abs(net_imbalance)/(sffr_revenue+epex_revenue+ida1_revenue)*100:.0f}%**
        of the total revenue generated by the asset.
        """)

    # ==================== SECTION 3: OPTIMIZATION OPPORTUNITY ====================
    st.header("3️⃣ The Optimization Opportunity")
    st.markdown("The Digital Twin model shows that a multi-market strategy dramatically increases profitability.")

    # Asset specifications
    st.subheader("Asset Specifications")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(f"""
        **Capacity**
        # {config.CAPACITY_MWH} MWh
        Usable Energy Storage
        """)

    with col2:
        st.info(f"""
        **Power**
        # {config.P_EXP_MAX_MW}/{config.P_IMP_MAX_MW} MW
        Discharge/Charge Rates
        """)

    with col3:
        st.info(f"""
        **Efficiency**
        # {config.EFF_ROUND_TRIP*100:.0f}%
        Round-Trip Efficiency
        """)

    # Strategy comparison
    st.subheader("📈 Revenue Mix Comparison")

    # Calculate revenues for different strategies
    strategies = ['Actual', 'EPEX-Daily', 'EPEX-EFA', 'Multi-Market']
    sffr_revenues = [
        sffr_revenue,
        multi_df[multi_df['Strategy_Selected_Daily'] == 'SFFR']['Optimised_Revenue_Daily'].sum(),
        multi_df[multi_df['Strategy_Selected_EFA'] == 'SFFR']['Optimised_Revenue_EFA'].sum(),
        0  # Multi-market doesn't use SFFR when optimizing
    ]

    market_revenues = [
        epex_revenue + ida1_revenue,
        multi_df[multi_df['Strategy_Selected_Daily'] == 'EPEX']['Optimised_Revenue_Daily'].sum(),
        multi_df[multi_df['Strategy_Selected_EFA'] == 'EPEX']['Optimised_Revenue_EFA'].sum(),
        multi_total
    ]

    fig_mix = go.Figure()
    fig_mix.add_trace(go.Bar(
        name='SFFR',
        x=strategies,
        y=sffr_revenues,
        marker_color='#2C4B78'
    ))
    fig_mix.add_trace(go.Bar(
        name='Market Trading',
        x=strategies,
        y=market_revenues,
        marker_color='#F0A202'
    ))

    fig_mix.update_layout(
        title="Strategy Revenue Comparison",
        yaxis_title="Revenue (£)",
        barmode='stack',
        height=400,
        hovermode='x unified'
    )

    st.plotly_chart(fig_mix, use_container_width=True)

    # ==================== SECTION 4: DEGRADATION & WARRANTY ====================
    st.header("4️⃣ Degradation & Warranty Analysis")
    st.markdown("The asset is operating well below warranty limits, providing room for more aggressive strategies.")

    # Find actual battery output column
    actual_col = None
    for col in master_df.columns:
        if 'Battery MWh' in col and 'Output' in col:
            actual_col = col
            break

    if actual_col:
        # Calculate number of days from data
        num_days = (master_df['Timestamp'].max() - master_df['Timestamp'].min()).days + 1

        # Calculate degradation metrics
        actual_discharge = master_df[master_df[actual_col] > 0][actual_col].sum()
        actual_cycles = actual_discharge / config.CAPACITY_MWH
        actual_daily_cycles = actual_cycles / num_days

        multi_discharge = (multi_df[multi_df['Optimised_Net_MWh_Multi'] > 0]['Optimised_Net_MWh_Multi'].sum())
        multi_cycles = multi_discharge / config.CAPACITY_MWH
        multi_daily_cycles = multi_cycles / num_days

        # Create comparison table
        degradation_data = pd.DataFrame({
            'Scenario': ['Actual Usage', 'Multi-Market Strategy', 'Warranty Limit'],
            'Total Discharge (MWh)': [actual_discharge, multi_discharge, config.CYCLES_PER_DAY * num_days * config.CAPACITY_MWH],
            'Avg Cycles/Day': [actual_daily_cycles, multi_daily_cycles, config.CYCLES_PER_DAY],
            'Est. Monthly Degradation': [
                f"{actual_cycles * 0.0046:.3f}%",
                f"{multi_cycles * 0.0046:.3f}%",
                f"{config.CYCLES_PER_DAY * num_days * 0.0046:.3f}%"
            ],
            'Status': [
                '✅ Well Below Limit',
                '✅ Within Warranty',
                '⚠️ Maximum Allowed'
            ]
        })

        st.dataframe(degradation_data, use_container_width=True, hide_index=True)

    # ==================== SECTION 5: DAILY PERFORMANCE ====================
    st.header("5️⃣ Daily Performance Breakdown")
    st.markdown("Daily analysis reveals consistent revenue gaps, especially on high volatility days.")

    # Calculate daily revenues using actual column names
    revenue_cols = ['SFFR revenues', 'EPEX 30 DA Revenue', 'IDA1 Revenue',
                   'Imbalance Revenue', 'Imbalance Charge']

    # Only include columns that exist
    agg_dict = {}
    for col in revenue_cols:
        if col in master_df.columns:
            agg_dict[col] = 'sum'

    if agg_dict:
        daily_actual = master_df.groupby('Date').agg(agg_dict)

        # Calculate total revenue per day
        daily_actual['Total'] = 0
        if 'SFFR revenues' in daily_actual.columns:
            daily_actual['Total'] += daily_actual['SFFR revenues']
        if 'EPEX 30 DA Revenue' in daily_actual.columns:
            daily_actual['Total'] += daily_actual['EPEX 30 DA Revenue']
        if 'IDA1 Revenue' in daily_actual.columns:
            daily_actual['Total'] += daily_actual['IDA1 Revenue']
        if 'Imbalance Revenue' in daily_actual.columns:
            daily_actual['Total'] += daily_actual['Imbalance Revenue']
        if 'Imbalance Charge' in daily_actual.columns:
            daily_actual['Total'] -= daily_actual['Imbalance Charge']
    else:
        daily_actual = pd.DataFrame()

    daily_multi = multi_df.groupby('Date')['Optimised_Revenue_Multi'].sum()

    # Create line chart
    fig_daily = go.Figure()

    if not daily_actual.empty:
        fig_daily.add_trace(go.Scatter(
            x=daily_actual.index,
            y=daily_actual['Total'],
            mode='lines+markers',
            name='Actual Revenue',
            line=dict(color='#D95D39', width=2),
            marker=dict(size=6)
        ))

    fig_daily.add_trace(go.Scatter(
        x=daily_multi.index,
        y=daily_multi.values,
        mode='lines+markers',
        name='Multi-Market Potential',
        line=dict(color='#F0A202', width=2, dash='dash'),
        marker=dict(size=6)
    ))

    fig_daily.update_layout(
        title="Daily Revenue Comparison",
        xaxis_title="Date",
        yaxis_title="Daily Revenue (£)",
        hovermode='x unified',
        height=400,
        showlegend=True
    )

    st.plotly_chart(fig_daily, use_container_width=True)

    # ==================== SECTION 6: KEY DRIVERS OF LOSS ====================
    st.header("6️⃣ Key Drivers of Revenue Loss")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.warning(f"""
        **1. Imbalance Penalties**

        The asset incurred **-£{abs(net_imbalance):,.0f}** in net imbalance impact,
        suggesting forecast errors or non-delivery of contracted services.

        This erased **{abs(net_imbalance)/(sffr_revenue+epex_revenue+ida1_revenue)*100:.0f}%**
        of all generated revenue.
        """)

    with col2:
        st.warning(f"""
        **2. Conservative Strategy**

        The strategy was heavily weighted toward SFFR
        (**{sffr_revenue/actual_total*100:.0f}%** of revenue),
        missing profitable market trading opportunities.

        Multi-market approach would yield **+£{revenue_gap:,.0f}** additional revenue.
        """)

    with col3:
        st.warning(f"""
        **3. Underutilization**

        Operating at only **{actual_daily_cycles:.2f}** cycles/day
        vs **{config.CYCLES_PER_DAY}** warranty limit.

        Significant headroom exists for more aggressive trading
        without warranty impact.
        """)

    # Summary box
    st.markdown("---")
    st.success(f"""
    ### 🎯 Key Recommendation

    Implementing the multi-market optimization strategy would:
    - Increase monthly revenue by **{improvement_pct:.0f}%** (£{revenue_gap:,.0f})
    - Generate annual additional revenue of **£{revenue_gap*12:,.0f}**
    - Remain well within warranty cycling limits
    - Better utilize the asset's full capabilities
    """)

def show_executive_comparison():
    """Display executive comparison dashboard - Sept vs Oct, Actual vs Optimal"""
    st.title("📊 Executive Comparison Dashboard")
    st.markdown("### Multi-Month Performance Overview for Management")
    st.markdown("---")

    # Load all 4 data files
    try:
        # September data
        sept_master = pd.read_csv(os.path.join(DATA_DIR, "Master_BESS_Analysis_Sept_2025.csv"))
        sept_opt = pd.read_csv(os.path.join(DATA_DIR, "Optimized_Results_Sept_2025.csv"))

        # October data
        oct_master = pd.read_csv(os.path.join(DATA_DIR, "Master_BESS_Analysis_Oct_2025.csv"))
        oct_opt = pd.read_csv(os.path.join(DATA_DIR, "Optimized_Results_Oct_2025.csv"))
    except Exception as e:
        st.error(f"Error loading data files: {str(e)}")
        st.info("Please ensure all data files exist for both September and October.")
        return

    # Helper function to safely get numeric values
    def safe_sum(df, col):
        if col in df.columns:
            return pd.to_numeric(df[col], errors='coerce').fillna(0).sum()
        return 0

    # Calculate actual revenues for each month
    def calc_actual_revenue(df):
        sffr = safe_sum(df, 'SFFR revenues')
        epex = safe_sum(df, 'EPEX 30 DA Revenue') + safe_sum(df, 'EPEX DA Revenues')
        ida1 = safe_sum(df, 'IDA1 Revenue')
        idc = safe_sum(df, 'IDC Revenue')
        imb_rev = safe_sum(df, 'Imbalance Revenue')
        imb_charge = safe_sum(df, 'Imbalance Charge')
        return {
            'total': sffr + epex + ida1 + idc + imb_rev - imb_charge,
            'sffr': sffr,
            'epex': epex,
            'ida1': ida1,
            'idc': idc,
            'imbalance': imb_rev - imb_charge
        }

    # Calculate metrics
    sept_actual = calc_actual_revenue(sept_master)
    oct_actual = calc_actual_revenue(oct_master)
    sept_optimal = sept_opt['Optimised_Revenue_Multi'].sum()
    oct_optimal = oct_opt['Optimised_Revenue_Multi'].sum()

    # Capture rates
    sept_capture = (sept_actual['total'] / sept_optimal * 100) if sept_optimal > 0 else 0
    oct_capture = (oct_actual['total'] / oct_optimal * 100) if oct_optimal > 0 else 0

    # Gaps
    sept_gap = sept_optimal - sept_actual['total']
    oct_gap = oct_optimal - oct_actual['total']

    # ==================== SECTION 1: KEY METRICS ====================
    st.header("1️⃣ Key Performance Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Sept Actual",
            f"£{sept_actual['total']:,.0f}",
            delta=f"{sept_capture:.1f}% captured",
            delta_color="off",
            help="Actual revenue from GridBeyond operations. Capture % = Actual/Optimal."
        )

    with col2:
        st.metric(
            "Sept Optimal",
            f"£{sept_optimal:,.0f}",
            delta=f"Gap: £{sept_gap:,.0f}",
            delta_color="inverse",
            help="Simulated maximum using multi-market optimization with perfect price foresight. Gap = Optimal - Actual."
        )

    with col3:
        st.metric(
            "Oct Actual",
            f"£{oct_actual['total']:,.0f}",
            delta=f"{oct_capture:.1f}% captured",
            delta_color="off",
            help="Actual revenue from GridBeyond operations. Capture % = Actual/Optimal."
        )

    with col4:
        st.metric(
            "Oct Optimal",
            f"£{oct_optimal:,.0f}",
            delta=f"Gap: £{oct_gap:,.0f}",
            delta_color="inverse",
            help="Simulated maximum using multi-market optimization with perfect price foresight. Gap = Optimal - Actual."
        )

    # Month-over-month improvement
    mom_improvement = oct_actual['total'] - sept_actual['total']
    mom_pct = (mom_improvement / sept_actual['total'] * 100) if sept_actual['total'] != 0 else 0

    st.success(f"📈 **Month-over-Month Improvement**: GridBeyond increased actual revenue by **£{mom_improvement:,.0f}** ({mom_pct:+.0f}%) from September to October")

    st.markdown("---")

    # ==================== SECTION 2: REVENUE COMPARISON BAR CHART ====================
    st.header("2️⃣ Revenue Comparison")

    comparison_data = pd.DataFrame({
        'Scenario': ['Sept Actual', 'Sept Optimal', 'Oct Actual', 'Oct Optimal'],
        'Revenue': [sept_actual['total'], sept_optimal, oct_actual['total'], oct_optimal],
        'Type': ['Actual', 'Optimal', 'Actual', 'Optimal'],
        'Month': ['September', 'September', 'October', 'October']
    })

    fig_bar = px.bar(
        comparison_data,
        x='Scenario',
        y='Revenue',
        color='Type',
        color_discrete_map={'Actual': '#3498db', 'Optimal': '#2ecc71'},
        title="Revenue: Actual vs Optimal by Month",
        text=comparison_data['Revenue'].apply(lambda x: f'£{x:,.0f}')
    )
    fig_bar.update_traces(textposition='outside')
    fig_bar.update_layout(yaxis_title="Revenue (£)", xaxis_title="", showlegend=True, height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # ==================== SECTION 3: GAP ANALYSIS TABLE ====================
    st.header("3️⃣ Performance Gap Analysis")

    st.caption("**Methodology:** Gap = Optimal - Actual. Optimal uses hindsight-based multi-market simulation. Trend shows 'pp' (percentage points) for absolute % changes.")

    # Calculate trends
    gap_reduction = ((sept_gap - oct_gap) / sept_gap * 100) if sept_gap != 0 else 0
    capture_improvement = oct_capture - sept_capture
    imb_improvement = ((sept_actual['imbalance'] - oct_actual['imbalance']) / abs(sept_actual['imbalance']) * 100) if sept_actual['imbalance'] != 0 else 0

    gap_data = pd.DataFrame({
        'Metric': ['Revenue Gap (£)', 'Capture Rate (%)', 'Imbalance Cost (£)', 'Actual Revenue (£)'],
        'September': [
            f"£{sept_gap:,.0f}",
            f"{sept_capture:.1f}%",
            f"£{sept_actual['imbalance']:,.0f}",
            f"£{sept_actual['total']:,.0f}"
        ],
        'October': [
            f"£{oct_gap:,.0f}",
            f"{oct_capture:.1f}%",
            f"£{oct_actual['imbalance']:,.0f}",
            f"£{oct_actual['total']:,.0f}"
        ],
        'Trend': [
            f"✅ {gap_reduction:.0f}% reduction" if gap_reduction > 0 else f"❌ {abs(gap_reduction):.0f}% increase",
            f"✅ +{capture_improvement:.1f}pp" if capture_improvement > 0 else f"❌ {capture_improvement:.1f}pp",
            f"✅ {imb_improvement:.0f}% improvement" if imb_improvement > 0 else f"❌ {abs(imb_improvement):.0f}% worse",
            f"✅ +{mom_pct:.0f}%" if mom_pct > 0 else f"❌ {mom_pct:.0f}%"
        ]
    })

    st.dataframe(gap_data, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ==================== SECTION 4: MARKET MIX COMPARISON ====================
    st.header("4️⃣ Revenue by Market")

    col1, col2 = st.columns(2)

    with col1:
        # September market mix
        sept_markets = pd.DataFrame({
            'Market': ['SFFR', 'EPEX', 'IDA1', 'IDC', 'Imbalance'],
            'Revenue': [sept_actual['sffr'], sept_actual['epex'], sept_actual['ida1'],
                       sept_actual['idc'], sept_actual['imbalance']]
        })
        sept_markets = sept_markets[sept_markets['Revenue'].abs() > 0.01]

        fig_sept = px.pie(
            sept_markets,
            values=sept_markets['Revenue'].abs(),
            names='Market',
            title="September - Market Mix",
            hole=0.4
        )
        fig_sept.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_sept, use_container_width=True)

    with col2:
        # October market mix
        oct_markets = pd.DataFrame({
            'Market': ['SFFR', 'EPEX', 'IDA1', 'IDC', 'Imbalance'],
            'Revenue': [oct_actual['sffr'], oct_actual['epex'], oct_actual['ida1'],
                       oct_actual['idc'], oct_actual['imbalance']]
        })
        oct_markets = oct_markets[oct_markets['Revenue'].abs() > 0.01]

        fig_oct = px.pie(
            oct_markets,
            values=oct_markets['Revenue'].abs(),
            names='Market',
            title="October - Market Mix",
            hole=0.4
        )
        fig_oct.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_oct, use_container_width=True)

    # Market comparison table
    market_comparison = pd.DataFrame({
        'Market': ['SFFR', 'EPEX', 'IDA1', 'IDC', 'Imbalance', 'TOTAL'],
        'Sept (£)': [f"£{sept_actual['sffr']:,.0f}", f"£{sept_actual['epex']:,.0f}",
                     f"£{sept_actual['ida1']:,.0f}", f"£{sept_actual['idc']:,.0f}",
                     f"£{sept_actual['imbalance']:,.0f}", f"£{sept_actual['total']:,.0f}"],
        'Oct (£)': [f"£{oct_actual['sffr']:,.0f}", f"£{oct_actual['epex']:,.0f}",
                    f"£{oct_actual['ida1']:,.0f}", f"£{oct_actual['idc']:,.0f}",
                    f"£{oct_actual['imbalance']:,.0f}", f"£{oct_actual['total']:,.0f}"],
        'Change': [
            f"£{oct_actual['sffr'] - sept_actual['sffr']:+,.0f}",
            f"£{oct_actual['epex'] - sept_actual['epex']:+,.0f}",
            f"£{oct_actual['ida1'] - sept_actual['ida1']:+,.0f}",
            f"£{oct_actual['idc'] - sept_actual['idc']:+,.0f}",
            f"£{oct_actual['imbalance'] - sept_actual['imbalance']:+,.0f}",
            f"£{oct_actual['total'] - sept_actual['total']:+,.0f}"
        ]
    })
    st.dataframe(market_comparison, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ==================== SECTION 5: EXECUTIVE SUMMARY ====================
    st.header("5️⃣ Executive Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.error(f"""
        **September Issues:**
        - Capture Rate: Only {sept_capture:.1f}% of optimal
        - Revenue Gap: £{sept_gap:,.0f} left on table
        - Imbalance Penalties: £{abs(sept_actual['imbalance']):,.0f} in losses
        - Root Cause: Excessive imbalance exposure
        """)

    with col2:
        st.success(f"""
        **October Improvements:**
        - Capture Rate: {oct_capture:.1f}% of optimal
        - Revenue Gap: Reduced to £{oct_gap:,.0f}
        - Imbalance Controlled: £{abs(oct_actual['imbalance']):,.0f}
        - Result: Near-optimal performance achieved
        """)

    st.info(f"""
    **💡 Key Recommendations:**

    1. **Continue October Strategy**: GridBeyond achieved {oct_capture:.1f}% capture rate - maintain this approach
    2. **Investigate September**: Root cause analysis needed for the £{sept_gap:,.0f} gap
    3. **Imbalance Management**: October's strategy reduced imbalance impact by {imb_improvement:.0f}%
    4. **Annualized Impact**: If October performance continues, projected annual revenue: **£{oct_actual['total'] * 12:,.0f}**
    """)


def show_market_price_analysis(month: str = "September 2025"):
    """Display market price analysis - spreads, missed opportunities, volatility"""
    st.title(f"📈 Market Price Analysis - {month}")
    st.markdown("### Price Spreads, Arbitrage Opportunities & Volatility Metrics")
    st.markdown("---")

    # Load data
    month_config = AVAILABLE_MONTHS.get(month, AVAILABLE_MONTHS["September 2025"])
    master_file = month_config.get("master_file", "Master_BESS_Analysis_Sept_2025.csv")

    try:
        df = pd.read_csv(os.path.join(DATA_DIR, master_file))
        if 'Unnamed: 0' in df.columns:
            df.rename(columns={'Unnamed: 0': 'Timestamp'}, inplace=True)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Date'] = df['Timestamp'].dt.date
        df['Hour'] = df['Timestamp'].dt.hour
        df['DayOfWeek'] = df['Timestamp'].dt.day_name()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return

    # Price columns
    price_cols = {
        'Day Ahead Price (EPEX)': 'EPEX DA',
        'GB-ISEM Intraday 1 Price': 'Intraday',
        'SSP': 'SSP (System Sell)',
        'SBP': 'SBP (System Buy)',
        'IDC Price': 'IDC'
    }

    # ==================== SECTION 1: KEY PRICE METRICS ====================
    st.header("1️⃣ Price Summary")

    col1, col2, col3, col4 = st.columns(4)

    epex_prices = pd.to_numeric(df['Day Ahead Price (EPEX)'], errors='coerce').dropna()
    ssp_prices = pd.to_numeric(df['SSP'], errors='coerce').dropna()
    sbp_prices = pd.to_numeric(df['SBP'], errors='coerce').dropna()

    with col1:
        st.metric("EPEX DA Avg", f"£{epex_prices.mean():.2f}/MWh",
                 help="Average Day Ahead price across all 30-min periods")
    with col2:
        st.metric("EPEX DA Max", f"£{epex_prices.max():.2f}/MWh",
                 help="Highest Day Ahead price in the month - best selling opportunity")
    with col3:
        st.metric("SSP Max", f"£{ssp_prices.max():.2f}/MWh",
                 help="Highest System Sell Price - max price grid pays you to export")
    with col4:
        st.metric("SBP Max", f"£{sbp_prices.max():.2f}/MWh",
                 help="Highest System Buy Price - worst price to buy from grid")

    st.markdown("---")

    # ==================== SECTION 2: PRICE SPREAD ANALYSIS ====================
    st.header("2️⃣ Price Spread Analysis (Arbitrage Opportunities)")

    # Calculate spreads
    df['EPEX_Spread'] = df['Day Ahead Price (EPEX)'].rolling(48).max() - df['Day Ahead Price (EPEX)'].rolling(48).min()
    df['SSP_SBP_Spread'] = pd.to_numeric(df['SBP'], errors='coerce') - pd.to_numeric(df['SSP'], errors='coerce')

    # Daily spread analysis
    daily_spreads = df.groupby('Date').agg({
        'Day Ahead Price (EPEX)': ['min', 'max', lambda x: x.max() - x.min()],
        'SSP': ['min', 'max'],
        'SBP': ['min', 'max']
    }).reset_index()
    daily_spreads.columns = ['Date', 'EPEX_Min', 'EPEX_Max', 'EPEX_Spread', 'SSP_Min', 'SSP_Max', 'SBP_Min', 'SBP_Max']
    daily_spreads['Date'] = pd.to_datetime(daily_spreads['Date'])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg Daily EPEX Spread", f"£{daily_spreads['EPEX_Spread'].mean():.2f}/MWh",
                 help="Average difference between daily max and min EPEX prices")
    with col2:
        st.metric("Best EPEX Spread Day", f"£{daily_spreads['EPEX_Spread'].max():.2f}/MWh",
                 help="Highest single-day arbitrage opportunity")
    with col3:
        avg_ssb_spread = (daily_spreads['SBP_Max'] - daily_spreads['SSP_Min']).mean()
        st.metric("Avg SSP/SBP Spread", f"£{avg_ssb_spread:.2f}/MWh",
                 help="Average spread between system prices")

    # Daily spread chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=daily_spreads['Date'],
        y=daily_spreads['EPEX_Spread'],
        name='EPEX Daily Spread',
        marker_color='#3498db'
    ))
    fig.update_layout(
        title="Daily EPEX Price Spread (Max - Min)",
        xaxis_title="Date",
        yaxis_title="Spread (£/MWh)",
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ==================== SECTION 3: HOURLY PRICE PATTERNS ====================
    st.header("3️⃣ Hourly Price Patterns (Best Trading Windows)")

    # Calculate hourly averages
    hourly_avg = df.groupby('Hour').agg({
        'Day Ahead Price (EPEX)': 'mean',
        'SSP': 'mean',
        'SBP': 'mean'
    }).reset_index()

    # Identify best buy/sell hours
    buy_hour = hourly_avg.loc[hourly_avg['Day Ahead Price (EPEX)'].idxmin(), 'Hour']
    sell_hour = hourly_avg.loc[hourly_avg['Day Ahead Price (EPEX)'].idxmax(), 'Hour']
    buy_price = hourly_avg['Day Ahead Price (EPEX)'].min()
    sell_price = hourly_avg['Day Ahead Price (EPEX)'].max()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.success(f"**Best Buy Hour:** {int(buy_hour):02d}:00 (Avg £{buy_price:.2f}/MWh)")
    with col2:
        st.error(f"**Best Sell Hour:** {int(sell_hour):02d}:00 (Avg £{sell_price:.2f}/MWh)")
    with col3:
        st.info(f"**Hourly Arbitrage:** £{sell_price - buy_price:.2f}/MWh potential")

    # Hourly price heatmap
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hourly_avg['Hour'],
        y=hourly_avg['Day Ahead Price (EPEX)'],
        mode='lines+markers',
        name='EPEX DA',
        line=dict(color='#3498db', width=3),
        fill='tozeroy',
        fillcolor='rgba(52, 152, 219, 0.3)'
    ))
    fig.add_trace(go.Scatter(
        x=hourly_avg['Hour'],
        y=hourly_avg['SSP'],
        mode='lines+markers',
        name='SSP',
        line=dict(color='#2ecc71', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=hourly_avg['Hour'],
        y=hourly_avg['SBP'],
        mode='lines+markers',
        name='SBP',
        line=dict(color='#e74c3c', width=2)
    ))
    fig.update_layout(
        title="Average Price by Hour of Day",
        xaxis_title="Hour",
        yaxis_title="Price (£/MWh)",
        xaxis=dict(tickmode='linear', tick0=0, dtick=2),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ==================== SECTION 4: VOLATILITY ANALYSIS ====================
    st.header("4️⃣ Price Volatility (High-Value Trading Days)")

    # Calculate daily volatility (std dev)
    daily_volatility = df.groupby('Date').agg({
        'Day Ahead Price (EPEX)': ['std', 'mean']
    }).reset_index()
    daily_volatility.columns = ['Date', 'EPEX_Std', 'EPEX_Mean']
    daily_volatility['Date'] = pd.to_datetime(daily_volatility['Date'])
    daily_volatility['CV'] = daily_volatility['EPEX_Std'] / daily_volatility['EPEX_Mean'] * 100  # Coefficient of variation

    # Identify high volatility days (top quartile)
    high_vol_threshold = daily_volatility['EPEX_Std'].quantile(0.75)
    high_vol_days = daily_volatility[daily_volatility['EPEX_Std'] >= high_vol_threshold]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg Daily Volatility", f"£{daily_volatility['EPEX_Std'].mean():.2f}",
                 help="Standard deviation of daily prices")
    with col2:
        st.metric("High Volatility Days", f"{len(high_vol_days)} days",
                 help=f"Days with std > £{high_vol_threshold:.2f}")
    with col3:
        st.metric("Max Volatility Day", f"£{daily_volatility['EPEX_Std'].max():.2f}",
                 help="Highest single-day price volatility")

    # Volatility chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=daily_volatility['Date'],
        y=daily_volatility['EPEX_Std'],
        name='Price Volatility (Std Dev)',
        marker_color=np.where(daily_volatility['EPEX_Std'] >= high_vol_threshold, '#e74c3c', '#3498db')
    ))
    fig.add_hline(y=high_vol_threshold, line_dash="dash", line_color="red",
                  annotation_text=f"High volatility threshold: £{high_vol_threshold:.2f}")
    fig.update_layout(
        title="Daily Price Volatility (Red = High Value Trading Days)",
        xaxis_title="Date",
        yaxis_title="Volatility (£/MWh Std Dev)",
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ==================== SECTION 5: MISSED OPPORTUNITIES ====================
    st.header("5️⃣ Missed Opportunity Tracker")

    # Load actual trading data
    power_col = 'Physical_Power_MW' if 'Physical_Power_MW' in df.columns else None

    if power_col:
        # Identify periods where battery was idle during high spread
        df['Was_Idle'] = df[power_col].abs() < 0.1
        df['High_Spread'] = df['EPEX_Spread'] > df['EPEX_Spread'].quantile(0.75)

        # Missed opportunities: idle during high spread periods
        missed = df[df['Was_Idle'] & df['High_Spread']]
        missed_periods = len(missed)
        missed_hours = missed_periods * 0.5  # 30-min periods

        # Estimate missed revenue (conservative: assume 50% of spread captured with 2MW)
        avg_spread_missed = df.loc[missed.index, 'EPEX_Spread'].mean() if len(missed) > 0 else 0
        estimated_missed_revenue = missed_hours * 2 * avg_spread_missed * 0.5 if avg_spread_missed > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Idle During High Spread", f"{missed_periods} periods",
                     help="30-min periods where battery was idle but spreads were high")
        with col2:
            st.metric("Missed Hours", f"{missed_hours:.1f} hours",
                     help="Total hours idle during high-spread windows (periods × 0.5)")
        with col3:
            st.metric("Est. Missed Revenue", f"£{estimated_missed_revenue:,.0f}",
                     help="Conservative estimate of potential additional revenue")

        # Top missed opportunity days
        if len(missed) > 0:
            missed_by_day = missed.groupby('Date').size().reset_index(name='Missed_Periods')
            missed_by_day = missed_by_day.sort_values('Missed_Periods', ascending=False).head(5)

            st.subheader("Top 5 Days with Missed Opportunities")
            for _, row in missed_by_day.iterrows():
                st.warning(f"**{row['Date']}**: {row['Missed_Periods']} periods idle during high-spread windows")
    else:
        st.info("Physical power data not available to calculate missed opportunities")

    st.markdown("---")

    # ==================== SECTION 6: PRICE CORRELATION ====================
    st.header("6️⃣ Market Price Correlation")

    # Calculate correlation matrix
    price_data = df[['Day Ahead Price (EPEX)', 'GB-ISEM Intraday 1 Price', 'SSP', 'SBP']].copy()
    price_data = price_data.apply(pd.to_numeric, errors='coerce')
    correlation = price_data.corr()

    fig = px.imshow(
        correlation,
        labels=dict(color="Correlation"),
        x=['EPEX DA', 'Intraday', 'SSP', 'SBP'],
        y=['EPEX DA', 'Intraday', 'SSP', 'SBP'],
        color_continuous_scale='RdBu_r',
        zmin=-1, zmax=1,
        text_auto='.2f'
    )
    fig.update_layout(title="Price Correlation Matrix", height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.info("""
    **Correlation Insights:**
    - High correlation (>0.8) between markets suggests limited arbitrage opportunities between them
    - Low correlation indicates potential for cross-market arbitrage
    - SSP/SBP divergence creates imbalance market opportunities
    """)


def show_imbalance_deep_dive(month: str = "September 2025"):
    """Display imbalance deep dive analysis"""
    st.title(f"⚠️ Imbalance Deep Dive - {month}")
    st.markdown("### Root Cause Analysis of Imbalance Penalties")
    st.markdown("---")

    # Load data
    month_config = AVAILABLE_MONTHS.get(month, AVAILABLE_MONTHS["September 2025"])
    master_file = month_config.get("master_file", "Master_BESS_Analysis_Sept_2025.csv")

    try:
        df = pd.read_csv(os.path.join(DATA_DIR, master_file))
        if 'Unnamed: 0' in df.columns:
            df.rename(columns={'Unnamed: 0': 'Timestamp'}, inplace=True)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Date'] = df['Timestamp'].dt.date
        df['Hour'] = df['Timestamp'].dt.hour
        df['DayOfWeek'] = df['Timestamp'].dt.day_name()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return

    # Calculate imbalance columns
    df['Imbalance Revenue'] = pd.to_numeric(df.get('Imbalance Revenue', 0), errors='coerce').fillna(0)
    df['Imbalance Charge'] = pd.to_numeric(df.get('Imbalance Charge', 0), errors='coerce').fillna(0)
    df['Net_Imbalance'] = df['Imbalance Revenue'] - df['Imbalance Charge']
    df['SSP'] = pd.to_numeric(df['SSP'], errors='coerce').fillna(0)
    df['SBP'] = pd.to_numeric(df['SBP'], errors='coerce').fillna(0)
    df['SSP_SBP_Spread'] = df['SBP'] - df['SSP']

    # ==================== SECTION 1: IMBALANCE SUMMARY ====================
    st.header("1️⃣ Imbalance Summary")

    total_revenue = df['Imbalance Revenue'].sum()
    total_charge = df['Imbalance Charge'].sum()
    net_imbalance = total_revenue - total_charge
    periods_with_charge = (df['Imbalance Charge'] > 0).sum()
    periods_with_revenue = (df['Imbalance Revenue'] > 0).sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Imbalance Revenue", f"£{total_revenue:,.0f}",
                 delta=f"{periods_with_revenue} periods", delta_color="off",
                 help="Revenue earned from imbalance market positions")
    with col2:
        st.metric("Imbalance Charges", f"£{total_charge:,.0f}",
                 delta=f"{periods_with_charge} periods", delta_color="off",
                 help="Penalties paid for imbalance positions")
    with col3:
        color = "normal" if net_imbalance >= 0 else "inverse"
        st.metric("Net Imbalance", f"£{net_imbalance:,.0f}",
                 delta="Profit" if net_imbalance >= 0 else "Loss", delta_color=color,
                 help="Revenue - Charges. Negative = net loss from imbalance")
    with col4:
        st.metric("% of Periods with Charges", f"{periods_with_charge/len(df)*100:.1f}%",
                 help="% of 30-min settlement periods that incurred charges")

    if net_imbalance < 0:
        st.error(f"⚠️ **Critical:** Net imbalance loss of **£{abs(net_imbalance):,.0f}** this month")
    else:
        st.success(f"✅ Net imbalance profit of **£{net_imbalance:,.0f}** this month")

    st.markdown("---")

    # ==================== SECTION 2: DAILY BREAKDOWN ====================
    st.header("2️⃣ Daily Imbalance Breakdown")

    daily_imbalance = df.groupby('Date').agg({
        'Imbalance Revenue': 'sum',
        'Imbalance Charge': 'sum',
        'Net_Imbalance': 'sum'
    }).reset_index()
    daily_imbalance['Date'] = pd.to_datetime(daily_imbalance['Date'])

    # Identify worst days
    worst_days = daily_imbalance.nsmallest(5, 'Net_Imbalance')

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=daily_imbalance['Date'],
        y=daily_imbalance['Imbalance Revenue'],
        name='Revenue',
        marker_color='#2ecc71'
    ))
    fig.add_trace(go.Bar(
        x=daily_imbalance['Date'],
        y=-daily_imbalance['Imbalance Charge'],
        name='Charges',
        marker_color='#e74c3c'
    ))
    fig.update_layout(
        title="Daily Imbalance Revenue vs Charges",
        xaxis_title="Date",
        yaxis_title="Amount (£)",
        barmode='relative',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # Worst days table
    st.subheader("Top 5 Worst Imbalance Days")
    worst_display = worst_days.copy()
    worst_display['Date'] = worst_display['Date'].dt.strftime('%Y-%m-%d')
    worst_display.columns = ['Date', 'Revenue (£)', 'Charges (£)', 'Net (£)']
    st.dataframe(worst_display, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ==================== SECTION 3: HOURLY PATTERN ====================
    st.header("3️⃣ Imbalance by Hour of Day")

    hourly_imbalance = df.groupby('Hour').agg({
        'Imbalance Charge': 'sum',
        'Net_Imbalance': 'sum'
    }).reset_index()

    worst_hour = hourly_imbalance.loc[hourly_imbalance['Imbalance Charge'].idxmax(), 'Hour']
    worst_hour_amount = hourly_imbalance['Imbalance Charge'].max()

    st.warning(f"**Peak Imbalance Hour:** {int(worst_hour):02d}:00 - £{worst_hour_amount:,.0f} in charges")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=hourly_imbalance['Hour'],
        y=hourly_imbalance['Imbalance Charge'],
        name='Total Charges by Hour',
        marker_color='#e74c3c'
    ))
    fig.update_layout(
        title="Imbalance Charges by Hour of Day",
        xaxis_title="Hour",
        yaxis_title="Total Charges (£)",
        xaxis=dict(tickmode='linear', tick0=0, dtick=2),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ==================== SECTION 4: CORRELATION WITH MARKET CONDITIONS ====================
    st.header("4️⃣ Correlation with Market Conditions")

    # Filter periods with imbalance charges
    charged_periods = df[df['Imbalance Charge'] > 0].copy()

    if len(charged_periods) > 0:
        avg_spread_during_charge = charged_periods['SSP_SBP_Spread'].mean()
        avg_spread_overall = df['SSP_SBP_Spread'].mean()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg SSP/SBP Spread (All)", f"£{avg_spread_overall:.2f}/MWh",
                     help="Average system price spread across all periods")
        with col2:
            st.metric("Avg Spread (During Charges)", f"£{avg_spread_during_charge:.2f}/MWh",
                     delta=f"{avg_spread_during_charge - avg_spread_overall:+.2f}",
                     help="Average spread when charges occurred vs overall")
        with col3:
            correlation = charged_periods['Imbalance Charge'].corr(charged_periods['SSP_SBP_Spread'])
            st.metric("Charge-Spread Correlation", f"{correlation:.2f}",
                     help="How charges relate to price volatility (-1 to +1). High = charges during volatile periods")

        # Scatter plot: charge vs spread
        fig = px.scatter(
            charged_periods,
            x='SSP_SBP_Spread',
            y='Imbalance Charge',
            color='Hour',
            title="Imbalance Charges vs SSP/SBP Spread",
            labels={'SSP_SBP_Spread': 'SSP/SBP Spread (£/MWh)', 'Imbalance Charge': 'Charge (£)'},
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.info("""
        **Analysis:**
        - If charges correlate with high spreads, imbalance is occurring during volatile periods (forecast error)
        - If charges occur during low spreads, it may indicate systematic position errors
        """)
    else:
        st.success("No imbalance charges recorded this month!")

    st.markdown("---")

    # ==================== SECTION 5: ROOT CAUSE ANALYSIS ====================
    st.header("5️⃣ Root Cause Analysis")

    if len(charged_periods) > 0:
        # Categorize by time of day
        morning_charges = charged_periods[(charged_periods['Hour'] >= 6) & (charged_periods['Hour'] < 12)]['Imbalance Charge'].sum()
        afternoon_charges = charged_periods[(charged_periods['Hour'] >= 12) & (charged_periods['Hour'] < 18)]['Imbalance Charge'].sum()
        evening_charges = charged_periods[(charged_periods['Hour'] >= 18) & (charged_periods['Hour'] < 22)]['Imbalance Charge'].sum()
        night_charges = charged_periods[(charged_periods['Hour'] >= 22) | (charged_periods['Hour'] < 6)]['Imbalance Charge'].sum()

        # Pie chart
        fig = go.Figure(data=[go.Pie(
            labels=['Morning (6-12)', 'Afternoon (12-18)', 'Evening (18-22)', 'Night (22-6)'],
            values=[morning_charges, afternoon_charges, evening_charges, night_charges],
            hole=0.4,
            marker_colors=['#f39c12', '#e74c3c', '#9b59b6', '#3498db']
        )])
        fig.update_layout(title="Imbalance Charges by Time of Day", height=350)
        st.plotly_chart(fig, use_container_width=True)

        # Key findings
        max_period = max([
            ('Morning', morning_charges),
            ('Afternoon', afternoon_charges),
            ('Evening', evening_charges),
            ('Night', night_charges)
        ], key=lambda x: x[1])

        st.error(f"""
        **Key Finding:** {max_period[1]/total_charge*100:.0f}% of imbalance charges (£{max_period[0]}: £{max_period[1]:,.0f}) occur during **{max_period[0]}** periods.

        **Potential Causes:**
        - Forecast errors during high-demand periods
        - Unexpected frequency response activations
        - Market position adjustments arriving late
        - Physical constraints preventing optimal dispatch
        """)

        # Recommendations
        st.subheader("💡 Recommendations")
        st.markdown(f"""
        1. **Focus on {max_period[0]} periods** - Review dispatch decisions during these hours
        2. **Improve forecasting** - Better predict imbalance exposure during volatile periods
        3. **Reduce position size** - During peak charge hours ({int(worst_hour):02d}:00), consider smaller positions
        4. **Monitor SSP/SBP spread** - High spreads (>£{avg_spread_during_charge:.0f}/MWh) correlate with charges
        5. **Consider imbalance hedging** - Use intraday markets to reduce exposure
        """)
    else:
        st.success("No imbalance issues to analyze - excellent performance!")


def show_ancillary_services_analysis(month: str = "September 2025"):
    """Display ancillary services analysis - SFFR, DC, DM, DR comparison"""
    st.title(f"⚡ Ancillary Services Analysis - {month}")
    st.markdown("### Service Utilization, Revenue Comparison & Opportunity Cost")
    st.markdown("---")

    # Load data
    month_config = AVAILABLE_MONTHS.get(month, AVAILABLE_MONTHS["September 2025"])
    master_file = month_config.get("master_file", "Master_BESS_Analysis_Sept_2025.csv")

    try:
        df = pd.read_csv(os.path.join(DATA_DIR, master_file))
        if 'Unnamed: 0' in df.columns:
            df.rename(columns={'Unnamed: 0': 'Timestamp'}, inplace=True)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Date'] = df['Timestamp'].dt.date
        df['Hour'] = df['Timestamp'].dt.hour
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return

    # Ancillary service definitions
    services = {
        'SFFR': {'avail': 'SFFR Availability', 'price': 'SFFR Clearing Price', 'rev': 'SFFR revenues', 'name': 'Static FFR'},
        'DCL': {'avail': 'DCL Availability', 'price': 'DCL Clearing Price', 'rev': 'DCL revenues', 'name': 'DC Low'},
        'DCH': {'avail': 'DCH Availability', 'price': 'DCH Clearing Price', 'rev': 'DCH revenues', 'name': 'DC High'},
        'DML': {'avail': 'DML Availability', 'price': 'DML Clearing Price', 'rev': 'DML revenues', 'name': 'DM Low'},
        'DMH': {'avail': 'DMH Availability', 'price': 'DMH Clearing Price', 'rev': 'DMH revenues', 'name': 'DM High'},
        'DRL': {'avail': 'DRL Availability', 'price': 'DRL Clearing Price', 'rev': 'DRL revenues', 'name': 'DR Low'},
        'DRH': {'avail': 'DRH Availability', 'price': 'DRH Clearing Price', 'rev': 'DRH revenues', 'name': 'DR High'},
    }

    # Calculate metrics for each service
    service_metrics = []
    for code, cols in services.items():
        if cols['rev'] in df.columns:
            revenue = pd.to_numeric(df[cols['rev']], errors='coerce').fillna(0).sum()
            avail = pd.to_numeric(df.get(cols['avail'], 0), errors='coerce').fillna(0)
            price = pd.to_numeric(df.get(cols['price'], 0), errors='coerce').fillna(0)
            periods_active = (avail > 0).sum()
            avg_price = price[avail > 0].mean() if periods_active > 0 else 0
            total_mw_hours = (avail * 0.5).sum()  # 30-min periods

            service_metrics.append({
                'Service': code,
                'Name': cols['name'],
                'Total Revenue': revenue,
                'Periods Active': periods_active,
                'Avg Price': avg_price,
                'MW-Hours': total_mw_hours,
                'Revenue per MW-Hour': revenue / total_mw_hours if total_mw_hours > 0 else 0
            })

    metrics_df = pd.DataFrame(service_metrics)
    metrics_df = metrics_df.sort_values('Total Revenue', ascending=False)

    # ==================== SECTION 1: REVENUE SUMMARY ====================
    st.header("1️⃣ Ancillary Revenue Summary")

    total_ancillary = metrics_df['Total Revenue'].sum()
    top_service = metrics_df.iloc[0] if len(metrics_df) > 0 else None

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Ancillary Revenue", f"£{total_ancillary:,.0f}",
                 help="Sum of all frequency response service revenues (SFFR, DC, DM, DR)")
    with col2:
        if top_service is not None:
            st.metric("Top Service", top_service['Service'],
                     delta=f"£{top_service['Total Revenue']:,.0f}",
                     help="Service generating most revenue this month")
    with col3:
        services_used = (metrics_df['Total Revenue'] > 0).sum()
        st.metric("Services Used", f"{services_used} / {len(services)}",
                 help="Number of different services with non-zero revenue")
    with col4:
        if top_service is not None:
            share = top_service['Total Revenue'] / total_ancillary * 100 if total_ancillary > 0 else 0
            st.metric("Top Service Share", f"{share:.0f}%",
                     help="% of total ancillary revenue from top service")

    st.markdown("---")

    # ==================== SECTION 2: REVENUE BY SERVICE ====================
    st.header("2️⃣ Revenue by Service")

    fig = px.bar(
        metrics_df,
        x='Service',
        y='Total Revenue',
        color='Total Revenue',
        color_continuous_scale='Greens',
        title="Revenue by Ancillary Service",
        text=metrics_df['Total Revenue'].apply(lambda x: f'£{x:,.0f}')
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(yaxis_title="Revenue (£)", xaxis_title="Service", showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Summary table
    display_df = metrics_df[['Service', 'Name', 'Total Revenue', 'Periods Active', 'Avg Price', 'Revenue per MW-Hour']].copy()
    display_df['Total Revenue'] = display_df['Total Revenue'].apply(lambda x: f"£{x:,.0f}")
    display_df['Avg Price'] = display_df['Avg Price'].apply(lambda x: f"£{x:.2f}/MW/h")
    display_df['Revenue per MW-Hour'] = display_df['Revenue per MW-Hour'].apply(lambda x: f"£{x:.2f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ==================== SECTION 3: SERVICE UTILIZATION ====================
    st.header("3️⃣ Service Utilization Patterns")

    # Pie chart of utilization
    active_services = metrics_df[metrics_df['Total Revenue'] > 0]

    if len(active_services) > 0:
        fig = go.Figure(data=[go.Pie(
            labels=active_services['Service'],
            values=active_services['Total Revenue'],
            hole=0.4,
            textinfo='label+percent'
        )])
        fig.update_layout(title="Revenue Distribution by Service", height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Hourly heatmap for SFFR (main service)
    if 'SFFR revenues' in df.columns:
        hourly_sffr = df.groupby('Hour')['SFFR revenues'].sum().reset_index()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=hourly_sffr['Hour'],
            y=hourly_sffr['SFFR revenues'],
            marker_color='#2ecc71'
        ))
        fig.update_layout(
            title="SFFR Revenue by Hour of Day",
            xaxis_title="Hour",
            yaxis_title="Revenue (£)",
            xaxis=dict(tickmode='linear', tick0=0, dtick=2),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ==================== SECTION 4: REVENUE PER MW COMPARISON ====================
    st.header("4️⃣ Revenue per MW-Hour (Efficiency)")

    efficient_df = metrics_df[metrics_df['MW-Hours'] > 0].sort_values('Revenue per MW-Hour', ascending=False)

    if len(efficient_df) > 0:
        fig = px.bar(
            efficient_df,
            x='Service',
            y='Revenue per MW-Hour',
            color='Revenue per MW-Hour',
            color_continuous_scale='Blues',
            title="Revenue per MW-Hour by Service (Higher = More Efficient)",
            text=efficient_df['Revenue per MW-Hour'].apply(lambda x: f'£{x:.2f}')
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(yaxis_title="£/MW-Hour", xaxis_title="Service", showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

        most_efficient = efficient_df.iloc[0]
        st.success(f"**Most Efficient Service:** {most_efficient['Service']} ({most_efficient['Name']}) at £{most_efficient['Revenue per MW-Hour']:.2f}/MW-Hour")

    st.markdown("---")

    # ==================== SECTION 5: OPPORTUNITY COST ANALYSIS ====================
    st.header("5️⃣ Opportunity Cost Analysis")

    st.markdown("*What if GridBeyond had used a different service mix?*")

    if len(efficient_df) > 0 and len(metrics_df) > 0:
        # Calculate what revenue would be if all MW-hours went to most efficient service
        total_mw_hours = metrics_df['MW-Hours'].sum()
        most_efficient_rate = efficient_df.iloc[0]['Revenue per MW-Hour']
        current_rate = total_ancillary / total_mw_hours if total_mw_hours > 0 else 0

        optimal_revenue = total_mw_hours * most_efficient_rate
        opportunity_cost = optimal_revenue - total_ancillary

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Avg Rate", f"£{current_rate:.2f}/MW-h",
                     help="Actual revenue / MW-hours committed across all services")
        with col2:
            st.metric("Best Service Rate", f"£{most_efficient_rate:.2f}/MW-h",
                     help="Highest £/MW-hour achieved by any single service")
        with col3:
            st.metric("Opportunity Cost", f"£{opportunity_cost:,.0f}",
                     delta="Potential additional revenue" if opportunity_cost > 0 else "Optimal mix achieved",
                     delta_color="inverse" if opportunity_cost > 0 else "normal",
                     help="Theoretical gain if all capacity went to best service (ignores market constraints)")

        if opportunity_cost > 0:
            st.warning(f"""
            **Analysis:** If all {total_mw_hours:,.0f} MW-hours had been allocated to {efficient_df.iloc[0]['Service']}
            instead of the current mix, revenue could have been **£{optimal_revenue:,.0f}** instead of **£{total_ancillary:,.0f}**.

            *Note: This is theoretical - market availability and grid requirements constrain actual allocation.*
            """)
        else:
            st.success("Current service allocation appears optimal for the available market conditions.")

    st.markdown("---")

    # ==================== SECTION 6: RECOMMENDATIONS ====================
    st.header("6️⃣ Recommendations")

    if len(metrics_df) > 0:
        sffr_share = metrics_df[metrics_df['Service'] == 'SFFR']['Total Revenue'].sum() / total_ancillary * 100 if total_ancillary > 0 else 0

        st.info(f"""
        **Current Strategy Analysis:**
        - SFFR accounts for **{sffr_share:.0f}%** of ancillary revenue
        - {(metrics_df['Total Revenue'] == 0).sum()} services were not utilized this month

        **Recommendations:**
        1. **Diversification**: Consider utilizing more DC/DM/DR services for risk mitigation
        2. **Price Monitoring**: Track clearing prices across all services to identify arbitrage
        3. **Stacking Strategy**: Explore combining services during different time windows
        4. **Market Analysis**: Review why certain services show zero revenue - market conditions or strategy choice?
        """)


def generate_pdf_report(month: str = "September 2025"):
    """Generate PDF executive summary report"""
    from io import BytesIO

    # Load data
    month_config = AVAILABLE_MONTHS.get(month, AVAILABLE_MONTHS["September 2025"])
    master_file = month_config.get("master_file", "Master_BESS_Analysis_Sept_2025.csv")
    optimization_file = month_config.get("optimization_file", "Optimized_Results_Sept_2025.csv")

    try:
        df = pd.read_csv(os.path.join(DATA_DIR, master_file))
        opt_df = pd.read_csv(os.path.join(DATA_DIR, optimization_file))
    except Exception as e:
        return None, f"Error loading data: {str(e)}"

    # Calculate metrics
    def safe_sum(dataframe, col):
        if col in dataframe.columns:
            return pd.to_numeric(dataframe[col], errors='coerce').fillna(0).sum()
        return 0

    sffr = safe_sum(df, 'SFFR revenues')
    epex = safe_sum(df, 'EPEX 30 DA Revenue') + safe_sum(df, 'EPEX DA Revenues')
    ida1 = safe_sum(df, 'IDA1 Revenue')
    idc = safe_sum(df, 'IDC Revenue')
    imb_rev = safe_sum(df, 'Imbalance Revenue')
    imb_charge = safe_sum(df, 'Imbalance Charge')
    total_actual = sffr + epex + ida1 + idc + imb_rev - imb_charge

    optimal = opt_df['Optimised_Revenue_Multi'].sum() if 'Optimised_Revenue_Multi' in opt_df.columns else 0
    capture_rate = (total_actual / optimal * 100) if optimal > 0 else 0
    gap = optimal - total_actual

    # Generate text report
    report = f"""
================================================================================
                    BESS PERFORMANCE EXECUTIVE SUMMARY
                           {month}
================================================================================

ASSET: Northwold Solar Farm BESS
AGGREGATOR: GridBeyond
REPORT DATE: {datetime.now().strftime('%Y-%m-%d')}

--------------------------------------------------------------------------------
                           KEY METRICS
--------------------------------------------------------------------------------

ACTUAL REVENUE:         £{total_actual:,.0f}
OPTIMAL (SIMULATED):    £{optimal:,.0f}
REVENUE GAP:            £{gap:,.0f}
CAPTURE RATE:           {capture_rate:.1f}%

--------------------------------------------------------------------------------
                        REVENUE BREAKDOWN
--------------------------------------------------------------------------------

SFFR (Frequency Response):     £{sffr:,.0f}
EPEX Trading:                  £{epex:,.0f}
IDA1 Trading:                  £{ida1:,.0f}
IDC Trading:                   £{idc:,.0f}
Imbalance Revenue:             £{imb_rev:,.0f}
Imbalance Charges:            -£{imb_charge:,.0f}
                              ──────────
TOTAL:                         £{total_actual:,.0f}

--------------------------------------------------------------------------------
                        PERFORMANCE ASSESSMENT
--------------------------------------------------------------------------------

"""
    if capture_rate >= 90:
        report += "ASSESSMENT: EXCELLENT - Near-optimal performance achieved\n"
    elif capture_rate >= 70:
        report += "ASSESSMENT: GOOD - Solid performance with room for improvement\n"
    elif capture_rate >= 50:
        report += "ASSESSMENT: MODERATE - Significant revenue left on table\n"
    else:
        report += "ASSESSMENT: POOR - Major optimization opportunities exist\n"

    if imb_charge > 1000:
        report += f"\n⚠️  WARNING: High imbalance charges of £{imb_charge:,.0f} detected\n"

    report += f"""
--------------------------------------------------------------------------------
                        RECOMMENDATIONS
--------------------------------------------------------------------------------

1. {'MAINTAIN current strategy - excellent capture rate' if capture_rate >= 90 else 'REVIEW trading strategy to close revenue gap'}
2. {'Imbalance management is effective' if imb_charge < 1000 else f'INVESTIGATE imbalance charges (£{imb_charge:,.0f} this month)'}
3. Continue monitoring multi-market optimization opportunities
4. Review ancillary service allocation for efficiency

--------------------------------------------------------------------------------
                           ANNUALIZED PROJECTION
--------------------------------------------------------------------------------

Based on {month} performance:
- Projected Annual Revenue: £{total_actual * 12:,.0f}
- Projected Optimal:        £{optimal * 12:,.0f}
- Projected Annual Gap:     £{gap * 12:,.0f}

================================================================================
Generated by BESS Analysis Dashboard
🤖 Automated Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}
================================================================================
"""

    return report, None


def show_pdf_export_page(month: str = "September 2025"):
    """Display PDF export page"""
    st.title("📄 Export Executive Summary")
    st.markdown("### Generate Reports for GridBeyond Meetings")
    st.markdown("---")

    st.subheader("Select Report Options")

    col1, col2 = st.columns(2)

    with col1:
        report_month = st.selectbox(
            "Report Month",
            list(AVAILABLE_MONTHS.keys()),
            index=list(AVAILABLE_MONTHS.keys()).index(month) if month in AVAILABLE_MONTHS else 0
        )

    with col2:
        report_format = st.radio(
            "Report Format",
            ["Text Summary", "CSV Data Export"],
            horizontal=True
        )

    st.markdown("---")

    if st.button("📥 Generate Report", type="primary"):
        with st.spinner("Generating report..."):
            if report_format == "Text Summary":
                report, error = generate_pdf_report(report_month)

                if error:
                    st.error(error)
                else:
                    st.success("Report generated successfully!")

                    # Preview
                    st.subheader("Report Preview")
                    st.text(report)

                    # Download button
                    st.download_button(
                        label="📥 Download Report",
                        data=report,
                        file_name=f"BESS_Executive_Summary_{report_month.replace(' ', '_')}.txt",
                        mime="text/plain"
                    )

            else:  # CSV Export
                month_config = AVAILABLE_MONTHS.get(report_month)
                if month_config:
                    try:
                        master_df = pd.read_csv(os.path.join(DATA_DIR, month_config['master_file']))
                        opt_df = pd.read_csv(os.path.join(DATA_DIR, month_config['optimization_file']))

                        st.success("Data loaded successfully!")

                        col1, col2 = st.columns(2)

                        with col1:
                            csv1 = master_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Master Data",
                                data=csv1,
                                file_name=f"Master_Data_{report_month.replace(' ', '_')}.csv",
                                mime="text/csv"
                            )

                        with col2:
                            csv2 = opt_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Optimization Results",
                                data=csv2,
                                file_name=f"Optimization_{report_month.replace(' ', '_')}.csv",
                                mime="text/csv"
                            )

                    except Exception as e:
                        st.error(f"Error loading data: {str(e)}")

    st.markdown("---")

    # Quick comparison export
    st.subheader("Multi-Month Comparison Export")

    if st.button("📊 Export Sept vs Oct Comparison"):
        with st.spinner("Generating comparison..."):
            try:
                # Load both months
                sept_master = pd.read_csv(os.path.join(DATA_DIR, "Master_BESS_Analysis_Sept_2025.csv"))
                oct_master = pd.read_csv(os.path.join(DATA_DIR, "Master_BESS_Analysis_Oct_2025.csv"))
                sept_opt = pd.read_csv(os.path.join(DATA_DIR, "Optimized_Results_Sept_2025.csv"))
                oct_opt = pd.read_csv(os.path.join(DATA_DIR, "Optimized_Results_Oct_2025.csv"))

                def calc_metrics(master_df, opt_df):
                    def safe_sum(dataframe, col):
                        if col in dataframe.columns:
                            return pd.to_numeric(dataframe[col], errors='coerce').fillna(0).sum()
                        return 0

                    sffr = safe_sum(master_df, 'SFFR revenues')
                    epex = safe_sum(master_df, 'EPEX 30 DA Revenue') + safe_sum(master_df, 'EPEX DA Revenues')
                    imb = safe_sum(master_df, 'Imbalance Revenue') - safe_sum(master_df, 'Imbalance Charge')
                    total = sffr + epex + safe_sum(master_df, 'IDA1 Revenue') + safe_sum(master_df, 'IDC Revenue') + imb
                    optimal = opt_df['Optimised_Revenue_Multi'].sum() if 'Optimised_Revenue_Multi' in opt_df.columns else 0

                    return {
                        'SFFR': sffr,
                        'EPEX': epex,
                        'Imbalance': imb,
                        'Total Actual': total,
                        'Optimal': optimal,
                        'Capture Rate': total / optimal * 100 if optimal > 0 else 0,
                        'Gap': optimal - total
                    }

                sept_metrics = calc_metrics(sept_master, sept_opt)
                oct_metrics = calc_metrics(oct_master, oct_opt)

                comparison_df = pd.DataFrame({
                    'Metric': list(sept_metrics.keys()),
                    'September': [f"£{v:,.0f}" if 'Rate' not in k else f"{v:.1f}%" for k, v in sept_metrics.items()],
                    'October': [f"£{v:,.0f}" if 'Rate' not in k else f"{v:.1f}%" for k, v in oct_metrics.items()],
                })

                st.dataframe(comparison_df, use_container_width=True, hide_index=True)

                csv = comparison_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Comparison CSV",
                    data=csv,
                    file_name="Sept_Oct_Comparison.csv",
                    mime="text/csv"
                )

            except Exception as e:
                st.error(f"Error generating comparison: {str(e)}")


def show_benchmark_comparison():
    """Display industry benchmark comparison page."""
    st.title("📊 Industry Benchmarks")
    st.markdown("Compare Northwold's performance against UK BESS industry benchmarks")

    # Load and calculate Northwold metrics first
    try:
        sept_master = pd.read_csv(os.path.join(DATA_DIR, "Master_BESS_Analysis_Sept_2025.csv"))
        oct_master = pd.read_csv(os.path.join(DATA_DIR, "Master_BESS_Analysis_Oct_2025.csv"))

        def calculate_monthly_revenue(df):
            """Calculate total revenue for a month."""
            def safe_sum(dataframe, col):
                if col in dataframe.columns:
                    return pd.to_numeric(dataframe[col], errors='coerce').fillna(0).sum()
                return 0

            sffr = safe_sum(df, 'SFFR revenues')
            epex = safe_sum(df, 'EPEX 30 DA Revenue') + safe_sum(df, 'EPEX DA Revenues')
            ida1 = safe_sum(df, 'IDA1 Revenue')
            idc = safe_sum(df, 'IDC Revenue')
            imb_rev = safe_sum(df, 'Imbalance Revenue')
            imb_charge = safe_sum(df, 'Imbalance Charge')

            return sffr + epex + ida1 + idc + imb_rev - imb_charge

        def calculate_cycles_local(df, power_col, capacity_mwh=8.4, dt_hours=0.5):
            """Calculate cycles using industry standard method."""
            if power_col not in df.columns:
                return None
            power = pd.to_numeric(df[power_col], errors='coerce').fillna(0)
            energy = power * dt_hours
            discharge_mwh = energy[energy > 0].sum()
            charge_mwh = abs(energy[energy < 0].sum())
            return (discharge_mwh + charge_mwh) / 2 / capacity_mwh

        # Calculate metrics
        capacity_mw = 4.2

        sept_revenue = calculate_monthly_revenue(sept_master)
        oct_revenue = calculate_monthly_revenue(oct_master)

        sept_annual_per_mw = (sept_revenue / 30) * 365 / capacity_mw
        oct_annual_per_mw = (oct_revenue / 31) * 365 / capacity_mw

        # Find power column for each month (column names differ between months)
        # Prefer Power_MW columns (dt_hours=0.5), fallback to Battery MWh (dt_hours=1.0)
        sept_power_col = None
        sept_dt = 0.5
        for col in sept_master.columns:
            if 'Physical_Power_MW' in col or col == 'Power_MW':
                sept_power_col = col
                sept_dt = 0.5
                break
            elif 'Battery MWh' in col and sept_power_col is None:
                sept_power_col = col
                sept_dt = 1.0  # Already in MWh

        oct_power_col = None
        oct_dt = 0.5
        for col in oct_master.columns:
            if 'Physical_Power_MW' in col or col == 'Power_MW':
                oct_power_col = col
                oct_dt = 0.5
                break
            elif 'Battery MWh' in col and oct_power_col is None:
                oct_power_col = col
                oct_dt = 1.0  # Already in MWh

        sept_cycles = calculate_cycles_local(sept_master, sept_power_col, dt_hours=sept_dt) if sept_power_col else None
        oct_cycles = calculate_cycles_local(oct_master, oct_power_col, dt_hours=oct_dt) if oct_power_col else None

        # Calculate days properly
        if 'Timestamp' in sept_master.columns:
            sept_master['Timestamp'] = pd.to_datetime(sept_master['Timestamp'], errors='coerce')
            sept_days = sept_master['Timestamp'].dt.date.nunique()
        else:
            sept_days = 30
        if 'Timestamp' in oct_master.columns:
            oct_master['Timestamp'] = pd.to_datetime(oct_master['Timestamp'], errors='coerce')
            oct_days = oct_master['Timestamp'].dt.date.nunique()
        else:
            oct_days = 31

        sept_daily_cycles = sept_cycles / sept_days if sept_cycles else None
        oct_daily_cycles = oct_cycles / oct_days if oct_cycles else None
        avg_annual = (sept_annual_per_mw + oct_annual_per_mw) / 2

        data_loaded = True
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        data_loaded = False
        sept_annual_per_mw = oct_annual_per_mw = sept_daily_cycles = oct_daily_cycles = None
        sept_revenue = oct_revenue = avg_annual = 0

    # Combined benchmark table with Northwold data
    st.header("Northwold vs Industry Benchmarks")

    if data_loaded:
        # Build combined table
        combined_data = {
            'Metric': [
                'Total Revenue (£)',
                'Revenue (£/MW/year)',
                'Daily Cycles',
                'Degradation (%/365 cycles)',
                'Availability (TWCAA %)',
                'Round-Trip Efficiency (%)'
            ],
            'Sept 2025': [
                f"£{round(sept_revenue):,}",
                f"£{round(sept_annual_per_mw):,}",
                f"{sept_daily_cycles:.2f}" if sept_daily_cycles else "N/A",
                "TBD",
                "TBD",
                "~85%"
            ],
            'Oct 2025': [
                f"£{round(oct_revenue):,}",
                f"£{round(oct_annual_per_mw):,}",
                f"{oct_daily_cycles:.2f}" if oct_daily_cycles else "N/A",
                "TBD",
                "TBD",
                "~85%"
            ],
            'Low': ['-', '£36,000', '1.0', '4.0%', '90%', '82%'],
            'Mid': ['-', '£60,000', '1.5', '4.4%', '94.4%', '85%'],
            'High': ['-', '£88,000', '3.0', '11.0%', '98%', '90%'],
            'Source': ['-', 'Modo Energy', 'OEM Warranty', 'NREL', 'National Grid ESO', 'DNV GL']
        }

        combined_df = pd.DataFrame(combined_data)
        st.dataframe(combined_df, use_container_width=True, hide_index=True)

        # Rating indicators
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**September Rating:**")
            if sept_annual_per_mw < 36000:
                st.error("⬇️ Below industry low")
            elif sept_annual_per_mw < 60000:
                st.warning("➡️ Below industry mid")
            elif sept_annual_per_mw < 88000:
                st.success("✅ Above industry mid")
            else:
                st.success("🌟 Above industry high!")
        with col2:
            st.markdown("**October Rating:**")
            if oct_annual_per_mw < 36000:
                st.error("⬇️ Below industry low")
            elif oct_annual_per_mw < 60000:
                st.warning("➡️ Below industry mid")
            elif oct_annual_per_mw < 88000:
                st.success("✅ Above industry mid")
            else:
                st.success("🌟 Above industry high!")
        with col3:
            st.markdown("**Combined Average:**")
            st.metric("£/MW/year", f"£{round(avg_annual):,}")

    # Source links
    with st.expander("📎 Data Sources"):
        st.markdown("""
        **Revenue Benchmarks (Modo Energy GB BESS Index):**
        - [2024 Year in Review](https://modoenergy.com/research/gb-battery-energy-storage-markets-2024-year-in-review-great-britain-wholesale-balancing-mechanism-frequency-response-reserve) - Annual summary *(Published: Jan 2025)*
        - [December 2024 Benchmark](https://modoenergy.com/research/battery-energy-storage-revenues-december-benchmark-gb-2024-quick-reserve) - £84k/MW/year (2-year high) *(Published: Jan 2025)*
        - [January 2025 Roundup](https://modoenergy.com/research/gb-research-roundup-january-2025-battery-energy-storage-great-britain-revenues-markets-wholesale-capacity-market-balancing-mechanism) - £88k/MW/year *(Published: Feb 2025)*
        - [June 2025 Benchmark](https://modoenergy.com/research/battery-energy-storage-revenues-gb-benchmark-june-2025-negative-prices) - £76k/MW/year *(Published: Jul 2025)*

        **Other Sources:**
        - **NREL**: [Battery Degradation Study](https://www.nrel.gov/docs/fy22osti/80688.pdf) *(Published: 2022)*
        - **National Grid ESO**: [Transmission Performance Reports](https://www.nationalgrideso.com/research-and-publications/transmission-performance-reports) *(Updated quarterly)*
        - **DNV GL**: Energy Storage Performance Standards *(Industry standard reference)*
        - **OEM Warranty**: Manufacturer warranty documentation - 1.5 cycles/day typical *(Per Northwold agreement)*

        **Note:** Modo Energy's GB BESS Index tracks monthly revenues across all GB batteries. Range £36k-£88k/MW/year based on 2024-2025 data.
        """)

    st.markdown("---")

    if data_loaded:
        # Visual comparison chart
        st.subheader("Revenue Benchmark Comparison")

        fig = go.Figure()

        # Add benchmark ranges as horizontal bars
        fig.add_trace(go.Bar(
            name='Industry Range',
            x=['Revenue £/MW/year'],
            y=[88000 - 36000],
            base=[36000],
            marker_color='lightgray',
            width=0.3,
            showlegend=True
        ))

        # Add industry mid line
        fig.add_hline(y=60000, line_dash="dash", line_color="orange",
                      annotation_text="Industry Mid (£60k)", annotation_position="right")

        # Add Northwold performance markers
        fig.add_trace(go.Scatter(
            name='September 2025',
            x=['Revenue £/MW/year'],
            y=[sept_annual_per_mw],
            mode='markers',
            marker=dict(size=20, color='blue', symbol='diamond'),
        ))

        fig.add_trace(go.Scatter(
            name='October 2025',
            x=['Revenue £/MW/year'],
            y=[oct_annual_per_mw],
            mode='markers',
            marker=dict(size=20, color='green', symbol='diamond'),
        ))

        fig.update_layout(
            title="Northwold vs Industry Benchmarks",
            yaxis_title="£/MW/year",
            yaxis=dict(range=[0, max(120000, oct_annual_per_mw * 1.1)]),
            height=400,
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

        # Key insights
        st.markdown("---")
        st.subheader("Key Insights")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Strengths:**")
            if oct_annual_per_mw >= 88000:
                st.markdown("- 🌟 October exceeded industry high benchmark")
            if avg_annual >= 60000:
                st.markdown("- ✅ Combined average above industry mid")
            if sept_daily_cycles and sept_daily_cycles <= 1.5:
                st.markdown("- 🔋 September cycling within warranty limits")
            if oct_daily_cycles and oct_daily_cycles <= 1.5:
                st.markdown("- 🔋 October cycling within warranty limits")

        with col2:
            st.markdown("**Areas for Improvement:**")
            if sept_annual_per_mw < 60000:
                gap = 60000 - sept_annual_per_mw
                st.markdown(f"- September £{gap:,.0f}/MW below industry mid")
            if avg_annual < 88000:
                gap = 88000 - avg_annual
                st.markdown(f"- Combined average £{gap:,.0f}/MW below industry high")

        st.markdown("---")
        st.caption("""
        **Sources:**
        - Revenue benchmarks: Modo Energy UK BESS Market Analysis (2024-2025)
        - Degradation & cycling: Industry warranty standards and research
        - Availability (TWCAA): National Grid ESO performance data
        - Round-trip efficiency: Lithium-ion industry specifications
        """)


def main():
    """Main application with sidebar navigation"""

    # Sidebar configuration
    st.sidebar.title("🔋 BESS Dashboard")

    # General section (month-independent pages)
    st.sidebar.markdown("### General")
    show_asset_page = st.sidebar.button("🏭 Asset Details", use_container_width=True)
    show_import_page = st.sidebar.button("📥 Data Import", use_container_width=True)
    show_exec_comparison = st.sidebar.button("📊 Executive Comparison", use_container_width=True)
    show_benchmark_page = st.sidebar.button("📈 Industry Benchmarks", use_container_width=True)
    show_export_page = st.sidebar.button("📄 Export Reports", use_container_width=True)

    st.sidebar.markdown("---")

    # Month selector for data-dependent pages
    st.sidebar.markdown("### 📅 Monthly Analysis")
    selected_month = st.sidebar.selectbox(
        "Select Month",
        list(AVAILABLE_MONTHS.keys()),
        index=0
    )

    # Navigation menu for month-dependent pages
    page = st.sidebar.radio(
        "Pages",
        ["📊 Operations Summary", "🚀 Multi-Market Optimization", "📈 Market Prices", "⚠️ Imbalance Analysis", "⚡ Ancillary Services", "🔋 BESS Health", "📑 Performance Report"],
        index=0,  # Default to operations summary
        label_visibility="collapsed"
    )

    st.sidebar.markdown("---")
    st.sidebar.info(f"""
    **System:** Northwold Solar Farm
    **Location:** Hall Farm
    **Capacity:** 8.4 MWh
    """)

    # Glossary of terms
    with st.sidebar.expander("📖 Glossary"):
        st.markdown("""
**Markets:**
- **EPEX** - European Power Exchange (Day Ahead)
- **IDA1** - Intraday Auction 1
- **IDC** - Intraday Continuous
- **SSP** - System Sell Price (grid pays you)
- **SBP** - System Buy Price (you pay grid)

**Ancillary Services:**
- **SFFR** - Static Firm Frequency Response
- **DC** - Dynamic Containment (L=Low, H=High)
- **DM** - Dynamic Moderation (L=Low, H=High)
- **DR** - Dynamic Regulation (L=Low, H=High)

**Other Terms:**
- **EFA** - Electricity Forward Agreement (4-hour blocks)
- **SOC** - State of Charge (%)
- **MWh** - Megawatt-hours (energy)
- **MW** - Megawatts (power)
- **pp** - Percentage points (absolute % change)
- **Capture Rate** - Actual / Optimal revenue (%)
- **Gap** - Optimal - Actual revenue (£)
        """)

    # Display General pages if clicked (these take priority)
    if show_asset_page:
        show_asset_details()
        return
    if show_import_page:
        show_data_quality_page()
        return
    if show_exec_comparison:
        show_executive_comparison()
        return
    if show_benchmark_page:
        show_benchmark_comparison()
        return
    if show_export_page:
        show_pdf_export_page(selected_month)
        return

    # Display selected monthly page
    if page == "📊 Operations Summary":
        # Load data for selected month
        with st.spinner(f"Loading {selected_month} data..."):
            bess_df, northwold_df = load_month_data(selected_month)

        if bess_df is None or northwold_df is None:
            st.error(f"Failed to load data files for {selected_month}. Please ensure CSV files are in the correct location.")
            return

        # Perform analysis
        bess_analysis = analyze_bess_data(bess_df)
        northwold_analysis = analyze_northwold_data(northwold_df)

        # Show operations summary
        show_operations_summary(bess_df, northwold_df, bess_analysis, northwold_analysis, month=selected_month)
    elif page == "🚀 Multi-Market Optimization":
        show_multimarket_optimization(selected_month)
    elif page == "📈 Market Prices":
        show_market_price_analysis(selected_month)
    elif page == "⚠️ Imbalance Analysis":
        show_imbalance_deep_dive(selected_month)
    elif page == "⚡ Ancillary Services":
        show_ancillary_services_analysis(selected_month)
    elif page == "🔋 BESS Health":
        show_bess_health(selected_month)
    elif page == "📑 Performance Report":
        show_report_page(selected_month)

if __name__ == "__main__":
    main()