import pandas as pd
import numpy as np

# Constants from Northwold Agreement
CAPACITY_MWH = 8.4
WARRANTY_CYCLES_DAILY = 1.5
WARRANTY_DEGRADATION_ANNUAL_PCT = 2.5  # Lower bound of 2.5-3% estimate

# Degradation Factor Calculation
# We assume the 2.5% annual loss is based on fully utilizing the 1.5 cycle warranty every day.
# Annual Max Cycles = 1.5 * 365 = 547.5 cycles
DEGRADATION_PER_CYCLE_PCT = WARRANTY_DEGRADATION_ANNUAL_PCT / (WARRANTY_CYCLES_DAILY * 365)


def calculate_cycles_all_methods(df, power_col, capacity_mwh=CAPACITY_MWH, dt_hours=0.5):
    """
    Calculate battery cycles using three methodologies.

    Args:
        df: DataFrame with power data
        power_col: Column name for power (positive = discharge, negative = charge)
        capacity_mwh: Battery capacity (default 8.4)
        dt_hours: Time step in hours (default 0.5 for 30-min, use 1.0 if already MWh)

    Returns:
        dict with cycles for all three methods
    """
    power = pd.to_numeric(df[power_col], errors='coerce').fillna(0)

    # Convert power (MW) to energy (MWh) for each period
    energy = power * dt_hours

    # Method A: Discharge-only (current method)
    discharge_mwh = energy[energy > 0].sum()
    cycles_discharge = discharge_mwh / capacity_mwh

    # Method B: Full Equivalent Cycles (Industry Standard)
    charge_mwh = abs(energy[energy < 0].sum())
    cycles_full = (discharge_mwh + charge_mwh) / 2 / capacity_mwh

    # Method C: Throughput-based (mathematically same as B)
    total_throughput = discharge_mwh + charge_mwh
    cycles_throughput = total_throughput / (2 * capacity_mwh)

    return {
        'discharge_mwh': discharge_mwh,
        'charge_mwh': charge_mwh,
        'cycles_A_discharge': cycles_discharge,
        'cycles_B_full': cycles_full,
        'cycles_C_throughput': cycles_throughput
    }


def calculate_metrics(master_file='Master_BESS_Analysis_Sept_2025.csv',
                      optimized_file='Optimized_Results.csv'):
    print(f"--- Phase 5: Analyzing Cycles & Degradation ---")
    print(f"\nCycle Calculation Methods:")
    print("  A: Discharge-only = Discharge MWh / Capacity")
    print("  B: Full Equivalent = (Discharge + Charge) / 2 / Capacity  [Industry Standard]")
    print("  C: Throughput = Total Throughput / (2 x Capacity)")

    # Load master file for actual data
    master_df = pd.read_csv(master_file)
    if 'Unnamed: 0' in master_df.columns:
        master_df.rename(columns={'Unnamed: 0': 'Timestamp'}, inplace=True)
    master_df['Timestamp'] = pd.to_datetime(master_df['Timestamp'])
    master_df['Date'] = master_df['Timestamp'].dt.date

    # Load optimized results
    opt_df = pd.read_csv(optimized_file)
    opt_df['Timestamp'] = pd.to_datetime(opt_df['Timestamp'])

    # Merge the datasets
    merged_df = pd.merge(master_df, opt_df, on='Timestamp', how='inner')

    num_days = merged_df['Date'].nunique()
    print(f"\nAnalysis Period: {num_days} days")

    # Find the actual battery power column
    actual_col = None
    is_mwh = False  # Flag to track if column is already in MWh

    # First try to find Battery MWh Output column
    for col in master_df.columns:
        if 'Battery MWh' in col and 'Output' in col:
            actual_col = col
            is_mwh = True
            break

    # Fallback to Physical_Power_MW
    if actual_col is None and 'Physical_Power_MW' in master_df.columns:
        actual_col = 'Physical_Power_MW'
        is_mwh = False

    if actual_col is None:
        print("Warning: Could not find actual battery column")
        return None

    print(f"Using actual column: {actual_col} (is_mwh={is_mwh})")

    # Define scenarios
    scenarios = {
        "Actual (Aggregator)": (actual_col, is_mwh),
        "Optimized (Daily Switching)": ("Optimised_Net_MWh", True)
    }

    # Calculate cycles for each scenario using all methods
    print("\n" + "="*80)
    print("CYCLE METHODOLOGY COMPARISON")
    print("="*80)

    all_results = []

    for name, (col, col_is_mwh) in scenarios.items():
        if col not in merged_df.columns:
            print(f"Warning: Column '{col}' not found, skipping {name}")
            continue

        dt = 1.0 if col_is_mwh else 0.5
        cycles = calculate_cycles_all_methods(merged_df, col, CAPACITY_MWH, dt)

        print(f"\n--- {name} ---")
        print(f"  Discharge Energy: {cycles['discharge_mwh']:.2f} MWh")
        print(f"  Charge Energy:    {cycles['charge_mwh']:.2f} MWh")
        print(f"\n  Method A (Discharge-only):     {cycles['cycles_A_discharge']:.2f} cycles ({cycles['cycles_A_discharge']/num_days:.3f}/day)")
        print(f"  Method B (Full Equivalent):    {cycles['cycles_B_full']:.2f} cycles ({cycles['cycles_B_full']/num_days:.3f}/day) [Industry Std]")
        print(f"  Method C (Throughput):         {cycles['cycles_C_throughput']:.2f} cycles ({cycles['cycles_C_throughput']/num_days:.3f}/day)")

        # Use Industry Standard (Method B) for degradation and warranty check
        total_cycles_b = cycles['cycles_B_full']
        avg_daily_cycles_b = total_cycles_b / num_days
        est_degradation = total_cycles_b * DEGRADATION_PER_CYCLE_PCT

        warranty_status = "OK" if avg_daily_cycles_b <= WARRANTY_CYCLES_DAILY else "WARRANTY VOID"
        print(f"\n  [Using Industry Std Method B]")
        print(f"  Est. Degradation: {est_degradation:.4f}%")
        print(f"  Warranty Status: {warranty_status}")

        # Add all methods to results
        for method, method_name, cycles_val in [
            ('A', 'Discharge-only', cycles['cycles_A_discharge']),
            ('B', 'Full Equivalent (Ind. Std)', cycles['cycles_B_full']),
            ('C', 'Throughput', cycles['cycles_C_throughput'])
        ]:
            daily_avg = cycles_val / num_days
            degradation = cycles_val * DEGRADATION_PER_CYCLE_PCT
            all_results.append({
                "Scenario": name,
                "Method": f"{method}: {method_name}",
                "Total Cycles": round(cycles_val, 2),
                "Avg Cycles/Day": round(daily_avg, 3),
                "Est. Degradation (%)": round(degradation, 4),
                "Warranty Status": "OK" if daily_avg <= WARRANTY_CYCLES_DAILY else "EXCEEDED"
            })

    # Convert to DataFrame for display
    results_df = pd.DataFrame(all_results)

    print("\n" + "="*80)
    print("SUMMARY TABLE (All Methods)")
    print("="*80)
    print(results_df.to_string(index=False))

    # Export
    results_df.to_csv("Northwold_Cycle_Degradation_Report.csv", index=False)
    print("\nReport saved to: Northwold_Cycle_Degradation_Report.csv")

    return results_df


if __name__ == "__main__":
    import os

    # Try to find data files in common locations
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')

    master_file = os.path.join(data_dir, 'Master_BESS_Analysis_Sept_2025.csv')
    opt_file = os.path.join(data_dir, 'Optimized_Results_Sept_2025.csv')

    if os.path.exists(master_file) and os.path.exists(opt_file):
        calculate_metrics(master_file, opt_file)
    else:
        print("Data files not found. Please provide paths to:")
        print("  - Master_BESS_Analysis_*.csv")
        print("  - Optimized_Results_*.csv")