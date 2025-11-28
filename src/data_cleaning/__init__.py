"""
Data Cleaning Module for BESS Dashboard

This module handles:
- Loading raw Excel files from GridBeyond and BESS SCADA
- Validating and cleaning data
- Resampling SCADA data from 10-min to 30-min intervals
- Merging data sources into harmonized output
- Generating data quality reports
"""

from .loader import load_gridbeyond, load_scada, find_files, get_data_info
from .transformer import resample_scada, convert_units, calculate_missing_soc
from .merger import merge_data, align_timestamps, create_master_dataset
from .report import DataQualityReport, generate_quality_report
from .pipeline import process_monthly_data, process_files_direct

__all__ = [
    # Loader functions
    'load_gridbeyond',
    'load_scada',
    'find_files',
    'get_data_info',
    # Transformer functions
    'resample_scada',
    'convert_units',
    'calculate_missing_soc',
    # Merger functions
    'merge_data',
    'align_timestamps',
    'create_master_dataset',
    # Report classes and functions
    'DataQualityReport',
    'generate_quality_report',
    # Pipeline functions
    'process_monthly_data',
    'process_files_direct',
]
