"""
Data Cleaning Module for BESS Dashboard

This module handles two pipelines:

1. GridBeyond + SCADA pipeline (interactive, user-driven):
   - Loads raw Excel files from GridBeyond and SCADA
   - Resamples SCADA from 10-min to 30-min
   - Merges into Master_BESS_Analysis_*.csv (in data/)

2. Invoice ETL (batch, run via CLI):
   - process_invoices.run() reads raw/New/ once and writes
     pre-processed parquet/json files to data/invoices/
   - Streamlit pages then read from data/invoices/ via the
     process_invoices.read_* functions

Pages MUST NOT import from invoice_loader directly. The boundary is
enforced here by re-exporting only the read_* readers, not the live
load_* parsers. Live raw access is restricted to ETL only.
"""

from .loader import load_gridbeyond, load_scada, find_files, get_data_info
from .transformer import resample_scada, convert_units, calculate_missing_soc
from .merger import merge_data, align_timestamps, create_master_dataset
from .report import DataQualityReport, generate_quality_report
from .pipeline import process_monthly_data, process_files_direct
from .process_invoices import (
    run as run_invoice_etl,
    read_emr_capacity_market,
    read_emr_invoice_totals,
    read_summary_statement,
    read_hartree_bess_readings,
    read_hartree_pv_readings,
    read_solar_generation,
    read_scada_monitoring,
    read_pdf_invoices,
)
from .invoice_reconciler import (
    reconcile_bess_energy,
    reconcile_solar_pv,
    reconcile_revenue,
    compute_aggregator_fee_breakdown,
    reconcile_capacity_market,
)

__all__ = [
    # GridBeyond/SCADA pipeline (interactive)
    'load_gridbeyond',
    'load_scada',
    'find_files',
    'get_data_info',
    'resample_scada',
    'convert_units',
    'calculate_missing_soc',
    'merge_data',
    'align_timestamps',
    'create_master_dataset',
    'DataQualityReport',
    'generate_quality_report',
    'process_monthly_data',
    'process_files_direct',
    # Invoice ETL — readers used by pages, run() used by CLI
    'run_invoice_etl',
    'read_emr_capacity_market',
    'read_emr_invoice_totals',
    'read_summary_statement',
    'read_hartree_bess_readings',
    'read_hartree_pv_readings',
    'read_solar_generation',
    'read_scada_monitoring',
    'read_pdf_invoices',
    # Invoice reconciliation (operates on read_* outputs)
    'reconcile_bess_energy',
    'reconcile_solar_pv',
    'reconcile_revenue',
    'compute_aggregator_fee_breakdown',
    'reconcile_capacity_market',
]
