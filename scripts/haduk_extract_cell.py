#!/usr/bin/env python3
"""Extract monthly HadUK-Grid 1 km rainfall for the Lopcombe Corner borehole cell.

Reads the yearly NetCDF files downloaded by get_haduk_1km.sh and writes one CSV
row per month with the rainfall of the 1 km cell containing the borehole and the
mean of its 3x3 neighbourhood.

Usage:
    python scripts/haduk_extract_cell.py \
        --nc-dir "/Volumes/Crucial X9 Pro for Mac/HadUK-Grid" \
        --out data/haduk/lopcombe_haduk1km_monthly_rainfall.csv

Requires: numpy, netCDF4
"""
import argparse
import csv
import glob
import os
import sys

import numpy as np
import netCDF4 as nc

# Lopcombe Corner GWL, EA station E14150 (British National Grid)
EASTING, NORTHING = 425007, 135427


def find_index(bounds, value):
    """Index of the grid cell whose [lower, upper) bounds contain value."""
    hit = np.where((bounds[:, 0] <= value) & (value < bounds[:, 1]))[0]
    if hit.size == 0:
        raise ValueError(f"{value} is outside the grid")
    return int(hit[0])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--nc-dir", required=True, help="folder holding rainfall_hadukgrid_uk_1km_mon_*.nc")
    ap.add_argument("--out", default="data/haduk/lopcombe_haduk1km_monthly_rainfall.csv")
    ap.add_argument("--easting", type=float, default=EASTING)
    ap.add_argument("--northing", type=float, default=NORTHING)
    ap.add_argument("--start", type=int, default=1963, help="first year to include")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.nc_dir, "rainfall_hadukgrid_uk_1km_mon_*.nc")))
    files = [f for f in files if int(os.path.basename(f).split("_mon_")[1][:4]) >= args.start]
    if not files:
        sys.exit(f"No HadUK-Grid files found in {args.nc_dir}")

    rows = []
    for path in files:
        with nc.Dataset(path) as d:
            ix = find_index(d["projection_x_coordinate_bnds"][:], args.easting)
            iy = find_index(d["projection_y_coordinate_bnds"][:], args.northing)
            if path == files[0]:
                print(f"Cell centre E {d['projection_x_coordinate'][ix]:.0f}, "
                      f"N {d['projection_y_coordinate'][iy]:.0f}")
            block = np.ma.filled(d["rainfall"][:, iy - 1:iy + 2, ix - 1:ix + 2].astype(float), np.nan)
            year = int(os.path.basename(path).split("_mon_")[1][:4])
            for m in range(block.shape[0]):
                rows.append((year, m + 1, round(float(block[m, 1, 1]), 2),
                             round(float(np.nanmean(block[m])), 2)))

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["year", "month", "rain_cell_mm", "rain_3x3_mean_mm"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} months ({rows[0][0]}-{rows[-1][0]}) to {args.out}")


if __name__ == "__main__":
    main()
