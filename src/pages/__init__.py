"""
Dashboard Pages Module

Deliberately EMPTY — do not re-export the page modules here.

This file used to eagerly import data_quality, invoice_analysis and
monthly_checklist. That meant importing any ONE page pulled in all three,
and with them the whole data_cleaning + config import chain. Streamlit runs
each session's script in its own thread, so two sessions starting at once
imported those modules concurrently in different orders; Python 3.14 detects
the resulting lock cycle and kills the app with

    _DeadlockError: deadlock detected by _ModuleLock('pages.data_quality')

Consumers import the page modules directly (``from pages.data_quality import
show_data_quality_page``), so nothing needed these re-exports. Keeping this
module inert means no thread ever holds the ``pages`` package lock while
acquiring a child module lock, which is what closed the cycle.
"""
