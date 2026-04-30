"""
Invoice ETL — the single boundary between raw/ and the Streamlit pages.

This module:
  1. Reads everything in raw/New/ via the parsers in invoice_loader.py
  2. Writes the parsed outputs to data/invoices/ (parquet + a small JSON)
  3. Provides reader functions that the pages use instead of touching raw/

Run once whenever raw files change:

    python -m src.data_cleaning.process_invoices

The Streamlit pages must NEVER import from invoice_loader directly — they
import from this module so the live runtime has zero dependency on raw/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional, Dict

import pandas as pd

# Allow running as a script as well as `python -m`
_SRC_DIR = Path(__file__).resolve().parents[1]
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from data_cleaning.invoice_loader import (
    load_emr_capacity_market,
    load_emr_txt_files,
    load_summary_statement,
    load_hartree_bess_readings,
    load_hartree_pv_readings,
    load_solar_generation,
    load_scada_monitoring,
    load_all_pdfs,
)


# ─────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR_DEFAULT = PROJECT_ROOT / "raw" / "New"
DATA_DIR = PROJECT_ROOT / "data" / "invoices"

PATHS = {
    "emr":            DATA_DIR / "emr_capacity_market.parquet",
    "emr_txt":        DATA_DIR / "emr_invoice_totals.parquet",
    "summary_meta":   DATA_DIR / "summary_statement_meta.json",
    "summary_detail": DATA_DIR / "summary_statement_detail.parquet",
    "hartree_bess":   DATA_DIR / "hartree_bess_readings.parquet",
    "hartree_pv":     DATA_DIR / "hartree_pv_readings.parquet",
    "solar_gen":      DATA_DIR / "solar_generation.parquet",
    "scada":          DATA_DIR / "scada_monitoring.parquet",
    "pdfs":           DATA_DIR / "pdf_invoices.parquet",
}


# ─────────────────────────────────────────────────────────────
# Writers (called by the ETL run)
# ─────────────────────────────────────────────────────────────

def _write_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=True)


def _write_summary_statement(raw_dir: Path) -> bool:
    """Save the Summary Statement (dict with embedded DataFrame) as JSON + parquet."""
    candidates = sorted(raw_dir.glob("Northwold - *.xlsx"))
    if not candidates:
        # Clear stale outputs so the reader returns None cleanly.
        for key in ("summary_meta", "summary_detail"):
            if PATHS[key].exists():
                PATHS[key].unlink()
        return False

    summary = load_summary_statement(str(candidates[0]))
    if summary is None:
        return False

    PATHS["summary_meta"].parent.mkdir(parents=True, exist_ok=True)

    # Period Timestamps -> ISO strings for JSON
    period = summary.get("period", {}) or {}
    period_iso = {
        k: (v.isoformat() if isinstance(v, pd.Timestamp) else v)
        for k, v in period.items()
    }

    meta = {
        "summary": summary["summary"],            # dicts of floats / strings
        "commentary": summary.get("commentary", ""),
        "period": period_iso,
        "source_file": candidates[0].name,
    }
    with open(PATHS["summary_meta"], "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)

    detail = summary.get("detail")
    if detail is not None and not detail.empty:
        _write_df(detail, PATHS["summary_detail"])
    elif PATHS["summary_detail"].exists():
        PATHS["summary_detail"].unlink()
    return True


def run(raw_dir: Optional[Path] = None, verbose: bool = True) -> Dict[str, int]:
    """Run the full invoice ETL: raw/New/ -> data/invoices/.

    Returns a dict of {output_name: row_count} for logging/verification.
    """
    raw_dir = Path(raw_dir) if raw_dir else RAW_DIR_DEFAULT
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"Invoice ETL: {raw_dir} -> {DATA_DIR}")

    counts: Dict[str, int] = {}

    emr = load_emr_capacity_market(str(raw_dir))
    _write_df(emr, PATHS["emr"])
    counts["emr_capacity_market"] = len(emr)
    if verbose:
        print(f"  emr_capacity_market.parquet      {len(emr):>5} rows")

    emr_txt = load_emr_txt_files(str(raw_dir))
    _write_df(emr_txt, PATHS["emr_txt"])
    counts["emr_invoice_totals"] = len(emr_txt)
    if verbose:
        print(f"  emr_invoice_totals.parquet       {len(emr_txt):>5} rows")

    saved = _write_summary_statement(raw_dir)
    counts["summary_statement"] = 1 if saved else 0
    if verbose:
        print(f"  summary_statement_*              {'saved' if saved else 'no Northwold - *.xlsx found'}")

    hartree_bess = load_hartree_bess_readings(str(raw_dir))
    _write_df(hartree_bess, PATHS["hartree_bess"])
    counts["hartree_bess_readings"] = len(hartree_bess)
    if verbose:
        print(f"  hartree_bess_readings.parquet    {len(hartree_bess):>5} rows")

    hartree_pv = load_hartree_pv_readings(str(raw_dir))
    _write_df(hartree_pv, PATHS["hartree_pv"])
    counts["hartree_pv_readings"] = len(hartree_pv)
    if verbose:
        print(f"  hartree_pv_readings.parquet      {len(hartree_pv):>5} rows")

    solar_gen = load_solar_generation(str(raw_dir))
    _write_df(solar_gen, PATHS["solar_gen"])
    counts["solar_generation"] = len(solar_gen)
    if verbose:
        print(f"  solar_generation.parquet         {len(solar_gen):>5} rows")

    scada = load_scada_monitoring(str(raw_dir))
    _write_df(scada, PATHS["scada"])
    counts["scada_monitoring"] = len(scada)
    if verbose:
        print(f"  scada_monitoring.parquet         {len(scada):>5} rows")

    pdfs = load_all_pdfs(str(raw_dir))
    _write_df(pdfs, PATHS["pdfs"])
    counts["pdf_invoices"] = len(pdfs)
    if verbose:
        print(f"  pdf_invoices.parquet             {len(pdfs):>5} rows")

    if verbose:
        print("ETL complete.")
    return counts


# ─────────────────────────────────────────────────────────────
# Readers (used by the Streamlit pages — the only public API)
# ─────────────────────────────────────────────────────────────

def _read_parquet_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


def read_emr_capacity_market() -> pd.DataFrame:
    return _read_parquet_or_empty(PATHS["emr"])


def read_emr_invoice_totals() -> pd.DataFrame:
    return _read_parquet_or_empty(PATHS["emr_txt"])


def read_summary_statement() -> Optional[Dict]:
    """Reconstruct the Summary Statement dict from JSON + parquet.

    Returns the same shape as invoice_loader.load_summary_statement, so
    consumers can swap one call for the other.
    """
    meta_path = PATHS["summary_meta"]
    detail_path = PATHS["summary_detail"]
    if not meta_path.exists():
        return None

    with open(meta_path, "r", encoding="utf-8") as fh:
        meta = json.load(fh)

    detail = pd.read_parquet(detail_path) if detail_path.exists() else pd.DataFrame()

    period_iso = meta.get("period", {}) or {}
    period = {
        k: (pd.to_datetime(v) if isinstance(v, str) else v)
        for k, v in period_iso.items()
    }

    return {
        "summary": meta.get("summary", {}),
        "detail": detail,
        "commentary": meta.get("commentary", ""),
        "period": period,
    }


def read_hartree_bess_readings() -> pd.DataFrame:
    return _read_parquet_or_empty(PATHS["hartree_bess"])


def read_hartree_pv_readings() -> pd.DataFrame:
    return _read_parquet_or_empty(PATHS["hartree_pv"])


def read_solar_generation() -> pd.DataFrame:
    return _read_parquet_or_empty(PATHS["solar_gen"])


def read_scada_monitoring() -> pd.DataFrame:
    return _read_parquet_or_empty(PATHS["scada"])


def read_pdf_invoices() -> pd.DataFrame:
    return _read_parquet_or_empty(PATHS["pdfs"])


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pre-process raw invoice files into data/invoices/")
    parser.add_argument("--raw-dir", default=str(RAW_DIR_DEFAULT),
                        help=f"Path to raw input folder (default: {RAW_DIR_DEFAULT})")
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args()

    run(raw_dir=Path(args.raw_dir), verbose=not args.quiet)
