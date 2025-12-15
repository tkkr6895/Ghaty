# Western Ghats Spatial Analysis

## About This Project

This repository contains geospatial analysis and research on the Western Ghats biodiversity hotspot, undertaken as a personal project to understand landscape changes, forest ecology, and urbanization patterns across this critical conservation area.

The research explores land use transformations, forest typology, and agricultural pressures across 109,486 km² of the Western Ghats using satellite imagery and geospatial datasets. Analysis and writing from this work are published on my research blog:

**Read the analysis:** [Bettada Jeeva, or the Life of the Hill](https://tkkr.substack.com/p/bettada-jeeva-or-the-life-of-the)

## Project Scope

Comprehensive spatial analysis of the Western Ghats biodiversity hotspot examining:
- Land use and land cover changes (2018-2024)
- Forest typology: Old-growth natural forests vs. commercial plantations
- Urbanization hotspots and built-area expansion
- Agricultural intensification and water balance impacts
- District-level trends across six states (Gujarat, Maharashtra, Goa, Karnataka, Kerala, Tamil Nadu)

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

## Personal Research Context

This work represents independent spatial analysis conducted to better understand the ecological and social dynamics of the Western Ghats. The research combines satellite imagery analysis with field observations and published literature to document landscape transformations in this biodiversity hotspot.

Narrative analysis and interpretation of these findings are published on my research blog. The technical methods, data processing scripts, and spatial outputs in this repository support those published articles.

## Data Sources

- **Dynamic World V1**: Google Earth Engine global LULC dataset (10m resolution)
- **CEPF Boundary**: Conservation Biology Institute Western Ghats ecosystem boundary
- **Hansen Global Forest Change**: Tree cover and loss data (2000-2023)
- **Nature-Trace Natural Forest 2020**: Forest typology classification
- **Core Stack API**: Agricultural and hydrological indicators (limited coverage)
- **Processing Platform**: Google Earth Engine cloud computing platform

## Data and API Configuration

This repository uses external APIs and requires credentials:

1. **Google Earth Engine**: Requires authentication and project setup
2. **Core Stack API**: Copy `config_template.py` to `config.py` and add your API key
3. See `QUICK_START.md` for detailed setup instructions

Sensitive credentials are excluded from version control via `.gitignore`.

---

**Repository**: https://github.com/tkkr6895/Ghaty  
**Research Blog**: https://tkkr.substack.com  
**Contact**: Personal research project - correspondence welcome via Substack

## Key Analyses

### 1. Land Use Land Cover Change (2018-2024)
- Comprehensive LULC classification using Dynamic World V1
- 61% increase in built-up areas
- Tree cover stability at 79% despite development pressure
- Outputs: Statistical summaries, spatial exports, change visualizations

### 2. Forest Typology Assessment
- Classification of old-growth natural forests vs. plantations
- Nature-Trace 2020 dataset analysis
- 18,226 km² old-growth (57.5%), 13,458 km² plantations (42.5%)
- Regional patterns: Southern strongholds vs. coastal conversion

### 3. Urbanization Hotspot Analysis
- District-level built-area expansion (1987-2025)
- Top hotspots: Pune (80x growth), Raigarh (99x), Thane (16x)
- Animated visualizations of urban sprawl
- 87 districts across six states analyzed

### 4. Agricultural Pressure Assessment
- Core Stack API integration attempt (limited Western Ghats coverage)
- Alternative Google Earth Engine methodology developed
- Focus: Cropping intensity impacts on old-growth forests
- Analysis pending implementation

## Repository Structure

```
├── Core Stack Content/             # API reference notebooks and debug tests
├── data/                           # Boundary shapefiles and metadata
├── outputs/                        # Analysis results (gitignored)
│   ├── forest_typology_corrected/
│   ├── district_analysis/
│   └── hotspot_animations/
├── archive/                        # Archived exploratory scripts
├── config_template.py              # API configuration template
├── *.py                            # Analysis scripts (see REPOSITORY_STRUCTURE.md)
└── *.md                            # Documentation and methodology
```

See `REPOSITORY_STRUCTURE.md` for detailed file organization.

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
## License

Analysis code is provided for transparency and reproducibility. Original satellite data and boundary datasets retain their respective licenses. This is a personal research project not affiliated with any institution.
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
