"""Solar KPI universe + survey-response parsing (shared data layer).

The 35-KPI Solar universe (mirrors survey/solar-kpi-selector.html) plus helpers
to read the reviewers' exported CSVs from survey/responses/ and tally selections.
Used by the Tinte Solar dashboard. No Streamlit dependency.
"""

from __future__ import annotations

import csv
import glob
import math
import os
import re
from collections import OrderedDict

import pandas as pd

# ─────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────
_HERE = os.path.dirname(__file__)
RESPONSES_DIR = os.path.join(_HERE, "..", "..", "survey", "responses")

# ─────────────────────────────────────────────────────────────
# KPI universe — mirrors KPI_DATA in solar-kpi-selector.html
# (8 categories, 35 KPIs). The response CSV identifies a KPI only by its
# display name, so NAME → id is the join key.
# ─────────────────────────────────────────────────────────────
CATEGORIES = OrderedDict([
    ("revenue",     ("Revenue & Profitability", "Top-line, margin, returns and asset value.")),
    ("cash",        ("Cash & Distributions", "Cash the asset generates and returns to shareholders.")),
    ("debt",        ("Debt & Covenants", "Coverage ratios, leverage and interest-rate risk lenders monitor.")),
    ("contracting", ("Revenue Contracting", "How much future revenue is secured under contract.")),
    ("market",      ("Market & Trading", "Price capture, imbalance and merchant-market dynamics.")),
    ("generation",  ("Generation & Availability", "Production performance versus the model.")),
    ("cost",        ("Cost Control", "Operating-cost efficiency and response time.")),
    ("risk",        ("Counterparty & Risk", "Collections, counterparty credit and merchant exposure.")),
])

# (id, name, category_id, priority, cadence)
KPI_UNIVERSE = [
    ("revenue-vs-budget",          "Revenue vs. Budget",                  "revenue",     "critical", "Monthly"),
    ("ebitda-margin",              "EBITDA Margin",                       "revenue",     "critical", "Monthly"),
    ("net-profit-after-tax",       "Net Profit After Tax (PAT)",          "revenue",     "high",     "Quarterly"),
    ("equity-irr",                 "Equity IRR (Project Lifetime)",       "revenue",     "high",     "Annual"),
    ("revenue-waterfall",          "Monthly Revenue Waterfall (MTD)",     "revenue",     "critical", "Monthly"),
    ("net-book-value",             "Net Book Value & Asset Valuation",    "revenue",     "medium",   "Annual"),
    ("fy-reforecast",              "Full-Year Reforecast vs. Budget",     "revenue",     "high",     "Monthly"),
    ("cfads",                      "CFADS",                               "cash",        "critical", "Quarterly"),
    ("liquidity-reserves",         "Liquidity & Reserve Accounts",        "cash",        "critical", "Monthly"),
    ("distributions-equity",       "Distributions to Equity (FCFE)",      "cash",        "critical", "Quarterly"),
    ("dscr",                       "DSCR (Debt Service Coverage Ratio)",  "debt",        "critical", "Quarterly"),
    ("llcr",                       "LLCR / PLCR",                         "debt",        "high",     "Quarterly"),
    ("gearing-amortization",       "Gearing & Debt Amortization",         "debt",        "medium",   "Quarterly"),
    ("cost-of-debt",               "Cost of Debt & Hedge Status",         "debt",        "high",     "Quarterly"),
    ("contracted-revenue-horizon", "Contracted Revenue Horizon",          "contracting", "high",     "Monthly"),
    ("revenue-mix",                "Revenue Mix by Channel",              "contracting", "high",     "Monthly"),
    ("ppa-delivery-accuracy",      "PPA Delivery Accuracy",               "contracting", "high",     "Weekly"),
    ("realized-revenue-channel",   "Realized Revenue by Channel",         "contracting", "high",     "Weekly"),
    ("subsidy-certificate-revenue","Subsidy & Certificate Revenue",       "contracting", "medium",   "Monthly"),
    ("portfolio-capture-rate",     "Portfolio Capture Rate",              "market",      "critical", "Monthly"),
    ("capture-price",              "Daily Capture Price",                 "market",      "critical", "Daily"),
    ("imbalance-cost",             "Imbalance Cost per MWh",              "market",      "critical", "Daily"),
    ("negative-price-exposure",    "Negative Price Hour Exposure",        "market",      "high",     "Daily"),
    ("cumulative-yield-deviation", "Cumulative Yield Deviation from P50",  "generation",  "high",     "Monthly"),
    ("epi-budget",                 "Budget EPI (BEPI)",                   "generation",  "high",     "Weekly"),
    ("epi",                        "Energy Performance Index (EPI)",      "generation",  "critical", "Daily"),
    ("availability",               "System Availability",                 "generation",  "high",     "Daily"),
    ("curtailment-rate",           "Curtailment Rate",                    "generation",  "high",     "Daily"),
    ("degradation-warranty",       "Module Degradation vs. Warranty",     "generation",  "medium",   "Annual"),
    ("total-opex-budget",          "Total OpEx vs. Budget",               "cost",        "high",     "Monthly"),
    ("om-cost-mwh",                "O&M Cost per MWh",                    "cost",        "medium",   "Monthly"),
    ("mttr",                       "Mean Time To Repair (MTTR)",          "cost",        "medium",   "Weekly"),
    ("merchant-exposure",          "Merchant Exposure (%)",               "risk",        "high",     "Monthly"),
    ("dso-receivables",            "DSO & Aged Receivables",              "risk",        "high",     "Monthly"),
    ("counterparty-credit",        "Counterparty Credit Exposure",        "risk",        "high",     "Quarterly"),
]

KPI_BY_ID = {k[0]: {"id": k[0], "name": k[1], "category": k[2], "priority": k[3], "cadence": k[4]} for k in KPI_UNIVERSE}
NAME_TO_ID = {k[1]: k[0] for k in KPI_UNIVERSE}
# Normalised name lookup (lower, collapsed punctuation/space) for robustness if
# Excel mangles a label slightly on re-save.
def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())
NORM_NAME_TO_ID = {_norm(k[1]): k[0] for k in KPI_UNIVERSE}

# Known reviewers (display names). Daniel left the survey name field blank, so
# his export filename is "...-unknown-...". Filename slug → display name.
REVIEWER_ALIASES = {
    "unknown": "Daniel Peschel",
    "lars": "Lars Maehl",
    "matt": "Matt van Staden",
    "markos": "Markos Farag",
    "daniel": "Daniel Peschel",
}

PRIORITY_RANK = {"critical": 0, "high": 1, "medium": 2}


# ─────────────────────────────────────────────────────────────
# Parsing
# ─────────────────────────────────────────────────────────────
def _display_name_from_file(path: str, reviewer_field: str) -> str:
    rf = (reviewer_field or "").strip()
    base = os.path.basename(path)
    m = re.match(r"kpi-selections-(.+?)-(\d{4}-\d{2}-\d{2})\.csv$", base, re.IGNORECASE)
    slug = m.group(1).lower() if m else os.path.splitext(base)[0].lower()
    if rf and rf.lower() != "unknown":
        return rf
    if slug in REVIEWER_ALIASES:
        return REVIEWER_ALIASES[slug]
    return slug.replace("-", " ").title() or "Unknown"


def parse_response_csv(path: str) -> dict | None:
    """Parse one survey-export CSV (4-block format) into a response dict."""
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.reader(fh))
    except (OSError, UnicodeDecodeError):
        return None

    reviewer_field, date_str = "", ""
    declared_sel, declared_must = None, None
    comment = ""
    selected: set[str] = set()
    must_have: set[str] = set()
    unmatched: list[str] = []

    in_kpi_table = False
    for i, row in enumerate(rows):
        if not row or all((c or "").strip() == "" for c in row):
            in_kpi_table = False
            continue
        c0 = (row[0] or "").strip().lstrip("﻿")

        if c0 == "Reviewer" and len(row) >= 2 and (row[1] or "").strip() == "Date":
            # next non-empty row is the metadata values
            if i + 1 < len(rows):
                vals = rows[i + 1]
                reviewer_field = (vals[0] if len(vals) > 0 else "").strip()
                date_str = (vals[1] if len(vals) > 1 else "").strip()
                try:
                    declared_sel = int((vals[2] or "").strip()) if len(vals) > 2 else None
                    declared_must = int((vals[3] or "").strip()) if len(vals) > 3 else None
                except ValueError:
                    pass
            continue

        if c0 == "KPI Name":
            in_kpi_table = True
            continue

        if c0.startswith("Additional KPIs"):
            comment = (row[1] if len(row) > 1 else "").strip()
            in_kpi_table = False
            continue

        if in_kpi_table:
            name = c0
            kid = NAME_TO_ID.get(name) or NORM_NAME_TO_ID.get(_norm(name))
            if not kid:
                unmatched.append(name)
                continue
            selected.add(kid)
            if len(row) > 2 and (row[2] or "").strip().upper() == "YES":
                must_have.add(kid)

    if not selected and declared_sel is None:
        return None  # not a recognisable response file

    return {
        "reviewer": _display_name_from_file(path, reviewer_field),
        "reviewer_field": reviewer_field,
        "source_file": os.path.basename(path),
        "date": date_str,
        "selected": selected,
        "must_have": must_have,
        "declared_selected": declared_sel,
        "declared_must": declared_must,
        "comment": comment,
        "unmatched": unmatched,
    }


def load_responses() -> list[dict]:
    if not os.path.isdir(RESPONSES_DIR):
        return []
    out = []
    for path in sorted(glob.glob(os.path.join(RESPONSES_DIR, "*.csv"))):
        r = parse_response_csv(path)
        if r:
            out.append(r)
    # stable, friendly order
    out.sort(key=lambda r: r["reviewer"].lower())
    return out


# ─────────────────────────────────────────────────────────────
# Analysis
# ─────────────────────────────────────────────────────────────
def build_tally(responses: list[dict]) -> pd.DataFrame:
    n = len(responses)
    majority = math.floor(n / 2) + 1 if n else 1
    rec = []
    for kid, kpi in KPI_BY_ID.items():
        votes = sum(1 for r in responses if kid in r["selected"])
        musts = sum(1 for r in responses if kid in r["must_have"])
        if votes == n and n > 0:
            tier = "Core — unanimous"
        elif musts >= majority and n > 0:
            tier = "Core — must-have"
        elif votes >= majority and n > 0:
            tier = "Include — majority"
        elif votes >= 1:
            tier = "Consider — minority"
        else:
            tier = "Drop — no support"
        rec.append({
            "id": kid,
            "KPI": kpi["name"],
            "Category": CATEGORIES[kpi["category"]][0],
            "_cat_id": kpi["category"],
            "Survey priority": kpi["priority"].title(),
            "Cadence": kpi["cadence"],
            "Votes": votes,
            "Vote %": round(100 * votes / n) if n else 0,
            "Must-have": musts,
            "Tier": tier,
            "_pr": PRIORITY_RANK.get(kpi["priority"], 3),
        })
    df = pd.DataFrame(rec)
    cat_order = {cid: i for i, cid in enumerate(CATEGORIES)}
    df["_cat_ord"] = df["_cat_id"].map(cat_order)
    return df


TIER_ORDER = ["Core — unanimous", "Core — must-have", "Include — majority",
              "Consider — minority", "Drop — no support"]
TIER_COLOR = {
    "Core — unanimous": "#1a9850", "Core — must-have": "#66bd63",
    "Include — majority": "#a6d96a", "Consider — minority": "#fdae61",
    "Drop — no support": "#d73027",
}
