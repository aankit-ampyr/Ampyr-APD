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
from .invoice_loader import (
    load_emr_capacity_market,
    load_emr_txt_files,
    load_summary_statement,
    load_hartree_bess_readings,
    load_hartree_pv_readings,
    load_solar_generation,
    load_scada_monitoring,
    load_all_pdfs,
)
from .invoice_reconciler import (
    reconcile_bess_energy,
    reconcile_solar_pv,
    reconcile_revenue,
    compute_aggregator_fee_breakdown,
    reconcile_capacity_market,
)

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
    # Invoice loader functions
    'load_emr_capacity_market',
    'load_emr_txt_files',
    'load_summary_statement',
    'load_hartree_bess_readings',
    'load_hartree_pv_readings',
    'load_solar_generation',
    'load_scada_monitoring',
    'load_all_pdfs',
    # Invoice reconciler functions
    'reconcile_bess_energy',
    'reconcile_solar_pv',
    'reconcile_revenue',
    'compute_aggregator_fee_breakdown',
    'reconcile_capacity_market',
]
