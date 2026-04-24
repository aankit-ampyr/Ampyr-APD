"""
Configuration Module for BESS Dashboard

Centralized configuration for the Northwold Solar Farm battery asset.
"""

from .asset_config import (
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
from .revenue_config import (
    GB_FEE_PCT,
    GB_REVENUE_NET_SHARE,
    GB_NET_FOOTNOTE,
    GB_NET_FOOTNOTE_SHORT,
    GB_FEE_COLUMNS,
    OPT_FEE_COLUMN_PREFIXES,
    apply_gb_net,
    is_gb_fee_column,
    net_gb_columns,
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
    'GB_FEE_PCT',
    'GB_REVENUE_NET_SHARE',
    'GB_NET_FOOTNOTE',
    'GB_NET_FOOTNOTE_SHORT',
    'GB_FEE_COLUMNS',
    'OPT_FEE_COLUMN_PREFIXES',
    'apply_gb_net',
    'is_gb_fee_column',
    'net_gb_columns',
]
