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
| `docs/notes/` | Analysis notes (`haduk_rainfall_analysis.md`, `start_of_winter_level.md`, `flood_probability.md`, this file) |
| `scripts/get_haduk_1km.sh` | Downloads HadUK-Grid 1 km monthly rainfall from CEDA |
| `scripts/haduk_extract_cell.py` | Extracts the borehole's 1 km cell to CSV |
| `scripts/haduk_rainfall_analysis.py` | Rainfall vs peak, cyclicity, trend and chart |
| `scripts/start_level_analysis.py` | Effect of start-of-winter level on the winter peak |
| `scripts/winter_summary.py` | Winter peaks and 1 October levels from `data/levels/` → `output/levels/winter_summary.csv` |
| `scripts/export_levels.py` | Downloads the full EA level record (dips + daily logger) to `data/levels/` |
| `scripts/flood_probability.py` | Chance of reaching 97 m by month-end level |
| `data/haduk/` | Monthly rainfall CSV for the borehole cell, 1963–2025 |
| `data/levels/` | Full EA level record: manual dips (1963–) and daily logger (1999–) |
| `output/levels/` | `winter_summary.csv` — peak, peak date and 1 Oct level per winter |
| `output/flood/` | Flood-probability tables, results JSON and chart |
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
