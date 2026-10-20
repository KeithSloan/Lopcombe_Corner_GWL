# Lopcombe Corner — Chance of reaching 97 m, by month-end level

Analysis of 20 Oct 2026. Full report: [`docs/reports/Lopcombe_Flood_Probability.pdf`](../reports/Lopcombe_Flood_Probability.pdf).

## Question
Given the borehole level at the end of October, November, December, January or February, what is the chance the
level is at or above 97 mAOD (Pitton groundwater-flood threshold) at some time later that winter (up to 31 May)?

## Reproduce
```bash
python scripts/export_levels.py       # downloads full EA record to data/levels/ (needs internet)
python scripts/flood_probability.py   # outputs in output/flood/
```

## Data
- `data/levels/E14150_dipped.csv` — 2,168 manual dips, 1963-04-23 to 2025-12-16 (spurious 105.08 m dip of 15 May 2025 removed).
- `data/levels/E14150_logged_daily.csv` — 9,940 daily 09:00 logger readings, 1999-08-04 to 2026-10-20.
- 63 winters 1963/64–2025/26; 7 reached 97 m: 1994/95, 2000/01, 2002/03, 2013/14, 2019/20, 2023/24, 2025/26.

## Methods
- **History:** Firth-penalised logistic regression of “reached 97 m after the month end” on the month-end level.
- **Rainfall scenario:** regression of the highest level after the month end on month-end level + HadUK-Grid rain
  still to come (next month to April); averaged over the 62 historical rainfall sequences with residual scatter.
- Curves only drawn within the range of levels seen at each time of year.

## Results (50:50 level, scenario / history)
| Month end | 50:50 level | Highest level, no flood | Lowest level, then flooded |
|---|---|---|---|
| Oct | 82.0 m / — | 82.8 m | 78.2 m |
| Nov | 89.0 / 88.0 m | 87.6 m | 78.5 m |
| Dec | 93.0 / 91.8 m | 93.2 m | 79.6 m (2013/14) |
| Jan | 95.5 / 93.2 m | 93.7 m | 89.6 m (2025/26) |
| Feb | 96.5 / 96.2 m | 94.2 m | 93.7 m (2023/24) |

- End of October says little (levels 77.6–82.9 m): about 1 in 10 at ordinary levels; methods disagree above 80 m.
- Every flood winter was ≥ 89.6 m by end of January; only 3 first crossed 97 m after end of January, none after end of February.
- Calibration: history expects 7.3 vs 7 observed; scenario runs ~20% low (4.9 vs 6) — treat as lower bound.
- On 2026-10-20 the level was 78.25 m (ordinary autumn level).

## Data note — earlier peaks were too low
The full daily record shows several logger-era winter peaks in earlier analyses were under-read, e.g.
2023/24 99.11 m (12 Apr 2024, not 97.54), 2024/25 95.04 (not 90.31), 2014/15 87.78 (not 83.13),
2021/22 82.68 (not 79.61), 2012/13 95.73 (not 94.42). 2025/26 (99.02 m, 27 Feb 2026) is new.
The HadUK-Grid, start-of-winter, annual-maximum and Oct–Mar reports have been re-run with it (20 Oct 2026).
