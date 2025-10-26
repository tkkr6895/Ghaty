# Western Ghats Land Use Land Cover (LULC) Analysis

## Project Overview

Comprehensive analysis of land use and land cover changes in the **Western Ghats biodiversity hotspot** using Google Earth Engine's Dynamic World V1 dataset. This project provides detailed insights into ecosystem changes across **109,486 km²** of critical conservation area.

## Key Results Summary

### Regional Coverage
- **Total Area Analyzed**: 109,486 km² (98.2% of Western Ghats boundary)
- **Analysis Period**: 2018, 2020, 2022, 2024
- **Data Source**: Google Earth Engine Dynamic World V1
- **Resolution**: 10m native, processed at optimized scales

### Major Findings

| Year | Total Area (km²) | Tree Cover (%) | Built-up Area (km²) | Built-up (%) |
|------|------------------|----------------|---------------------|--------------|
| 2018 | 108,469         | 77.3           | 2,140              | 1.97         |
| 2020 | 107,858         | 77.9           | 2,653              | 2.46         |
| 2022 | 106,907         | 79.9           | 3,068              | 2.87         |
| 2024 | 106,689         | 79.1           | 3,449              | 3.23         |

### Critical Insights
- **Built-up Growth**: 61.2% increase from 2018-2024 (+1,309 km²)
- **Forest Stability**: Tree cover maintained around 79% despite development pressure
- **Regional Optimization**: Successfully eliminated 75 km² of impossible snow/ice classifications

## **Important Classification Note**
**Dynamic World "Trees" class includes natural forests AND large-scale plantations.** This analysis reports "tree cover" which may include commercial/agricultural plantations and should not be interpreted as natural forest cover per Forest Survey of India definitions. Cross-validation with FSI data recommended for forest-specific analysis.

## 🛠️ Methodology

### Data Processing Pipeline
1. **Boundary Integration**: Official CEPF Western Ghats shapefile with robust geometry validation
2. **Regional Optimization**: Custom probability thresholds eliminating snow/ice (geographically impossible)
3. **Temporal Analysis**: Mode composite from label band for stability across seasons
4. **Quality Control**: Cloud masking (<30%) and comprehensive error handling
5. **Progress Tracking**: Real-time logging throughout 27-minute analysis execution

### Technical Approach
- **Ultra-Robust Analysis**: Mode statistics from Dynamic World label band
- **Geometry Processing**: Fixed invalid polygon geometries, achieved 4,055x coverage improvement  
- **Regional Corrections**: Eliminated snow/ice false positives through probability band optimization
- **Spatial Validation**: Verified complete 6-polygon boundary coverage (109,486 km²)

## Repository Structure

```
├── data/
│   ├── cepfbnd_prj.*           # Official CEPF Western Ghats boundary shapefile
│   └── metadata.md             # Data source documentation
├── outputs/
│   ├── western_ghats_complete_lulc_results_*.csv  # Main analysis results
│   ├── lulc_analysis_charts.png                   # Visualization outputs
│   └── western_ghats_lulc_results.csv            # Summary table
├── methodology/
│   └── analysis_documentation.md                  # Detailed methodology
├── western_ghats_analysis_clean.ipynb            # Complete analysis notebook
└── README.md                                      # This file
```

## Spatial Exports


| Year | Built-up Areas | Barren/Bare Areas |
|------|---------------|-------------------|
| 2018 | `western_ghats_built_2018.shp` | `western_ghats_bare_2018.shp` |
| 2020 | `western_ghats_built_2020.shp` | `western_ghats_bare_2020.shp` |
| 2022 | `western_ghats_built_2022.shp` | `western_ghats_bare_2022.shp` |
| 2024 | `western_ghats_built_2024.shp` | `western_ghats_bare_2024.shp` |

**Specifications**:
- Format: ESRI Shapefile (.shp)
- Resolution: 100m (optimized for analysis)
- Coordinate System: WGS84 / UTM (appropriate zone)
- Ready for QGIS/ArcGIS import

## 🔬 Analysis Validation

### Quality Metrics
- **Complete Regional Coverage**: 98.2% average coverage across all years
- **Regional Accuracy**: Zero snow/ice classifications after optimization
- **Progress Transparency**: Real-time logging throughout analysis execution

### Error Corrections Applied
- Fixed invalid geometry in polygon 5 (116,683 km² boundary issue)
- Eliminated snow/ice false positives (75 km² total corrected)
- Applied regional probability thresholds for Western Ghats ecosystem
- Implemented ultra-robust processing for large-scale analysis stability

## Usage Instructions

### Prerequisites
```python
# Required packages
ee                    # Google Earth Engine API
geopandas            # Geospatial data processing  
pandas               # Data manipulation
matplotlib           # Visualization
```

### Running the Analysis
1. **Authentication**: Configure Google Earth Engine credentials
2. **Execution**: Run `western_ghats_analysis_clean.ipynb` 
3. **Monitoring**: Analysis includes real-time progress updates
4. **Results**: Check `outputs/` folder for CSV results and visualizations

### Earth Engine Task Monitoring
Check Google Earth Engine [Tasks tab](https://code.earthengine.google.com/tasks) for spatial export progress.

## Conservation Implications

### Development Pressure
- **Rapid Urbanization**: 61% increase in built-up areas over 6 years
- **Development Rate**: ~218 km² additional built-up area per year
- **Forest Resilience**: Tree cover maintained despite development pressure

### Biodiversity Hotspot Status
- **Critical Habitat**: 79% tree cover across 109,486 km² 
- **Fragmentation Risk**: Built-up areas concentrated in accessible zones
- **Conservation Priority**: Monitor development corridors for connectivity

## Contributing

This analysis supports Western Ghats conservation research. For questions, improvements, or collaborations:

1. Review methodology in `western_ghats_analysis_clean.ipynb`
2. Validate results using provided spatial exports
3. Extend analysis with additional years or LULC classes
4. Integrate with local conservation planning initiatives

## Data Sources

- **Dynamic World V1**: Google Earth Engine global LULC dataset (10m resolution)
- **CEPF Boundary**: Conservation Biology Institute Western Ghats ecosystem boundary
- **Processing Platform**: Google Earth Engine cloud computing platform

---

**Analysis Completed**: September 16, 2024  
**Repository**: https://github.com/tkkr6895/Ghaty  
**Contact**: Research collaboration welcome for Western Ghats conservation initiatives

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

### Spatial Data Exports 
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
