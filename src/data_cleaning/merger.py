"""
Data Merger Module for BESS Dashboard

Handles merging GridBeyond and SCADA data sources into a unified dataset.
"""

import pandas as pd
from typing import Tuple, Optional
from datetime import datetime


def align_timestamps(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    tolerance: str = '1min'
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Align timestamps between two DataFrames within a tolerance.

    Args:
        df1: First DataFrame (timestamp as index)
        df2: Second DataFrame (timestamp as index)
        tolerance: Maximum time difference for alignment

    Returns:
        Tuple of aligned DataFrames trimmed to common date range
    """
    # Find common date range
    start_date = max(df1.index.min(), df2.index.min())
    end_date = min(df1.index.max(), df2.index.max())

    # Trim to common range
    df1_aligned = df1[(df1.index >= start_date) & (df1.index <= end_date)].copy()
    df2_aligned = df2[(df2.index >= start_date) & (df2.index <= end_date)].copy()

    return df1_aligned, df2_aligned


def merge_data(
    gridbeyond_df: pd.DataFrame,
    scada_df: pd.DataFrame,
    how: str = 'outer',
    validate_overlap: bool = True
) -> pd.DataFrame:
    """
    Merge GridBeyond and SCADA DataFrames on timestamp.

    SCADA provides: SOC, Power_MW, Frequency
    GridBeyond provides: Market prices, Revenues, Ancillary services

    Args:
        gridbeyond_df: GridBeyond DataFrame (timestamp as index)
        scada_df: SCADA DataFrame (timestamp as index)
        how: Merge type ('inner', 'outer', 'left', 'right')
        validate_overlap: If True, warn if there's poor timestamp overlap

    Returns:
        Merged DataFrame with all columns from both sources
    """
    # Add source prefixes to avoid column name conflicts
    # SCADA columns get prefix for clarity
    scada_cols = {col: f'SCADA_{col}' if col not in ['Power_MW', 'SOC', 'Frequency'] else col
                  for col in scada_df.columns}
    scada_df = scada_df.rename(columns=scada_cols)

    # Merge on index (timestamp)
    merged = pd.merge(
        gridbeyond_df,
        scada_df,
        left_index=True,
        right_index=True,
        how=how,
        suffixes=('_GB', '_SCADA')
    )

    # Sort by timestamp
    merged = merged.sort_index()

    if validate_overlap:
        overlap_info = _calculate_overlap(gridbeyond_df, scada_df, merged)
        merged.attrs['overlap_info'] = overlap_info

    return merged


def _calculate_overlap(df1: pd.DataFrame, df2: pd.DataFrame, merged: pd.DataFrame) -> dict:
    """
    Calculate overlap statistics between two DataFrames.

    Args:
        df1: First DataFrame
        df2: Second DataFrame
        merged: Merged DataFrame

    Returns:
        Dictionary with overlap statistics
    """
    df1_timestamps = set(df1.index)
    df2_timestamps = set(df2.index)

    common = df1_timestamps & df2_timestamps
    only_df1 = df1_timestamps - df2_timestamps
    only_df2 = df2_timestamps - df1_timestamps

    return {
        'total_timestamps': len(merged),
        'common_timestamps': len(common),
        'only_gridbeyond': len(only_df1),
        'only_scada': len(only_df2),
        'overlap_pct': len(common) / len(merged) * 100 if len(merged) > 0 else 0
    }


def create_master_dataset(
    gridbeyond_df: pd.DataFrame,
    scada_df: pd.DataFrame,
    output_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Create the master merged dataset for analysis.

    This function:
    1. Aligns timestamps to common date range
    2. Merges data sources
    3. Selects key columns for analysis
    4. Optionally saves to CSV

    Args:
        gridbeyond_df: Cleaned GridBeyond DataFrame
        scada_df: Cleaned and resampled SCADA DataFrame
        output_path: Optional path to save CSV

    Returns:
        Master DataFrame ready for analysis
    """
    # Align to common date range
    gb_aligned, scada_aligned = align_timestamps(gridbeyond_df, scada_df)

    # Merge
    merged = merge_data(gb_aligned, scada_aligned, how='outer')

    # Define priority columns for the master dataset
    priority_columns = [
        # SCADA physical data
        'SOC', 'Power_MW', 'Frequency',

        # Market prices
        'EPEX Day Ahead £/MWh', 'GB-ISEM Intraday 1 £/MWh',
        'DA HH £/MWh', 'SSP £/MWh', 'SBP £/MWh', 'IDC Price £/MWh',

        # Revenue streams
        'SFFR Revenue £', 'EPEX 30 DA Revenue £', 'IDA1 Revenue £',
        'IDC Revenue £', 'Imbalance Revenue £', 'Imbalance Charge £',

        # Ancillary services
        'SFFR Availability MW', 'SFFR Price £/MW/h', 'SFFR Revenue  £',
        'DCL Availability MW', 'DCL Price £/MW/h', 'DCL Revenue £',
        'DCH Availability MW', 'DCH Price £/MW/h', 'DCH Revenue £',
        'DML Availability MW', 'DML Price £/MW/h', 'DML Revenue £',
        'DMH Availability MW', 'DMH Price £/MW/h', 'DMH Revenue £',
        'DRL Availability MW', 'DRL Price £/MW/h', 'DRL Revenue £',
        'DRH Availability MW', 'DRH Price £/MW/h', 'DRH Revenue £',

        # Energy volumes
        'Credited Energy Volume Battery MWh Output',
    ]

    # Select columns that exist in merged data
    available_columns = [col for col in priority_columns if col in merged.columns]

    # Also include any columns not in priority list
    other_columns = [col for col in merged.columns if col not in priority_columns]

    # Create final column order
    final_columns = available_columns + other_columns
    merged = merged[final_columns]

    # Add metadata
    merged.attrs['gridbeyond_rows'] = len(gb_aligned)
    merged.attrs['scada_rows'] = len(scada_aligned)
    merged.attrs['date_range_start'] = merged.index.min()
    merged.attrs['date_range_end'] = merged.index.max()

    # Save to CSV if path provided
    if output_path:
        merged.to_csv(output_path)
        print(f"Master dataset saved to: {output_path}")

    return merged


def detect_timestamp_gaps(df: pd.DataFrame, expected_freq: str = '30min') -> pd.DataFrame:
    """
    Detect gaps in timestamp sequence.

    Args:
        df: DataFrame with timestamp index
        expected_freq: Expected time frequency

    Returns:
        DataFrame listing gaps with start, end, and duration
    """
    expected_delta = pd.Timedelta(expected_freq)

    # Calculate time differences
    time_diffs = df.index.to_series().diff()

    # Find gaps (where diff > expected)
    gaps = time_diffs[time_diffs > expected_delta]

    if len(gaps) == 0:
        return pd.DataFrame(columns=['gap_start', 'gap_end', 'missing_periods'])

    gap_records = []
    for idx, diff in gaps.items():
        gap_start = df.index[df.index.get_loc(idx) - 1]
        gap_end = idx
        missing_periods = int(diff / expected_delta) - 1

        gap_records.append({
            'gap_start': gap_start,
            'gap_end': gap_end,
            'duration': diff,
            'missing_periods': missing_periods
        })

    return pd.DataFrame(gap_records)


def fill_timestamp_gaps(
    df: pd.DataFrame,
    freq: str = '30min',
    fill_method: Optional[str] = None
) -> pd.DataFrame:
    """
    Fill gaps in timestamp sequence with empty rows.

    Args:
        df: DataFrame with timestamp index
        freq: Time frequency to use
        fill_method: Optional method to fill values ('ffill', 'bfill', None)

    Returns:
        DataFrame with complete timestamp sequence
    """
    # Create complete date range
    full_range = pd.date_range(
        start=df.index.min(),
        end=df.index.max(),
        freq=freq
    )

    # Reindex to fill gaps
    df_filled = df.reindex(full_range)

    if fill_method:
        df_filled = df_filled.fillna(method=fill_method)

    return df_filled
