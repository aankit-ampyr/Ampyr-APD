"""
GridBeyond Revenue Share Configuration.

GridBeyond optimises and trades Northwold's merchant and ancillary positions
and takes a 5% share of the revenue. Ampyr receives the remaining 95%.

All revenue figures loaded from the Master CSVs (the GridBeyond backing data)
are GROSS — i.e. pre the 5% share. To compare them apples-to-apples against:
  - the GridBeyond invoice (which shows net 95%);
  - the IAR model (which already projects net 95%);
  - any algorithmic optimisation output (which should also assume an
    aggregator fee in real-world deployment);
we multiply the GB-traded streams by GB_REVENUE_NET_SHARE.

GB-traded streams (apply fee):
  Wholesale Day Ahead   — EPEX 30 DA Revenue, EPEX DA Revenue(s)
  Wholesale Intraday    — IDA1 Revenue, IDC Revenue
  Balancing Mechanism   — (not currently tracked from GB)
  Frequency Response    — SFFR revenues, DCL/DCH/DRL/DRH/DML/DMH revenues
  Imbalance             — Imbalance Revenue, Imbalance Charge
  Any Optimised_Revenue_* column produced by the in-house optimiser

NOT GB-traded (no fee — paid direct):
  Capacity Market       — paid by EMR / ESC Settlement
  DUoS Battery credits  — paid by Hartree Partners
  DUoS Fixed Charges    — paid by Hartree Partners
  TNUoS                 — paid by National Grid ESO
"""

from __future__ import annotations

from typing import Iterable, Union

import pandas as pd

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────

GB_FEE_PCT: float = 0.05
GB_REVENUE_NET_SHARE: float = 1.0 - GB_FEE_PCT  # 0.95

GB_NET_FOOTNOTE: str = (
    "*Actual and algorithm-optimised revenue figures are shown **net of the "
    "5% GridBeyond revenue share**. Capacity Market, DUoS and TNUoS amounts "
    "are paid direct (no GB fee) and are not adjusted.*"
)

GB_NET_FOOTNOTE_SHORT: str = (
    "*All revenue values shown net of the 5% GridBeyond revenue share.*"
)

# Master CSV columns that are GB-traded and therefore subject to the fee.
GB_FEE_COLUMNS: tuple[str, ...] = (
    'EPEX 30 DA Revenue',
    'EPEX DA Revenue',
    'EPEX DA Revenues',
    'IDA1 Revenue',
    'IDC Revenue',
    'SFFR revenues',
    'SFFR Revenue',
    'DCL revenues',
    'DCH revenues',
    'DRL revenues',
    'DRH revenues',
    'DML revenues',
    'DMH revenues',
    'Imbalance Revenue',
    'Imbalance Charge',
)

# Optimiser output columns — also net by 5% so Actual vs Optimised is like-for-like.
OPT_FEE_COLUMN_PREFIXES: tuple[str, ...] = (
    'Optimised_Revenue_',
    'Optimized_Revenue_',
)


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

Numeric = Union[int, float, pd.Series]


def apply_gb_net(value: Numeric) -> Numeric:
    """Multiply a gross GB-traded figure by GB_REVENUE_NET_SHARE."""
    if value is None:
        return value
    return value * GB_REVENUE_NET_SHARE


def is_gb_fee_column(col: str) -> bool:
    """True if the column is a GB-traded revenue stream subject to the 5% fee."""
    if col in GB_FEE_COLUMNS:
        return True
    return any(col.startswith(p) for p in OPT_FEE_COLUMN_PREFIXES)


def net_gb_columns(
    df: pd.DataFrame,
    columns: Iterable[str] | None = None,
    inplace: bool = False,
) -> pd.DataFrame:
    """
    Return a copy of df with GB-traded revenue columns scaled by 0.95.

    If `columns` is None, auto-detects using is_gb_fee_column().
    """
    target = df if inplace else df.copy()
    if columns is None:
        columns = [c for c in target.columns if is_gb_fee_column(c)]
    for col in columns:
        if col in target.columns:
            try:
                target[col] = target[col].astype(float) * GB_REVENUE_NET_SHARE
            except (ValueError, TypeError):
                pass
    return target
