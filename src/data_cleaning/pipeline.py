"""
Data Processing Pipeline for BESS Dashboard

Main entry point for processing raw data files into analysis-ready format.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Tuple
import sys

from .loader import load_gridbeyond, load_scada, find_files, get_data_info
from .transformer import resample_scada, calculate_missing_soc, validate_soc_range
from .merger import merge_data, align_timestamps, create_master_dataset, detect_timestamp_gaps
from .report import DataQualityReport, generate_quality_report


def process_monthly_data(
    input_folder: str,
    output_folder: Optional[str] = None,
    month: Optional[str] = None,
    year: Optional[str] = None,
    verbose: bool = True
) -> Tuple[pd.DataFrame, DataQualityReport]:
    """
    Process raw monthly data from GridBeyond and SCADA into merged dataset.

    Args:
        input_folder: Path to folder containing raw Excel files
        output_folder: Path to save output CSV (default: data/)
        month: Month name for output filename (auto-detected if not provided)
        year: Year for output filename (auto-detected if not provided)
        verbose: Print progress messages

    Returns:
        Tuple of (merged DataFrame, DataQualityReport)
    """
    if verbose:
        print("=" * 60)
        print("BESS Data Processing Pipeline")
        print("=" * 60)

    # Step 1: Find files
    if verbose:
        print("\n[1/6] Finding data files...")

    files = find_files(input_folder)

    if not files['gridbeyond']:
        raise FileNotFoundError(f"No GridBeyond file found in {input_folder}")
    if not files['scada']:
        raise FileNotFoundError(f"No SCADA file found in {input_folder}")

    if verbose:
        print(f"  GridBeyond: {Path(files['gridbeyond']).name}")
        print(f"  SCADA:      {Path(files['scada']).name}")

    # Step 2: Load data
    if verbose:
        print("\n[2/6] Loading data files...")

    gridbeyond_df = load_gridbeyond(files['gridbeyond'])
    scada_df_original = load_scada(files['scada'], convert_power_to_mw=True)

    if verbose:
        print(f"  GridBeyond: {len(gridbeyond_df):,} rows, {len(gridbeyond_df.columns)} columns")
        print(f"  SCADA:      {len(scada_df_original):,} rows, {len(scada_df_original.columns)} columns")
        print(f"  GridBeyond date range: {gridbeyond_df.index.min()} to {gridbeyond_df.index.max()}")
        print(f"  SCADA date range:      {scada_df_original.index.min()} to {scada_df_original.index.max()}")

    # Step 3: Resample SCADA from 10-min to 30-min
    if verbose:
        print("\n[3/6] Resampling SCADA to 30-minute intervals...")

    scada_df_resampled = resample_scada(scada_df_original, target_freq='30min')

    if verbose:
        print(f"  Original:   {len(scada_df_original):,} rows (10-min)")
        print(f"  Resampled:  {len(scada_df_resampled):,} rows (30-min)")

    # Step 4: Calculate missing SOC values
    if verbose:
        print("\n[4/6] Calculating missing SOC values...")

    soc_before = scada_df_resampled['SOC'].isna().sum() if 'SOC' in scada_df_resampled.columns else 0

    if 'SOC' in scada_df_resampled.columns and 'Power_MW' in scada_df_resampled.columns:
        scada_df_resampled = calculate_missing_soc(
            scada_df_resampled,
            power_col='Power_MW',
            soc_col='SOC',
            dt_hours=0.5  # 30-min intervals
        )
        soc_after = scada_df_resampled['SOC'].isna().sum()
        soc_calculated = (scada_df_resampled['SOC_calculated'] == True).sum() if 'SOC_calculated' in scada_df_resampled.columns else 0

        if verbose:
            print(f"  Missing SOC before: {soc_before}")
            print(f"  Missing SOC after:  {soc_after}")
            print(f"  SOC values calculated from power: {soc_calculated}")

    # Step 5: Merge data sources
    if verbose:
        print("\n[5/6] Merging GridBeyond and SCADA data...")

    # Align timestamps first
    gb_aligned, scada_aligned = align_timestamps(gridbeyond_df, scada_df_resampled)

    if verbose:
        print(f"  Common date range: {gb_aligned.index.min()} to {gb_aligned.index.max()}")

    # Merge
    merged_df = merge_data(gb_aligned, scada_aligned, how='outer')

    if verbose:
        print(f"  Merged rows: {len(merged_df):,}")
        if hasattr(merged_df, 'attrs') and 'overlap_info' in merged_df.attrs:
            overlap = merged_df.attrs['overlap_info']
            print(f"  Timestamp overlap: {overlap['overlap_pct']:.1f}%")

    # Step 6: Generate quality report and save
    if verbose:
        print("\n[6/6] Generating quality report...")

    report = generate_quality_report(
        gridbeyond_df=gridbeyond_df,
        scada_df_original=scada_df_original,
        scada_df_resampled=scada_df_resampled,
        merged_df=merged_df,
        gridbeyond_file=files['gridbeyond'],
        scada_file=files['scada']
    )

    # Save output
    if output_folder:
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)

        # Auto-detect month/year from data if not provided
        if not month or not year:
            mid_date = merged_df.index[len(merged_df) // 2]
            month = month or mid_date.strftime('%b')
            year = year or mid_date.strftime('%Y')

        output_file = output_path / f"Master_BESS_Analysis_{month}_{year}.csv"
        merged_df.to_csv(output_file)

        if verbose:
            print(f"\n  Output saved to: {output_file}")

    if verbose:
        print("\n" + "=" * 60)
        print("Processing complete!")
        print("=" * 60)

        # Print warnings
        if report.warnings:
            print("\nWarnings:")
            for warning in report.warnings:
                print(f"  [!] {warning}")

    return merged_df, report


def process_files_direct(
    gridbeyond_file: str,
    scada_file: str,
    output_path: Optional[str] = None,
    verbose: bool = True
) -> Tuple[pd.DataFrame, DataQualityReport]:
    """
    Process specific GridBeyond and SCADA files directly.

    Args:
        gridbeyond_file: Path to GridBeyond Excel file
        scada_file: Path to SCADA Excel file
        output_path: Optional path to save merged CSV
        verbose: Print progress messages

    Returns:
        Tuple of (merged DataFrame, DataQualityReport)
    """
    if verbose:
        print("Loading GridBeyond file...")
    gridbeyond_df = load_gridbeyond(gridbeyond_file)

    if verbose:
        print("Loading SCADA file...")
    scada_df_original = load_scada(scada_file, convert_power_to_mw=True)

    if verbose:
        print("Resampling SCADA to 30-minute intervals...")
    scada_df_resampled = resample_scada(scada_df_original, target_freq='30min')

    if verbose:
        print("Calculating missing SOC values...")
    if 'SOC' in scada_df_resampled.columns and 'Power_MW' in scada_df_resampled.columns:
        scada_df_resampled = calculate_missing_soc(
            scada_df_resampled,
            power_col='Power_MW',
            soc_col='SOC',
            dt_hours=0.5
        )

    if verbose:
        print("Merging data sources...")
    merged_df = create_master_dataset(
        gridbeyond_df,
        scada_df_resampled,
        output_path=output_path
    )

    report = generate_quality_report(
        gridbeyond_df=gridbeyond_df,
        scada_df_original=scada_df_original,
        scada_df_resampled=scada_df_resampled,
        merged_df=merged_df,
        gridbeyond_file=gridbeyond_file,
        scada_file=scada_file
    )

    return merged_df, report


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process BESS data files")
    parser.add_argument("input_folder", help="Folder containing raw Excel files")
    parser.add_argument("-o", "--output", help="Output folder for processed CSV", default="data")
    parser.add_argument("-m", "--month", help="Month name for output filename")
    parser.add_argument("-y", "--year", help="Year for output filename")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output")

    args = parser.parse_args()

    try:
        merged_df, report = process_monthly_data(
            input_folder=args.input_folder,
            output_folder=args.output,
            month=args.month,
            year=args.year,
            verbose=not args.quiet
        )

        print("\n" + report.summary_text())

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
