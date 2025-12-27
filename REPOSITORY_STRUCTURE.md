# Western Ghats Analysis - Repository Structure

This file is a lightweight index of the top-level scripts and folders in this workspace.

## Analysis scripts

- `western_ghats_historical_analysis.py` - Historical analysis workflow
- `corrected_glc_analysis.py` - Corrected historical LULC calculations
- `create_complete_historical_analysis.py` - End-to-end historical analysis outputs
- `spatial_analysis_comprehensive.py` - Spatial analysis suite (GEE exports and summaries)
- `forest_agriculture_integration.py` - Forest/agriculture analysis (includes Core Stack integration)
- `create_optimized_tree_cover_analysis.py` - Optimized tree cover analysis

## Visualization and deliverables

- `create_dashboard_clean.py` - Dashboard generation
- `create_combined_dashboard.py` - Combined dashboard output
- `create_comprehensive_outputs.py` - Generates comprehensive outputs bundle
- `create_final_comprehensive_outputs.py` - Final reporting bundle
- `create_animated_visualizations.py` - Visualization generation

## Core Stack utilities

- `check_corestack_wg_district_coverage.py` - Coverage check for Western Ghats districts
- `export_corestack_western_ghats_to_kml.py` - KML export for Google Earth / QGIS (online links)
- `download_corestack_offline_pack.py` - Offline pack downloader (WFS vectors and optional WCS rasters)
- `download_corestack_dakshina_kannada_offline.py` - Earlier Dakshina Kannada focused downloader

## Field validation

- `build_dakshina_kannada_fieldpack.py` - Creates an offline field pack (PNGs + stats) for Dakshina Kannada

## Data preparation

- `download_district_boundaries.py` - Downloads district boundaries
- `district_boundaries/` - District boundary shapefiles
- `data/` - Western Ghats boundary shapefiles and supporting layers

## Documentation

- `README.md` - Project overview
- `QUICK_START.md` - Minimal run instructions
- `README_SPATIAL_ANALYSIS.md` - Spatial analysis and visualization notes
- `CORE_STACK_ANALYSIS_RESULTS.md` - Core Stack coverage findings

## Outputs

- `outputs/` - Generated outputs (should be excluded from version control)
