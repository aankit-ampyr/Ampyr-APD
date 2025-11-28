"""
Data Quality Report Module for BESS Dashboard

Generates comprehensive data quality reports for imported data.
"""

import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class DataQualityReport:
    """
    Container for data quality report information.
    """
    # Source information
    gridbeyond_file: Optional[str] = None
    scada_file: Optional[str] = None

    # Record counts
    gridbeyond_rows: int = 0
    scada_rows_original: int = 0
    scada_rows_resampled: int = 0
    merged_rows: int = 0

    # Date ranges
    gridbeyond_start: Optional[datetime] = None
    gridbeyond_end: Optional[datetime] = None
    scada_start: Optional[datetime] = None
    scada_end: Optional[datetime] = None
    merged_start: Optional[datetime] = None
    merged_end: Optional[datetime] = None

    # Time resolution
    gridbeyond_resolution_min: float = 30.0
    scada_resolution_min: float = 10.0
    output_resolution_min: float = 30.0

    # Missing values
    gridbeyond_missing: Dict[str, int] = field(default_factory=dict)
    scada_missing: Dict[str, int] = field(default_factory=dict)
    merged_missing: Dict[str, int] = field(default_factory=dict)

    # Columns with 100% missing
    gridbeyond_empty_columns: List[str] = field(default_factory=list)
    scada_empty_columns: List[str] = field(default_factory=list)

    # Data gaps
    gridbeyond_gaps: List[Dict] = field(default_factory=list)
    scada_gaps: List[Dict] = field(default_factory=list)

    # Overlap statistics
    overlap_pct: float = 0.0
    common_timestamps: int = 0
    only_gridbeyond: int = 0
    only_scada: int = 0

    # Value range issues
    soc_below_0: int = 0
    soc_above_100: int = 0
    power_outliers: int = 0

    # Calculated values
    soc_calculated_count: int = 0

    # Processing notes
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    # Timestamp
    generated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for serialization."""
        return {
            'source_info': {
                'gridbeyond_file': self.gridbeyond_file,
                'scada_file': self.scada_file,
                'generated_at': self.generated_at.isoformat()
            },
            'record_counts': {
                'gridbeyond_rows': self.gridbeyond_rows,
                'scada_rows_original': self.scada_rows_original,
                'scada_rows_resampled': self.scada_rows_resampled,
                'merged_rows': self.merged_rows
            },
            'date_ranges': {
                'gridbeyond': {
                    'start': self.gridbeyond_start.isoformat() if self.gridbeyond_start else None,
                    'end': self.gridbeyond_end.isoformat() if self.gridbeyond_end else None
                },
                'scada': {
                    'start': self.scada_start.isoformat() if self.scada_start else None,
                    'end': self.scada_end.isoformat() if self.scada_end else None
                },
                'merged': {
                    'start': self.merged_start.isoformat() if self.merged_start else None,
                    'end': self.merged_end.isoformat() if self.merged_end else None
                }
            },
            'missing_values': {
                'gridbeyond': self.gridbeyond_missing,
                'scada': self.scada_missing,
                'merged': self.merged_missing
            },
            'empty_columns': {
                'gridbeyond': self.gridbeyond_empty_columns,
                'scada': self.scada_empty_columns
            },
            'data_quality': {
                'overlap_pct': self.overlap_pct,
                'common_timestamps': self.common_timestamps,
                'soc_below_0': self.soc_below_0,
                'soc_above_100': self.soc_above_100,
                'power_outliers': self.power_outliers,
                'soc_calculated_count': self.soc_calculated_count
            },
            'gaps': {
                'gridbeyond': self.gridbeyond_gaps,
                'scada': self.scada_gaps
            },
            'warnings': self.warnings,
            'errors': self.errors
        }

    def summary_text(self) -> str:
        """Generate human-readable summary text."""
        lines = [
            "=" * 60,
            "DATA QUALITY REPORT",
            "=" * 60,
            f"Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "SOURCE FILES:",
            f"  GridBeyond: {self.gridbeyond_file or 'Not loaded'}",
            f"  SCADA:      {self.scada_file or 'Not loaded'}",
            "",
            "RECORD COUNTS:",
            f"  GridBeyond rows:      {self.gridbeyond_rows:,}",
            f"  SCADA rows (10-min):  {self.scada_rows_original:,}",
            f"  SCADA rows (30-min):  {self.scada_rows_resampled:,}",
            f"  Merged rows:          {self.merged_rows:,}",
            "",
            "DATE RANGES:",
        ]

        if self.gridbeyond_start:
            lines.append(f"  GridBeyond: {self.gridbeyond_start.strftime('%Y-%m-%d')} to {self.gridbeyond_end.strftime('%Y-%m-%d')}")
        if self.scada_start:
            lines.append(f"  SCADA:      {self.scada_start.strftime('%Y-%m-%d')} to {self.scada_end.strftime('%Y-%m-%d')}")
        if self.merged_start:
            lines.append(f"  Merged:     {self.merged_start.strftime('%Y-%m-%d')} to {self.merged_end.strftime('%Y-%m-%d')}")

        lines.extend([
            "",
            "TIMESTAMP OVERLAP:",
            f"  Common timestamps:    {self.common_timestamps:,}",
            f"  Only in GridBeyond:   {self.only_gridbeyond:,}",
            f"  Only in SCADA:        {self.only_scada:,}",
            f"  Overlap percentage:   {self.overlap_pct:.1f}%",
        ])

        if self.gridbeyond_empty_columns or self.scada_empty_columns:
            lines.extend([
                "",
                "100% MISSING COLUMNS:",
            ])
            if self.gridbeyond_empty_columns:
                lines.append(f"  GridBeyond: {', '.join(self.gridbeyond_empty_columns)}")
            if self.scada_empty_columns:
                lines.append(f"  SCADA: {', '.join(self.scada_empty_columns)}")

        lines.extend([
            "",
            "DATA QUALITY ISSUES:",
            f"  SOC values < 0:       {self.soc_below_0}",
            f"  SOC values > 100:     {self.soc_above_100}",
            f"  Power outliers:       {self.power_outliers}",
            f"  SOC values calculated:{self.soc_calculated_count}",
        ])

        if self.gridbeyond_gaps or self.scada_gaps:
            lines.extend([
                "",
                "TIMESTAMP GAPS DETECTED:",
                f"  GridBeyond gaps: {len(self.gridbeyond_gaps)}",
                f"  SCADA gaps:      {len(self.scada_gaps)}",
            ])

        if self.warnings:
            lines.extend([
                "",
                "WARNINGS:",
            ])
            for warning in self.warnings:
                lines.append(f"  ⚠ {warning}")

        if self.errors:
            lines.extend([
                "",
                "ERRORS:",
            ])
            for error in self.errors:
                lines.append(f"  ✗ {error}")

        lines.append("=" * 60)

        return "\n".join(lines)


def generate_quality_report(
    gridbeyond_df: Optional[pd.DataFrame] = None,
    scada_df_original: Optional[pd.DataFrame] = None,
    scada_df_resampled: Optional[pd.DataFrame] = None,
    merged_df: Optional[pd.DataFrame] = None,
    gridbeyond_file: Optional[str] = None,
    scada_file: Optional[str] = None
) -> DataQualityReport:
    """
    Generate a comprehensive data quality report.

    Args:
        gridbeyond_df: Loaded GridBeyond DataFrame
        scada_df_original: Original SCADA DataFrame (10-min)
        scada_df_resampled: Resampled SCADA DataFrame (30-min)
        merged_df: Merged DataFrame
        gridbeyond_file: Path to GridBeyond file
        scada_file: Path to SCADA file

    Returns:
        DataQualityReport with all metrics
    """
    report = DataQualityReport(
        gridbeyond_file=gridbeyond_file,
        scada_file=scada_file
    )

    # GridBeyond metrics
    if gridbeyond_df is not None:
        report.gridbeyond_rows = len(gridbeyond_df)
        report.gridbeyond_start = gridbeyond_df.index.min()
        report.gridbeyond_end = gridbeyond_df.index.max()
        report.gridbeyond_missing = gridbeyond_df.isna().sum().to_dict()
        report.gridbeyond_empty_columns = [
            col for col in gridbeyond_df.columns
            if gridbeyond_df[col].isna().all()
        ]

        # Detect gaps
        gaps = _detect_gaps(gridbeyond_df, expected_minutes=30)
        report.gridbeyond_gaps = gaps

    # SCADA metrics
    if scada_df_original is not None:
        report.scada_rows_original = len(scada_df_original)
        report.scada_start = scada_df_original.index.min()
        report.scada_end = scada_df_original.index.max()
        report.scada_missing = scada_df_original.isna().sum().to_dict()
        report.scada_empty_columns = [
            col for col in scada_df_original.columns
            if scada_df_original[col].isna().all()
        ]

        # Detect gaps
        gaps = _detect_gaps(scada_df_original, expected_minutes=10)
        report.scada_gaps = gaps

    if scada_df_resampled is not None:
        report.scada_rows_resampled = len(scada_df_resampled)

    # Merged metrics
    if merged_df is not None:
        report.merged_rows = len(merged_df)
        report.merged_start = merged_df.index.min()
        report.merged_end = merged_df.index.max()
        report.merged_missing = merged_df.isna().sum().to_dict()

        # Overlap info from merge
        if hasattr(merged_df, 'attrs') and 'overlap_info' in merged_df.attrs:
            overlap = merged_df.attrs['overlap_info']
            report.overlap_pct = overlap.get('overlap_pct', 0)
            report.common_timestamps = overlap.get('common_timestamps', 0)
            report.only_gridbeyond = overlap.get('only_gridbeyond', 0)
            report.only_scada = overlap.get('only_scada', 0)

        # SOC quality checks
        if 'SOC' in merged_df.columns:
            soc = merged_df['SOC'].dropna()
            report.soc_below_0 = (soc < 0).sum()
            report.soc_above_100 = (soc > 100).sum()

        # Calculated SOC count
        if 'SOC_calculated' in merged_df.columns:
            report.soc_calculated_count = merged_df['SOC_calculated'].sum()

    # Add warnings based on thresholds
    _add_warnings(report)

    return report


def _detect_gaps(df: pd.DataFrame, expected_minutes: int) -> List[Dict]:
    """
    Detect timestamp gaps in DataFrame.

    Args:
        df: DataFrame with timestamp index
        expected_minutes: Expected time resolution in minutes

    Returns:
        List of gap dictionaries
    """
    if len(df) < 2:
        return []

    expected_delta = pd.Timedelta(minutes=expected_minutes)
    time_diffs = df.index.to_series().diff()

    gaps = []
    for idx, diff in time_diffs.items():
        if pd.notna(diff) and diff > expected_delta * 1.5:  # Allow 50% tolerance
            prev_idx = df.index[df.index.get_loc(idx) - 1]
            gaps.append({
                'start': prev_idx.isoformat(),
                'end': idx.isoformat(),
                'duration_minutes': diff.total_seconds() / 60,
                'missing_periods': int(diff / expected_delta) - 1
            })

    return gaps


def _add_warnings(report: DataQualityReport) -> None:
    """
    Add warnings based on data quality thresholds.

    Args:
        report: DataQualityReport to update
    """
    # Low overlap warning
    if report.overlap_pct < 90 and report.overlap_pct > 0:
        report.warnings.append(
            f"Low timestamp overlap: {report.overlap_pct:.1f}% "
            f"({report.common_timestamps} common timestamps)"
        )

    # SOC out of range warnings
    if report.soc_below_0 > 0:
        report.warnings.append(f"{report.soc_below_0} SOC values below 0%")

    if report.soc_above_100 > 0:
        report.warnings.append(f"{report.soc_above_100} SOC values above 100%")

    # Significant calculated SOC
    if report.soc_calculated_count > 0:
        pct = (report.soc_calculated_count / max(report.merged_rows, 1)) * 100
        if pct > 10:
            report.warnings.append(
                f"{report.soc_calculated_count} SOC values ({pct:.1f}%) "
                "were calculated from power integration"
            )

    # Empty columns warning
    if report.gridbeyond_empty_columns:
        report.warnings.append(
            f"GridBeyond has {len(report.gridbeyond_empty_columns)} "
            "columns with 100% missing values"
        )

    # Date range mismatch
    if report.gridbeyond_start and report.scada_start:
        if abs((report.gridbeyond_start - report.scada_start).days) > 1:
            report.warnings.append(
                "GridBeyond and SCADA start dates differ by more than 1 day"
            )

    # Gaps warning
    if len(report.gridbeyond_gaps) > 0:
        report.warnings.append(
            f"GridBeyond data has {len(report.gridbeyond_gaps)} timestamp gap(s)"
        )

    if len(report.scada_gaps) > 0:
        report.warnings.append(
            f"SCADA data has {len(report.scada_gaps)} timestamp gap(s)"
        )
