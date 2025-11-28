"""
Data Quality Dashboard Page

Provides interface for importing raw data and viewing data quality reports.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_cleaning import (
    find_files,
    load_gridbeyond,
    load_scada,
    resample_scada,
    calculate_missing_soc,
    merge_data,
    align_timestamps,
    generate_quality_report,
    DataQualityReport
)


def show_data_quality_page():
    """Display the data quality and import page."""
    st.title("📥 Data Import & Quality")
    st.markdown("Import raw data files and review data quality metrics")

    # Create tabs for different functionality
    tab1, tab2, tab3 = st.tabs(["📂 Import Data", "📊 Quality Report", "🔍 Data Preview"])

    with tab1:
        show_import_section()

    with tab2:
        show_quality_report_section()

    with tab3:
        show_data_preview_section()


def show_import_section():
    """Show the data import interface."""
    st.header("Import Raw Data Files")

    st.markdown("""
    Upload GridBeyond and SCADA Excel files to process and merge them into a unified dataset.

    **Expected file formats:**
    - **GridBeyond**: `Northwold_{Month}_{Year}.xlsx` - Contains market prices, revenues, ancillary services
    - **SCADA**: `export-*.xlsx` - Contains physical battery data (SOC, Power, Frequency)
    """)

    # File upload option
    st.subheader("Option 1: Upload Files")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**GridBeyond File**")
        gridbeyond_file = st.file_uploader(
            "Upload GridBeyond Excel file",
            type=['xlsx', 'xls'],
            key='gridbeyond_upload'
        )

    with col2:
        st.markdown("**SCADA File**")
        scada_file = st.file_uploader(
            "Upload SCADA Excel file",
            type=['xlsx', 'xls'],
            key='scada_upload'
        )

    # Or folder path option
    st.subheader("Option 2: Specify Folder Path")

    folder_path = st.text_input(
        "Enter path to folder containing raw files",
        placeholder="e.g., C:/repos/bess-dashboard/raw/october2025"
    )

    # Process button
    st.markdown("---")

    if st.button("🔄 Process Data", type="primary"):
        process_data(gridbeyond_file, scada_file, folder_path)


def process_data(gridbeyond_file, scada_file, folder_path):
    """Process uploaded or specified data files."""

    # Determine source of files
    if gridbeyond_file is not None and scada_file is not None:
        # Process uploaded files
        with st.spinner("Processing uploaded files..."):
            try:
                gridbeyond_df = pd.read_excel(gridbeyond_file)
                scada_df = pd.read_excel(scada_file)

                # Parse timestamps
                gridbeyond_df = _parse_gridbeyond(gridbeyond_df)
                scada_df = _parse_scada(scada_df)

                # Store in session state
                st.session_state['raw_gridbeyond'] = gridbeyond_df
                st.session_state['raw_scada'] = scada_df

                # Process pipeline
                _run_processing_pipeline()

                st.success("Files processed successfully!")

            except Exception as e:
                st.error(f"Error processing files: {str(e)}")

    elif folder_path:
        # Process files from folder
        with st.spinner(f"Processing files from {folder_path}..."):
            try:
                files = find_files(folder_path)

                if not files['gridbeyond']:
                    st.error("No GridBeyond file found in folder")
                    return
                if not files['scada']:
                    st.error("No SCADA file found in folder")
                    return

                # Load files
                gridbeyond_df = load_gridbeyond(files['gridbeyond'])
                scada_df = load_scada(files['scada'], convert_power_to_mw=True)

                # Store file paths
                st.session_state['gridbeyond_file'] = files['gridbeyond']
                st.session_state['scada_file'] = files['scada']

                # Store raw data
                st.session_state['raw_gridbeyond'] = gridbeyond_df
                st.session_state['raw_scada'] = scada_df

                # Process pipeline
                _run_processing_pipeline()

                st.success("Files processed successfully!")

            except FileNotFoundError as e:
                st.error(f"Folder not found: {str(e)}")
            except Exception as e:
                st.error(f"Error processing files: {str(e)}")
    else:
        st.warning("Please upload files or specify a folder path")


def _parse_gridbeyond(df):
    """Parse GridBeyond dataframe."""
    # Find timestamp column
    timestamp_col = None
    for col in df.columns:
        if 'timestamp' in col.lower():
            timestamp_col = col
            break

    if timestamp_col:
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])
        df = df.rename(columns={timestamp_col: 'Timestamp'})
        df = df.set_index('Timestamp')

    return df


def _parse_scada(df):
    """Parse SCADA dataframe."""
    # Find date column
    date_col = None
    for col in df.columns:
        if 'date' in col.lower():
            date_col = col
            break

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], format='%d/%m/%Y %H:%M:%S')
        df = df.rename(columns={date_col: 'Timestamp'})
        df = df.set_index('Timestamp')

    # Convert power to MW
    if 'Power' in df.columns:
        df['Power_MW'] = df['Power'] / 1000.0
        df = df.drop(columns=['Power'])

    # Drop empty Availability column
    if 'Availability' in df.columns and df['Availability'].isna().all():
        df = df.drop(columns=['Availability'])

    return df


def _run_processing_pipeline():
    """Run the data processing pipeline."""

    gridbeyond_df = st.session_state.get('raw_gridbeyond')
    scada_df = st.session_state.get('raw_scada')

    if gridbeyond_df is None or scada_df is None:
        return

    # Resample SCADA
    scada_resampled = resample_scada(scada_df, target_freq='30min')
    st.session_state['scada_resampled'] = scada_resampled

    # Calculate missing SOC
    if 'SOC' in scada_resampled.columns and 'Power_MW' in scada_resampled.columns:
        scada_resampled = calculate_missing_soc(
            scada_resampled,
            power_col='Power_MW',
            soc_col='SOC',
            dt_hours=0.5
        )
        st.session_state['scada_resampled'] = scada_resampled

    # Align and merge
    gb_aligned, scada_aligned = align_timestamps(gridbeyond_df, scada_resampled)
    merged_df = merge_data(gb_aligned, scada_aligned)

    st.session_state['merged_df'] = merged_df
    st.session_state['gb_aligned'] = gb_aligned
    st.session_state['scada_aligned'] = scada_aligned

    # Generate quality report
    report = generate_quality_report(
        gridbeyond_df=gridbeyond_df,
        scada_df_original=scada_df,
        scada_df_resampled=scada_resampled,
        merged_df=merged_df,
        gridbeyond_file=st.session_state.get('gridbeyond_file', 'Uploaded'),
        scada_file=st.session_state.get('scada_file', 'Uploaded')
    )

    st.session_state['quality_report'] = report


def show_quality_report_section():
    """Show the data quality report."""
    st.header("Data Quality Report")

    report = st.session_state.get('quality_report')

    if report is None:
        st.info("No data has been processed yet. Go to 'Import Data' tab to load files.")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("GridBeyond Rows", f"{report.gridbeyond_rows:,}")
    with col2:
        st.metric("SCADA Rows (Original)", f"{report.scada_rows_original:,}")
    with col3:
        st.metric("SCADA Rows (Resampled)", f"{report.scada_rows_resampled:,}")
    with col4:
        st.metric("Merged Rows", f"{report.merged_rows:,}")

    st.markdown("---")

    # Date ranges
    st.subheader("Date Ranges")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**GridBeyond**")
        if report.gridbeyond_start:
            st.write(f"Start: {report.gridbeyond_start.strftime('%Y-%m-%d %H:%M')}")
            st.write(f"End: {report.gridbeyond_end.strftime('%Y-%m-%d %H:%M')}")

    with col2:
        st.markdown("**SCADA**")
        if report.scada_start:
            st.write(f"Start: {report.scada_start.strftime('%Y-%m-%d %H:%M')}")
            st.write(f"End: {report.scada_end.strftime('%Y-%m-%d %H:%M')}")

    st.markdown("---")

    # Overlap statistics
    st.subheader("Timestamp Overlap")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Common Timestamps", f"{report.common_timestamps:,}")
    with col2:
        st.metric("Only in GridBeyond", f"{report.only_gridbeyond:,}")
    with col3:
        st.metric("Only in SCADA", f"{report.only_scada:,}")

    # Overlap bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=['Common', 'GridBeyond Only', 'SCADA Only'],
            y=[report.common_timestamps, report.only_gridbeyond, report.only_scada],
            marker_color=['green', 'blue', 'orange']
        )
    ])
    fig.update_layout(
        title="Timestamp Distribution",
        xaxis_title="Category",
        yaxis_title="Count",
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Missing values
    st.subheader("Missing Values")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**GridBeyond Missing Values**")
        gb_missing = {k: v for k, v in report.gridbeyond_missing.items() if v > 0}
        if gb_missing:
            missing_df = pd.DataFrame({
                'Column': list(gb_missing.keys()),
                'Missing Count': list(gb_missing.values()),
                'Missing %': [v / report.gridbeyond_rows * 100 for v in gb_missing.values()]
            })
            missing_df = missing_df.sort_values('Missing Count', ascending=False)
            st.dataframe(missing_df, use_container_width=True, hide_index=True)
        else:
            st.success("No missing values!")

    with col2:
        st.markdown("**SCADA Missing Values**")
        scada_missing = {k: v for k, v in report.scada_missing.items() if v > 0}
        if scada_missing:
            missing_df = pd.DataFrame({
                'Column': list(scada_missing.keys()),
                'Missing Count': list(scada_missing.values()),
                'Missing %': [v / report.scada_rows_original * 100 for v in scada_missing.values()]
            })
            missing_df = missing_df.sort_values('Missing Count', ascending=False)
            st.dataframe(missing_df, use_container_width=True, hide_index=True)
        else:
            st.success("No missing values!")

    st.markdown("---")

    # Data quality issues
    st.subheader("Data Quality Checks")

    col1, col2, col3 = st.columns(3)

    with col1:
        if report.soc_below_0 > 0:
            st.error(f"SOC < 0%: {report.soc_below_0}")
        else:
            st.success("SOC < 0%: None")

    with col2:
        if report.soc_above_100 > 0:
            st.error(f"SOC > 100%: {report.soc_above_100}")
        else:
            st.success("SOC > 100%: None")

    with col3:
        st.info(f"SOC Calculated: {report.soc_calculated_count}")

    st.markdown("---")

    # Warnings and errors
    if report.warnings:
        st.subheader("Warnings")
        for warning in report.warnings:
            st.warning(warning)

    if report.errors:
        st.subheader("Errors")
        for error in report.errors:
            st.error(error)

    # Export options
    st.markdown("---")
    st.subheader("Export")

    col1, col2 = st.columns(2)

    with col1:
        merged_df = st.session_state.get('merged_df')
        if merged_df is not None:
            csv = merged_df.to_csv()
            st.download_button(
                label="📥 Download Merged CSV",
                data=csv,
                file_name="merged_bess_data.csv",
                mime="text/csv"
            )

    with col2:
        if report:
            report_text = report.summary_text()
            st.download_button(
                label="📥 Download Quality Report",
                data=report_text,
                file_name="data_quality_report.txt",
                mime="text/plain"
            )


def show_data_preview_section():
    """Show preview of loaded data."""
    st.header("Data Preview")

    # GridBeyond preview
    st.subheader("GridBeyond Data")
    gridbeyond_df = st.session_state.get('raw_gridbeyond')

    if gridbeyond_df is not None:
        st.write(f"Shape: {gridbeyond_df.shape[0]:,} rows × {gridbeyond_df.shape[1]} columns")

        # Column selector
        all_cols = gridbeyond_df.columns.tolist()
        selected_cols = st.multiselect(
            "Select columns to display",
            options=all_cols,
            default=all_cols[:5] if len(all_cols) > 5 else all_cols,
            key='gb_cols'
        )

        if selected_cols:
            st.dataframe(gridbeyond_df[selected_cols].head(50), use_container_width=True)
    else:
        st.info("No GridBeyond data loaded")

    st.markdown("---")

    # SCADA preview
    st.subheader("SCADA Data (Original 10-min)")
    scada_df = st.session_state.get('raw_scada')

    if scada_df is not None:
        st.write(f"Shape: {scada_df.shape[0]:,} rows × {scada_df.shape[1]} columns")
        st.dataframe(scada_df.head(50), use_container_width=True)
    else:
        st.info("No SCADA data loaded")

    st.markdown("---")

    # Resampled SCADA preview
    st.subheader("SCADA Data (Resampled 30-min)")
    scada_resampled = st.session_state.get('scada_resampled')

    if scada_resampled is not None:
        st.write(f"Shape: {scada_resampled.shape[0]:,} rows × {scada_resampled.shape[1]} columns")
        st.dataframe(scada_resampled.head(50), use_container_width=True)
    else:
        st.info("No resampled SCADA data available")

    st.markdown("---")

    # Merged data preview
    st.subheader("Merged Data")
    merged_df = st.session_state.get('merged_df')

    if merged_df is not None:
        st.write(f"Shape: {merged_df.shape[0]:,} rows × {merged_df.shape[1]} columns")

        # Column selector for merged
        all_cols = merged_df.columns.tolist()
        selected_cols = st.multiselect(
            "Select columns to display",
            options=all_cols,
            default=all_cols[:8] if len(all_cols) > 8 else all_cols,
            key='merged_cols'
        )

        if selected_cols:
            st.dataframe(merged_df[selected_cols].head(50), use_container_width=True)
    else:
        st.info("No merged data available")
