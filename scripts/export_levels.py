#!/usr/bin/env python3
"""Download the full Lopcombe Corner level history from the EA Hydrology API to CSV.

Writes
  data/levels/<station>_dipped.csv        every manual dip (1963 onwards)
  data/levels/<station>_logged_daily.csv  logger reading at 09:00 each day (1999 onwards)

Dips that disagree with the logger by more than --max-discrepancy (e.g. the
spurious 105.08 m dip of 15 May 2025) are dropped and listed.

Run from the repo root:
    python scripts/export_levels.py
Requires: requests, pandas (as for run.py)
"""
import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from gwl import api, analysis  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--station", default="E14150")
    ap.add_argument("--outdir", default=os.path.join(REPO, "data", "levels"))
    ap.add_argument("--max-discrepancy", type=float, default=5.0)
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    client = api.HydrologyClient()
    station = client.get_station(args.station)
    print(f"Station: {station.get('label', args.station)} ({args.station})")
    split = analysis.classify_measures(client.get_measures(station["notation"]))

    print("Fetching manual dips...")
    dipped = analysis.fetch_series(client, split["dipped"])
    print("Fetching logger readings at 09:00 each day...")
    logged = analysis.fetch_series(client, split["logged"], time="09:00:00")

    dipped, bad = analysis.detect_discrepant_readings(dipped, logged, max_diff=args.max_discrepancy)
    for _, r in bad.iterrows():
        print(f"  dropped dip {r['dateTime']:%Y-%m-%d}: {r['value']:.2f} m vs logger ~{r['reference_value']:.2f} m")

    for name, df in (("dipped", dipped), ("logged_daily", logged)):
        path = os.path.join(args.outdir, f"{args.station}_{name}.csv")
        df[["dateTime", "value", "quality"]].to_csv(path, index=False)
        if df.empty:
            print(f"  {name}: no readings")
        else:
            print(f"  {name}: {len(df)} readings, {df.dateTime.min():%Y-%m-%d} to "
                  f"{df.dateTime.max():%Y-%m-%d}, max {df.value.max():.2f} m -> {path}")
    print("Data: Environment Agency Hydrology API, Open Government Licence v3.0.")


if __name__ == "__main__":
    main()
