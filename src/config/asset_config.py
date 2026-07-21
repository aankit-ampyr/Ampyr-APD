"""
Asset Configuration for Northwold Solar Farm BESS

Physical and commercial constraints extracted from the
Northwold Storage Asset Optimisation Agreement.
"""

import numpy as np

# --- Asset Identity ---
ASSET_NAME = "Northwold Solar Farm (Hall Farm)"

# --- Power Constraints (Asymmetric) ---
#
# IMPORTANT — which of these is the "rated power"?
#
#   P_IMP_MAX_MW (4.2 MW) is the battery's RATED POWER. It is the correct
#   denominator for any £/MW normalisation, and the basis for the asset's
#   duration: 8.4 MWh ÷ 4.2 MW = exactly 2.0 hours. That puts Northwold in
#   Modo's 2H bracket (1.5–2.5h), which is its benchmark peer group.
#
#   P_EXP_MAX_MW (7.5 MW) is the EXPORT / GRID-CONNECTION limit, not the
#   battery's rating. Using it as the denominator understates £/MW by 44%,
#   and dividing capacity by it implies a 1.12h asset, which would place
#   Northwold in the wrong benchmark bracket entirely.
#
# Both mistakes have been made in this codebase and reached the dashboard:
# the Performance Report normalised by 7.5 MW and reported £20,230/MW/yr
# where every other page said £36,627 for the same month, and the benchmark
# pages briefly compared Northwold against the 1H peer index. Normalise by
# P_IMP_MAX_MW unless you specifically mean the grid export constraint.
P_IMP_MAX_MW = 4.2   # Rated power / charge rate (MW) — use for £/MW and duration
P_EXP_MAX_MW = 7.5   # Export (grid connection) limit (MW) — NOT the power rating

# --- Energy Capacity ---
CAPACITY_MWH = 8.4   # Usable Energy Capacity in MWh (= 4.2 MW × 2.0 h)

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
