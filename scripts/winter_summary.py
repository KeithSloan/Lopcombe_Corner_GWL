#!/usr/bin/env python3
"""Per-winter summary of Lopcombe Corner levels from the full EA record.

For each winter (1 October to 31 May) writes the peak level and date, the level
on 1 October (start of winter, interpolated) and the autumn low (lowest reading
1 September - 30 November). This replaces the hand-transcribed peak tables used
in earlier analyses.

Inputs   data/levels/E14150_dipped.csv, data/levels/E14150_logged_daily.csv  (export_levels.py)
Output   output/levels/winter_summary.csv

Usage:
    python scripts/winter_summary.py
Requires: numpy, pandas
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flood_probability import load_levels, level_at  # noqa: E402

THRESHOLD = 97.0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dipped", default="data/levels/E14150_dipped.csv")
    ap.add_argument("--logged", default="data/levels/E14150_logged_daily.csv")
    ap.add_argument("--out", default="output/levels/winter_summary.csv")
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    s = load_levels(args.dipped, args.logged)
    last = s.dateTime.max()
    rows = []
    for y in range(s.dateTime.min().year + 1, last.year + 1):
        start, end = pd.Timestamp(f"{y - 1}-10-01"), pd.Timestamp(f"{y}-05-31 23:59")
        if end > last:
            continue
        w = s[(s.dateTime >= start) & (s.dateTime <= end)]
        if len(w) < 6:
            continue
        i = w.value.idxmax()
        aut = s[(s.dateTime >= f"{y - 1}-09-01") & (s.dateTime <= f"{y - 1}-11-30 23:59")]
        logger_share = (w.source == "logger").mean()
        rows.append(dict(
            winter_end_year=y, winter=f"{y - 1}/{str(y)[2:]}",
            peak_mAOD=round(float(w.value[i]), 3), peak_date=w.dateTime[i].strftime("%Y-%m-%d"),
            peak_source=w.source[i], start_level_1oct=round(level_at(s, start), 3),
            autumn_low=round(float(aut.value.min()), 3) if len(aut) else np.nan,
            n_readings=len(w), main_source="logger" if logger_share > 0.5 else "dip",
            reached_threshold=int(w.value[i] >= THRESHOLD)))
    df = pd.DataFrame(rows)
    df.to_csv(args.out, index=False)
    print(f"{len(df)} winters {df.winter.iloc[0]}-{df.winter.iloc[-1]} -> {args.out}; "
          f"{df.reached_threshold.sum()} reached {THRESHOLD:g} m")


if __name__ == "__main__":
    main()
