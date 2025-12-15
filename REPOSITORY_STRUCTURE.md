# Western Ghats Analysis - Repository Structure

## Core Analysis Scripts (Production)
- `analyze_forest_corrected.py` - Forest typology analysis (corrected threshold)
- `analyze_districts_efficient.py` - District-level urbanization analysis  
- `compare_forest_types_efficient.py` - Spatial comparison old-growth vs plantations
- `forest_agriculture_integration.py` - Core Stack API integration (requires config.py)
- `forest_typology_export_optimized.py` - Export forest classification rasters
- `spatial_analysis_comprehensive.py` - Comprehensive spatial analysis
- `download_district_boundaries.py` - District boundary data preparation

## Visualization Scripts
- `create_animated_visualizations.py` - Animated hotspot visualizations
- `create_final_comparison.py` - Final comparison outputs
- `create_animations_from_gdrive.py` - Google Drive export animations
- `create_animations_from_local_files.py` - Local file animations

## Validation and Inspection
- `validate_forest_outputs.py` - Forest output validation
- `inspect_forest_outputs.py` - Forest output inspection
- `analyze_data_quality.py` - Data quality assessment

## Utility Scripts
- `run_all_analyses.py` - Execute complete analysis pipeline
- `simplified_spatial_analysis.py` - Simplified spatial workflow

## Configuration
- `config_template.py` - Template for API keys (copy to config.py)
- `.gitignore` - Excludes sensitive data and large files

## Documentation
- `QUICK_START.md` - Getting started guide
- `README.md` - Project overview
- `FOREST_TYPOLOGY_METHODOLOGY_EXPLAINED.md` - Methodology details
- `CORE_STACK_ANALYSIS_RESULTS.md` - API coverage findings
- Various analysis summaries in markdown files

## Data Directories
- `Core Stack Content/` - Core Stack API reference notebooks
- `district_boundaries/` - Administrative boundaries
- `outputs/` - Analysis outputs (excluded from git)
- `archive/` - Archived old scripts

## Notes
- API keys stored in `config.py` (gitignored)
- Large data outputs excluded via .gitignore
- See individual scripts for detailed documentation
