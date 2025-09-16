# Western Ghats Land Use Land Cover Analysis

Analysis of land use and land cover changes in the Western Ghats biodiversity hotspot using satellite data from Google Earth Engine's Dynamic World dataset.

## **⚠️ Important Classification Note**
**Dynamic World "Trees" class includes natural forests AND large-scale plantations.** This analysis reports "tree cover" which may include commercial/agricultural plantations and should not be interpreted as natural forest cover per Forest Survey of India definitions. Cross-validation with FSI data recommended for forest-specific analysis.

## TODOs
✅ Map Y-o-Y representation of built up area and barren land  
✅ Google Earth & QGIS layer export files for validation  
- Writeup & Publish

## Study Area

The Western Ghats is a UNESCO World Heritage biodiversity hotspot covering approximately 107,000 km² along India's western coast. This analysis focuses on land cover changes from 2018-2024.

## Data Sources and Attribution

This analysis uses data from multiple sources:

### Satellite Data
- **Google Earth Engine Dynamic World V1**: Near real-time global land use/land cover dataset
- **Copernicus Sentinel-2**: European Space Agency satellite program providing optical-NIR imagery
[Year]

### Study Boundary
- **Conservation Biology Institute**: Western Ghats boundary shapefile

### Analysis Platform
- **Google Earth Engine**: Cloud platform for planetary-scale geospatial analysis

## Key Findings

### Built-up Area Expansion (2018-2024)
- Initial area: 2,359 km² (2.2% of study area)
- Final area: 3,739 km² (3.5% of study area)
- Total growth: 58.5% over 6 years
- Average annual growth: 9.8%

### Tree Cover Status (⚠️ Includes Plantations)
- 2018 tree cover: 76.0%
- 2024 tree cover: 77.6%
- Net change: +1.6 percentage points
- Status: Tree cover maintained above 75%
- **Note**: Values include both natural forests and large-scale plantations per Dynamic World classification

## Methodology

The analysis employs a refined approach using Dynamic World probability bands with quality filtering to ensure geographic accuracy. See `methodology/refined_approach.md` for technical details.

## Repository Structure

```
├── data/                          # Input data
│   └── western_ghats_boundary.*   # Study area shapefiles
├── outputs/                       # Analysis results
│   ├── western_ghats_lulc_results.csv
│   └── western_ghats_lulc_trends.png
├── methodology/                   # Technical documentation
│   └── refined_approach.md
└── western_ghats_analysis_clean.ipynb  # Main analysis notebook
```

## Usage

1. Set up Google Earth Engine authentication
2. Install required Python packages: `earthengine-api`, `geopandas`, `matplotlib`, `plotly`
3. Run the Jupyter notebook `western_ghats_analysis_clean.ipynb`

## Outputs and Data Products

### Statistical Analysis
- `outputs/western_ghats_lulc_results.csv` - Area calculations and trends
- `outputs/lulc_analysis_charts.png` - Visualization summaries

### Spatial Data Exports (NEW!)
**Google Drive Folders:**
- `Western_Ghats_LULC_Export/` - GeoTIFF files for GIS analysis
  - Built-up area masks by year (2018, 2020, 2022, 2024)
  - Barren land masks by year
  - Probability layers for uncertainty assessment
  - Full classification layers

### Map Visualizations (NEW!)
- `Western_Ghats_Maps/` - Year-on-year change maps
  - RGB change highlights (Red=Built, Green=Barren, Blue=Trees)
  - Full classification maps with Dynamic World colors
  - Ready for import into QGIS/ArcGIS/Web GIS

### Usage Instructions
1. **For QGIS/ArcGIS**: Import GeoTIFF files for spatial analysis and cartographic production
2. **For Google Earth Engine**: Use exported data for further cloud-based processing
3. **For Web Applications**: Map files suitable for online visualization platforms

## Technical Requirements

- Python 3.8+
- Google Earth Engine account and project
- Required packages listed in notebook

## Citation

If using this analysis or methodology, please cite:

- Google Earth Engine Dynamic World dataset
- Copernicus Sentinel-2 program
- Conservation Biology Institute for boundary data

## Contact

This is an open data package supporting biodiversity conservation research in the Western Ghats region.

## License

Data processing code is provided under MIT License. Original data sources retain their respective licenses.