# BESS Analysis Dashboard

A comprehensive Streamlit dashboard for analyzing Battery Energy Storage System (BESS) performance and multi-market trading optimization for the Northwold Solar Farm.

## 🔋 Overview

This dashboard provides in-depth analysis of:
- BESS physical operations and state of charge
- Market trading revenues across multiple electricity markets
- Multi-market optimization strategies
- Battery health and degradation analysis
- Performance comparison between actual and optimized strategies
- Industry benchmarks and IAR (Internal Appraisal Report) comparison

## 🚀 Features

### 1. **Asset Details**
- Physical specifications of the Northwold Solar Farm BESS
- 8.4 MWh capacity with asymmetric 7.5/4.2 MW charge/discharge rates
- 87% round-trip efficiency

### 2. **September 2025 Operations Summary**
- Trading analysis with revenue breakdown
- Market price analysis across EPEX, SSP, SBP, and other markets
- Ancillary services pricing
- Interactive visualizations of battery operations

### 3. **Multi-Market Optimization**
- Cross-market arbitrage opportunities
- 172% revenue improvement potential
- Market utilization analysis
- Price spread analysis

### 4. **BESS Health Analysis**
- Cycling and degradation comparison
- Warranty compliance monitoring
- Projected battery lifespan
- Comparison across different trading strategies

### 5. **Performance Report**
- Executive summary of performance gaps
- Actual vs optimized revenue comparison
- Key drivers of revenue loss
- Strategic recommendations

### 6. **Benchmarks**

- Industry performance benchmarks (revenue per MW, utilization rates)
- IAR (Internal Appraisal Report) vs Actual revenue comparison
- Variance analysis by revenue stream (Day Ahead, Intraday, Frequency Response, etc.)
- Monthly capture rate metrics (Sept: 72%, Oct: 166%)

## 📊 Key Metrics

### September 2025

- **Actual Revenue**: £14,457
- **IAR Projected**: £19,973
- **Capture Rate**: 72%

### October 2025

- **Actual Revenue**: £38,344
- **IAR Projected**: £23,134
- **Capture Rate**: 166%

### Battery Operations

- **Daily Cycles**: ~0.95 (well below 1.5 warranty limit)
- **Round-trip Efficiency**: 87%
- **Capacity**: 8.4 MWh

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Optimization**: SciPy (Linear Programming)
- **Visualization**: Plotly
- **Language**: Python 3.11

## 📁 Project Structure

```
bess-analysis-dashboard/
│
├── data/                      # Data files
│   ├── BESS_Sept_2025_converted.csv
│   ├── Northwold_Sep_2025_converted.csv
│   ├── BESS_Oct_2025.csv
│   ├── Northwold_Oct_2025.csv
│   ├── Master_BESS_Analysis_Sept_2025.csv
│   ├── Master_BESS_Analysis_Oct_2025.csv
│   └── Optimized_Results_MultiMarket.csv
│
├── extra/                     # Additional data sources
│   └── Northwold BESS Revenue_IAR.xlsx  # IAR projections
│
├── src/                       # Source modules
│   ├── digital_twin_config.py
│   ├── phase3_multimarket.py
│   └── phase5.py
│
├── .streamlit/               # Streamlit configuration
│   └── config.toml
│
├── streamlit_dashboard.py    # Main application
├── requirements.txt          # Python dependencies
├── runtime.txt              # Python version
└── README.md               # This file
```

## 🚀 Deployment

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/bess-analysis-dashboard.git
cd bess-analysis-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the dashboard:
```bash
streamlit run streamlit_dashboard.py
```

### Streamlit Cloud Deployment

This dashboard is deployed on Streamlit Cloud. To deploy your own instance:

1. Fork this repository
2. Sign in to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app and connect your GitHub repository
4. Select `streamlit_dashboard.py` as the main file
5. Deploy!

## 📈 Dashboard Pages

### Asset Details
Displays the physical specifications and operational constraints of the BESS system.

### September 2025 Operations
Comprehensive analysis of actual trading performance including:
- Revenue streams (SFFR, EPEX, IDA1)
- Imbalance penalties analysis
- Market price comparisons

### Multi-Market Optimization
Shows optimization results across multiple electricity markets:
- EPEX Day-Ahead
- SSP (System Sell Price)
- SBP (System Buy Price)
- GB-ISEM Intraday
- DA Half-Hourly

### BESS Health
Monitors battery cycling and degradation:
- Daily cycle counts
- Warranty compliance
- Projected lifespan analysis

### Performance Report

Executive summary comparing actual vs optimized performance with key recommendations.

### Benchmarks

Industry benchmarks and IAR vs Actual comparison:

- Performance benchmarks against industry standards
- IAR projected revenue vs actual GridBeyond revenue
- Variance analysis by revenue stream
- Capture rate metrics with monthly trends

## 🔑 Key Insights

1. **Significant Revenue Opportunity**: Multi-market optimization can increase revenue by 172%
2. **Imbalance Penalties**: Current operations incur -£8,337 in penalties, erasing 37% of revenue
3. **Underutilization**: Operating at only 0.95 cycles/day vs 1.5 warranty limit
4. **Market Arbitrage**: SSP market provides best arbitrage opportunities with spreads up to £138/MWh

## 📝 License

This project is proprietary and confidential.

## 👥 Authors

- BESS Analysis Team
- Northwold Solar Farm Operations

## 📧 Contact

For questions or support, please contact the development team.

---

*Dashboard Version: 1.1.0*
*Last Updated: November 2025*