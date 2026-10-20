#!/usr/bin/env python3
"""Lopcombe Corner: HadUK-Grid Oct-Mar rainfall vs winter peak level, cyclicity and trend.

Inputs
  data/haduk/lopcombe_haduk1km_monthly_rainfall.csv  (from haduk_extract_cell.py)
Outputs (in --outdir)
  lopcombe_winter_rain_vs_peak.csv    winter rainfall totals and peak level, 1963/64-2024/25
  haduk_results.json                  all statistics
  Lopcombe_HadUK_rainfall_cyclicity.png

Winter Y = October (Y-1) to March (Y). Peak levels: manual-dip annual maxima
1964-1999 and corrected logger winter peaks 2001-2025 (winter 1999/2000 omitted).
Significance of periodogram peaks uses Monte Carlo (shuffled = white noise,
fitted AR(1) = red noise).

Usage:
    python scripts/haduk_rainfall_analysis.py [--csv ...] [--outdir output/haduk] [--nsim 5000]

Requires: numpy, pandas, scipy, matplotlib
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import lombscargle
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ----------------------------------------------------------------- level data
DIP_PEAKS = {1964: 84.76, 1965: 80.18, 1966: 93.73, 1967: 94.44, 1968: 87.78, 1969: 92.38,
             1970: 87.01, 1971: 89.48, 1972: 92.30, 1973: 81.97, 1974: 90.85, 1975: 95.12,
             1976: 79.12, 1977: 89.05, 1978: 89.37, 1979: 90.22, 1980: 89.69, 1981: 87.71,
             1982: 92.84, 1983: 89.07, 1984: 83.85, 1985: 86.84, 1986: 87.11, 1987: 89.41,
             1988: 87.92, 1989: 82.78, 1990: 93.30, 1991: 80.06, 1992: 79.24, 1993: 87.02,
             1994: 94.20, 1995: 98.26, 1996: 84.75, 1997: 79.84, 1998: 84.38, 1999: 92.59}
LOGGER_PEAKS = {2001: 101.39, 2002: 85.33, 2003: 100.79, 2004: 82.72, 2005: 80.05, 2006: 79.33,
                2007: 90.76, 2008: 85.76, 2009: 92.62, 2010: 88.15, 2011: 81.05, 2012: 78.4,
                2013: 94.42, 2014: 102.01, 2015: 83.13, 2016: 88.15, 2017: 78.86, 2018: 89.54,
                2019: 80.66, 2020: 97.25, 2021: 91.72, 2022: 79.61, 2023: 92.62, 2024: 97.54,
                2025: 90.31}
PEAKS = {**DIP_PEAKS, **LOGGER_PEAKS}
THRESHOLD = 97.0  # Pitton groundwater flood threshold, mAOD

OCT_MAR = [(-1, 10), (-1, 11), (-1, 12), (0, 1), (0, 2), (0, 3)]
PERIODS = np.linspace(2, 30, 600)
FREQS = 2 * np.pi / PERIODS


# -------------------------------------------------------------------- helpers
def acf(x, nlags=15):
    x = np.asarray(x, float) - np.mean(x)
    d = (x * x).sum()
    return np.array([(x[:-k] * x[k:]).sum() / d for k in range(1, nlags + 1)])


def ls_power(t, x):
    x = (np.asarray(x, float) - np.mean(x)) / np.std(x)
    return lombscargle(np.asarray(t, float), x, FREQS, normalize=True)


def peak_list(p, n=5):
    loc = [i for i in range(1, len(p) - 1) if p[i] >= p[i - 1] and p[i] >= p[i + 1]]
    loc.sort(key=lambda i: -p[i])
    return [(round(float(PERIODS[i]), 1), round(float(p[i]), 3)) for i in loc[:n]]


def mc_pvalue(t, x, obs_max, nsim, rng, ar1=False):
    """Chance that a noise series has a periodogram maximum >= the observed one."""
    x = np.asarray(x, float)
    phi = acf(x, 1)[0] if ar1 else 0.0
    sd = x.std()
    maxes = np.empty(nsim)
    for k in range(nsim):
        if ar1:
            e = rng.normal(0, sd * np.sqrt(1 - phi ** 2), len(x) + 50)
            s = np.zeros_like(e)
            for i in range(1, len(e)):
                s[i] = phi * s[i - 1] + e[i]
            s = s[50:]
        else:
            s = rng.permutation(x)
        maxes[k] = ls_power(t, s).max()
    return float((maxes >= obs_max).mean()), float(np.quantile(maxes, 0.95))


def runs_test(x):
    x = np.asarray(x, float)
    med = np.median(x)
    s = x[x != med] > med
    n1, n2 = s.sum(), (~s).sum()
    runs = 1 + (s[1:] != s[:-1]).sum()
    mu = 2 * n1 * n2 / (n1 + n2) + 1
    var = 2 * n1 * n2 * (2 * n1 * n2 - n1 - n2) / ((n1 + n2) ** 2 * (n1 + n2 - 1))
    return int(runs), float(mu), float((runs - mu) / np.sqrt(var))


def cyclicity(name, t, x, nsim, rng):
    t = np.asarray(t)
    x = np.asarray(x, float)
    idx = np.arange(len(x))
    tau, p_mk = stats.kendalltau(idx, x)
    slope = stats.theilslopes(x, idx)[0]
    a = acf(x)
    band = 1.96 / np.sqrt(len(x))
    p = ls_power(t, x)
    p_white, q95_white = mc_pvalue(t, x, p.max(), nsim, rng)
    p_red, q95_red = mc_pvalue(t, x, p.max(), nsim, rng, ar1=True)
    half = len(x) // 2
    h1, h2 = ls_power(t[:half], x[:half]), ls_power(t[half:], x[half:])
    runs, mu, z = runs_test(x)
    return dict(name=name, n=len(x), mean=float(x.mean()), sd=float(x.std(ddof=1)),
                mk_tau=float(tau), mk_p=float(p_mk), sen_slope_per_yr=float(slope),
                acf=[round(float(v), 2) for v in a], acf_band=round(float(band), 2),
                acf_exceed=[i + 1 for i, v in enumerate(a) if abs(v) > band],
                ls_peaks=peak_list(p), p_white=p_white, p_red=p_red,
                q95_white=q95_white, q95_red=q95_red,
                half1=[int(t[0]), int(t[half - 1]), round(float(PERIODS[h1.argmax()]), 1)],
                half2=[int(t[half]), int(t[-1]), round(float(PERIODS[h2.argmax()]), 1)],
                runs=runs, runs_expected=round(mu, 1), runs_z=round(z, 2),
                high_years=t[x >= np.quantile(x, 0.8)].astype(int).tolist(), power=p.tolist())


# ---------------------------------------------------------------------- chart
def plot(res, table, path):
    blue, orange, ink, ink2, grid, surf = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": ink2, "axes.labelcolor": ink2,
                         "xtick.color": ink2, "ytick.color": ink2, "axes.spines.top": False,
                         "axes.spines.right": False, "figure.facecolor": surf, "axes.facecolor": surf})
    fig, ax = plt.subplots(3, 1, figsize=(9, 11.5), gridspec_kw=dict(hspace=0.45))

    a = ax[0]
    y, r = table.winter_end_year, table.oct_mar_mm
    a.bar(y, r, width=0.75, color=blue, label="Oct–Mar rainfall")
    t = np.arange(len(y))
    s = res["rain"]["sen_slope_per_yr"]
    c = np.median(r - s * t)
    a.plot(y, c + s * t, color=ink2, lw=1.5, ls="--",
           label=f"Sen trend +{s:.1f} mm/yr (p = {res['rain']['mk_p']:.2f}, not significant)")
    a.axhline(r.mean(), color=grid, lw=1)
    a.set_title(f"HadUK-Grid 1 km Oct–Mar rainfall at Lopcombe Corner, winters "
                f"{int(y.iloc[0]) - 1}/{str(int(y.iloc[0]))[2:]}–{int(y.iloc[-1]) - 1}/{str(int(y.iloc[-1]))[2:]}",
                loc="left", color=ink, fontsize=10)
    a.set_ylabel("mm")
    a.legend(frameon=False, loc="upper left")
    a.grid(axis="y", color=grid, lw=0.6)
    a.set_axisbelow(True)

    a = ax[1]
    dd = table[table.peak_level_mAOD.notna()]
    dip = dd.winter_end_year < 2000
    rl = res["rain_level"]
    a.scatter(dd.oct_mar_mm[dip], dd.peak_level_mAOD[dip], s=30, color=blue, edgecolor=surf, lw=1,
              label=f"Manual dips 1964–1999 (r = {rl['dip_r']:.2f})")
    a.scatter(dd.oct_mar_mm[~dip], dd.peak_level_mAOD[~dip], s=30, color=orange, edgecolor=surf, lw=1,
              label=f"Logger 2001–2025 (r = {rl['log_r']:.2f})")
    k, b = rl["fit"]
    xx = np.array([200, 900])
    a.plot(xx, k * xx + b, color=ink2, lw=1.2, ls="--")
    a.axhline(THRESHOLD, color=ink2, lw=1, ls=":")
    a.text(205, THRESHOLD + 0.3, "97 m Pitton flood threshold", color=ink2, fontsize=8)
    offsets = {1995: (-48, 4), 2020: (6, -11), 2001: (-48, 4)}
    for yr, rr, lv in rl["breach"] + [[w, round(float(v)), PEAKS[w]] for w, v in rl["wet_no_breach"]]:
        a.annotate(f"{yr - 1}/{str(yr)[2:]}", (rr, lv), xytext=offsets.get(yr, (6, -3)),
                   textcoords="offset points", fontsize=7.5, color=ink)
    a.set_title(f"Winter peak level vs Oct–Mar rainfall (all {rl['all_n']} winters: r = {rl['all_r']:.2f})",
                loc="left", color=ink, fontsize=10)
    a.set_xlabel("Oct–Mar rainfall (mm)")
    a.set_ylabel("Winter peak (mAOD)")
    a.legend(frameon=False, loc="upper left")
    a.grid(color=grid, lw=0.6)
    a.set_axisbelow(True)

    a = ax[2]
    a.plot(PERIODS, res["rain"]["power"], color=blue, lw=2, label="Oct–Mar rainfall")
    a.plot(PERIODS, res["level"]["power"], color=orange, lw=2, label="Winter peak level")
    a.axhline(res["rain"]["q95_white"], color=ink2, lw=1, ls="--")
    a.text(8.5, res["rain"]["q95_white"] + 0.005, "95% noise threshold (Monte Carlo)", ha="left",
           color=ink2, fontsize=8)
    for key in ("rain", "level"):
        p, pw = res[key]["ls_peaks"][0]
        a.annotate(f"{p} yr", (p, pw), xytext=(4, 4), textcoords="offset points", fontsize=8, color=ink)
    a.set_title("Periodogram: no peak reaches significance", loc="left", color=ink, fontsize=10)
    a.set_xlabel("Period (years)")
    a.set_ylabel("Normalised power")
    a.set_xlim(2, 30)
    a.set_ylim(0, 0.26)
    a.legend(frameon=False, loc="center right", bbox_to_anchor=(1, 0.55))
    a.grid(color=grid, lw=0.6)
    a.set_axisbelow(True)
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--csv", default="data/haduk/lopcombe_haduk1km_monthly_rainfall.csv")
    ap.add_argument("--outdir", default="output/haduk")
    ap.add_argument("--nsim", type=int, default=5000, help="Monte Carlo runs (5000 takes ~2 min)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    os.makedirs(args.outdir, exist_ok=True)

    r = pd.read_csv(args.csv).set_index(["year", "month"])["rain_cell_mm"]
    first, last = r.index.get_level_values(0).min(), r.index.get_level_values(0).max()
    years = np.arange(first + 1, last + 1)

    def total(y, months):
        return sum(r[(y + oy, m)] for oy, m in months)

    octdec = np.array([total(y, OCT_MAR[:3]) for y in years])
    octjan = np.array([total(y, OCT_MAR[:4]) for y in years])
    octmar = np.array([total(y, OCT_MAR) for y in years])
    annual = np.array([r[y].sum() for y in range(first, last + 1)])

    table = pd.DataFrame(dict(winter_end_year=years, oct_dec_mm=octdec.round(1), oct_jan_mm=octjan.round(1),
                              oct_mar_mm=octmar.round(1),
                              peak_level_mAOD=[PEAKS.get(int(y), np.nan) for y in years]))
    table.to_csv(os.path.join(args.outdir, "lopcombe_winter_rain_vs_peak.csv"), index=False)

    lv_years = np.array(sorted(y for y in PEAKS if first < y <= last))
    lv = np.array([PEAKS[y] for y in lv_years])
    res = {"rain": cyclicity("Oct-Mar rainfall", years, octmar, args.nsim, rng),
           "annual": cyclicity("Calendar-year rainfall", np.arange(first, last + 1), annual, args.nsim, rng),
           "level": cyclicity("Winter peak level", lv_years, lv, args.nsim, rng)}

    m = np.isin(years, lv_years)
    yy, rr = years[m], octmar[m]
    ll = np.array([PEAKS[y] for y in yy])
    dip = yy < 2000
    breach = [(int(y), round(float(a)), float(b)) for y, a, b in zip(yy, rr, ll) if b >= THRESHOLD]
    min_breach_rain = min(b[1] for b in breach)
    res["rain_level"] = dict(
        all_r=float(stats.pearsonr(rr, ll)[0]), all_n=int(len(yy)),
        dip_r=float(stats.pearsonr(rr[dip], ll[dip])[0]), dip_n=int(dip.sum()),
        log_r=float(stats.pearsonr(rr[~dip], ll[~dip])[0]), log_n=int((~dip).sum()),
        fit=[float(v) for v in np.polyfit(rr, ll, 1)], breach=breach,
        wet_no_breach=[(int(y), float(a)) for y, a, b in zip(yy, rr, ll) if a >= min_breach_rain and b < THRESHOLD])

    with open(os.path.join(args.outdir, "haduk_results.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    plot(res, table, os.path.join(args.outdir, "Lopcombe_HadUK_rainfall_cyclicity.png"))

    rl = res["rain_level"]
    print(f"Winters {years[0] - 1}/{str(years[0])[2:]}-{years[-1] - 1}/{str(years[-1])[2:]}: "
          f"peak vs Oct-Mar r = {rl['all_r']:.2f} (dips {rl['dip_r']:.2f}, logger {rl['log_r']:.2f})")
    print(f"97 m breaches: {[b[0] for b in breach]}, all with Oct-Mar >= {min_breach_rain} mm; "
          f"wet winters that did not breach: {[w[0] for w in rl['wet_no_breach']]}")
    for k in ("rain", "annual", "level"):
        d = res[k]
        print(f"{d['name']}: top period {d['ls_peaks'][0][0]} yr, p(white) {d['p_white']:.2f}, "
              f"p(red) {d['p_red']:.2f}, Sen slope {d['sen_slope_per_yr']:+.2f}/yr (MK p {d['mk_p']:.3f})")
    print(f"Outputs in {args.outdir}")


if __name__ == "__main__":
    main()
