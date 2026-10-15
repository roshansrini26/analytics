import glob
import os
import pandas as pd

# -- SETTINGS --
RAW_DIR = "raw"
OUT_DIR = "cleaned"
SPEED_MAX = 200
ACC_MAX = 20
ACC_COLS = ['acc_x', 'acc_y', 'acc_z']
MAX_FILL = 5




def load_trip(path):
    df = pd.read_excel(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d.%m.%Y %H:%M:%S')
    n_raw = len(df)
    df = df.drop_duplicates().sort_values('timestamp').reset_index(drop=True)
    return df, n_raw - len(df)

def remove_outliers(df):
    speed_out = df['speed_kmh'] > SPEED_MAX
    acc_out = (df['acc_x'].abs() > ACC_MAX) | (df['acc_y'].abs() > ACC_MAX)
    df.loc[speed_out, 'speed_kmh'] = float('nan')
    df.loc[acc_out, ACC_COLS] = float('nan')
    return speed_out.sum(), acc_out.sum()

def fill_short_gaps(df, cols, max_fill=MAX_FILL):
    missing = df[cols[0]].isna()
    run_id = (missing != missing.shift()).cumsum()
    gap_len = missing.groupby(run_id).transform('sum')

    filled = df[cols].interpolate()
    short = missing & (gap_len <= max_fill)
    df.loc[short, cols] = filled.loc[short, cols]

    long_flag = missing & (gap_len > max_fill)
    return short.sum(), long_flag

def clean_trip(path):
    df, n_dupes = load_trip(path)
    n_speed_out, n_acc_out = remove_outliers(df)          # outliers BEFORE filling
    n_acc_filled, _ = fill_short_gaps(df, ACC_COLS)
    n_speed_filled, _ = fill_short_gaps(df, ["speed_kmh"])
    _, gps_flag = fill_short_gaps(df, ["lat", "lon"])
    df["gps_gap_flag"] = gps_flag
 
    report = {
        "file": os.path.basename(path),
        "trip_id": df["trip_id"].iloc[0],
        "user_id": df["user_id"].iloc[0],
        "rows_clean": len(df),
        "duplicates_removed": n_dupes,
        "speed_outliers": n_speed_out,
        "acc_outliers": n_acc_out,
        "acc_values_filled": n_acc_filled,
        "speed_values_filled": n_speed_filled,
        "gps_rows_flagged": gps_flag.sum(),
        "pct_rows_usable": round(100 * (~gps_flag).mean(), 1),
    }
    report["usable_for_ml"] = report["pct_rows_usable"] >= 90
    return df, report

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join(RAW_DIR, "*.xlsx")))
    if not files:
        print(f"No files found in {RAW_DIR}/")
        return
 
    reports = []
    for path in files:
        df, report = clean_trip(path)
        out_path = os.path.join(OUT_DIR, f"{report['trip_id']}_clean.csv")
        df.to_csv(out_path, index=False)
        reports.append(report)
        print(f"✔ {report['file']}: {report['pct_rows_usable']}% usable")
 
    report_df = pd.DataFrame(reports)
    report_df.to_csv(os.path.join(OUT_DIR, "quality_report.csv"), index=False)
    print(f"\nProcessed {len(files)} trips. Report saved to {OUT_DIR}/quality_report.csv")
    print(report_df.to_string(index=False))


if __name__ == "__main__":
    main()
