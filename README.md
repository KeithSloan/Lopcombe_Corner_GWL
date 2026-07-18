# Lopcombe Corner GWL

Fetches and analyses groundwater level data from the Environment Agency's
[Hydrology API](https://environment.data.gov.uk/hydrology/doc/reference). No
API key is required.

Defaults to **Lopcombe Corner Gwl**, station reference `E14150` (a chalk
borehole near Salisbury), but works for any EA groundwater station via
`--station`.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python run.py
```

This resolves the station, prints its groundwater measures and current
level, and writes charts + a table to `./output/`:

- `full_history.png` - the full period of record, manual "dipped" readings
  and instrument "logged" telemetry plotted in different colours on the same
  axes.
- `annual_stats.png` / `annual_stats.csv` - per-year absolute max and the
  chosen percentile (default 90th) of the level.
- `last_7_days.png` - the most recent week, from the 15-minute logged
  series.

### CLI options

| Flag | Default | Meaning |
|---|---|---|
| `--station` | `E14150` | EA station reference to analyse |
| `--start` | full record | Earliest date (`YYYY-MM-DD`) to include in the history chart/table |
| `--percentile` | `90` | Percentile for the annual summary |
| `--full-resolution` | off | Use the full 15-minute logged series for the history chart and annual stats, instead of a daily 09:00 sample |
| `--days` | `7` | Trailing days shown in the recent-levels plot |
| `--outdir` | `output` | Where to write charts and tables |
| `--max-discrepancy` | `5.0` | Max allowed difference (mAOD) between a dipped reading and the nearest logged reading before it's excluded, see below |

Example, a different station over the full 15-minute resolution:

```bash
python run.py --station E14150 --full-resolution --percentile 95 --outdir output_full
```

## Why daily sampling by default

Groundwater levels move slowly compared to river flow, so a single 09:00
reading per day from the logged (telemetry) series is a good proxy for
annual peaks and percentiles, and keeps downloads small - the logged series
for this station alone is 15-minute data back to 1999 (roughly a million
readings at full resolution). Pass `--full-resolution` to use every reading
instead. The last-N-days plot always uses the full 15-minute series
regardless of this setting.

## Package layout

```
gwl/
  api.py       # HydrologyClient: talks to the Hydrology API
  analysis.py  # parses API responses into DataFrames, computes stats
  plots.py     # matplotlib chart builders
run.py         # CLI entry point
tests/         # unit tests for the API client and analysis functions
```

## How series are told apart

The station's `measures` endpoint returns one measure per record type,
identified by notation, e.g.:

- `<station>-gw-dipped-i-mAOD-qualified` - manual "dipped" (tape/dipmeter)
  readings. This is the only record before telemetry was installed, and
  continues afterwards as periodic site-visit checks used to
  calibrate/validate the logger - it isn't purely a legacy series. For
  E14150 these visits have continued at roughly monthly-to-quarterly
  intervals since telemetry began in 2001.
- `<station>-gw-logged-i-subdaily-mAOD-qualified` - continuous instrument
  telemetry.

`gwl.analysis.classify_measures` splits on `"logged"` / `"dipped"` appearing
in the measure notation. This held for E14150 at the time of writing;
`run.py` prints every measure it finds under "Series found" so you can
confirm the split looks right for other stations.

## Discrepancy filtering

A manual dip and the logger reading around the same visit occasionally
disagree by far more than groundwater could plausibly move (e.g. a logger
fault during the visit, or a transcription error in the field reading) - one
was found for E14150 on 2025-05-15 (dipped: 105.08 mAOD vs logged: ~82.7
mAOD that day). `gwl.analysis.detect_discrepant_readings` compares each
dipped reading against the nearest logged reading within 48 hours and drops
any that differ by more than `--max-discrepancy` (default 5.0 mAOD) before
they reach the charts or stats. `run.py` prints what it dropped and why;
readings with no nearby logged reading to check against (e.g. the
pre-telemetry record) are left alone.

## Tests

```bash
python -m unittest discover tests
```

These test the API client's parsing of sample responses and the analysis
functions' DataFrame/statistics logic - they do not hit the live API.

## Data licence

Data is provided by the Environment Agency under the
[Open Government Licence v3.0](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
When sharing outputs, attribute as: "Contains Environment Agency data
sourced from the Hydrology API, licensed under the Open Government Licence
v3.0."

## Nearby boreholes

See [`docs/nearby_boreholes.md`](docs/nearby_boreholes.md) for other EA
groundwater stations near Witt Road, Winterslow (including Nelson Arms
Winterslow, ~1.2km away and in the same Chalk block as Lopcombe Corner),
plus a few older BGS-referenced boreholes that aren't in this API.

## Possible next step

Pre-1990s manual dip data for some stations lives in the separate National
Groundwater Level Archive (NGLA) rather than this API - worth adding as a
follow-up if you need levels further back than the Hydrology API's dipped
record covers.
