"""Matplotlib chart builders for groundwater level data."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DIPPED_COLOR = "#d95f02"  # manual dipped readings (older/non-telemetered record)
LOGGED_COLOR = "#1b9e77"  # instrument/telemetry readings


def plot_full_history(dipped_df, logged_df, station_label, unit, outpath):
    """Full-history chart with dipped (manual) and logged (telemetry) series in different colours."""
    fig, ax = plt.subplots(figsize=(12, 6))
    if not dipped_df.empty:
        ax.plot(dipped_df["dateTime"], dipped_df["value"], ".", color=DIPPED_COLOR,
                markersize=3, label="Dipped (manual)")
    if not logged_df.empty:
        ax.plot(logged_df["dateTime"], logged_df["value"], "-", color=LOGGED_COLOR,
                linewidth=0.8, label="Logged (telemetry)")
    ax.set_title(f"{station_label}: full groundwater level history")
    ax.set_xlabel("Date")
    ax.set_ylabel(f"Level ({unit})")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def plot_annual_stats(stats_df, percentile, station_label, unit, outpath):
    """Bar/line chart of per-year absolute max and percentile level."""
    pct_col = f"p{percentile:g}"
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(stats_df["year"], stats_df["max"], "o-", label="Annual max")
    ax.plot(stats_df["year"], stats_df[pct_col], "s-", label=f"Annual {pct_col}")
    ax.set_title(f"{station_label}: annual peak and {pct_col} level")
    ax.set_xlabel("Year")
    ax.set_ylabel(f"Level ({unit})")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def plot_last_n_days(df, days, station_label, unit, outpath):
    """Fine-resolution chart of the most recent `days` days of logged data."""
    fig, ax = plt.subplots(figsize=(12, 6))
    if not df.empty:
        ax.plot(df["dateTime"], df["value"], "-", color=LOGGED_COLOR, linewidth=1.2)
    ax.set_title(f"{station_label}: last {days} days (15-minute logged series)")
    ax.set_xlabel("Date/time")
    ax.set_ylabel(f"Level ({unit})")
    ax.grid(alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
