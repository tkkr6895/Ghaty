# Western Ghats LULC Analysis Outputs# Western Ghats LULC Analysis - Clean Workspace



This directory contains outputs from comprehensive Land Use Land Cover (LULC) analysis of the Western Ghats biodiversity hotspot.## Current Files



## Analysis Coverage### Analysis Results

- `western_ghats_complete_lulc_results_20250916_193422.csv` - Main LULC analysis results (2018-2024)

### Temporal Range- `western_ghats_analysis_metadata_20250916_195923.json` - Analysis metadata and methodology

- **Dynamic World Dataset**: 2018-2023 (annual analysis)- `western_ghats_boundary_20250916_195923.geojson` - Study area boundary (corrected coordinates)

- **GLC-FCS30D Dataset**: 1985-2020 (5-year intervals)

### Visualizations  

### Study Area- `western_ghats_clean_map_20250928_145212.html` - WORKING interactive map (fixed coordinates)

- **Location**: Western Ghats, India- `lulc_analysis_charts.png` - Analysis summary charts

- **Area**: Approximately 140,000 km²- `western_ghats_lulc_trends.png/.pdf` - Temporal trend visualizations

- **Coordinate System**: WGS84 (EPSG:4326)

### Tools

## File Structure- `clean_map_viewer.py` - Interactive map generator (coordinates fixed)

- `results_viewer.py` - HTML report generator  

### Core Data Files- `western_ghats_clean_analysis.ipynb` - Working analysis notebook

- `western_ghats_boundary_20250928_203521.geojson` - Study area boundary

- `western_ghats_lulc_analysis_results_20250928_203521.csv` - Complete LULC statistics## Key Findings (2018-2024)

- `western_ghats_analysis_metadata_20250928_203521.json` - Analysis parameters and metadata

**Study Area**: 109,486 km²

### Interactive Visualizations

- `western_ghats_year_comparison_map_20251001_203751.html` - Year-on-year comparison interface**Tree Cover** (includes plantations):

- `western_ghats_lulc_visualization_20250928_203623.png` - Static trend charts- 2018: 77.3%  

- 2024: 79.1%

### Python Scripts- Change: +1.8 percentage points

- `year_comparison_lulc_map.py` - Year-on-year comparison map generator

- `advanced_interactive_lulc_map.py` - Advanced interactive map generation**Built-up Areas**:

- 2018: 1,972 km²

### Configuration- 2024: 3,232 km²  

- `requirements.txt` - Python package dependencies- Growth: +63.9%



## Interactive Map Features**Note**: Tree cover classification includes both natural stands AND plantations per Dynamic World methodology.



The HTML maps provide comprehensive analysis tools:## Fixed Issues

- Year-on-year comparison with dropdown selectors

- Individual class layers (Trees, Built, Crops, Bare, Water, Grass, Shrub)1. **Coordinate System**: Boundary data now properly converted from UTM to WGS84

- Temporal difference maps showing change patterns2. **Interactive Map**: No more Arctic markers - map centers correctly on Western Ghats

- Quantitative statistics for selected time periods3. **Clean Workspace**: Removed redundant and deprecated files

- Multiple basemap options (OpenStreetMap, Satellite, Terrain)4. **Working Notebook**: Simple, functional analysis pipeline

- Global geocoding search

- Screenshot mode for clean exports## Usage

- Collapsible UI panels

1. **View Results**: Open `western_ghats_clean_map_20250928_145212.html` in browser

## Data Sources and Methods2. **Run New Analysis**: Use `western_ghats_clean_analysis.ipynb` 

3. **Generate Reports**: Run `python results_viewer.py` in outputs folder

### Dynamic World (2018-2023)

- **Resolution**: 10 metersThe interactive map now correctly shows the Western Ghats region in India with proper satellite imagery overlays.
- **Source**: Google Earth Engine
- **Method**: Probability band optimization with regional thresholds

### GLC-FCS30D (1985-2020)
- **Resolution**: 30 meters  
- **Source**: Google Earth Engine
- **Method**: 5-year interval analysis for long-term trends

## Land Cover Classes

1. **Trees**: Natural forests and plantations
2. **Built**: Urban and built-up areas
3. **Crops**: Agricultural land and croplands
4. **Bare**: Bare ground, quarries, mining areas
5. **Water**: Water bodies and rivers
6. **Grass**: Grasslands and meadows
7. **Shrub and Scrub**: Scrubland and degraded forest

## Usage Instructions

1. Open HTML files in any modern web browser
2. Use dropdown menus to select years for comparison
3. Toggle layers using the layer control panel
4. Adjust opacity for better overlay visualization
5. Use screenshot mode for presentations
6. Refer to parent directory notebooks for analysis code

## Analysis Notebooks

See parent directory for Jupyter notebooks:
- `western_ghats_clean_analysis.ipynb` - Dynamic World analysis (2018-2023)
- `western_ghats_historical_analysis.ipynb` - GLC-FCS30D analysis (1985-2020)
