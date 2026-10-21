"""
Elsterheide solar ETL — raw/Elsterheide/*.xlsx -> data/elsterheide/*.parquet (+ meta.json).

Elsterheide is a ~160 MWp PV site in Saxony, Germany (Goldbeck Solar EPC for
NaGa Solar Project V GmbH), built as two EPC parks on two grid connections:
  * park "1+2" (Nardt,   70,285.64 kWp) -> UW Neuwiese, 110 kV, MITNETZ STROM
  * park "3+4" (Brothen, 89,878.62 kWp) -> UW Bluno
The portal exports one workbook per metering GROUP: a 5-minute series of export
energy (kWh per interval) per Janitza UMG 604 feeder meter.
  * "Elsterheide 1 & 2 UWNW TR101" -> 2 meters (H01, H02) -> group "1&2"
  * "Elsterheide 3 TR102 (H05)"    -> 2 meters             -> group "3 (TR102)"
  * "Elsterheide 4 TR101 (H03)"    -> 1 meter              -> group "4 (TR101)"
Groups "3"/"4" are transformer-feeder groups on the Bluno connection, NOT the
EPC's ELST 3 / ELST 4 fields. Per-group kWp is unknown until the as-built
single-line diagram arrives, so yields are only normalised per EPC park.

Conventions (flagged in meta.json until the portal confirms them):
  * timestamps are naive plant-local time labelling the END of the 5-min interval;
  * blank cells are missing data and stay NaN — never zero;
  * the two "1&2" meters are summed (assumed additive: two parallel feeders).

Drop new portal exports (any month, same layout) into raw/Elsterheide/ and run:
    python -m src.data_cleaning.process_elsterheide
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "raw" / "Elsterheide"
OUT = ROOT / "data" / "elsterheide"

STEP = pd.Timedelta(minutes=5)
CAP_DC_KWP = {"1+2": 70285.64, "3+4": 89878.62}      # contract DC per EPC park
PARK_OF_GROUP = {"1&2": "1+2", "3 (TR102)": "3+4", "4 (TR101)": "3+4"}
CONNECTION_OF_GROUP = {
    "1&2": "UW Neuwiese (110 kV, MITNETZ STROM)",
    "3 (TR102)": "UW Bluno",
    "4 (TR101)": "UW Bluno",
}
GROUPS = list(PARK_OF_GROUP)

_GROUP_RE = re.compile(r"Elsterheide (1 ?& ?2|3|4)\b")
_METER_RE = re.compile(r"\((\d{8})\)")


def _group(header: str) -> str:
    m = _GROUP_RE.search(header)
    if not m:
        raise ValueError(f"unrecognised meter header: {header[:90]}")
    return {"1&2": "1&2", "3": "3 (TR102)", "4": "4 (TR101)"}[m.group(1).replace(" ", "")]


def _export_stamp(path: Path) -> str:
    """Portal export time = the first sheet's name ('Reports-2026-09-28-13-26'); zero-padded, so it sorts chronologically."""
    with pd.ExcelFile(path) as xf:
        return xf.sheet_names[0]


def _load_workbook(path: Path) -> pd.DataFrame:
    """One portal export -> long 5-min frame: time, group, meter_id, export_kwh."""
    # First sheet by position: its name is the export timestamp and changes every export.
    df = pd.read_excel(path, sheet_name=0, header=0)
    time = pd.to_datetime(df.iloc[:, 0], errors="coerce")
    parts = []
    for col in df.columns[1:]:
        header = str(col)
        m = _METER_RE.search(header)
        if not m:
            raise ValueError(f"no 8-digit device id in header: {header[:90]}")
        parts.append(pd.DataFrame({
            "time": time,
            "group": _group(header),
            "meter_id": m.group(1),
            # blanks -> NaN (missing), real zeros stay 0
            "export_kwh": pd.to_numeric(df[col], errors="coerce").round(3),
        }))
    out = pd.concat(parts, ignore_index=True)
    return out[out["time"].notna()].reset_index(drop=True)


def _meter_15min(m5: pd.DataFrame) -> pd.DataFrame:
    """Right-closed, right-labelled 15-min sums per meter. A bucket is NaN unless
    all three 5-min values are present (n_present < 3)."""
    rows = []
    for (g, mid), s in m5.groupby(["group", "meter_id"]):
        r = s.set_index("time")["export_kwh"].resample("15min", closed="right", label="right")
        n_rows = r.size()
        df = pd.DataFrame({
            "time": n_rows.index, "group": g, "meter_id": mid,
            "export_kwh": r.sum(min_count=3).values,
            "n_present": r.count().values.astype(int),
        })
        rows.append(df[n_rows.values > 0])      # drop empty buckets between non-contiguous months
    return pd.concat(rows, ignore_index=True)


def _group_15min(m15: pd.DataFrame) -> pd.DataFrame:
    """Per-group 15-min export (meters summed) and average power; NaN if any meter is missing."""
    g = m15.groupby(["time", "group"]).agg(
        export_kwh=("export_kwh", "sum"), n_meters=("export_kwh", "count"), n_expected=("meter_id", "size"),
    ).reset_index()
    g.loc[g["n_meters"] < g["n_expected"], "export_kwh"] = float("nan")
    g["power_mw"] = g["export_kwh"] * 4 / 1000.0
    return g[["time", "group", "export_kwh", "power_mw"]]


def _daily(m5: pd.DataFrame, g15: pd.DataFrame) -> pd.DataFrame:
    """Per group and interval-START date: energy, completeness, peak 15-min power."""
    d5 = m5.assign(date=(m5["time"] - STEP).dt.date)
    day = d5.groupby(["date", "group"])["export_kwh"].agg(
        energy_kwh="sum", n_present="count", n_rows="size",
    ).reset_index()
    day["energy_mwh"] = day["energy_kwh"] / 1000.0
    day["complete"] = day["n_present"] == day["n_rows"]
    p = g15.assign(date=(g15["time"] - 3 * STEP).dt.date)
    peak = p.groupby(["date", "group"])["power_mw"].max().rename("peak_mw").reset_index()
    day = day.merge(peak, on=["date", "group"], how="left")
    return day[["date", "group", "energy_mwh", "n_present", "n_rows", "complete", "peak_mw"]]


def run(verbose: bool = True) -> dict:
    files = sorted(RAW.glob("*.xlsx"), key=_export_stamp)
    if not files:
        raise FileNotFoundError(f"no portal exports in {RAW}")
    OUT.mkdir(parents=True, exist_ok=True)

    m5 = pd.concat([_load_workbook(f) for f in files], ignore_index=True)
    # the later export (by stamp, whatever the file was named) wins when a meter+interval is exported twice
    m5 = m5.drop_duplicates(["meter_id", "time"], keep="last").sort_values(["group", "meter_id", "time"]).reset_index(drop=True)
    m15 = _meter_15min(m5)
    g15 = _group_15min(m15)
    day = _daily(m5, g15)

    m5.to_parquet(OUT / "meter_5min.parquet", index=False)
    m15.to_parquet(OUT / "meter_15min.parquet", index=False)
    g15.to_parquet(OUT / "group_15min.parquet", index=False)
    day.to_parquet(OUT / "daily.parquet", index=False)

    site = g15.pivot(index="time", columns="group", values="power_mw").dropna().sum(axis=1)
    totals = day.groupby("group")["energy_mwh"].sum()
    peaks = g15.groupby("group")["power_mw"].max()
    missing = m5[m5["export_kwh"].isna()].groupby("group").size()
    meters = m5.groupby("group")["meter_id"].unique()
    meta = {
        "asset": "Elsterheide",
        "type": "Solar PV",
        "country": "Germany",
        "location": "Gemeinde Elsterheide, Landkreis Bautzen, Saxony",
        "epc_parks": {
            park: {"dc_kwp": kwp, "groups": [g for g in GROUPS if PARK_OF_GROUP[g] == park]}
            for park, kwp in CAP_DC_KWP.items()
        },
        "groups": {
            g: {"park": PARK_OF_GROUP[g], "connection": CONNECTION_OF_GROUP[g],
                "meters": sorted(meters.get(g, [])), "dc_kwp": None}
            for g in GROUPS
        },
        "assumptions": {
            "interval_label": "period_end_assumed",
            "timezone": "naive plant-local time (Europe/Berlin), DST untested",
            "h01_h02_additive_assumed": True,
            "meters_are": "Janitza UMG 604 MV feeder meters — control metering, not settlement meters",
        },
        "resolution_min": 5,
        "period_start": str(day["date"].min()),
        "period_end": str(day["date"].max()),
        "n_days": int(day["date"].nunique()),
        "total_energy_mwh": {**{g: round(float(totals.get(g, 0.0)), 3) for g in GROUPS},
                             "site": round(float(totals.sum()), 3)},
        "missing_5min_meter_intervals": {g: int(missing.get(g, 0)) for g in GROUPS},
        "peak_15min_mw": {**{g: round(float(peaks.get(g, float("nan"))), 2) for g in GROUPS},
                          "site": round(float(site.max()), 2) if len(site) else None,
                          "site_at": str(site.idxmax()) if len(site) else None},
        "files": [f.name for f in files],
    }
    with open(OUT / "meta.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)

    if verbose:
        print("Elsterheide ETL ->", OUT)
        for k, v in meta.items():
            print(f"  {k:24} {v}")
    return meta


# ---- readers ----
def _read(name):
    p = OUT / name
    return pd.read_parquet(p) if p.exists() else pd.DataFrame()


def read_meter_5min():
    return _read("meter_5min.parquet")


def read_meter_15min():
    return _read("meter_15min.parquet")


def read_group_15min():
    return _read("group_15min.parquet")


def read_daily():
    return _read("daily.parquet")


def read_meta():
    p = OUT / "meta.json"
    if p.exists():
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


if __name__ == "__main__":
    run()
