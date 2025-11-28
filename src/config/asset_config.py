"""
Asset Configuration for Northwold Solar Farm BESS

Physical and commercial constraints extracted from the
Northwold Storage Asset Optimisation Agreement.
"""

import numpy as np

# --- Asset Identity ---
ASSET_NAME = "Northwold Solar Farm (Hall Farm)"

# --- Power Constraints (Asymmetric) ---
P_IMP_MAX_MW = 4.2   # Maximum Import (Charge) Rate in MW
P_EXP_MAX_MW = 7.5   # Maximum Export (Discharge) Rate in MW

# --- Energy Capacity ---
CAPACITY_MWH = 8.4   # Usable Energy Capacity in MWh

# --- Efficiency ---
EFF_ROUND_TRIP = 0.87  # Round-trip efficiency (87%)
EFF_ONE_WAY = np.sqrt(EFF_ROUND_TRIP)  # One-way efficiency (~93.3%)

# --- State of Charge Limits (Safety Buffers) ---
SOC_MIN_PCT = 0.05  # Minimum SOC: 5%
SOC_MAX_PCT = 0.95  # Maximum SOC: 95%
SOC_MIN_MWH = CAPACITY_MWH * SOC_MIN_PCT  # 0.42 MWh
SOC_MAX_MWH = CAPACITY_MWH * SOC_MAX_PCT  # 7.98 MWh

# --- Warranty Constraints ---
CYCLES_PER_DAY = 1.5  # Maximum cycles per day under warranty
MAX_DAILY_THROUGHPUT_MWH = CAPACITY_MWH * CYCLES_PER_DAY  # 12.6 MWh

# --- Optimization Constants ---
DT_HOURS = 0.5  # Time step duration (30 minutes = 0.5 hours)

# --- Aggregator Information ---
AGGREGATOR_NAME = "GridBeyond"
OWNER_SHARE = 0.95  # Owner gets 95% of revenue
AGGREGATOR_SHARE = 0.05  # Aggregator gets 5% of revenue
