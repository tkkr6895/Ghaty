# Western Ghats Land Use Land Cover Analysis

Analysis of land use and land cover changes in the Western Ghats biodiversity hotspot using satellite data from Google Earth Engine's Dynamic World dataset.


## TODOs
- Map Y-o-Y representation of built up area and barren land
- Google Earth & QGIS layer export files for validation
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

### Forest Conservation
- 2018 forest coverage: 76.0%
- 2024 forest coverage: 77.6%
- Net change: +1.6 percentage points
- Status: Forest cover maintained above 75%

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