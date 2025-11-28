"""
Data Loader Module for BESS Dashboard

Handles loading raw Excel files from GridBeyond and BESS SCADA systems.
"""

import pandas as pd
from pathlib import Path
from typing import Tuple, Optional, List
import re


def find_files(folder_path: str) -> dict:
    """
    Auto-detect GridBeyond and SCADA files in a folder.

    Args:
        folder_path: Path to folder containing raw data files

    Returns:
        dict with keys 'gridbeyond' and 'scada' containing file paths
    """
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    files = {
        'gridbeyond': None,
        'scada': None
    }

    for file in folder.glob("*.xlsx"):
        filename = file.name.lower()

        # GridBeyond files match pattern: Northwold_{Month}_{Year}.xlsx
        if 'northwold' in filename and not filename.startswith('~$'):
            files['gridbeyond'] = str(file)

        # SCADA files match pattern: export-*.xlsx
        elif filename.startswith('export-') and not filename.startswith('~$'):
            files['scada'] = str(file)

    return files


def load_gridbeyond(filepath: str) -> pd.DataFrame:
    """
    Load GridBeyond Excel file and parse timestamps.

    Args:
        filepath: Path to GridBeyond Excel file

    Returns:
        DataFrame with parsed Timestamp column as index
    """
    if not Path(filepath).exists():
        raise FileNotFoundError(f"GridBeyond file not found: {filepath}")

    # Read Excel file
    df = pd.read_excel(filepath)

    # Find timestamp column (case-insensitive)
    timestamp_col = None
    for col in df.columns:
        if 'timestamp' in col.lower():
            timestamp_col = col
            break

    if timestamp_col is None:
        raise ValueError("No Timestamp column found in GridBeyond file")

    # Parse timestamp - GridBeyond uses datetime format
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])

    # Rename to standard name
    df = df.rename(columns={timestamp_col: 'Timestamp'})

    # Set as index
    df = df.set_index('Timestamp')
    df = df.sort_index()

    # Clean column names (remove newlines, extra spaces)
    df.columns = [_clean_column_name(col) for col in df.columns]

    return df


def load_scada(filepath: str, convert_power_to_mw: bool = True) -> pd.DataFrame:
    """
    Load SCADA Excel file, parse dates, and optionally convert power units.

    Args:
        filepath: Path to SCADA Excel file
        convert_power_to_mw: If True, convert Power from kW to MW

    Returns:
        DataFrame with parsed timestamp as index
    """
    if not Path(filepath).exists():
        raise FileNotFoundError(f"SCADA file not found: {filepath}")

    # Read Excel file
    df = pd.read_excel(filepath)

    # Find date column (usually 'date')
    date_col = None
    for col in df.columns:
        if 'date' in col.lower():
            date_col = col
            break

    if date_col is None:
        raise ValueError("No date column found in SCADA file")

    # Parse date - SCADA uses format: DD/MM/YYYY HH:MM:SS
    df[date_col] = pd.to_datetime(df[date_col], format='%d/%m/%Y %H:%M:%S')

    # Rename to standard name
    df = df.rename(columns={date_col: 'Timestamp'})

    # Set as index
    df = df.set_index('Timestamp')
    df = df.sort_index()

    # Convert Power from kW to MW if requested
    if convert_power_to_mw and 'Power' in df.columns:
        df['Power'] = df['Power'] / 1000.0
        # Rename to indicate units
        df = df.rename(columns={'Power': 'Power_MW'})

    # Drop Availability column if it's all null (as noted in data analysis)
    if 'Availability' in df.columns and df['Availability'].isna().all():
        df = df.drop(columns=['Availability'])

    return df


def _clean_column_name(name: str) -> str:
    """
    Clean column names by removing newlines and extra whitespace.

    Args:
        name: Original column name

    Returns:
        Cleaned column name
    """
    # Replace newlines with space
    name = name.replace('\n', ' ')
    # Replace multiple spaces with single space
    name = re.sub(r'\s+', ' ', name)
    # Strip leading/trailing whitespace
    name = name.strip()
    return name


def get_data_info(df: pd.DataFrame, source_name: str) -> dict:
    """
    Get summary information about a loaded DataFrame.

    Args:
        df: Loaded DataFrame
        source_name: Name of the data source (e.g., 'GridBeyond', 'SCADA')

    Returns:
        Dictionary with data summary info
    """
    info = {
        'source': source_name,
        'rows': len(df),
        'columns': len(df.columns),
        'start_date': df.index.min(),
        'end_date': df.index.max(),
        'date_range_days': (df.index.max() - df.index.min()).days,
        'missing_values': df.isna().sum().to_dict(),
        'missing_pct': (df.isna().sum() / len(df) * 100).to_dict(),
        'columns_100pct_missing': [
            col for col in df.columns
            if df[col].isna().all()
        ]
    }

    # Detect time resolution
    if len(df) > 1:
        time_diffs = df.index.to_series().diff().dropna()
        most_common_diff = time_diffs.mode()[0]
        info['time_resolution_minutes'] = most_common_diff.total_seconds() / 60

    return info
