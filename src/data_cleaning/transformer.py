"""
Data Transformer Module for BESS Dashboard

Handles resampling, unit conversion, and calculated fields.
"""

import pandas as pd
import numpy as np
from typing import Optional

# Battery specifications for Northwold
CAPACITY_MWH = 8.4  # Total battery capacity in MWh


def resample_scada(df: pd.DataFrame, target_freq: str = '30min') -> pd.DataFrame:
    """
    Resample SCADA data from 10-min to 30-min intervals.

    Resampling strategy:
    - Power_MW: mean of readings in period
    - SOC: last value in period (end-of-period state)
    - Frequency: mean of readings in period

    Args:
        df: SCADA DataFrame with 10-min resolution
        target_freq: Target frequency (default '30min')

    Returns:
        Resampled DataFrame
    """
    # Define aggregation rules for each column
    agg_rules = {}

    if 'Power_MW' in df.columns:
        agg_rules['Power_MW'] = 'mean'

    if 'SOC' in df.columns:
        agg_rules['SOC'] = 'last'

    if 'Frequency' in df.columns:
        agg_rules['Frequency'] = 'mean'

    # Handle any other numeric columns with mean
    for col in df.columns:
        if col not in agg_rules and pd.api.types.is_numeric_dtype(df[col]):
            agg_rules[col] = 'mean'

    if not agg_rules:
        raise ValueError("No numeric columns found to resample")

    # Resample using defined rules
    # label='right' means the timestamp is the end of the period
    # closed='right' means the interval is (left, right]
    resampled = df.resample(target_freq, label='right', closed='right').agg(agg_rules)

    return resampled


def convert_units(df: pd.DataFrame, conversions: Optional[dict] = None) -> pd.DataFrame:
    """
    Apply unit conversions to DataFrame columns.

    Args:
        df: Input DataFrame
        conversions: Dict of {column_name: (multiplier, new_name)}
                    e.g., {'Power': (0.001, 'Power_MW')} converts kW to MW

    Returns:
        DataFrame with converted columns
    """
    if conversions is None:
        return df

    df = df.copy()

    for col, (multiplier, new_name) in conversions.items():
        if col in df.columns:
            df[new_name] = df[col] * multiplier
            if new_name != col:
                df = df.drop(columns=[col])

    return df


def calculate_missing_soc(
    df: pd.DataFrame,
    power_col: str = 'Power_MW',
    soc_col: str = 'SOC',
    capacity_mwh: float = CAPACITY_MWH,
    dt_hours: float = 0.5,
    efficiency: float = 0.87
) -> pd.DataFrame:
    """
    Calculate missing SOC values from power integration.

    Formula:
    - Charging (Power > 0): SOC[t] = SOC[t-1] + (Power_MW * dt * efficiency) / CAPACITY * 100
    - Discharging (Power < 0): SOC[t] = SOC[t-1] + (Power_MW * dt / efficiency) / CAPACITY * 100

    Args:
        df: DataFrame with Power and SOC columns
        power_col: Name of power column (MW)
        soc_col: Name of SOC column (%)
        capacity_mwh: Battery capacity in MWh
        dt_hours: Time step in hours
        efficiency: Round-trip efficiency (sqrt applied for one-way)

    Returns:
        DataFrame with filled SOC values
    """
    if power_col not in df.columns:
        raise ValueError(f"Power column '{power_col}' not found")

    if soc_col not in df.columns:
        # Create SOC column if it doesn't exist
        df = df.copy()
        df[soc_col] = np.nan

    df = df.copy()

    # One-way efficiency (sqrt of round-trip)
    eff_charge = np.sqrt(efficiency)
    eff_discharge = np.sqrt(efficiency)

    # Track which values were calculated
    df['SOC_calculated'] = False

    # Forward fill using power integration
    soc_values = df[soc_col].values.copy()
    power_values = df[power_col].values
    calculated_flags = df['SOC_calculated'].values.copy()

    for i in range(1, len(soc_values)):
        if pd.isna(soc_values[i]) and not pd.isna(soc_values[i-1]):
            power = power_values[i-1]  # Use previous power for integration

            if pd.isna(power):
                continue

            # Calculate energy change
            if power > 0:  # Charging
                energy_change = power * dt_hours * eff_charge
            else:  # Discharging
                energy_change = power * dt_hours / eff_discharge

            # Convert to SOC percentage change
            soc_change = (energy_change / capacity_mwh) * 100

            # Calculate new SOC
            new_soc = soc_values[i-1] + soc_change

            # Clamp to valid range
            new_soc = np.clip(new_soc, 0, 100)

            soc_values[i] = new_soc
            calculated_flags[i] = True

    df[soc_col] = soc_values
    df['SOC_calculated'] = calculated_flags

    # Also try backward fill for gaps at the start
    for i in range(len(soc_values) - 2, -1, -1):
        if pd.isna(soc_values[i]) and not pd.isna(soc_values[i+1]):
            power = power_values[i]

            if pd.isna(power):
                continue

            # Calculate energy change (reverse direction)
            if power > 0:  # Was charging
                energy_change = power * dt_hours * eff_charge
            else:  # Was discharging
                energy_change = power * dt_hours / eff_discharge

            soc_change = (energy_change / capacity_mwh) * 100

            # Previous SOC = next SOC - change
            new_soc = soc_values[i+1] - soc_change
            new_soc = np.clip(new_soc, 0, 100)

            soc_values[i] = new_soc
            calculated_flags[i] = True

    df[soc_col] = soc_values
    df['SOC_calculated'] = calculated_flags

    return df


def interpolate_small_gaps(
    df: pd.DataFrame,
    column: str,
    max_gap_periods: int = 3
) -> pd.DataFrame:
    """
    Interpolate small gaps in a column using linear interpolation.

    Args:
        df: Input DataFrame
        column: Column to interpolate
        max_gap_periods: Maximum consecutive NaN periods to fill

    Returns:
        DataFrame with interpolated values
    """
    if column not in df.columns:
        return df

    df = df.copy()
    df[column] = df[column].interpolate(
        method='linear',
        limit=max_gap_periods,
        limit_direction='both'
    )

    return df


def detect_outliers(
    df: pd.DataFrame,
    column: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None
) -> pd.Series:
    """
    Detect outlier values outside specified range.

    Args:
        df: Input DataFrame
        column: Column to check
        min_val: Minimum valid value
        max_val: Maximum valid value

    Returns:
        Boolean Series where True indicates an outlier
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found")

    outliers = pd.Series(False, index=df.index)

    if min_val is not None:
        outliers |= df[column] < min_val

    if max_val is not None:
        outliers |= df[column] > max_val

    return outliers


def validate_soc_range(df: pd.DataFrame, soc_col: str = 'SOC') -> dict:
    """
    Validate SOC values are within valid range (0-100%).

    Args:
        df: DataFrame with SOC column
        soc_col: Name of SOC column

    Returns:
        Dictionary with validation results
    """
    if soc_col not in df.columns:
        return {'valid': False, 'error': f"Column '{soc_col}' not found"}

    soc = df[soc_col].dropna()

    return {
        'valid': True,
        'min': soc.min(),
        'max': soc.max(),
        'below_0': (soc < 0).sum(),
        'above_100': (soc > 100).sum(),
        'in_range': ((soc >= 0) & (soc <= 100)).sum(),
        'total_non_null': len(soc)
    }
