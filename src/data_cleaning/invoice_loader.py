"""
Invoice Data Loader Module

Handles loading and parsing invoice-related data from multiple sources:
- EMR Capacity Market CSVs and TXT files
- GridBeyond Summary Statements
- Hartree Partner Readings (BESS and PV)
- Solar Generation Allocated Quantities
- SCADA Monitoring data
- PDF invoice extraction via pdfplumber
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, Dict, List
import re
import glob


# ─────────────────────────────────────────────────────────────
# 1. EMR Capacity Market
# ─────────────────────────────────────────────────────────────

def load_emr_capacity_market(raw_dir: str) -> pd.DataFrame:
    """
    Load EMR Capacity Market invoices from T062 CSV files.

    Args:
        raw_dir: Path to raw/New/ directory

    Returns:
        DataFrame with columns: invoice_number, invoice_date, payment_date,
        invoice_total, cm_month, capacity_obligation, capacity_price,
        weighting_factor, payment_due, payment_payable, source_file
    """
    raw_path = Path(raw_dir)
    csv_files = sorted(raw_path.glob("NORTHWO_*_T062.csv"))

    if not csv_files:
        return pd.DataFrame()

    records = []
    for f in csv_files:
        # Row 0 = field codes (J1889, etc.), Row 1 = human headers, Row 2+ = data
        df = pd.read_csv(f, skiprows=1)

        for _, row in df.iterrows():
            records.append({
                'invoice_number': int(row.get('EMR Invoice Number', 0)),
                'invoice_date': pd.to_datetime(str(int(row.get('EMR Invoice Date', 0))), format='%Y%m%d', errors='coerce'),
                'payment_date': pd.to_datetime(str(int(row.get('EMR Invoice Payment Date', 0))), format='%Y%m%d', errors='coerce'),
                'invoice_total': float(row.get('EMR Invoice Total', 0)),
                'cm_month': str(row.get('CM Month Id', '')),
                'capacity_agreement': str(row.get('Capacity Agreement', '')),
                'capacity_obligation': float(row.get('Auction Acquired Capacity Obligation', 0)),
                'capacity_price': float(row.get('Capacity Price', 0)),
                'cleared_price': float(row.get('Capacity Cleared Price', 0)),
                'cm_base_cpi': float(row.get('CM Base CPI', 0)),
                'cm_cpi': float(row.get('CM CPI', 0)),
                'weighting_factor': float(row.get('CM Monthly Weighting Factor', 0)),
                'payment_due': float(row.get('Monthly Capacity Payment Due', 0)),
                'payment_payable': float(row.get('Monthly Capacity Payment Payable', 0)),
                'suspension_flag': str(row.get('Capacity Payment Suspension Flag', '')),
                'source_file': f.name,
            })

    result = pd.DataFrame(records)

    # Parse cm_month into a proper label (e.g., "202510" -> "October 2025")
    if not result.empty:
        result['cm_month_label'] = result['cm_month'].apply(_parse_cm_month)
        result = result.sort_values('invoice_date').reset_index(drop=True)

    return result


def load_emr_txt_files(raw_dir: str) -> pd.DataFrame:
    """
    Load EMR data from pipe-delimited TXT files for cross-validation.

    Args:
        raw_dir: Path to raw/New/ directory

    Returns:
        DataFrame with invoice_number, invoice_date, payment_date, invoice_total
    """
    raw_path = Path(raw_dir)
    txt_files = sorted(raw_path.glob("NORTHWO_*_*.txt"))

    records = []
    for f in txt_files:
        with open(f, 'r') as fh:
            for line in fh:
                parts = line.strip().split('|')
                if parts and parts[0] == '93I':
                    # 93I|NORTHWO|invoice_num|date|payment_date|total|
                    records.append({
                        'invoice_number': int(parts[2]),
                        'invoice_date': pd.to_datetime(parts[3], format='%Y%m%d', errors='coerce'),
                        'payment_date': pd.to_datetime(parts[4], format='%Y%m%d', errors='coerce'),
                        'invoice_total': float(parts[5]),
                        'source_file': f.name,
                    })

    return pd.DataFrame(records) if records else pd.DataFrame()


# ─────────────────────────────────────────────────────────────
# 2. Summary Statement (GridBeyond Monthly)
# ─────────────────────────────────────────────────────────────

def load_summary_statement(filepath: str) -> Optional[Dict]:
    """
    Load GridBeyond Summary Statement Excel file.

    Parses the positional layout of Summary sheet and standard Detail sheet.

    Args:
        filepath: Path to the Summary Statement Excel file

    Returns:
        Dict with keys: 'summary' (revenue dict), 'detail' (DataFrame),
        'commentary' (str), 'period' (dict with from/to dates)
        Returns None if file not found.
    """
    path = Path(filepath)
    if not path.exists():
        return None

    # --- Summary sheet (positional parsing) ---
    summary_raw = pd.read_excel(filepath, sheet_name='Summary', header=None)

    energy_revenue = {}
    ancillary_revenue = {}
    commentary = ''
    period = {}

    for i in range(len(summary_raw)):
        row = summary_raw.iloc[i]

        # Period dates (col 3 = label, col 4 = value)
        if pd.notna(row.get(3)) and str(row.get(3)).strip() == 'From' and pd.notna(row.get(4)):
            period['from'] = pd.to_datetime(row[4])
        if pd.notna(row.get(3)) and str(row.get(3)).strip() == 'To' and pd.notna(row.get(4)):
            period['to'] = pd.to_datetime(row[4])

        # Energy Revenue (col 8 = stream name, col 9 = value)
        if pd.notna(row.get(8)) and pd.notna(row.get(9)):
            label = str(row[8]).strip()
            value = row[9]
            if label not in ('Energy Revenue', 'Total', 'Sub Total') and isinstance(value, (int, float)):
                energy_revenue[label] = float(value)
            elif label == 'Total':
                energy_revenue['_total'] = float(value)
            elif label == 'Sub Total':
                energy_revenue['_sub_total'] = float(value)

        # Ancillary Revenue (col 10 = stream name, col 11 = value)
        if pd.notna(row.get(10)) and pd.notna(row.get(11)):
            label = str(row[10]).strip()
            value = row[11]
            if label not in ('Ancillary Revenue', 'Total') and isinstance(value, (int, float)):
                ancillary_revenue[label] = float(value)
            elif label == 'Total':
                ancillary_revenue['_total'] = float(value)

        # Market Commentary (col 13)
        if pd.notna(row.get(13)):
            commentary = str(row[13]).strip()

    # Net 93% label detected from row 1
    summary = {
        'energy_revenue': energy_revenue,
        'ancillary_revenue': ancillary_revenue,
        'net_percentage': 0.93,
    }

    # --- Detail sheet (standard half-hourly) ---
    detail = pd.read_excel(filepath, sheet_name='Detail')
    if 'Timestamp' in detail.columns:
        detail['Timestamp'] = pd.to_datetime(detail['Timestamp'])

    return {
        'summary': summary,
        'detail': detail,
        'commentary': commentary,
        'period': period,
    }


# ─────────────────────────────────────────────────────────────
# 3. Hartree Readings
# ─────────────────────────────────────────────────────────────

def load_hartree_bess_readings(raw_dir: str) -> pd.DataFrame:
    """
    Load Hartree Partners BESS import/export readings from OneDrive folders.

    Args:
        raw_dir: Path to raw/New/ directory

    Returns:
        DataFrame with Timestamp index, BESS_Import_kWh, BESS_Export_kWh columns
    """
    raw_path = Path(raw_dir)
    bess_files = []

    # Search in OneDrive subfolders and root
    for pattern in ['OneDrive_*/*BESS*Readings.xlsx', '*BESS*Readings.xlsx']:
        bess_files.extend(raw_path.glob(pattern))

    if not bess_files:
        return pd.DataFrame()

    dfs = []
    for f in bess_files:
        try:
            df = pd.read_excel(f)
            # Keep only Date, BESS IMPORT, BESS EXPORT
            df = df[['Date', 'BESS IMPORT', 'BESS EXPORT']].copy()
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.rename(columns={
                'Date': 'Timestamp',
                'BESS IMPORT': 'BESS_Import_kWh',
                'BESS EXPORT': 'BESS_Export_kWh',
            })
            df = df.set_index('Timestamp').sort_index()
            dfs.append(df)
        except Exception:
            continue

    if not dfs:
        return pd.DataFrame()

    # Combine and deduplicate
    combined = pd.concat(dfs)
    combined = combined[~combined.index.duplicated(keep='first')]
    return combined.sort_index()


def load_hartree_pv_readings(raw_dir: str) -> pd.DataFrame:
    """
    Load Hartree Partners PV generation pivot table data.

    Parses the pivot summary (cols 4-9) from PV readings files showing
    monthly generation totals and under/over invoiced amounts.

    Args:
        raw_dir: Path to raw/New/ directory

    Returns:
        DataFrame with columns: month, generation_kwh, invoiced_sin2_01_02,
        invoiced_sin2_03, under_over_invoiced_kwh
    """
    raw_path = Path(raw_dir)
    pv_files = []

    for pattern in ['OneDrive_*/*PV*Readings.xlsx']:
        pv_files.extend(raw_path.glob(pattern))

    if not pv_files:
        return pd.DataFrame()

    # Use first PV readings file with pivot data
    for f in pv_files:
        try:
            df = pd.read_excel(f, sheet_name='Sheet3', header=None)
        except Exception:
            try:
                df = pd.read_excel(f, header=None)
            except Exception:
                continue

        # Find the pivot table rows: look for month names in col 4
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        records = []
        for i in range(len(df)):
            row = df.iloc[i]
            if pd.notna(row.get(4)) and str(row[4]).strip() in month_names:
                record = {
                    'month': str(row[4]).strip(),
                    'generation_kwh': float(row[5]) if pd.notna(row.get(5)) else 0,
                    'invoiced_sin2_01_02': float(row[7]) if pd.notna(row.get(7)) else 0,
                    'invoiced_sin2_03': float(row[8]) if pd.notna(row.get(8)) else 0,
                    'under_over_invoiced_kwh': float(row[9]) if pd.notna(row.get(9)) else 0,
                }
                records.append(record)
            elif pd.notna(row.get(4)) and str(row[4]).strip() == 'Grand Total':
                records.append({
                    'month': 'Grand Total',
                    'generation_kwh': float(row[5]) if pd.notna(row.get(5)) else 0,
                    'invoiced_sin2_01_02': float(row[7]) if pd.notna(row.get(7)) else 0,
                    'invoiced_sin2_03': float(row[8]) if pd.notna(row.get(8)) else 0,
                    'under_over_invoiced_kwh': float(row[9]) if pd.notna(row.get(9)) else 0,
                })

        if records:
            return pd.DataFrame(records)

    return pd.DataFrame()


# ─────────────────────────────────────────────────────────────
# 4. Solar Generation Allocated Quantity
# ─────────────────────────────────────────────────────────────

def load_solar_generation(raw_dir: str) -> pd.DataFrame:
    """
    Load Solar Generation Allocated Quantity files.

    Args:
        raw_dir: Path to raw/New/ directory

    Returns:
        DataFrame with Timestamp index and Allocated_Quantity_kWh column
    """
    raw_path = Path(raw_dir)
    files = sorted(raw_path.glob("Northwold Solar Generation*.xlsx"))

    if not files:
        return pd.DataFrame()

    dfs = []
    for f in files:
        try:
            df = pd.read_excel(f)
            # Find datetime and quantity columns
            date_col = [c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()]
            qty_col = [c for c in df.columns if 'allocated' in c.lower() or 'quantity' in c.lower()]

            if date_col and qty_col:
                df = df[[date_col[0], qty_col[0]]].copy()
                df.columns = ['Timestamp', 'Allocated_Quantity_kWh']
                df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                df = df.set_index('Timestamp').sort_index()
                dfs.append(df)
        except Exception:
            continue

    if not dfs:
        return pd.DataFrame()

    combined = pd.concat(dfs)
    combined = combined[~combined.index.duplicated(keep='first')]
    return combined.sort_index()


# ─────────────────────────────────────────────────────────────
# 5. SCADA Monitoring (10-minute data)
# ─────────────────────────────────────────────────────────────

def load_scada_monitoring(raw_dir: str) -> pd.DataFrame:
    """
    Load SCADA monitoring files (10-minute BESS data).

    These files follow the pattern: {month}-{yy}-{timestamp}.xlsx
    with sheet name 'msrc10m'.

    Args:
        raw_dir: Path to raw/New/ directory

    Returns:
        DataFrame with Timestamp index and columns: Daily_Export_kWh,
        Daily_Import_kWh, Power_kW, RTE, SOH, Daily_Cycles, Availability
    """
    raw_path = Path(raw_dir)
    month_pattern = re.compile(r'^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)-\d{2}-', re.IGNORECASE)
    files = [f for f in raw_path.glob("*.xlsx") if month_pattern.match(f.name)]

    if not files:
        return pd.DataFrame()

    dfs = []
    for f in sorted(files):
        try:
            df = pd.read_excel(f, sheet_name='msrc10m')

            # Strip [Northwold] suffix from column names
            df.columns = [
                col.replace(' [Northwold]', '').strip() if '[Northwold]' in str(col) else col
                for col in df.columns
            ]

            # Find and parse timestamp
            ts_col = [c for c in df.columns if 'timestamp' in c.lower()]
            if not ts_col:
                continue
            df[ts_col[0]] = pd.to_datetime(df[ts_col[0]])
            df = df.rename(columns={ts_col[0]: 'Timestamp'})
            df = df.set_index('Timestamp').sort_index()

            # Rename columns to standard names
            column_map = {
                'BESS Exported Energy Site (daily) (kWh)': 'Daily_Export_kWh',
                'BESS Imported Energy Site (daily) (kWh)': 'Daily_Import_kWh',
                'Batteries Power Output Inverters AC (kW)': 'Power_kW',
                'BESS Cumulative Round Trip Efficiency (POC) (%)': 'RTE',
                'BESS State Of Health (%)': 'SOH',
                'Batteries Total Cycles (-)': 'Daily_Cycles',
                'Batteries Total Cycles (to date) (-)': 'Cumulative_Cycles',
                'BESS Site batteries availability (%)': 'Battery_Availability',
                'BESS Site inverters availability (%)': 'Inverter_Availability',
            }
            df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})
            dfs.append(df)
        except Exception:
            continue

    if not dfs:
        return pd.DataFrame()

    combined = pd.concat(dfs)
    combined = combined[~combined.index.duplicated(keep='first')]
    return combined.sort_index()


# ─────────────────────────────────────────────────────────────
# 6. PDF Invoice Extraction
# ─────────────────────────────────────────────────────────────

def extract_pdf_invoice(filepath: str) -> Optional[Dict]:
    """
    Extract invoice data from a PDF file using pdfplumber.

    Args:
        filepath: Path to PDF file

    Returns:
        Dict with invoice_number, date, total, type, line_items, raw_text, source_file
        Returns None if extraction fails.
    """
    try:
        import pdfplumber
    except ImportError:
        return None

    path = Path(filepath)
    if not path.exists():
        return None

    try:
        with pdfplumber.open(str(path)) as pdf:
            full_text = ''
            tables = []
            for page in pdf.pages:
                text = page.extract_text() or ''
                full_text += text + '\n'
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
    except Exception:
        return None

    # Classify PDF type from filename
    fname = path.name.upper()
    fname_spaced = fname.replace('_', ' ')
    if 'GRIDBEYOND' in fname_spaced or 'GRID BEYOND' in fname_spaced:
        pdf_type = 'GridBeyond'
    elif 'BESS' in fname_spaced and ('HARTREE' in fname_spaced or fname.startswith('NWOSFL')):
        pdf_type = 'Hartree BESS'
    elif 'PV' in fname_spaced and ('HARTREE' in fname_spaced or fname.startswith('NWOSFL')):
        pdf_type = 'Hartree PV'
    elif 'POW' in fname_spaced and fname.startswith('NWOSFL'):
        # Power invoices (BESS_POW, Solar_POW, Aux_POW)
        if 'SOLAR' in fname_spaced:
            pdf_type = 'Hartree Solar Power'
        elif 'AUX' in fname_spaced:
            pdf_type = 'Hartree Auxiliary'
        else:
            pdf_type = 'Hartree BESS Power'
    elif fname.startswith('NORTHWO') and fname.endswith('.PDF'):
        pdf_type = 'EMR'
    elif 'HARTREE' in fname_spaced or fname.startswith('NWOSFL'):
        pdf_type = 'Hartree Other'
    else:
        pdf_type = 'Unknown'

    # Extract invoice number
    invoice_number = None
    patterns = [
        r'Invoice\s+(?:No|Number|Ref)[.:\s]*(\S+)',
        r'Inv[.\s]*(?:No|#)[.:\s]*(\S+)',
        r'Reference[:\s]*(\d+)',
    ]
    for pat in patterns:
        m = re.search(pat, full_text, re.IGNORECASE)
        if m:
            invoice_number = m.group(1)
            break

    # Extract date
    invoice_date = None
    date_patterns = [
        r'(?:Invoice\s+)?Date[:\s]*(\d{1,2}[\s/.-]\w{3,9}[\s/.-]\d{2,4})',
        r'(?:Invoice\s+)?Date[:\s]*(\d{1,2}/\d{1,2}/\d{2,4})',
        r'(?:Invoice\s+)?Date[:\s]*(\d{4}-\d{2}-\d{2})',
    ]
    for pat in date_patterns:
        m = re.search(pat, full_text, re.IGNORECASE)
        if m:
            try:
                invoice_date = pd.to_datetime(m.group(1), dayfirst=True)
            except Exception:
                pass
            break

    # Extract total amount
    total_amount = None
    amount_patterns = [
        r'(?:Total|Net|Amount\s+Due|Balance\s+Due)[:\s]*[£$]?\s*([\d,]+\.\d{2})',
        r'(?:Total|Net)[:\s]*-?\s*[£$]?\s*([\d,]+\.\d{2})',
        r'[£]([\d,]+\.\d{2})',
    ]
    for pat in amount_patterns:
        m = re.search(pat, full_text, re.IGNORECASE)
        if m:
            total_amount = float(m.group(1).replace(',', ''))
            break

    # Extract line items from tables
    line_items = []
    for table in tables:
        if table and len(table) > 1:
            headers = [str(h).strip() if h else '' for h in table[0]]
            for row in table[1:]:
                item = {}
                for j, cell in enumerate(row):
                    if j < len(headers) and headers[j]:
                        item[headers[j]] = cell
                if item:
                    line_items.append(item)

    return {
        'invoice_number': invoice_number,
        'date': invoice_date,
        'total': total_amount,
        'type': pdf_type,
        'line_items': line_items,
        'raw_text': full_text[:2000],
        'source_file': path.name,
    }


def load_all_pdfs(raw_dir: str) -> pd.DataFrame:
    """
    Scan all PDF files in raw_dir and subdirectories, extract invoice data.

    Args:
        raw_dir: Path to raw/New/ directory

    Returns:
        DataFrame with columns: source_file, type, invoice_number, date, total, raw_text
    """
    raw_path = Path(raw_dir)
    pdf_files = list(raw_path.rglob("*.pdf"))

    if not pdf_files:
        return pd.DataFrame()

    records = []
    for f in sorted(pdf_files):
        result = extract_pdf_invoice(str(f))
        if result:
            records.append({
                'source_file': result['source_file'],
                'subfolder': str(f.parent.relative_to(raw_path)) if f.parent != raw_path else '',
                'type': result['type'],
                'invoice_number': result['invoice_number'],
                'date': result['date'],
                'total': result['total'],
                'raw_text': result['raw_text'],
            })

    return pd.DataFrame(records) if records else pd.DataFrame()


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _parse_cm_month(cm_month_str: str) -> str:
    """Convert CM Month ID (e.g., '202510') to label (e.g., 'October 2025')."""
    try:
        dt = pd.to_datetime(cm_month_str, format='%Y%m')
        return dt.strftime('%B %Y')
    except Exception:
        return str(cm_month_str)


def get_available_invoice_months(raw_dir: str) -> List[str]:
    """
    Detect which months have invoice data available.

    Returns:
        List of month labels (e.g., ['October 2025', 'November 2025', ...])
    """
    emr = load_emr_capacity_market(raw_dir)
    if emr.empty:
        return []
    return sorted(emr['cm_month_label'].unique().tolist())
