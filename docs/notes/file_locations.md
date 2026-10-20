# Lopcombe Corner — Where the files live (as of 2026-10-20)

## Main copy and SSD copy
- **Main working copy:** `/Users/ksloan/github/Lopcombe_Corner_GWL` (Mac internal drive). Save new work here first.
- **Secondary copy:** `/Volumes/Crucial X9 Pro for Mac/github/Lopcombe_Corner_GWL` — update it when the SSD is mounted.
- Both point to `github.com/KeithSloan/Lopcombe_Corner_GWL` (branch `main`).

## In this repo
| Path | Contents |
|---|---|
| `run.py`, `gwl/`, `tests/` | Groundwater-level retrieval and analysis code |
| `docs/reports/` | PDF reports (see `docs/reports/README.md`) |
| `docs/notes/` | Analysis notes (`haduk_rainfall_analysis.md`, `start_of_winter_level.md`, this file) |
| `scripts/get_haduk_1km.sh` | Downloads HadUK-Grid 1 km monthly rainfall from CEDA |
| `scripts/haduk_extract_cell.py` | Extracts the borehole's 1 km cell to CSV |
| `scripts/haduk_rainfall_analysis.py` | Rainfall vs peak, cyclicity, trend and chart |
| `scripts/start_level_analysis.py` | Effect of start-of-winter level on the winter peak |
| `data/haduk/` | Monthly rainfall CSV for the borehole cell, 1963–2025 |
| `output/haduk/` | Winter tables, results JSON and chart PNGs for the HadUK and start-level analyses |

## Outside the repo
- `/Volumes/Crucial X9 Pro for Mac/HadUK-Grid/` — the 63 HadUK-Grid NetCDF files (2.6 GB), 1963–2025,
  HadUK-Grid v1.3.2.ceda, release v20260512, from CEDA `1km/rainfall/mon/`.
- `/Users/ksloan/Documents/Claude/Projects/Lopcombe Corner GWL` — Claude project folder on the Mac (empty when checked).
- Claude project "Lopcombe Bore hole" — the earlier analysis notes (level records, truncation correction,
  Broughton correlations, cyclicity check).

## Data sources
- Borehole: EA Hydrology API, station E14150 (GUID c962ac5b-0532-4220-ac82-160104126de1), E 425007 / N 135427.
- Rain gauge: Broughton E13580 (EA). Grid rainfall: Met Office HadUK-Grid via CEDA (login and access token needed).
