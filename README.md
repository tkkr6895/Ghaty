# Western Ghats Spatial Analysis

This repository contains geospatial analysis and research workflows for the Western Ghats biodiversity hotspot, built as an independent research project.

Long-form analysis and writing based on these outputs is published here:

- Research blog: https://tkkr.substack.com/p/bettada-jeeva-or-the-life-of-the

## What is in this repository

- Western Ghats boundary and district boundary preparation
- Land use / land cover summaries and visualizations
- Forest typology assessment outputs (natural forest vs plantations, where supported by data)
- Core Stack coverage validation for Western Ghats districts
- Core Stack exports for GIS and offline field use

## Important interpretation note

Dynamic World "Trees" includes both natural forests and many plantation systems. Where this repository reports "tree cover" it should not be interpreted as "natural forest" without additional classification/validation.

## Quick start

1. Create configuration for API access (if using Core Stack)
   - Copy `config_template.py` to `config.py`
   - Add your API key in `config.py` (this file should not be committed)
2. Run the quick workflows in `QUICK_START.md`

## Core Stack workflows

### 1) Western Ghats coverage check

- Script: `check_corestack_wg_district_coverage.py`
- Output: `outputs/corestack_coverage/` (CSV/Markdown/JSON)
- Purpose: list Western Ghats districts and identify which ones appear in Core Stack active locations

### 2) Western Ghats KML export (online links)

- Script: `export_corestack_western_ghats_to_kml.py`
- Output: `outputs/corestack_wg_kml/`
- Notes:
  - Some tehsils can fail server-side when enumerating generated layer URLs; these are recorded in the CSV/KML.
  - Many layer URLs depend on GeoServer access (often via port 8443). Some networks block this.

### 3) Offline pack download (vectors and rasters)

- Script: `download_corestack_offline_pack.py`
- Output: `outputs/corestack_offline_pack/<pack-name>/`
- Purpose: download discovered WFS layers (GeoJSON/KML) and optionally WCS coverages (GeoTIFF) so work can continue fully offline.

## Repository layout

See `REPOSITORY_STRUCTURE.md` for an up-to-date file map.

## Data sources

- CEPF / CBI Western Ghats boundary
- Google Earth Engine datasets (e.g., Dynamic World)
- Nature-Trace (where applicable)
- Core Stack API and Core Stack GeoServer (coverage varies by district/tehsil)

## License

Code is provided for transparency and reproducibility. Source datasets retain their respective licenses and terms.
