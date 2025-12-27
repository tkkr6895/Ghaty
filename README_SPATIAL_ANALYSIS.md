# Western Ghats LULC Analysis - Enhanced Spatial Analysis and Visualizations

## Analysis overview

This analysis suite provides spatial insights into Western Ghats land use and land cover change across multiple time periods.

### Generated: November 1, 2025

---

## What's included

### 1. Deeper spatial analysis (`spatial_analysis_comprehensive.py`)
- Urbanization hotspot detection (kernel density)
- Protected area analysis (inside vs outside WDPA protected areas)
- Elevation stratification (0-200m, 200-500m, 500-1000m, >1000m)
- District-level breakdown (requires uploading Census 2011 boundaries)
- Change detection maps (Forest to Built, Forest to Crops, etc.)
- Distance-to-cities gradient
- Forest fragmentation (edge density and patch metrics)

### 2. Enhanced visualizations (`create_animated_visualizations.py`)
- Animated time-series outputs
- Hotspot zoom outputs (selected locations)
- Change intensity maps
- Before/after imagery for storytelling

---

## Quick start

### Step 1: Run the Spatial Analysis

```bash
python spatial_analysis_comprehensive.py
```

**This will:**
- Submit ~11 export tasks to Google Earth Engine
- Generate maps: urbanization hotspots, change detection, elevation overlay, protected areas
- Calculate statistics for protected areas, elevation bands, and distance gradients

**Outputs:**
- Google Drive folder: `Western_Ghats_Spatial_Analysis/`
- Local metadata: `outputs/spatial_analysis_metadata_YYYYMMDD_HHMMSS.json`

### Step 2: Run the Animation Generator

```bash
python create_animated_visualizations.py
```

**This will:**
- Submit ~90+ export tasks to Google Earth Engine
- Generate individual frames for:
  - 39 full Western Ghats frames (1987-2025)
  - ~50 hotspot zoom frames
  - ~8 change intensity maps

**Outputs:**
- Google Drive folder: `Western_Ghats_Animations/`
- Local script: `outputs/animations/create_gifs_from_exports.py`

### Step 3: Enable District-Level Analysis (Optional)

```bash
python download_district_boundaries.py
```

**This will:**
- Download India Census 2011 district shapefiles from DataMeet GitHub
- Extract to `data/district_boundaries/`
- Provide instructions for uploading to Google Earth Engine

**After uploading to GEE:**
1. Update `spatial_analysis_comprehensive.py` line ~170:
   ```python
   districts = ee.FeatureCollection('users/YOUR_USERNAME/india_districts_2011')
   ```
2. Re-run the spatial analysis to get district-level statistics

### Step 4: Create Animated GIFs (After Exports Complete)

1. **Download all frames** from Google Drive folder `Western_Ghats_Animations/`
2. **Update path** in `outputs/animations/create_gifs_from_exports.py`
3. **Install dependencies**:
   ```bash
   pip install imageio pillow numpy
   ```
4. **Run the script**:
   ```bash
   python outputs/animations/create_gifs_from_exports.py
   ```

**Outputs:**
- `western_ghats_1987_2025.gif` - Full time-lapse
- `hotspot_Wayanad.gif` - Wayanad zoom
- `hotspot_Kodagu.gif` - Kodagu zoom
- `hotspot_Goa.gif` - Goa zoom
- `hotspot_Bangalore_Periphery.gif` - Bangalore zoom
- `hotspot_Munnar.gif` - Munnar zoom
- `change_intensity_1987_2025.gif` - Change highlights

---

## 📍 Analyzed Hotspots

### 1. **Wayanad, Kerala**
- **Coordinates**: 11.61°N, 76.08°E
- **Focus**: Tourism & development impact
- **Expected Changes**: Rapid hotel/resort construction, forest fragmentation

### 2. **Kodagu (Coorg), Karnataka**
- **Coordinates**: 12.42°N, 75.74°E
- **Focus**: Coffee estates + real estate boom
- **Expected Changes**: Estate expansion, weekend homes, homestays

### 3. **Goa**
- **Coordinates**: 15.36°N, 74.12°E
- **Focus**: Mining & coastal tourism
- **Expected Changes**: Quarrying impacts, resort development

### 4. **Bangalore Periphery**
- **Coordinates**: 12.80°N, 77.30°E
- **Focus**: Rapid urban sprawl
- **Expected Changes**: Massive built area expansion, peri-urban growth

### 5. **Munnar, Kerala**
- **Coordinates**: 10.09°N, 77.06°E
- **Focus**: Tea plantations & tourism
- **Expected Changes**: Plantation expansion, tourism infrastructure

---

## 📊 Key Analyses Explained

### Protected Area Effectiveness
**Question**: Are protected areas actually protecting forests?

**Method**:
- Compare LULC changes inside WDPA protected areas vs outside
- Calculate forest loss rates in protected vs unprotected regions
- Identify protected areas with significant encroachment

**Output**: CSV with yearly statistics for each protection level

---

### Elevation Stratification
**Question**: Are lowlands urbanizing faster than highlands?

**Method**:
- Divide Western Ghats into 4 elevation bands using SRTM DEM
- Calculate LULC areas for each band over time
- Identify elevation-specific trends

**Hypothesis**: Lowlands (0-200m) experiencing faster urbanization, highlands (>1000m) more stable

**Output**: Statistics showing LULC distribution across elevation zones

---

### Distance-to-Cities Gradient
**Question**: How far is urban influence spreading?

**Method**:
- Create distance buffers from 8 major cities (Bangalore, Mangalore, Kochi, etc.)
- Measure LULC changes at distances: 0-10km, 10-25km, 25-50km, 50-75km, 75-100km, 100-150km, 150-200km
- Track forest loss and built area gain by distance band

**Expected Pattern**: Rapid urbanization near cities, decreasing with distance

**Output**: Gradient statistics for storytelling (e.g., "Forest loss extends 100km from Bangalore")

---

### Urbanization Hotspots
**Question**: Where exactly is development concentrating?

**Method**:
- Identify new built area (2025 - 1987)
- Apply Gaussian kernel density to create "heat map"
- Extract top 10 hotspot coordinates

**Use Case**: Target specific locations for detailed case studies

**Output**: Heatmap showing concentration of urban growth

---

### Change Detection
**Question**: What are the dominant land use transitions?

**Method**:
- Compare 1987 vs 2025 classifications pixel-by-pixel
- Identify 4 critical transitions:
  1. **Forest → Built**: Direct deforestation for urban development
  2. **Forest → Crops**: Agricultural expansion into forests
  3. **Grass → Built**: Development on grasslands/shrublands
  4. **Crops → Built**: Urban sprawl consuming farmland

**Output**: 4 separate maps highlighting each transition type

---

### Forest Fragmentation
**Question**: Are forests becoming more isolated?

**Method**:
- Calculate edge pixels (forest adjacent to non-forest)
- Track edge density over time
- Higher edge density = more fragmentation

**Interpretation**:
- **Increasing edge density**: Forests breaking into smaller patches
- **Decreasing edge density**: Forest consolidation or loss

**Output**: Time-series of fragmentation metrics

---

## Expected results (use with care)

Built-up area and other change rates are sensitive to sensor resolution and dataset choice. Do not compute change rates by mixing incompatible datasets across time.

Practical approach used in this repository:

- 1987-2015 trends: use GLC-FCS30D consistently
- 2018+ trends: use Dynamic World consistently

### Example summary statistics

- 1987-2015 (GLC-FCS30D): built-up area increased about 4x in the Western Ghats boundary used in this workspace
- 2018-2024 (Dynamic World): built-up area increased about 61% over that period in the same boundary

### Spatial Patterns (Hypothesized)
1. **Lowland Squeeze**: Urbanization concentrated 0-500m elevation
2. **City Sprawl**: Rapid growth within 50km of Bangalore, Kochi, Mangalore
3. **Protected Area Pressure**: Encroachment at protected area boundaries
4. **Hotspot Corridors**: Development along highway corridors (NH 275, NH 66)
5. **Tourism Zones**: Wayanad, Kodagu, Munnar showing mixed patterns (forests + development)

---

## Visualization guide

### For Your Substack Post

#### 1. **Opening Image**: Full Western Ghats GIF
- Use `western_ghats_1987_2025.gif`
- Caption: "Watch 38 years of change unfold: Western Ghats 1987-2025"
- Impact: Immediate visual proof of change

#### 2. **Hotspot Deep-Dives**: Individual Location GIFs
- Embed 2-3 hotspot GIFs (Wayanad, Bangalore, Kodagu)
- Caption with specific statistics
- Example: "Wayanad: Built area grew 450% since 1987"

#### 3. **Change Detection Maps**: Static Images
- Use forest→built transition map
- Overlay on basemap
- Red highlights show exactly where forests became cities

#### 4. **Elevation Chart**: Create from elevation statistics
- X-axis: Elevation band
- Y-axis: % Built area
- Show 1987 vs 2025 bars
- Message: "Lowlands urbanizing 3x faster than highlands"

#### 5. **Distance Gradient Graph**: Create from gradient statistics
- X-axis: Distance from Bangalore (km)
- Y-axis: Forest cover (%)
- Show decay curve
- Message: "Urban influence extends 100+ km from cities"

#### 6. **Protected Area Comparison**: Bar chart
- Inside PA: +X% forest change
- Outside PA: +Y% forest change
- Message: "Protected areas working, but not perfect"

---

## 🔬 Next Steps: Causal Linkages

### Phase 3 Analyses (To Be Implemented)

#### 1. Population Growth Correlation
**Data Source**: Census 2001, 2011, 2021 (district-level)
**Method**: Correlate urban growth with population increase
**Expected Finding**: Urban sprawl outpacing population (low-density development)

#### 2. Road Network Impact
**Data Source**: OpenStreetMap highway data or government road network
**Method**: Buffer analysis around highways, measure LULC changes
**Expected Finding**: Development corridors along NH 275, NH 66, NH 544

#### 3. Economic Activity Zones
**Data Sources**:
- Mining leases (Goa, Karnataka)
- Tea/coffee plantation boundaries
- Tourism infrastructure (hotels, resorts)

**Method**: Overlay with LULC changes
**Expected Finding**: Direct correlation between economic activity and forest loss

#### 4. Climate Patterns
**Data Sources**:
- CHIRPS rainfall data
- MODIS temperature data
- NDVI trends

**Method**: Time-series analysis of climate vs LULC
**Expected Finding**: Drying patterns correlating with forest stress

---

## 📁 File Structure

```
Western Ghats/
├── spatial_analysis_comprehensive.py      # Main spatial analysis
├── create_animated_visualizations.py      # Animation generator
├── download_district_boundaries.py        # District data downloader
├── data/
│   └── district_boundaries/               # Census 2011 shapefiles
├── outputs/
│   ├── animations/
│   │   ├── create_gifs_from_exports.py   # Local GIF generator
│   │   ├── western_ghats_1987_2025.gif
│   │   └── hotspot_*.gif
│   ├── spatial_analysis_metadata_*.json   # Analysis metadata
│   └── complete_lulc_dashboard_*.html     # Existing dashboards
└── README_SPATIAL_ANALYSIS.md             # This file
```

---

## ⏱️ Timeline Estimate

### GEE Export Tasks
- Spatial analysis exports: **1-2 hours**
- Animation frame exports: **3-6 hours**
- Total wait time: **4-8 hours** (depending on GEE queue)

### Local Processing
- Download from Google Drive: **30-60 minutes** (depending on internet)
- GIF generation: **5-10 minutes**
- Total local time: **~1 hour**

### Overall
- **Start to finish**: 5-9 hours (mostly automated waiting)
- **Active work**: ~30 minutes (running scripts, downloading)

---

## 🛠️ Troubleshooting

### Issue: "Districts not available"
**Solution**: Run `download_district_boundaries.py`, upload to GEE, update script

### Issue: GEE exports failing
**Possible causes**:
- Memory limit exceeded → Increase `scale` parameter (e.g., 30 → 100)
- Timeout → Break into smaller regions
- Asset not found → Check GEE asset paths

### Issue: GIF generation failing
**Possible causes**:
- Missing dependencies → `pip install imageio pillow numpy`
- Wrong file path → Update path in `create_gifs_from_exports.py`
- Corrupt frames → Re-download from Google Drive

### Issue: Out of memory during local processing
**Solution**: Process frames in batches, reduce image resolution

---

## 📚 Data Sources

### Satellite Data
- **GLC-FCS30D** (1987-2015): 30m global land cover, University of Maryland
- **Dynamic World V1** (2018-2025): 10m near-real-time, Google + WRI

### Auxiliary Data
- **SRTM DEM**: 30m elevation, USGS
- **WDPA**: Protected areas, UNEP-WCMC
- **Census 2011**: District boundaries, DataMeet (GOI data)

### Processing
- **Google Earth Engine**: Cloud-based geospatial analysis
- **Python**: Local statistics and GIF generation

---

## 📖 Citation

If using this analysis in publications:

```
Western Ghats Land Use/Land Cover Analysis (1987-2025)
Data: GLC-FCS30D (Potapov et al.), Dynamic World (Google/WRI)
Processing: Google Earth Engine + Python
Analysis Date: November 2025
```

---

## 🤝 Support

For questions or issues:
1. Check this README
2. Review script comments
3. Check GEE documentation: https://developers.google.com/earth-engine

---

## ✅ Checklist for Your Substack Story

- [ ] Run `spatial_analysis_comprehensive.py`
- [ ] Run `create_animated_visualizations.py`
- [ ] Monitor GEE tasks (4-8 hours)
- [ ] Download all exports from Google Drive
- [ ] Run `create_gifs_from_exports.py`
- [ ] Upload district boundaries (optional)
- [ ] Create static charts from statistics
- [ ] Write narrative around visualizations
- [ ] Embed GIFs and maps in Substack
- [ ] Publish! 🚀

---

**Generated**: November 1, 2025  
**Version**: 1.0  
**Status**: Ready for execution
