"""
Data Cleaning Module for BESS Dashboard

This module handles two pipelines:

1. GridBeyond + SCADA pipeline (interactive, user-driven):
   - Loads raw Excel files from GridBeyond and SCADA
   - Resamples SCADA from 10-min to 30-min
   - Merges into Master_BESS_Analysis_*.csv (in data/)

2. Invoice ETL (batch, run via CLI):
   - process_invoices.run() reads raw/ once and writes
     pre-processed parquet/json files to data/invoices/
   - Streamlit pages then read from data/invoices/ via the
     process_invoices.read_* functions

Pages MUST NOT import from invoice_loader directly. That boundary still
stands: pages import the read_* readers from process_invoices, never the
live load_* parsers.

Deliberately NO eager submodule imports in this file.

It used to re-export loader / transformer / merger / report / pipeline /
process_invoices / invoice_reconciler. Other modules import those submodules
directly (e.g. ``from data_cleaning.process_tinte import read_daily``), so
the package lock and the child locks were being acquired in opposite orders
by the concurrent Streamlit session threads — Streamlit runs each session's
script in its own thread. Python 3.14 detects the resulting cycle and kills
the app with ``_DeadlockError`` / ``KeyError: 'data_cleaning'``.

Keeping this module inert means importing one submodule never drags in the
rest, and no thread ever holds the package lock while taking a child lock.

Import the submodules directly instead::

    from data_cleaning.loader import find_files, load_gridbeyond
    from data_cleaning.process_invoices import read_pdf_invoices
"""
