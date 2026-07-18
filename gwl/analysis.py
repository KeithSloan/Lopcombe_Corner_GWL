"""Turn Hydrology API responses into pandas DataFrames and summary statistics."""

import pandas as pd

from . import api

READING_COLUMNS = ["dateTime", "date", "value", "quality"]

_EMPTY_DTYPES = {
    "dateTime": "datetime64[ns]",
    "date": "datetime64[ns]",
    "value": "float64",
    "quality": "object",
}


def _empty_readings_frame(extra_columns=()):
    """An empty readings DataFrame with real dtypes (not `object`) on every column.

    A plain `pd.DataFrame(columns=[...])` defaults every column to `object`
    dtype, which silently downgrades `dateTime` out of datetime64 the moment
    it's `pd.concat`-ed with a real (non-empty) readings frame - breaking
    `.dt` accessors downstream. This matters whenever a station has no
    readings for one series (e.g. a dipped-only station has no logged
    series at all).
    """
    dtypes = dict(_EMPTY_DTYPES)
    for col in extra_columns:
        dtypes[col] = "object"
    return pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype in dtypes.items()})


def readings_to_dataframe(readings):
    """Convert a list of reading dicts from the API into a DataFrame sorted by time."""
    if not readings:
        return _empty_readings_frame()
    df = pd.DataFrame(readings)
    df["dateTime"] = pd.to_datetime(df["dateTime"])
    df["date"] = pd.to_datetime(df["date"])
    return df[READING_COLUMNS].sort_values("dateTime").reset_index(drop=True)


def classify_measures(measures):
    """Split a station's measures into 'logged' (telemetry) and 'dipped' (manual) series.

    The API doesn't expose a consistent boolean flag for this, but groundwater
    measure notations observed in practice include either "logged" or "dipped",
    so we split on that.
    """
    logged, dipped, other = [], [], []
    for measure in measures:
        notation = measure.get("notation") or api.measure_notation(measure["@id"])
        if "logged" in notation:
            logged.append(measure)
        elif "dipped" in notation:
            dipped.append(measure)
        else:
            other.append(measure)
    return {"logged": logged, "dipped": dipped, "other": other}


def current_level(client, measures, reference_df=None, max_diff=5.0, tolerance_hours=48):
    """Return the most recent reading across a set of measures, as a dict, or None.

    If `reference_df` (typically the logged/telemetry series) is given, a
    candidate that disagrees with the nearest reference reading by more
    than `max_diff` is treated as suspect and skipped in favour of the next
    most recent candidate - see `detect_discrepant_readings`.
    """
    latest_readings = []
    for measure in measures:
        for reading in client.get_readings(measure["@id"], latest=True):
            latest_readings.append({
                "dateTime": pd.to_datetime(reading["dateTime"]),
                "value": reading["value"],
                "quality": reading.get("quality"),
                "measure": measure.get("notation") or api.measure_notation(measure["@id"]),
                "label": measure.get("label", ""),
            })
    if not latest_readings:
        return None

    candidates = pd.DataFrame(latest_readings).sort_values("dateTime", ascending=False).reset_index(drop=True)
    if reference_df is not None and not reference_df.empty:
        clean, _discrepant = detect_discrepant_readings(
            candidates, reference_df, max_diff=max_diff, tolerance_hours=tolerance_hours,
        )
        if not clean.empty:
            candidates = clean.sort_values("dateTime", ascending=False).reset_index(drop=True)
    return candidates.iloc[0].to_dict()


def detect_discrepant_readings(df, reference_df, max_diff=5.0, tolerance_hours=24):
    """Split `df` into rows that agree with `reference_df` and rows that don't.

    Groundwater levels move slowly, so if a reading disagrees with the
    nearest-in-time reading in `reference_df` by more than `max_diff`, it's
    more likely a field/logger fault or a transcription error than a real
    level jump. This is mainly used to catch manual "dipped" readings that
    disagree sharply with the logged telemetry around the same visit.

    Rows with no reference reading within `tolerance_hours` can't be
    checked and are treated as clean (e.g. dipped readings from before
    telemetry existed).

    Returns (clean, discrepant), both copies of `df`'s rows; `discrepant`
    also carries `reference_value` and `diff` columns for inspection.
    """
    if df.empty or reference_df.empty:
        return df.copy(), df.iloc[0:0].copy()

    reference_sorted = (
        reference_df[["dateTime", "value"]]
        .sort_values("dateTime")
        .rename(columns={"value": "reference_value"})
    )
    merged = pd.merge_asof(
        df.sort_values("dateTime"),
        reference_sorted,
        on="dateTime",
        direction="nearest",
        tolerance=pd.Timedelta(hours=tolerance_hours),
    )
    merged["diff"] = (merged["value"] - merged["reference_value"]).abs()
    discrepant_mask = merged["diff"] > max_diff
    clean = merged.loc[~discrepant_mask, df.columns].reset_index(drop=True)
    discrepant = merged.loc[discrepant_mask].reset_index(drop=True)
    return clean, discrepant


def fetch_series(client, measures, mineq_date=None, max_date=None, time=None, limit=None):
    """Fetch and concatenate readings for a list of measures into one DataFrame."""
    frames = []
    for measure in measures:
        readings = client.get_readings(
            measure["@id"], mineq_date=mineq_date, max_date=max_date, time=time, limit=limit,
        )
        df = readings_to_dataframe(readings)
        if not df.empty:
            df["measure"] = measure.get("notation") or api.measure_notation(measure["@id"])
            frames.append(df)
    if not frames:
        return _empty_readings_frame(extra_columns=["measure"])
    return pd.concat(frames, ignore_index=True).sort_values("dateTime").reset_index(drop=True)


def annual_stats(df, percentile=90):
    """Per-year absolute max and given percentile of `value`, indexed by year."""
    pct_col = f"p{percentile:g}"
    if df.empty:
        return pd.DataFrame(columns=["year", "max", pct_col, "count"])
    working = df.copy()
    working["year"] = working["dateTime"].dt.year
    grouped = working.groupby("year")["value"]
    stats = grouped.agg(max="max", count="count")
    stats[pct_col] = grouped.quantile(percentile / 100)
    return stats.reset_index()[["year", "max", pct_col, "count"]]


def last_n_days(df, days=7, reference=None):
    """Filter a readings DataFrame down to the last `days` days."""
    if df.empty:
        return df
    end = pd.to_datetime(reference) if reference is not None else df["dateTime"].max()
    start = end - pd.Timedelta(days=days)
    return df[df["dateTime"] >= start].reset_index(drop=True)
