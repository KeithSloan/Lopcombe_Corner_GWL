# Lopcombe Corner — Start-of-winter level analysis

Analysis of 20 Oct 2026. Full report: [`docs/reports/Lopcombe_Start_of_Winter_Level.pdf`](../reports/Lopcombe_Start_of_Winter_Level.pdf).
Reproduce: `python scripts/start_level_analysis.py` (outputs `start_level_winters.csv`, `start_level_results.json`,
`Lopcombe_start_level.png` in `output/haduk/`).

## Data
- 25 logger-era winters, 2000/01–2024/25. Corrected winter peaks; HadUK-Grid 1 km rainfall for the borehole cell.
- Start level = autumn recession low (≈ 1 Oct level), extracted 7 Sep 2026. Mean 78.49 ± 0.44 m,
  range 77.58 m (2006/07) to 79.36 m (2008/09). Uncorrelated with that winter's rainfall (r = 0.07).

## Result
| Model | R² | RMSE | Start-level effect |
|---|---|---|---|
| Peak ~ Oct–Mar rain | 0.80 | 3.3 m | — |
| Peak ~ Oct–Mar rain + start level | **0.85** | 2.9 m | **+3.6 m per m**, p = 0.02 (SE 1.4; 95% ≈ 0.6–6.6) |
| Peak ~ Oct–Jan rain | 0.76 | | — |
| Peak ~ Oct–Jan rain + start level | 0.81 | | +3.7 m per m, p = 0.03 |

Fit: peak ≈ −220.0 + 0.042 × Oct–Mar rain + 3.64 × start level. Partial r = 0.47; F-test p = 0.020.

- **Real but modest.** One SD of start level (0.44 m) ≈ +1.6 m of peak; one SD of Oct–Mar rain (127 mm) ≈ +5.3 m.
- **History:** Sept analyses with Broughton Oct–Jan/Oct–Dec and first-pass peaks found little or no effect
  (R² 0.52→0.56, 0.43→0.49 ns). With corrected peaks and Broughton Oct–Mar it became clear (0.74→0.83).
  With HadUK-Grid, rain alone explains more (0.80), leaving less for the start level (+5 points), still significant.
- **Helps:** 2004/05, 2005/06, 2008/09 (+9.6 → +6.3 m), 2012/13, 2022/23 (−3.3 → −1.6 m), 2024/25.
- **Worse:** 2019/20 (+1.1 → +3.2 m; low start but very wet Feb 2020), 2023/24 (−2.1 → −3.5 m; early-Jan peak),
  2006/07 (overshoots), 2014/15.
- **Still unexplained:** 2002/03 (+5.8 m), 2008/09 (+6.3 m), 2017/18 (+4.2 m, April peak) — rainfall timing.
- Flood-threshold (97 m) calls are the same with or without the start level; both miss 2002/03 and 2019/20.

## Next steps
- Extend to 61 winters from 1964 using autumn manual dips (needs EA API access).
- Add a rainfall-timing term (February rain, wettest 30 days) using the monthly HadUK-Grid data.
