# Lopcombe Corner — Start-of-winter level analysis

Updated 20 Oct 2026 using the full EA record. Full report:
[`docs/reports/Lopcombe_Start_of_Winter_Level.pdf`](../reports/Lopcombe_Start_of_Winter_Level.pdf).

## Reproduce
```bash
python scripts/winter_summary.py                                          # peaks + 1 Oct levels from data/levels/
python scripts/start_level_analysis.py                                    # all winters
python scripts/start_level_analysis.py --first-winter 2000 --tag _logger  # logger era only
```
Outputs in `output/haduk/`: `start_level_winters[_logger].csv`, `start_level_results[_logger].json`,
`Lopcombe_start_level[_logger].png`.

## Data
- Start level = level on 1 October (interpolated, readings within 21 days); matches the earlier autumn
  recession lows to within a few cm. Mean 78.45 ± 0.43 m, range 77.15 m (1976/77) to 79.39 m (2008/09).
- Uncorrelated with that winter's rainfall (r = −0.03). Peak = highest level Oct–May, full EA record.
- 59 winters 1963/64–2024/25 with rainfall and a 1 Oct level (1973/74, 1986/87, 1995/96 lack one;
  2025/26 lacks HadUK rainfall).

## Result
| Winters | Model | R² | RMSE | Start effect |
|---|---|---|---|---|
| All 59 | Oct–Mar rain | 0.69 | 3.4 m | — |
| All 59 | Oct–Mar rain + start | **0.79** | 2.8 m | **+4.5 m per m** (SE 0.9), p < 0.001 |
| Logger era 26 | Oct–Mar rain | 0.77 | 3.4 m | — |
| Logger era 26 | Oct–Mar rain + start | **0.86** | 2.7 m | **+5.0 m per m** (SE 1.3), p = 0.001 |
| All 59 | Oct–Jan rain (+ start) | 0.59 (0.71) | | +4.9 m per m |

Fit (all winters): peak ≈ −284.5 + 0.040 × Oct–Mar rain + 4.51 × 1 Oct level. Partial r = 0.56.

- **Clear and significant.** One SD of start level (0.43 m) ≈ +1.9 m of peak; 100 mm Oct–Mar rain ≈ +4.0 m;
  one SD of rain (127 mm) ≈ +5.1 m. A high start is worth about 50 mm of extra winter rain.
- **Why it changed:** the first 20 Oct version (25 winters, +3.6 m per m, p = 0.02) used peaks that were too low in
  winters that had started high — 2024/25 (95.04 m, not 90.31) and 2012/13 (95.73 m, not 94.42).
- **Helps most:** 1976/77 (−6.4 → −0.6 m), 2008/09 (+7.4 → +3.2), 1997/98, 2005/06, 1974/75, 2024/25.
- **Worse:** 1989/90 and 2019/20 (low start, very wet February); 2023/24 and 2007/08 (high start, lower peak).
- **Still unexplained:** 1965/66 (+8.7 m), 1981/82 (+5.8), 2018/19 (−5.2), 1968/69 (+4.7), 1999/2000 (+4.3).
- Flood calls: both models flag 4 of 6 flood winters with no false alarms; rain-only misses 1994/95 and 2002/03,
  rain + start misses 2002/03 and 2019/20.

## Next steps
- Add a rainfall-timing term (February rain, wettest 30 days) from monthly HadUK-Grid.
- Use the start level in the month-by-month flood-probability model.
