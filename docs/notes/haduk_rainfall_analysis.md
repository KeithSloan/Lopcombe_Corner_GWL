# Lopcombe Corner — HadUK-Grid 1 km rainfall: validation, cyclicity, rainfall vs peak

Analysis of 20 Oct 2026. Full report: [`docs/reports/Lopcombe_HadUK_Rainfall_Cyclicity.pdf`](../reports/Lopcombe_HadUK_Rainfall_Cyclicity.pdf).

## Data
- **Rainfall:** Met Office HadUK-Grid v1.3.2.ceda, release v20260512, 1 km monthly rainfall, 1963–2025.
  63 yearly NetCDF files (~42 MB each, 2.6 GB total) kept on the external SSD at
  `/Volumes/Crucial X9 Pro for Mac/HadUK-Grid/`, not in the repo.
- **Cell:** borehole E14150 at E 425007 / N 135427 → 1 km cell centred E 425500 / N 135500. The single cell matches
  its 3×3 mean to within 1.25 mm/month, so cell choice doesn't matter. Mean annual rainfall 844 mm.
- **Levels:** winter peaks — manual-dip annual maxima 1964–1999 and corrected logger winter peaks 2001–2025.
  Winter 1999/2000 omitted (no reliable peak). 61 winters.

## Reproduce
```bash
# 1. Download (asks for CEDA username + password; free account)
bash scripts/get_haduk_1km.sh
# 2. Extract the borehole cell (needs netCDF4)
python scripts/haduk_extract_cell.py --nc-dir "/Volumes/Crucial X9 Pro for Mac/HadUK-Grid"
# 3. Analysis + chart (needs numpy, pandas, scipy, matplotlib; ~2–3 min for 5,000 Monte Carlo runs)
python scripts/haduk_rainfall_analysis.py
```
Outputs: `data/haduk/lopcombe_haduk1km_monthly_rainfall.csv`, and in `output/haduk/`:
`lopcombe_winter_rain_vs_peak.csv`, `haduk_results.json`, `Lopcombe_HadUK_rainfall_cyclicity.png`.

## 1. Validation against Broughton E13580
- HadUK cell vs earlier Broughton Oct–Dec sums (2001–2025): **r = 0.96**, totals within 2%.
- vs Tim Vaughan's Broughton Oct–Jan figures (HadUK/Broughton): 2000/01 578/534, 2002/03 603/557,
  2013/14 634/605, 2019/20 496/484, 2023/24 505/509 — within −1% to +8%; the borehole cell is slightly wetter.
- The earlier API-summed Broughton Oct–Jan totals were internally inconsistent (Oct–Jan < Oct–Dec in 2001, 2006,
  2022, 2024), confirming the fetch dropped days. **HadUK-Grid supersedes them.**

## 2. Rainfall vs winter peak, 61 winters 1964–2025
- Oct–Mar rain vs peak: **r = 0.82** overall; dip era 1964–1999 r = 0.75; logger era 2001–2025 **r = 0.89**
  (better than 0.86 using Broughton). Fit: peak ≈ 0.039 × rain + 68.8 (≈ +3.9 m per +100 mm).
- **97 m Pitton threshold:** six winters reached it — 1994/95 (692 mm), 2000/01 (819), 2002/03 (671),
  2013/14 (860), 2019/20 (716), 2023/24 (796). **All had Oct–Mar ≥ ~670 mm.** Of the 7 winters above 670 mm,
  6 breached; the exception was 2022/23 (709 mm → 92.6 m). 1976/77 (669 mm → 89.1 m) followed the 1976 drought.
- Six breaches in 61 winters ≈ 1 in 10 overall, but 5 of the 6 since 2000.

## 3. Cyclicity (5,000 Monte Carlo runs)
| Series | Strongest period | p (white) | p (AR1 red) | Halves | ACF | Runs |
|---|---|---|---|---|---|---|
| Oct–Mar rainfall (62) | 3.3 yr | 0.43 | 0.44 | 2.7 / 3.2 yr | none outside ±0.25 | 32 vs 32 |
| Calendar-year rain (63) | 6.6 yr | 0.74 | 0.75 | 2.3 / 7.4 yr | none | 29 vs 32 |
| Winter peak level (61) | 6.7 yr | 0.51 | 0.50 | 2.7 / 6.3 yr | lag 9 = −0.26 only | 34 vs 30.5 |

**No significant cycle in rainfall or levels.** The levels' ~6–7 yr tendency has no counterpart in Oct–Mar
rainfall (3.3 yr), and neither is stable between halves.

## 4. Trend
- Oct–Mar rainfall: Sen slope **+1.4 mm/yr** (~+87 mm over 62 winters, ~18% of the mean), Mann–Kendall
  **p = 0.057** — suggestive, not significant at 5%. 8 of the 13 wettest-quintile winters are 2000/01 or later.
- Calendar-year rainfall +1.7 mm/yr, p = 0.12. Winter peak level: no trend (p = 0.77).
- Caveat: dip-era peaks may under-read where dips were sparse, which would mute any level trend.

## Possible next step
Add the start-of-winter groundwater level to the 62-winter model to explain wet winters such as 2022/23
that stayed below the threshold.
