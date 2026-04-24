"""
Invoice Reconciliation Engine

Computes reconciliation between multiple data sources:
- Energy volume reconciliation (BESS and Solar PV)
- Revenue reconciliation (gross vs net, per stream)
- Capacity market payment verification
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List

try:
    from config.revenue_config import GB_REVENUE_NET_SHARE
except ImportError:  # pragma: no cover — path/import variations across entry points
    GB_REVENUE_NET_SHARE = 0.95


# ─────────────────────────────────────────────────────────────
# 1. Energy Volume Reconciliation
# ─────────────────────────────────────────────────────────────

def reconcile_bess_energy(
    master_df: Optional[pd.DataFrame],
    hartree_bess: Optional[pd.DataFrame],
    summary_detail: Optional[pd.DataFrame],
    scada_df: Optional[pd.DataFrame],
    month_label: str = '',
) -> pd.DataFrame:
    """
    Compare BESS energy volumes (MWh) across up to 4 sources.

    Sources:
        1. Master CSV (GridBeyond backing data) — Credited Energy Volume
        2. Hartree BESS readings — Import + Export
        3. Summary Statement Detail — Import + Export
        4. SCADA Monitoring — Daily exported/imported energy

    Args:
        master_df: Master CSV data (northwold_df from load_month_data)
        hartree_bess: Hartree BESS readings DataFrame
        summary_detail: Detail sheet from Summary Statement
        scada_df: SCADA monitoring DataFrame
        month_label: Label for the month being reconciled

    Returns:
        DataFrame with columns: source, import_mwh, export_mwh, net_mwh
    """
    records = []

    # 1. Master CSV
    if master_df is not None and not master_df.empty:
        energy_col = _find_column(master_df, ['Credited Energy Volume Battery MWh Output',
                                               'Credited Energy Volume  Battery MWh Output'])
        if energy_col:
            # Positive = export, negative = import
            values = master_df[energy_col].astype(float)
            export_mwh = values[values > 0].sum()
            import_mwh = abs(values[values < 0].sum())
        else:
            # Try Power_MW column integrated over time
            power_col = _find_column(master_df, ['Power_MW', 'Physical_Power_MW'])
            if power_col:
                power = master_df[power_col].astype(float)
                export_mwh = (power[power > 0] * 0.5).sum()  # 30-min periods
                import_mwh = abs((power[power < 0] * 0.5).sum())
            else:
                export_mwh = import_mwh = 0

        records.append({
            'source': 'Master CSV (GridBeyond)',
            'import_mwh': round(import_mwh, 3),
            'export_mwh': round(export_mwh, 3),
            'net_mwh': round(export_mwh - import_mwh, 3),
        })

    # 2. Hartree BESS Readings
    if hartree_bess is not None and not hartree_bess.empty:
        # Filter to the month if possible
        filtered = _filter_to_month(hartree_bess, month_label)
        if not filtered.empty:
            import_kwh = filtered.get('BESS_Import_kWh', pd.Series([0])).sum()
            export_kwh = filtered.get('BESS_Export_kWh', pd.Series([0])).sum()
            records.append({
                'source': 'Hartree BESS Readings',
                'import_mwh': round(import_kwh / 1000, 3),
                'export_mwh': round(export_kwh / 1000, 3),
                'net_mwh': round((export_kwh - import_kwh) / 1000, 3),
            })

    # 3. Summary Statement Detail (values are in kWh, convert to MWh)
    if summary_detail is not None and not summary_detail.empty:
        import_kwh = summary_detail.get('Import', pd.Series([0])).sum()
        export_kwh = summary_detail.get('Export', pd.Series([0])).sum()
        records.append({
            'source': 'Summary Statement',
            'import_mwh': round(abs(import_kwh) / 1000, 3),
            'export_mwh': round(abs(export_kwh) / 1000, 3),
            'net_mwh': round((abs(export_kwh) - abs(import_kwh)) / 1000, 3),
        })

    # 4. SCADA Monitoring
    if scada_df is not None and not scada_df.empty:
        filtered = _filter_to_month(scada_df, month_label)
        if not filtered.empty:
            # Daily export/import are cumulative within each day, take max per day
            if 'Daily_Export_kWh' in filtered.columns:
                daily_export = filtered.groupby(filtered.index.date)['Daily_Export_kWh'].max()
                daily_import = filtered.groupby(filtered.index.date)['Daily_Import_kWh'].max()
                records.append({
                    'source': 'SCADA Monitoring',
                    'import_mwh': round(daily_import.sum() / 1000, 3),
                    'export_mwh': round(daily_export.sum() / 1000, 3),
                    'net_mwh': round((daily_export.sum() - daily_import.sum()) / 1000, 3),
                })

    result = pd.DataFrame(records)

    # Calculate variances against the first source (Master CSV as baseline)
    if len(result) > 1:
        baseline_export = result.iloc[0]['export_mwh']
        baseline_import = result.iloc[0]['import_mwh']
        result['export_variance_mwh'] = result['export_mwh'] - baseline_export
        result['import_variance_mwh'] = result['import_mwh'] - baseline_import
        result['export_variance_pct'] = np.where(
            baseline_export != 0,
            (result['export_variance_mwh'] / baseline_export * 100).round(2),
            0
        )

    return result


def reconcile_solar_pv(
    solar_gen: Optional[pd.DataFrame],
    hartree_pv: Optional[pd.DataFrame],
) -> pd.DataFrame:
    """
    Compare Solar PV generation: allocated quantity vs Hartree invoiced.

    Args:
        solar_gen: Solar Generation Allocated Quantity DataFrame
        hartree_pv: Hartree PV readings pivot DataFrame

    Returns:
        DataFrame with month, allocated_kwh, invoiced_kwh, under_over_kwh
    """
    if hartree_pv is not None and not hartree_pv.empty:
        # Hartree PV already has the comparison built in
        result = hartree_pv[hartree_pv['month'] != 'Grand Total'].copy()
        result = result.rename(columns={
            'generation_kwh': 'allocated_kwh',
            'under_over_invoiced_kwh': 'under_over_kwh',
        })
        result['invoiced_kwh'] = result['invoiced_sin2_01_02'] + result['invoiced_sin2_03']
        result['variance_pct'] = np.where(
            result['allocated_kwh'] != 0,
            (result['under_over_kwh'] / result['allocated_kwh'] * 100).round(2),
            0
        )
        return result

    return pd.DataFrame()


# ─────────────────────────────────────────────────────────────
# 2. Revenue Reconciliation
# ─────────────────────────────────────────────────────────────

def reconcile_revenue(
    master_df: Optional[pd.DataFrame],
    summary_statement: Optional[Dict],
    aggregator_share: float = GB_REVENUE_NET_SHARE,
) -> pd.DataFrame:
    """
    Compare revenue per stream: Master CSV (gross) vs Summary Statement (net 95%).

    Shows both gross and net to catch errors at both calculation and fee stages.

    Args:
        master_df: Master CSV data (northwold_df from load_month_data)
        summary_statement: Parsed summary statement dict
        aggregator_share: Asset owner's share (default 0.95 = 95%, i.e. 5% GridBeyond fee)

    Returns:
        DataFrame with columns: stream, gross_revenue, expected_net,
        reported_net, variance, variance_pct
    """
    # Map of stream names: (master_csv_columns, summary_energy_key, summary_ancillary_key)
    stream_mappings = [
        ('EPEX DAM 30', ['EPEX 30 DA Revenue'], 'EPEX DAM 30', None),
        ('EPEX DAM 60', ['EPEX DA Revenues', 'EPEX DA Revenue'], 'EPEX DAM 60', None),
        ('IDA1', ['IDA1 Revenue'], 'EPEX IDA1', None),
        ('IDC', ['IDC Revenue'], 'EPEX IDC', None),
        ('Imbalance', ['Imbalance Revenue', 'Imbalance Charge'], 'Imbalance', None),
        ('SFFR', ['SFFR revenues', 'SFFR Revenue'], None, 'SFFR'),
        ('DC', ['DCL revenues', 'DCH revenues'], None, 'DC'),
        ('DR', ['DRL revenues', 'DRH revenues'], None, 'DR'),
        ('DM', ['DML revenues', 'DMH revenues'], None, 'DM'),
    ]

    records = []

    for stream_name, master_cols, energy_key, ancillary_key in stream_mappings:
        # Gross revenue from Master CSV
        gross = 0.0
        if master_df is not None and not master_df.empty:
            for col in master_cols:
                matching = _find_column(master_df, [col])
                if matching:
                    gross += master_df[matching].astype(float).sum()

        # Reported net from Summary Statement
        reported_net = 0.0
        if summary_statement:
            summary = summary_statement.get('summary', {})
            if energy_key:
                reported_net += summary.get('energy_revenue', {}).get(energy_key, 0)
            if ancillary_key:
                reported_net += summary.get('ancillary_revenue', {}).get(ancillary_key, 0)

        expected_net = gross * aggregator_share
        variance = reported_net - expected_net if (reported_net != 0 or expected_net != 0) else 0

        records.append({
            'stream': stream_name,
            'gross_revenue': round(gross, 2),
            'expected_net': round(expected_net, 2),
            'reported_net': round(reported_net, 2),
            'variance': round(variance, 2),
            'variance_pct': round(variance / expected_net * 100, 2) if expected_net != 0 else 0,
        })

    result = pd.DataFrame(records)

    # Add totals row
    if not result.empty:
        totals = {
            'stream': 'TOTAL',
            'gross_revenue': result['gross_revenue'].sum(),
            'expected_net': result['expected_net'].sum(),
            'reported_net': result['reported_net'].sum(),
            'variance': result['variance'].sum(),
        }
        totals['variance_pct'] = (
            round(totals['variance'] / totals['expected_net'] * 100, 2)
            if totals['expected_net'] != 0 else 0
        )
        result = pd.concat([result, pd.DataFrame([totals])], ignore_index=True)

    return result


def compute_aggregator_fee_breakdown(
    master_df: Optional[pd.DataFrame],
    summary_statement: Optional[Dict],
    aggregator_share: float = GB_REVENUE_NET_SHARE,
) -> Dict:
    """
    Compute the aggregator fee waterfall:
    Gross Revenue -> Aggregator Fee (5%) -> Expected Net -> Reported Net -> Variance

    Returns:
        Dict with gross, fee, expected_net, reported_net, variance
    """
    gross = 0.0
    if master_df is not None and not master_df.empty:
        revenue_cols = [c for c in master_df.columns
                        if any(k in c.lower() for k in ['revenue', 'revenues'])]
        for col in revenue_cols:
            try:
                gross += master_df[col].astype(float).sum()
            except (ValueError, TypeError):
                pass

    reported_net = 0.0
    if summary_statement:
        summary = summary_statement.get('summary', {})
        energy_total = summary.get('energy_revenue', {}).get('_total', 0)
        ancillary_total = summary.get('ancillary_revenue', {}).get('_total', 0)
        reported_net = energy_total + ancillary_total

    fee = gross * (1 - aggregator_share)
    expected_net = gross * aggregator_share

    return {
        'gross': round(gross, 2),
        'fee': round(fee, 2),
        'expected_net': round(expected_net, 2),
        'reported_net': round(reported_net, 2),
        'variance': round(reported_net - expected_net, 2),
    }


# ─────────────────────────────────────────────────────────────
# 3. Capacity Market Reconciliation
# ─────────────────────────────────────────────────────────────

def reconcile_capacity_market(emr_data: pd.DataFrame) -> pd.DataFrame:
    """
    Verify EMR capacity market payments against expected formula.

    Formula: Payment = Obligation × Price × (CPI / Base_CPI) × Weighting
    (When CPI and Base_CPI are both 0, the CPI ratio is treated as 1.0)

    Args:
        emr_data: EMR capacity market DataFrame from load_emr_capacity_market()

    Returns:
        DataFrame with original data plus calculated_payment, verification_status
    """
    if emr_data.empty:
        return emr_data

    result = emr_data.copy()

    # Calculate expected payment
    def calc_expected(row):
        obligation = row['capacity_obligation']
        price = row['capacity_price']
        base_cpi = row['cm_base_cpi']
        cpi = row['cm_cpi']
        weighting = row['weighting_factor']

        # CPI adjustment: if both are 0, no CPI adjustment (ratio = 1)
        if base_cpi != 0:
            cpi_ratio = cpi / base_cpi
        else:
            cpi_ratio = 1.0

        return obligation * price * cpi_ratio * weighting

    result['calculated_payment'] = result.apply(calc_expected, axis=1).round(2)
    result['payment_match'] = abs(result['calculated_payment'] - abs(result['invoice_total'])) < 0.01
    result['cumulative_payment'] = result['invoice_total'].cumsum()

    return result


# ─────────────────────────────────────────────────────────────
# Cross-month Summary
# ─────────────────────────────────────────────────────────────

def build_cross_month_summary(
    months_data: Dict[str, Dict],
) -> pd.DataFrame:
    """
    Build a cross-month summary table from multiple months of reconciliation data.

    Args:
        months_data: Dict keyed by month label, values are dicts with:
            'master_revenue': total gross revenue from Master CSV
            'summary_revenue': total reported net from Summary Statement
            'capacity_payment': EMR capacity payment for that month
            'energy_variance_pct': max energy volume variance %

    Returns:
        DataFrame with one row per month and summary columns
    """
    records = []
    for month, data in months_data.items():
        records.append({
            'month': month,
            'gross_revenue': data.get('master_revenue', 0),
            'reported_net': data.get('summary_revenue', 0),
            'capacity_payment': data.get('capacity_payment', 0),
            'energy_variance_pct': data.get('energy_variance_pct', 0),
        })

    result = pd.DataFrame(records)
    if not result.empty:
        result['expected_net'] = (result['gross_revenue'] * 0.93).round(2)
        result['revenue_variance'] = (result['reported_net'] - result['expected_net']).round(2)

    return result


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _find_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    """Find first matching column name from a list of candidates."""
    for candidate in candidates:
        # Exact match
        if candidate in df.columns:
            return candidate
        # Fuzzy match (handle newlines/spaces in column names)
        for col in df.columns:
            cleaned = col.replace('\n', ' ').strip()
            if cleaned == candidate:
                return col
    return None


def _filter_to_month(df: pd.DataFrame, month_label: str) -> pd.DataFrame:
    """Filter a timestamped DataFrame to a specific month."""
    if df.empty or not month_label:
        return df

    # Parse month label (e.g., "November 2025" or "January 2026")
    try:
        month_dt = pd.to_datetime(month_label, format='%B %Y')
        year = month_dt.year
        month = month_dt.month
    except Exception:
        return df

    if isinstance(df.index, pd.DatetimeIndex):
        mask = (df.index.year == year) & (df.index.month == month)
        return df[mask]

    return df


def variance_status(variance_pct: float, warn_threshold: float = 1.0, error_threshold: float = 5.0) -> str:
    """Return a status indicator based on variance percentage."""
    abs_var = abs(variance_pct)
    if abs_var <= warn_threshold:
        return 'ok'
    elif abs_var <= error_threshold:
        return 'warning'
    else:
        return 'error'
