#!/usr/bin/env python3
"""Parse the raw Fama-French 3-factor CSV (KEN FRENCH DATA LIBRARY) into a
clean, machine-readable file for offline use by the Dartboard engine.

Pure stdlib (no pandas/numpy) so it runs in any environment.

Input : /tmp/ff3/F-F_Research_Data_Factors.csv  (header row = ',Mkt-RF,SMB,HML,RF')
Output: data/ff3_monthly.csv  columns: Date,Mkt-RF,SMB,HML,RF
        Values are PERCENTAGES as published by French (e.g. 2.89 == 2.89%).
        The engine MUST convert to decimals (divide by 100) before use.

Source: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/
        F-F_Research_Data_Factors_CSV.zip  (created from 202605 CRSP database)
"""
import csv
import os

RAW = "/tmp/ff3/F-F_Research_Data_Factors.csv"
OUT = os.path.join(os.path.dirname(__file__), "data", "ff3_monthly.csv")


def main():
    rows = []
    with open(RAW, encoding="latin-1") as f:
        # Find the header line containing the factor names
        for line in f:
            if line.strip().startswith(",") and "Mkt-RF" in line:
                break
        reader = csv.reader(f)
        for parts in reader:
            if not parts:
                continue
            date = parts[0].strip()
            if not (date.isdigit() and len(date) == 6):
                continue
            try:
                mkt = float(parts[1])
                smb = float(parts[2])
                hml = float(parts[3])
                rf = float(parts[4])
            except (ValueError, IndexError):
                continue
            rows.append((int(date), mkt, smb, hml, rf))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Mkt-RF", "SMB", "HML", "RF"])
        w.writerows(rows)

    print(f"Wrote {len(rows)} rows to {os.path.normpath(OUT)}")
    print("Range:", rows[0][0], "-", rows[-1][0])


if __name__ == "__main__":
    main()
