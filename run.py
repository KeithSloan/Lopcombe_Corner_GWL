#!/usr/bin/env python3
"""CLI: fetch and analyse groundwater levels for an EA Hydrology API station.

Defaults to Lopcombe Corner Gwl (station reference E14150), but works for
any EA groundwater station.
"""

import argparse
import os
import sys

import pandas as pd

from gwl import api, analysis, plots

DEFAULT_STATION = "E14150"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--station", default=DEFAULT_STATION,
                         help=f"EA station reference (default: {DEFAULT_STATION})")
    parser.add_argument("--start", default=None,
                         help="Earliest date (YYYY-MM-DD) for the full-history chart/table; "
                              "defaults to the start of each series' record")
    parser.add_argument("--percentile", type=float, default=90,
                         help="Percentile for the annual summary table/chart (default: 90)")
    parser.add_argument("--full-resolution", action="store_true",
                         help="Use the full 15-minute logged series for the full-history chart "
                              "and annual stats, instead of a daily 09:00 sample")
    parser.add_argument("--days", type=int, default=7,
                         help="Number of trailing days for the recent-levels plot (default: 7)")
    parser.add_argument("--outdir", default="output",
                         help="Directory to write charts and tables to (default: ./output)")
    parser.add_argument("--max-discrepancy", type=float, default=5.0,
                         help="Maximum allowed disagreement, in the station's unit (mAOD), "
                              "between a dipped reading and the nearest logged reading before "
                              "it's treated as suspect (field/logger fault or transcription "
                              "error) and excluded from analysis (default: 5.0)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    os.makedirs(args.outdir, exist_ok=True)

    client = api.HydrologyClient()
    unit = "mAOD"

    print(f"Resolving station {args.station}...")
    station = client.get_station(args.station)
    station_label = station.get("label", args.station)
    notation = station["notation"]
    print(f"Found station: {station_label} ({args.station}), notation={notation}")

    measures = client.get_measures(notation)
    if not measures:
        print("No groundwater measures found for this station.", file=sys.stderr)
        return 1

    split = analysis.classify_measures(measures)
    print("Series found:")
    for kind in ("logged", "dipped", "other"):
        for measure in split[kind]:
            print(f"  [{kind}] {measure.get('notation', measure['@id'])} - {measure.get('label', '')}")

    all_measures = split["logged"] + split["dipped"] + split["other"]

    time_filter = None if args.full_resolution else "09:00:00"
    dipped_df = analysis.fetch_series(client, split["dipped"], mineq_date=args.start)
    logged_df = analysis.fetch_series(client, split["logged"], mineq_date=args.start, time=time_filter)

    dipped_df, discrepant_df = analysis.detect_discrepant_readings(
        dipped_df, logged_df, max_diff=args.max_discrepancy,
    )
    if not discrepant_df.empty:
        print(f"\nIgnoring {len(discrepant_df)} dipped reading(s) that disagree with the logged "
              f"series by more than {args.max_discrepancy:g} {unit} (likely a field/logger fault "
              f"or a transcription error):")
        for _, row in discrepant_df.iterrows():
            print(f"  {row['dateTime']}: dipped={row['value']:.3f} vs logged~{row['reference_value']:.3f} "
                  f"{unit} (diff={row['diff']:.3f})")

    latest = analysis.current_level(client, all_measures, reference_df=logged_df,
                                     max_diff=args.max_discrepancy)
    if latest:
        print(f"\nCurrent level: {latest['value']} {unit} at {latest['dateTime']} "
              f"({latest['measure']}, quality={latest['quality']})")
    else:
        print("\nNo readings available for current level.")

    history_path = os.path.join(args.outdir, "full_history.png")
    plots.plot_full_history(dipped_df, logged_df, station_label, unit, history_path)
    print(f"\nWrote full-history chart to {history_path}")

    combined = pd.concat([dipped_df, logged_df], ignore_index=True)
    stats_df = analysis.annual_stats(combined, percentile=args.percentile)
    stats_path = os.path.join(args.outdir, "annual_stats.csv")
    stats_df.to_csv(stats_path, index=False)
    print(f"Wrote annual stats table to {stats_path}")

    stats_chart_path = os.path.join(args.outdir, "annual_stats.png")
    plots.plot_annual_stats(stats_df, args.percentile, station_label, unit, stats_chart_path)
    print(f"Wrote annual stats chart to {stats_chart_path}")

    if split["logged"]:
        recent_start = None
        if latest is not None:
            recent_start = (latest["dateTime"] - pd.Timedelta(days=args.days)).strftime("%Y-%m-%d")
        recent_df = analysis.fetch_series(client, split["logged"], mineq_date=recent_start)
        recent_df = analysis.last_n_days(recent_df, days=args.days)
        recent_path = os.path.join(args.outdir, f"last_{args.days}_days.png")
        plots.plot_last_n_days(recent_df, args.days, station_label, unit, recent_path)
        print(f"Wrote last-{args.days}-days chart to {recent_path}")
    else:
        print("No logged (telemetry) series available for the recent-levels plot.")

    print(f"\nData: Environment Agency, hydrology.data.gov.uk, under the Open Government Licence v3.0.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
