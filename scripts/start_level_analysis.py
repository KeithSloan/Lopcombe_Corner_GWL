#!/usr/bin/env python3
"""Lopcombe Corner: does the groundwater level at the start of winter change the winter peak?

Regresses the winter peak level on winter rainfall (HadUK-Grid 1 km) with and
without the start-of-winter level (the autumn recession low, about 1 October),
for the 25 logger-era winters 2000/01-2024/25.

Inputs
  output/haduk/lopcombe_winter_rain_vs_peak.csv   (from haduk_rainfall_analysis.py)
Outputs (in --outdir)
  start_level_winters.csv        per-winter data, fitted values and residuals
  start_level_results.json       model statistics
  Lopcombe_start_level.png       chart

Usage:
    python scripts/start_level_analysis.py [--csv ...] [--outdir output/haduk]

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

# Autumn recession low (mAOD), EA logger E14150, winter ending in year Y.
# Extracted 7 Sep 2026 (lopcombe-rainfall-correlation-v2-octdec); flat recession, so ~ the 1 Oct level.
START_LEVEL = {2001: 78.65, 2002: 78.55, 2003: 78.71, 2004: 78.30, 2005: 78.10, 2006: 77.70,
               2007: 77.58, 2008: 78.92, 2009: 79.36, 2010: 78.17, 2011: 78.25, 2012: 77.99,
               2013: 79.02, 2014: 78.58, 2015: 78.86, 2016: 78.56, 2017: 78.70, 2018: 78.47,
               2019: 78.40, 2020: 77.93, 2021: 78.66, 2022: 78.67, 2023: 78.07, 2024: 78.92,
               2025: 79.08}
THRESHOLD = 97.0


def ols(y, X, names):
    """Ordinary least squares with an intercept; returns coefficients, p-values and fit stats."""
    y = np.asarray(y, float)
    A = np.column_stack([np.ones(len(y))] + [np.asarray(x, float) for x in X])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    fitted = A @ beta
    resid = y - fitted
    n, k = A.shape
    dof = n - k
    s2 = resid @ resid / dof
    se = np.sqrt(np.diag(s2 * np.linalg.inv(A.T @ A)))
    tvals = beta / se
    pvals = 2 * stats.t.sf(np.abs(tvals), dof)
    r2 = 1 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean()))
    adj = 1 - (1 - r2) * (n - 1) / dof
    return dict(names=["intercept"] + names, coef=beta.tolist(), se=se.tolist(), p=pvals.tolist(),
                r2=float(r2), adj_r2=float(adj), rmse=float(np.sqrt(resid @ resid / n)),
                fitted=fitted, resid=resid)


def nested_f(small, big, n, k_big):
    """F-test that the extra term(s) in the bigger model improve the fit."""
    rss_s = (small["resid"] ** 2).sum()
    rss_b = (big["resid"] ** 2).sum()
    q = len(big["coef"]) - len(small["coef"])
    f = ((rss_s - rss_b) / q) / (rss_b / (n - k_big))
    return float(f), float(stats.f.sf(f, q, n - k_big))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--csv", default="output/haduk/lopcombe_winter_rain_vs_peak.csv")
    ap.add_argument("--outdir", default="output/haduk")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    t = pd.read_csv(args.csv)
    d = t[t.winter_end_year.isin(list(START_LEVEL))].copy().reset_index(drop=True)
    d["start_level_mAOD"] = d.winter_end_year.map(START_LEVEL)
    y, n = d.peak_level_mAOD.values, len(d)

    models = {
        "octmar": ols(y, [d.oct_mar_mm], ["oct_mar_mm"]),
        "octmar_start": ols(y, [d.oct_mar_mm, d.start_level_mAOD], ["oct_mar_mm", "start_level"]),
        "octjan": ols(y, [d.oct_jan_mm], ["oct_jan_mm"]),
        "octjan_start": ols(y, [d.oct_jan_mm, d.start_level_mAOD], ["oct_jan_mm", "start_level"]),
        "start_only": ols(y, [d.start_level_mAOD], ["start_level"]),
    }
    f_mar = nested_f(models["octmar"], models["octmar_start"], n, 3)
    f_jan = nested_f(models["octjan"], models["octjan_start"], n, 3)

    # partial correlation of start level with peak, controlling for Oct-Mar rain
    r_y = ols(y, [d.oct_mar_mm], ["r"])["resid"]
    r_s = ols(d.start_level_mAOD, [d.oct_mar_mm], ["r"])["resid"]
    partial_r = float(np.corrcoef(r_y, r_s)[0, 1])

    d["pred_rain_only"] = models["octmar"]["fitted"].round(2)
    d["pred_rain_start"] = models["octmar_start"]["fitted"].round(2)
    d["resid_rain_only"] = models["octmar"]["resid"].round(2)
    d["resid_rain_start"] = models["octmar_start"]["resid"].round(2)
    d.to_csv(os.path.join(args.outdir, "start_level_winters.csv"), index=False)

    sl = d.start_level_mAOD
    res = dict(n=n, start_level_mean=float(sl.mean()), start_level_sd=float(sl.std(ddof=1)),
               start_level_min=float(sl.min()), start_level_max=float(sl.max()),
               corr_start_rain=float(np.corrcoef(sl, d.oct_mar_mm)[0, 1]),
               corr_start_peak=float(np.corrcoef(sl, y)[0, 1]),
               partial_r_start=partial_r, f_test_octmar=f_mar, f_test_octjan=f_jan,
               models={k: {kk: vv for kk, vv in m.items() if kk not in ("fitted", "resid")}
                       for k, m in models.items()})
    with open(os.path.join(args.outdir, "start_level_results.json"), "w") as fh:
        json.dump(res, fh, indent=1)

    plot(d, res, os.path.join(args.outdir, "Lopcombe_start_level.png"), r_s, r_y)

    m1, m2 = models["octmar"], models["octmar_start"]
    print(f"{n} winters. Start level {res['start_level_mean']:.2f} ± {res['start_level_sd']:.2f} m "
          f"(range {res['start_level_min']:.2f}-{res['start_level_max']:.2f}); corr with rain {res['corr_start_rain']:.2f}")
    print(f"Oct-Mar only: R2 {m1['r2']:.3f}, RMSE {m1['rmse']:.2f} m")
    print(f"Oct-Mar + start: R2 {m2['r2']:.3f}, RMSE {m2['rmse']:.2f} m, start coef {m2['coef'][2]:.2f} m/m "
          f"(p {m2['p'][2]:.3f}); F {f_mar[0]:.2f} p {f_mar[1]:.3f}; partial r {partial_r:.2f}")
    print(f"Outputs in {args.outdir}")


def plot(d, res, path, r_s, r_y):
    blue, orange, ink, ink2, grid, surf = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": ink2, "axes.labelcolor": ink2,
                         "xtick.color": ink2, "ytick.color": ink2, "axes.spines.top": False,
                         "axes.spines.right": False, "figure.facecolor": surf, "axes.facecolor": surf})
    fig, ax = plt.subplots(3, 1, figsize=(9, 11.5), gridspec_kw=dict(hspace=0.5))
    lab = lambda y: f"{y - 1}/{str(y)[2:]}"

    a = ax[0]
    m, sd = res["start_level_mean"], res["start_level_sd"]
    a.axhspan(m - sd, m + sd, color=grid, alpha=0.7, lw=0)
    a.plot(d.winter_end_year, d.start_level_mAOD, "o-", color=blue, ms=5, lw=1.5)
    a.axhline(m, color=ink2, lw=1, ls="--")
    a.text(2000.6, m + sd + 0.05, f"mean {m:.2f} m ± {sd:.2f} m (shaded)", color=ink2, fontsize=8)
    for y in (2007, 2009, 2020, 2023, 2025):
        v = d.loc[d.winter_end_year == y, "start_level_mAOD"].iloc[0]
        a.annotate(lab(y), (y, v), xytext=(4, -10 if v < m else 5), textcoords="offset points", fontsize=7.5)
    a.set_title("Start-of-winter level (autumn recession low), winters 2000/01–2024/25", loc="left",
                color=ink, fontsize=10)
    a.set_ylabel("mAOD")
    a.grid(axis="y", color=grid, lw=0.6)
    a.set_axisbelow(True)

    a = ax[1]
    br = d.peak_level_mAOD >= THRESHOLD
    a.scatter(r_s[~br], r_y[~br], s=32, color=blue, edgecolor=surf, lw=1, label="Below 97 m")
    a.scatter(r_s[br], r_y[br], s=36, color=orange, edgecolor=surf, lw=1, label="Reached 97 m")
    k = res["models"]["octmar_start"]["coef"][2]
    xx = np.array([r_s.min() - 0.1, r_s.max() + 0.1])
    a.plot(xx, k * xx, color=ink2, ls="--", lw=1.2, label=f"slope {k:.1f} m per m")
    a.axhline(0, color=ink2, lw=0.8)
    for i, y in enumerate(d.winter_end_year):
        if y in (2003, 2009, 2020, 2023, 2024, 2007):
            a.annotate(lab(y), (r_s[i], r_y[i]), xytext=(5, -3), textcoords="offset points", fontsize=7.5)
    a.set_title(f"Peak left unexplained by Oct–Mar rain vs start level (partial r = {res['partial_r_start']:.2f})",
                loc="left", color=ink, fontsize=10)
    a.set_xlabel("Start level, relative to that expected for the winter's rainfall (m)")
    a.set_ylabel("Peak residual after Oct–Mar rain (m)")
    a.legend(frameon=False, loc="upper left")
    a.grid(color=grid, lw=0.6)
    a.set_axisbelow(True)

    a = ax[2]
    lo, hi = 76, 104
    a.plot([lo, hi], [lo, hi], color=ink2, lw=1)
    a.scatter(d.peak_level_mAOD, d.pred_rain_only, s=30, color=blue, edgecolor=surf, lw=1,
              label=f"Oct–Mar rain only (RMSE {res['models']['octmar']['rmse']:.1f} m)")
    a.scatter(d.peak_level_mAOD, d.pred_rain_start, s=30, color=orange, edgecolor=surf, lw=1,
              label=f"Rain + start level (RMSE {res['models']['octmar_start']['rmse']:.1f} m)")
    for _, r in d[d.winter_end_year.isin([2023, 2009, 2003])].iterrows():
        a.annotate("", (r.peak_level_mAOD, r.pred_rain_start), (r.peak_level_mAOD, r.pred_rain_only),
                   arrowprops=dict(arrowstyle="->", color=ink2, lw=0.9))
        a.annotate(lab(int(r.winter_end_year)), (r.peak_level_mAOD, r.pred_rain_start), xytext=(6, -3),
                   textcoords="offset points", fontsize=7.5)
    a.axhline(THRESHOLD, color=ink2, ls=":", lw=1)
    a.axvline(THRESHOLD, color=ink2, ls=":", lw=1)
    a.set_xlim(lo, hi)
    a.set_ylim(lo, hi)
    a.set_title("Predicted vs actual winter peak (arrows: effect of adding start level)", loc="left",
                color=ink, fontsize=10)
    a.set_xlabel("Actual winter peak (mAOD)")
    a.set_ylabel("Predicted peak (mAOD)")
    a.legend(frameon=False, loc="upper left")
    a.grid(color=grid, lw=0.6)
    a.set_axisbelow(True)
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
