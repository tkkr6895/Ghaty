# Western Ghats Land Cover Analysis (2018-2025)

## Overview
Comprehensive tree cover and built-up area analysis for the Western Ghats biodiversity hotspot using Google Earth Engine's Dynamic World dataset (10m resolution).

## Key Findings

### Tree Cover (2018-2025)
- **2018**: 83,840 km² (77.3%)
- **2025**: 87,346 km² (80.5%)
- **Change**: +3,506 km² (+4.18%)
- **Trend**: Increasing tree cover, particularly strong growth in 2022-2023

### Built-Up Area (2018-2025)
- **2018**: 2,140 km² (2.0%)
- **2025**: 3,375 km² (3.1%)
- **Change**: +1,235 km² (+57.74%)
- **Trend**: Rapid urbanization, especially in 2022-2024

## Methodology

### Data Source
- **Dataset**: Google Earth Engine Dynamic World V1
- **Resolution**: 10m (processed at 30m for efficiency)
- **Time Period**: January only (2018-2025)
- **Rationale**: January data avoids seasonal variations in monsoon-affected Western Ghats

### Regional Optimization
- **Snow/Ice Suppression**: Impossible in tropical Western Ghats climate
- **Cloud Filtering**: Minimized through January-only analysis (dry season)
- **Mode Composite**: Stable classification across multiple observations per month

### Classes Analyzed
1. **Water** - Rivers, reservoirs, coastal areas
2. **Trees** - Natural forests and large plantations
3. **Grass** - Grasslands and meadows
4. **Flooded Vegetation** - Wetlands and marshes
5. **Crops** - Agricultural areas
6. **Shrub and Scrub** - Degraded forest and shrubland
7. **Built** - Urban and developed areas
8. **Bare** - Mining, quarries, bare soil

## Outputs

### Statistical Data
- `outputs/dynamic_world_lulc_january_2018_2025_YYYYMMDD_HHMMSS.csv` - Complete area statistics for all years

### Geospatial Layers (Google Drive)
All exports available through Google Earth Engine Tasks → Google Drive:

**Western_Ghats_Tree_Cover/**
- `tree_cover_2018_january.tif` through `tree_cover_2025_january.tif`
- Binary masks (1 = tree cover, 0 = other)

**Western_Ghats_Built_Area/**
- `built_area_2018_january.tif` through `built_area_2025_january.tif`
- Binary masks (1 = built area, 0 = other)

**Western_Ghats_LULC/**
- `lulc_2018_january_dynamic_world.tif` through `lulc_2025_january_dynamic_world.tif`
- Full classification (values 0-8)

### Metadata
- `outputs/geospatial/export_metadata_YYYYMMDD_HHMMSS.json` - Complete export task information

## QGIS Visualization

### Tree Cover Analysis
1. Load all `tree_cover_*.tif` files as raster layers
2. Apply green color scheme (0=transparent, 1=green)
3. Toggle layer visibility to compare years
4. Use Raster Calculator: `"tree_cover_2025" - "tree_cover_2018"` to see changes

### Built-Up Area Analysis
1. Load all `built_area_*.tif` files as raster layers
2. Apply red/orange color scheme (0=transparent, 1=red)
3. Toggle layer visibility to track urbanization
4. Use Raster Calculator: `"built_area_2025" - "built_area_2018"` to quantify expansion

### Comparative Analysis
- **Swipe Tool**: Side-by-side year comparison
- **Overlay**: Combine tree cover and built area to identify conversion patterns
- **Change Detection**: Raster math to identify gains/losses

## Data Quality

### Validation
- ✓ All data from actual satellite observations
- ✓ No synthetic or placeholder values
- ✓ Regional probability thresholds applied
- ✓ Snow/ice class suppressed (tropical climate)
- ✓ Consistent January-only sampling

### Image Counts per Year
- 2018: 221 images
- 2019: 264 images
- 2020: 272 images
- 2021: 185 images
- 2022: 250 images
- 2023: 278 images
- 2024: 201 images
- 2025: 198 images

## Scripts

### Active
- `create_optimized_tree_cover_analysis.py` - Main analysis script
- `create_dashboard_clean.py` - Generate statistics dashboard

### Archived
- See `outputs/archive/` for historical scripts

## Repository
- **GitHub**: tkkr6895/Ghaty
- **Branch**: main

## References
- Dynamic World: https://dynamicworld.app/
- Western Ghats Boundary: CEPF Ecosystem Profile shapefile
- Study Area: 109,486 km² across 6 states (Karnataka, Kerala, Tamil Nadu, Goa, Maharashtra, Gujarat)

## Contact
Analysis conducted using Google Earth Engine Python API with regional optimization for Western Ghats biodiversity hotspot.

---
*Last Updated: October 25, 2025*
