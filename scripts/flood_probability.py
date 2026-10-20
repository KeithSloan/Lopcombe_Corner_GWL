#!/usr/bin/env python3
"""Lopcombe Corner: chance of reaching the 97 m flood threshold, given the level at a month end.

For each month end from October to February, estimates the probability that the
winter peak (max level October-May) reaches the threshold, as a function of the
level on that date. Two methods:

  A. History  - Firth-penalised logistic regression of "winter reached threshold"
                on the month-end level, over all winters since 1963/64.
  B. Scenario - regression of the winter peak on the month-end level and the
                rainfall still to come (month after, to April; HadUK-Grid 1 km),
                then averaged over every historical rainfall sequence (62 winters)
                with the model's residual scatter.

Inputs
  data/levels/E14150_dipped.csv, data/levels/E14150_logged_daily.csv   (export_levels.py)
  data/haduk/lopcombe_haduk1km_monthly_rainfall.csv                   (haduk_extract_cell.py)
Outputs (in --outdir)
  flood_prob_winters.csv     month-end levels, peak and outcome per winter
  flood_prob_table.csv       probabilities by month and level, both methods
  flood_prob_results.json    model coefficients and summary
  Lopcombe_flood_probability.png

Usage:
    python scripts/flood_probability.py [--threshold 97] [--outdir output/flood]
Requires: numpy, pandas, scipy, matplotlib
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MONTHS = [(10, "Oct"), (11, "Nov"), (12, "Dec"), (1, "Jan"), (2, "Feb")]
MAX_GAP_DAYS = 21          # a month-end level needs readings within this many days either side
LEVEL_GRID = np.round(np.arange(78.0, 100.01, 0.25), 2)


# ------------------------------------------------------------------ data
def load_levels(dipped_csv, logged_csv):
    """Combined reading series (logger at 09:00 daily from 1999, manual dips before and alongside)."""
    d = pd.read_csv(dipped_csv, parse_dates=["dateTime"])
    lg = pd.read_csv(logged_csv, parse_dates=["dateTime"])
    d["source"], lg["source"] = "dip", "logger"
    s = pd.concat([d, lg], ignore_index=True).dropna(subset=["value"])
    return s.sort_values("dateTime").reset_index(drop=True)


def level_at(s, when):
    """Linear interpolation of level at a time, or NaN if no readings close enough either side."""
    before = s[s.dateTime <= when]
    after = s[s.dateTime >= when]
    if before.empty or after.empty:
        return np.nan
    b, a = before.iloc[-1], after.iloc[0]
    gap = pd.Timedelta(days=MAX_GAP_DAYS)
    if when - b.dateTime > gap or a.dateTime - when > gap:
        return np.nan
    if a.dateTime == b.dateTime:
        return float(b.value)
    f = (when - b.dateTime) / (a.dateTime - b.dateTime)
    return float(b.value + f * (a.value - b.value))


def month_end(year, month):
    return pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0) + pd.Timedelta(hours=23)


def build_winters(s, rain, threshold):
    rows = []
    last_full = s.dateTime.max()
    for y in range(s.dateTime.min().year + 1, s.dateTime.max().year + 1):
        start, end = pd.Timestamp(f"{y - 1}-10-01"), pd.Timestamp(f"{y}-05-31 23:59")
        if end > last_full:
            continue
        w = s[(s.dateTime >= start) & (s.dateTime <= end)]
        if len(w) < 6:
            continue
        i = w.value.idxmax()
        row = dict(winter_end_year=y, winter=f"{y - 1}/{str(y)[2:]}", peak=float(w.value[i]),
                   peak_date=w.dateTime[i].strftime("%Y-%m-%d"), peak_source=w.source[i], n_readings=len(w))
        for m, name in MONTHS:
            yr = y - 1 if m >= 10 else y
            t = month_end(yr, m)
            row[f"L_{name}"] = level_at(s, t)
            row[f"R_after_{name}"] = remaining_rain(rain, y, m)
            before, after = w[w.dateTime <= t], w[w.dateTime > t]
            row[f"prior_max_{name}"] = float(before.value.max()) if len(before) else np.nan
            row[f"future_max_{name}"] = float(after.value.max()) if len(after) else np.nan
        rows.append(row)
    df = pd.DataFrame(rows)
    df["flood"] = (df.peak >= threshold).astype(int)
    for _, name in MONTHS:
        # outcome: level is at or above the threshold at some time after this month end (to 31 May)
        df[f"flood_after_{name}"] = (df[f"future_max_{name}"] >= threshold).astype(int)
        df[f"first_time_after_{name}"] = ((df[f"future_max_{name}"] >= threshold)
                                          & ~(df[f"prior_max_{name}"] >= threshold)).astype(int)
    return df


def remaining_rain(rain, y, m):
    """HadUK rainfall from the month after m up to April of the winter ending in year y."""
    seq = [(y - 1, 11), (y - 1, 12), (y, 1), (y, 2), (y, 3), (y, 4)]
    idx = {10: 0, 11: 1, 12: 2, 1: 3, 2: 4}[m]
    vals = [rain.get(k) for k in seq[idx:]]
    return float(sum(vals)) if all(v is not None for v in vals) else np.nan


# ----------------------------------------------------------- statistics
def firth_logit(x, y, iters=100):
    """Firth-penalised logistic regression (finite estimates even with separation)."""
    X = np.column_stack([np.ones(len(x)), x])
    beta = np.zeros(2)
    for _ in range(iters):
        p = 1 / (1 + np.exp(-X @ beta))
        W = p * (1 - p)
        XtWX = X.T @ (X * W[:, None])
        inv = np.linalg.inv(XtWX)
        h = np.einsum("ij,jk,ik->i", X * W[:, None], inv, X)
        step = inv @ (X.T @ (y - p + h * (0.5 - p)))
        beta = beta + step
        if np.max(np.abs(step)) < 1e-8:
            break
    p = 1 / (1 + np.exp(-X @ beta))
    se = np.sqrt(np.diag(np.linalg.inv(X.T @ (X * (p * (1 - p))[:, None]))))
    return beta, se


def ols(y, X):
    A = np.column_stack([np.ones(len(y))] + list(X))
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ beta
    dof = len(y) - A.shape[1]
    sigma = np.sqrt(resid @ resid / dof)
    se = np.sqrt(np.diag(sigma ** 2 * np.linalg.inv(A.T @ A)))
    r2 = 1 - resid @ resid / ((y - y.mean()) @ (y - y.mean()))
    return beta, se, sigma, r2


def level_for_prob(levels, probs, target):
    """Lowest level at which the probability curve reaches target (NaN if never)."""
    hit = np.where(np.asarray(probs) >= target)[0]
    return float(levels[hit[0]]) if hit.size else np.nan


# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dipped", default="data/levels/E14150_dipped.csv")
    ap.add_argument("--logged", default="data/levels/E14150_logged_daily.csv")
    ap.add_argument("--rain", default="data/haduk/lopcombe_haduk1km_monthly_rainfall.csv")
    ap.add_argument("--threshold", type=float, default=97.0)
    ap.add_argument("--outdir", default="output/flood")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    s = load_levels(args.dipped, args.logged)
    r = pd.read_csv(args.rain)
    rain = {(int(a), int(b)): float(c) for a, b, c in zip(r.year, r.month, r.rain_cell_mm)}
    win = build_winters(s, rain, args.threshold)
    win.round(3).to_csv(os.path.join(args.outdir, "flood_prob_winters.csv"), index=False)

    res = dict(threshold=args.threshold, n_winters=int(len(win)), n_flood=int(win.flood.sum()),
               flood_winters=win.loc[win.flood == 1, "winter"].tolist(), months={})
    table = []
    for m, name in MONTHS:
        L, R, F, Y = f"L_{name}", f"R_after_{name}", f"future_max_{name}", f"flood_after_{name}"
        live = win
        a = live.dropna(subset=[L, F])
        bA, seA = firth_logit(a[L].values, a[Y].values)
        pA = 1 / (1 + np.exp(-(bA[0] + bA[1] * LEVEL_GRID)))
        pA = np.where(LEVEL_GRID >= args.threshold, 1.0, pA)

        b = live.dropna(subset=[L, R, F])
        bB, seB, sigma, r2 = ols(b[F].values, [b[L].values, b[R].values])
        rain_scen = b[R].values
        pred = bB[0] + bB[1] * LEVEL_GRID[:, None] + bB[2] * rain_scen[None, :]
        pred = np.maximum(pred, LEVEL_GRID[:, None])          # the peak can't be below today's level
        pB = stats.norm.sf((args.threshold - pred) / sigma).mean(axis=1)
        pB = np.where(LEVEL_GRID >= args.threshold, 1.0, pB)

        res["months"][name] = dict(
            n_history=int(len(a)), n_flood_history=int(a[Y].sum()),
            flood_after_winters=a.loc[a[Y] == 1, "winter"].tolist(),
            first_time_after_winters=a.loc[a[f"first_time_after_{name}"] == 1, "winter"].tolist(),
            logit_intercept=float(bA[0]), logit_slope=float(bA[1]), logit_slope_se=float(seA[1]),
            n_scenario=int(len(b)), scen_intercept=float(bB[0]), scen_level_coef=float(bB[1]),
            scen_rain_coef=float(bB[2]), scen_level_se=float(seB[1]), scen_rain_se=float(seB[2]),
            scen_sigma=float(sigma), scen_r2=float(r2),
            level_range=[float(a[L].min()), float(a[L].max())],
            max_level_no_flood=float(a.loc[(a[Y] == 0) & (a[L] < args.threshold), L].max()),
            min_level_flood=float(a.loc[a[Y] == 1, L].min()),
            p10_history=level_for_prob(LEVEL_GRID, pA, 0.1), p50_history=level_for_prob(LEVEL_GRID, pA, 0.5),
            p90_history=level_for_prob(LEVEL_GRID, pA, 0.9),
            p10_scenario=level_for_prob(LEVEL_GRID, pB, 0.1), p50_scenario=level_for_prob(LEVEL_GRID, pB, 0.5),
            p90_scenario=level_for_prob(LEVEL_GRID, pB, 0.9),
            curve_history=pA.tolist(), curve_scenario=pB.tolist())
        lo, hi = float(a[L].min()) - 0.5, float(a[L].max()) + 1.0
        res["months"][name]["plot_range"] = [lo, hi]
        for lv, x, y in zip(LEVEL_GRID, pA, pB):
            table.append(dict(month_end=name, level_mAOD=lv, p_history=round(float(x), 3),
                              p_scenario=round(float(y), 3), within_observed_range=bool(lo <= lv <= hi)))
    pd.DataFrame(table).to_csv(os.path.join(args.outdir, "flood_prob_table.csv"), index=False)

    latest = s.iloc[-1]
    res["latest"] = dict(date=latest.dateTime.strftime("%Y-%m-%d"), level=float(latest.value))
    res["level_grid"] = LEVEL_GRID.tolist()
    plot(win, res, os.path.join(args.outdir, "Lopcombe_flood_probability.png"))
    calib = {}
    for m, name in MONTHS:
        d = res["months"][name]
        a = win.dropna(subset=[f"L_{name}", f"future_max_{name}"])
        b = a.dropna(subset=[f"R_after_{name}"])
        pred = (d["scen_intercept"] + d["scen_level_coef"] * b[f"L_{name}"].values[:, None]
                + d["scen_rain_coef"] * b[f"R_after_{name}"].values[None, :])
        pred = np.maximum(pred, b[f"L_{name}"].values[:, None])
        calib[name] = dict(
            observed=int(a[f"flood_after_{name}"].sum()),
            expected_history=float((1 / (1 + np.exp(-(d["logit_intercept"] + d["logit_slope"] * a[f"L_{name}"])))).sum()),
            observed_scenario_set=int(b[f"flood_after_{name}"].sum()),
            expected_scenario=float(stats.norm.sf((res["threshold"] - pred) / d["scen_sigma"]).mean(axis=1).sum()))
    res["calibration"] = calib
    with open(os.path.join(args.outdir, "flood_prob_results.json"), "w") as fh:
        json.dump(res, fh, indent=1)

    print(f"{res['n_winters']} winters, {res['n_flood']} reached {args.threshold:g} m: {', '.join(res['flood_winters'])}")
    for name, d in res["months"].items():
        print(f"end {name}: 50% at {d['p50_scenario']:.2f} m (scenario) / {d['p50_history']:.2f} m (history); "
              f"10-90% {d['p10_scenario']:.2f}-{d['p90_scenario']:.2f} m; scenario R2 {d['scen_r2']:.2f}, "
              f"sigma {d['scen_sigma']:.2f} m")
    print(f"Latest level {res['latest']['level']:.2f} m on {res['latest']['date']}. Outputs in {args.outdir}")


def plot(win, res, path):
    ink, ink2, grid, surf = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
    ramp = ["#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#0d366b"]   # light -> dark, Oct -> Feb
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": ink2, "axes.labelcolor": ink2,
                         "xtick.color": ink2, "ytick.color": ink2, "axes.spines.top": False,
                         "axes.spines.right": False, "figure.facecolor": surf, "axes.facecolor": surf})
    lv = np.array(res["level_grid"])
    thr = res["threshold"]
    fig, axs = plt.subplots(2, 1, figsize=(9, 10), gridspec_kw=dict(hspace=0.35))
    for ax, key, title in ((axs[0], "curve_scenario", "Rainfall-scenario method (62 historical rainfall sequences)"),
                           (axs[1], "curve_history", "History method (logistic fit to past winters)")):
        for (m, name), col in zip(MONTHS, ramp):
            p = np.array(res["months"][name][key])
            lo, hi = res["months"][name]["plot_range"]
            p = np.where((lv >= lo) & (lv <= hi) & (lv < thr), p, np.nan)
            ax.plot(lv, p * 100, color=col, lw=2.2, label=f"End of {name}")
            i = np.nanargmin(np.abs(p - 0.5))
            if abs(p[i] - 0.5) < 0.03:
                ax.annotate(name, (lv[i], p[i] * 100), xytext={"Feb": (6, -12)}.get(name, (-24, 4)),
                            textcoords="offset points",
                            fontsize=8, color=ink)
        if key == "curve_history":
            for (m, name), col in zip(MONTHS, ramp):
                a = win.dropna(subset=[f"L_{name}", f"future_max_{name}"])
                off = {"Oct": -8, "Nov": -4, "Dec": 0, "Jan": 4, "Feb": 8}[name]
                a = a[a[f"L_{name}"] < thr]
                ax.scatter(a[f"L_{name}"], a[f"flood_after_{name}"] * 100 + off, s=12, color=col, edgecolor=surf,
                           lw=0.5, zorder=3)
        ax.axhline(50, color=grid, lw=1)
        lt = res["latest"]
        ax.axvline(lt["level"], color=ink2, lw=0.8, ls="--")
        ax.text(lt["level"] + 0.15, 111, f"latest {lt['level']:.2f} m ({lt['date']})", fontsize=7.5, color=ink2,
                va="top")
        ax.axvline(thr, color=ink2, ls=":", lw=1)
        ax.text(thr + 0.1, 20, f"{thr:g} m threshold", rotation=90, ha="left",
                va="bottom", fontsize=7.5, color=ink2)
        ax.set_xlim(77.5, 97.5)
        ax.set_ylim(-14, 114)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_xlabel("Level at the end of the month (mAOD)")
        ax.set_ylabel("Chance of reaching 97 m later (%)")
        ax.set_title(title, loc="left", color=ink, fontsize=10)
        ax.grid(color=grid, lw=0.6)
        ax.set_axisbelow(True)
        ax.legend(frameon=False, loc="center left", bbox_to_anchor=(0.01, 0.62))
    axs[1].text(78.2, -12, "dots: past winters — at 0% did not reach 97 m afterwards, at 100% did (offset by month for legibility)",
                fontsize=7.5, color=ink2)
    fig.suptitle(f"Lopcombe Corner — chance the level is at or above {thr:g} m later in the winter, "
                 f"given the level at each month end ({res['n_winters']} winters)", x=0.06, ha="left", fontsize=11, color=ink)
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
