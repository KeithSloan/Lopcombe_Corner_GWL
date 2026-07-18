# Boreholes near Witt Road, Winterslow

Witt Road, Winterslow (postcode SP5 1PL, grid ref approx. SU 424857 132370)
sits in the Chalk aquifer, about 3km southeast of Lopcombe Corner (E14150).
This lists other groundwater monitoring boreholes in the same area, for
comparison against Lopcombe Corner's record.

## EA Hydrology API stations (usable with this package)

Found via `id/stations?observedProperty=groundwaterLevel&lat=51.090103&long=-1.646447&dist=8`
(a search from Witt Road's coordinates), distances computed from OS grid
easting/northing. All are in the regional Chalk aquifer; "Chalk unit" is the
specific BGS lithostratigraphic member recorded for that borehole.

Run any of these with `python run.py --station <reference>` - the
`stationReference` column is what most EA groundwater sites use, but many
manual-only sites have no `stationReference` at all, only a `wiskiID`; pass
whichever one is present (the package's station lookup now tries
`stationReference`, then `wiskiID`, then the station's notation/GUID).

| Dist. | Name | Reference | Type | Chalk unit | Depth (m) | Opened |
|---|---|---|---|---|---|---|
| 1.2km | Nelson Arms Winterslow | wiskiID `141811463` | manual (dipped-only) | Spetisbury Chalk Member | 96.9 | 1967 |
| 1.9km | Little Buckholt Cottage | wiskiID `141811458` | manual (dipped-only) | Newhaven Chalk Member | 27.3 | 1959 |
| 3.0km | Bentleigh Farm | wiskiID `141811466` | manual (dipped-only) | Newhaven Chalk Member | 23.3 | 1967 |
| 3.1km | **Lopcombe Corner** | `E14150` | logged + dipped | Chalk Group (undivided) | 54.3 | 1963 |
| 4.1km | West Tytherley | `9449SO` | logged + dipped | Chalk Group (undivided) | 19.2 | 1967 |
| 4.4km | Pitton Lodge | `9416SO` | logged + dipped | Lewes Nodular Chalk Member | 20.7 | 1959 |
| 4.7km | Jacks Bush | wiskiID `141808454` | manual (dipped-only) | Newhaven Chalk Member | 15.0 | 1959 |
| 4.8km | Strides Farm Cottage | wiskiID `141811482` | manual (dipped-only) | Spetisbury Chalk Member | 22.5 | 1959 |
| 5.5km | Leonards Grave | wiskiID `141808918` | manual (dipped-only) | Seaford Chalk Member | 50.0 | 1996 |
| 5.7km | Stock Bottom | wiskiID `141800488` | manual (dipped-only) | Spetisbury Chalk Member | 36.7 | 1967 |
| 5.9km | Clarendon 6 | `43168` | logged + dipped | Chalk | 83.6 | 2003 |
| 6.1km | Manor Farm East Dean | wiskiID `141811476` | manual (dipped-only) | Newhaven Chalk Member | 5.2 | 1967 |
| 6.1km | Manor Farm Broughton | wiskiID `141808926` | manual (dipped-only) | Chalk Group (undivided) | 15.0 | 1996 |
| 6.2km | Broughton Hill | wiskiID `1418101005` | manual (dipped-only) | Chalk Group (undivided) | 81.0 | 2004 |
| 6.6km | Dean Hill | wiskiID `141811904` | manual (dipped-only) | Spetisbury Chalk Member | 121.0 | 1994 |
| 7.1km | Beech Tree Cottage | wiskiID `141800489` | manual (dipped-only) | Spetisbury Chalk Member | 31.1 | 1967 |
| 7.4km | Darfield Farm Nether Wallop | wiskiID `141808519` | manual (dipped-only) | Seaford Chalk Member | 35.6 | 1968 |
| 7.5km | Gomeldon Seaford | wiskiID `90113302` | manual (dipped-only) | Chalk | 35.0 | 2002 |
| 7.6km | Gomeldon Lewes | wiskiID `90113303` | manual (dipped-only) | Chalk | 75.0 | 2002 |
| 8.3km | Hurdcott | `43191` | logged + dipped | Chalk | 21.8 | 2002 |
| 8.3km | Whaddon | wiskiID `90122301` | logged + dipped | Chalk | 69.2 | 2009 |
| 9.2km | Queen Manor Farm | `43167` | logged + dipped | Chalk | 33.9 | 2003 |

Notes:

- **Nelson Arms Winterslow** (1.2km) is the closest borehole to Witt Road by
  far, and shares Lopcombe Corner's Chalk aquifer block - its record tracks
  the same seasonal highs (1994-95, 2001-03, 2013-14, 2024-25) seen at
  Lopcombe Corner. See `output/nelson_arms_winterslow/full_history.png`.
- Most nearby stations are manual **dipped-only** sites - no telemetry, no
  15-minute series, so `run.py`'s `last_7_days.png` output will be empty for
  them (it prints "No logged (telemetry) series available").
- **West Tytherley, Pitton Lodge, Clarendon 6, Hurdcott, Whaddon, and Queen
  Manor Farm** are the only other fully telemetered stations in range - the
  only ones that would give a continuous chart comparable to Lopcombe
  Corner's post-2001 logged record.

## Older/historical boreholes - no accessible digital record found

These were supplied as known local groundwater observation sites near
Winterslow, using old-style National Grid borehole references (`SU23/nn` -
"SU23" is the 10km OS grid square covering Winterslow, Middle Winterslow,
and Witt Road; the suffix identifies the individual borehole, with `A`/`B`
distinguishing multiple boreholes at one site, typically at different
depths):

| Name | Reference | Status |
|---|---|---|
| Middle Winterslow, Hill Farm | SU23/83A | No digital record found |
| Middle Winterslow, Hill Farm | SU23/83B | No digital record found |
| East Winterslow | SU23/32 | No digital record found |

**No API or public data source could be found for any of the three**, so no
outputs (plots/tables) can currently be generated for them - this is not a
gap in this package's code, it's an absence of any queryable source. What
was checked:

- **EA Hydrology API, nationwide free-text search** (`id/stations?search=Winterslow`)
  - only returns Nelson Arms Winterslow. This search does return closed/
  discontinued stations too (confirmed: searching `search=Hill Farm`
  surfaces stations explicitly marked `status: Closed`), so this isn't a
  live-only filter hiding them - they are not in this API at all, active or
  historical.
- **EA Hydrology API, geographic radius search** around Witt Road at 8km,
  15km, and 25km - no "Hill Farm" or "East Winterslow" match near
  Winterslow at any radius.
- **BGS's old per-site National Groundwater Level Archive (NGLA) pages**
  (`www2.bgs.ac.uk/groundwater/datainfo/levels/sites/...`) - this entire
  subdomain now 302-redirects to the BGS homepage; the old per-site pages
  no longer resolve.
- **BGS's live NGLA** is a small, curated national archive (181 sites
  total, 28 of them "index" sites used for the national hydrological
  summary) - farm-scale local boreholes like these wouldn't be part of that
  curated set even if BGS holds the underlying paper/scanned record
  somewhere internally.

**Likely explanation**: the `SU23/nn` reference format (10km-grid-square +
local number, no modern WISKI ID) is consistent with a pre-EA local
monitoring scheme - most plausibly Wessex Water Authority (the regional
water authority responsible for this part of Wiltshire before the 1989
water industry privatisation and the creation of the National Rivers
Authority/Environment Agency). Sites in these legacy local networks were
not universally migrated into the EA's digital WISKI/Hydrology API, and
older readings are commonly paper records or scanned logs rather than a
queryable dataset. This package's `gwl/api.py` client only talks to
`environment.data.gov.uk/hydrology`, so it has no way to reach data that
was never digitised into that system (or any other public API) in the
first place.

If you're able to locate the underlying readings yourself (e.g. a scan,
spreadsheet, or an EA/BGS internal archive export), they could be wired
into the package as a third data source alongside the Hydrology API.

## Cost estimate: instrumenting Nelson Arms Winterslow

Nelson Arms Winterslow (1.2km from Witt Road, 96.9m borehole) is currently
manual "dipped-only" - no telemetry. This is an **unsourced, order-of-
magnitude estimate**, not a supplier quote: manufacturer/distributor sites
(Solinst, In-Situ, RS Hydro, etc.) quote-gate their instrument pricing
rather than publishing it, so nothing below was pulled from a live source -
it's a reasoned ballpark from general knowledge of UK groundwater
monitoring instrumentation. Get an actual site-specific quote before
budgeting against it.

Site-specific factors: the 96.9m depth needs a long cable run (though not
necessarily a high-pressure-range sensor, since the standing water column
above the likely sensor placement is much shallower than the total
borehole depth); it's a rural site with no visible power infrastructure, so
solar + cellular telemetry (the same setup Lopcombe Corner already uses)
is the likely approach.

| Item | Estimate (GBP) |
|---|---|
| Submersible pressure transducer/datalogger + ~100m cable | £1,500 - £3,000 |
| Telemetry unit (GSM/4G modem, solar panel, battery, enclosure) | £1,500 - £4,000 |
| Wellhead/headworks upgrade + secure housing | £500 - £2,000 |
| Installation & commissioning (site visit, mounting, initial calibration) | £1,000 - £2,500 |
| Validation period (dip checks against the new logger over the first few months) | £500 - £1,000 |
| Landowner access agreement / project admin | £500 - £1,500 |
| **One-off capital total** | **~£5,000 - £14,000**, likely £7k-£10k for a straightforward retrofit |

**Ongoing**: telemetry/SIM data plan (£200-£600/yr) plus periodic manual
dip checks to validate the logger, the same practice already visible in
Lopcombe Corner's record (£300-£800/yr) - roughly **£500-£1,500/year**.

Two caveats beyond the pricing itself:

1. This only covers physically instrumenting the borehole. For Nelson Arms
   to actually appear in the EA Hydrology API as a `logged` measure (like
   Lopcombe Corner), the EA would need to adopt it into their own WISKI
   network - a governance/procurement decision on their end, not something
   a private install alone achieves.
2. A real number needs a supplier (RS Hydro, In-Situ, a Solinst UK
   distributor, or a specialist environmental monitoring contractor) to
   quote against the actual site - power/signal survey, headworks
   condition, and access - since none of that is public pricing.

## Data licence

EA Hydrology API data: Environment Agency, under the
[Open Government Licence v3.0](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
