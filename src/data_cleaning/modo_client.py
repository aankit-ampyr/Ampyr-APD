"""
Modo Energy API client — ME-BESS-GB monthly index.

Single endpoint wrapper for the FCA-regulated ME-BESS-GB monthly revenue
benchmark, used by the Benchmark Comparison page to refresh the
MODO_BENCHMARKS / ME_BESS_GB_ALL / 1H / 2H dicts in streamlit_dashboard.py
without manual scraping or AI-chat copy-paste.

Endpoint:
    GET /pub/v1/gb/modo/benchmarking/monthly-index-live
    Auth: X-API-Key header
    Params: month_from, month_to (YYYY-MM), duration ('*' | '1' | '2')
    Returns: list of {month, market, duration, revenue_permw, revenue_permwh, ...}

The `market=total` row per month is the headline ME-BESS-GB monthly
£/MW figure; annualised = revenue_permw × 12.

Usage:
    from src.data_cleaning.modo_client import refresh_monthly_index
    refresh_monthly_index('2025-09', '2026-04')  # prints dict-ready output

CLI:
    python -m src.data_cleaning.modo_client --from 2025-09 --to 2026-04
"""
from __future__ import annotations

import json
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from calendar import monthrange
from datetime import datetime
from pathlib import Path
from typing import Dict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SECRETS_PATH = PROJECT_ROOT / ".streamlit" / "secrets.toml"
ENDPOINT = "/pub/v1/gb/modo/benchmarking/monthly-index-live"


def _load_secrets() -> dict:
    if not SECRETS_PATH.exists():
        raise FileNotFoundError(
            f"Modo credentials not found at {SECRETS_PATH}. "
            "Add a [modo] section with api_token and base_url."
        )
    return tomllib.loads(SECRETS_PATH.read_text())["modo"]


def _fetch(month_from: str, month_to: str, duration: str) -> list[dict]:
    cfg = _load_secrets()
    qs = urllib.parse.urlencode({
        "month_from": month_from,
        "month_to": month_to,
        "duration": duration,
    })
    url = f"{cfg['base_url']}{ENDPOINT}?{qs}"
    req = urllib.request.Request(url, headers={"X-API-Key": cfg["api_token"]})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read(500).decode("utf-8", errors="replace")
        raise RuntimeError(f"Modo API {e.code} {e.reason}: {body}") from e


def fetch_monthly_index(
    month_from: str,
    month_to: str,
    duration: str = "*",
) -> Dict[str, int]:
    """
    Fetch the ME-BESS-GB monthly index between two months for a given duration.

    Args:
        month_from: 'YYYY-MM' inclusive start
        month_to:   'YYYY-MM' inclusive end
        duration:   '*' (all assets), '1' (<1.5h), '2' (>=1.5h)

    Returns:
        {month_iso (YYYY-MM-01): annualised_revenue_per_mw_int}

    Methodology — must match what Modo publishes on the web UI:

    1. SUM ALL SIX STREAMS, don't use market='total'. The API's 'total' row
       is the sum of the five NON-capacity-market streams only; it silently
       omits 'cm'. Verified as an exact identity (total == sum of bm,
       frequency_response, imbalance, reserve, wholesale) across every day of
       June 2026 and every month Sep-25..Jun-26. Using 'total' understated
       the published index by £7k-£12k/MW/year depending on CM share.
    2. ANNUALISE BY 365/days-in-month, not ×12. Modo scales the mean daily
       rate to a 365-day year; ×12 assumes a 30.42-day month.

    Both corrections together reproduce Modo's published headline exactly:
    June 2026 1H = 4463.1918 × 365/30 = 54,302, matching the web UI. The
    previous formula returned 46,302 for the same month.
    """
    rows = _fetch(month_from, month_to, duration)

    # Accumulate every stream except the 'total' aggregate, which would
    # double-count the five streams it already contains.
    per_month: Dict[str, float] = {}
    for r in rows:
        if r.get("market") == "total":
            continue
        month = r["month"]  # 'YYYY-MM-DD'
        per_month[month] = per_month.get(month, 0.0) + float(r["revenue_permw"])

    out: Dict[str, int] = {}
    for month, revenue_permw in per_month.items():
        dt = datetime.strptime(month, "%Y-%m-%d")
        days_in_month = monthrange(dt.year, dt.month)[1]
        out[month] = round(revenue_permw * 365 / days_in_month)
    return out


def _short_label(month_iso: str) -> str:
    """'2026-06-01' -> 'Jun 26', matching the dashboard's dict keys.

    Derived rather than looked up: a hardcoded month list silently discarded
    every month past its last entry, so newly published months vanished from
    the refresh without any error being raised.
    """
    dt = datetime.strptime(month_iso, "%Y-%m-%d")
    return f"{dt.strftime('%b')} {dt.strftime('%y')}"


def refresh_monthly_index(
    month_from: str,
    month_to: str,
) -> dict[str, dict[str, int]]:
    """
    Pull all three duration cuts in one batch and return dicts keyed by the
    dashboard's short month labels ('Sep 25', 'Oct 25', ...).

    Returns:
        {
            'ALL': {'Sep 25': 64374, ...},
            '1H':  {'Sep 25': 49259, ...},
            '2H':  {'Sep 25': 74655, ...},
        }
    """
    out: dict[str, dict[str, int]] = {}
    for dur_code, dur_label in (("*", "ALL"), ("1", "1H"), ("2", "2H")):
        api_data = fetch_monthly_index(month_from, month_to, dur_code)
        out[dur_label] = {
            _short_label(k): v for k, v in sorted(api_data.items())
        }
    return out


def _print_dicts(data: dict[str, dict[str, int]]) -> None:
    """Print the three dicts in copy-paste form for updating streamlit_dashboard.py."""
    for label, d in data.items():
        print(f"\nME_BESS_GB_{label} = {{")
        for short, v in d.items():
            print(f"    {short!r}: {v},")
        print("}")
    # MODO_BENCHMARKS uses ALL-durations rounded to nearest 1000
    print("\nMODO_BENCHMARKS (ALL durations, rounded to nearest 1000):")
    print("MODO_BENCHMARKS = {")
    for short, v in data["ALL"].items():
        print(f"    {short!r}: {round(v / 1000) * 1000},")
    print("}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Refresh Modo ME-BESS-GB monthly index from the API")
    parser.add_argument("--from", dest="month_from", default="2025-09", help="Start month YYYY-MM (default: 2025-09)")
    parser.add_argument("--to", dest="month_to", default="2026-04", help="End month YYYY-MM (default: 2026-04)")
    args = parser.parse_args()
    data = refresh_monthly_index(args.month_from, args.month_to)
    _print_dicts(data)
