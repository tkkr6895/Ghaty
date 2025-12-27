# Quick start

This repository contains several independent workflows. This file covers the ones used most often.

## Prerequisites

- Python 3.10+ recommended
- Common packages used across scripts: `requests`, `pandas`, `geopandas`, `shapely`

If you are using Core Stack, create a local `config.py` from `config_template.py`.

## Core Stack: Western Ghats coverage check

Runs the coverage assessment of Western Ghats districts against Core Stack active locations.

```powershell
python check_corestack_wg_district_coverage.py
```

Outputs are written under `outputs/corestack_coverage/`.

## Core Stack: Western Ghats KML export (online links)

Exports a single KML that contains network links to WFS vector layers (where available) and includes an inventory CSV.

```powershell
python export_corestack_western_ghats_to_kml.py
```

Optional: include a points CSV with columns `lat`, `lon` (and optional `name`):

```powershell
python export_corestack_western_ghats_to_kml.py --points-csv path\to\points.csv
```

Outputs are written under `outputs/corestack_wg_kml/`.

## Core Stack: offline pack (Dakshina Kannada and Chikmagalur)

Discovers matching WFS layers (and optionally WCS coverages) from Core Stack GeoServer and downloads them for offline use.

Discover only (writes manifest and README, no downloads):

```powershell
python download_corestack_offline_pack.py --discover-only
```

Download vectors only:

```powershell
python download_corestack_offline_pack.py
```

Download vectors and rasters (GeoTIFF):

```powershell
python download_corestack_offline_pack.py --include-rasters
```

Retry only missing items:

```powershell
python download_corestack_offline_pack.py --include-rasters --only-missing
```

Outputs are written under `outputs/corestack_offline_pack/dk_chikmagalur/` by default.
