"""
Phase 2: Digital Twin Configuration

DEPRECATED: This file is maintained for backwards compatibility.
Please import from src.config instead:
    from config import CAPACITY_MWH, P_IMP_MAX_MW, ...
"""

# Re-export everything from the new config location. Via the `config`
# package facade, not config.asset_config directly — config/__init__ imports
# its own children, so reaching past it gave concurrent Streamlit session
# threads opposite module-lock orders (see pages/__init__.py for the full note).
from config import (
    ASSET_NAME,
    P_IMP_MAX_MW,
    P_EXP_MAX_MW,
    CAPACITY_MWH,
    EFF_ROUND_TRIP,
    EFF_ONE_WAY,
    SOC_MIN_PCT,
    SOC_MAX_PCT,
    SOC_MIN_MWH,
    SOC_MAX_MWH,
    CYCLES_PER_DAY,
    MAX_DAILY_THROUGHPUT_MWH,
    DT_HOURS,
)

__all__ = [
    'ASSET_NAME',
    'P_IMP_MAX_MW',
    'P_EXP_MAX_MW',
    'CAPACITY_MWH',
    'EFF_ROUND_TRIP',
    'EFF_ONE_WAY',
    'SOC_MIN_PCT',
    'SOC_MAX_PCT',
    'SOC_MIN_MWH',
    'SOC_MAX_MWH',
    'CYCLES_PER_DAY',
    'MAX_DAILY_THROUGHPUT_MWH',
    'DT_HOURS',
]