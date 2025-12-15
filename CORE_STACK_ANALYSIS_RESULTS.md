# Core Stack API Analysis Results
## Western Ghats Forest-Agriculture Integration

**Date:** December 14, 2024  
**API Key Status:** Valid  
**Analysis Status:** Coverage limitation identified

---

## EXECUTIVE SUMMARY

**KEY FINDING:** The Core Stack API does not currently have data coverage for the Western Ghats region. The API's geographic scope appears limited to northern and central India states (Uttar Pradesh, Bihar, Jharkhand, etc.), as evidenced by:

1. All 8 priority grid cells in Western Ghats returned **404 (Not Found)** responses
2. Example notebooks provided in Core Stack documentation focus on Uttar Pradesh and Bihar
3. API specification shows data organized by State → District → Tehsil hierarchy, likely covering MGNREGA-focused regions

**Testing Results:**
- Grid cells tested: 8 (covering Karnataka, Kerala, Goa, Tamil Nadu in Western Ghats)
- Successful MWS linkages: 0
- Coverage status: **No Western Ghats coverage confirmed**

---

## TESTED LOCATIONS

All locations returned `404 - Location not in Core Stack coverage`:

| Grid ID | Coordinates | Region | Forest Type | Coverage |
|---------|-------------|--------|-------------|----------|
| 12 | 12.5°N, 75.5°E | Kodagu, Karnataka | 61.3% plantation (coffee estates) | ❌ Not covered |
| 13 | 13.5°N, 75.5°E | Karnataka-Kerala border | 54.2% plantation (mixed) | ❌ Not covered |
| 20 | 12.5°N, 76.5°E | Central Karnataka | 55.6% plantation | ❌ Not covered |
| 22 | 9.5°N, 77.5°E | Kerala-Tamil Nadu border | 84.7% old-growth | ❌ Not covered |
| 18 | 10.5°N, 76.5°E | Wayanad-Idukki, Kerala | 79.1% old-growth | ❌ Not covered |
| 21 | 8.5°N, 77.5°E | Southern Western Ghats | 85.2% old-growth | ❌ Not covered |
| 0 | 15.5°N, 73.5°E | Coastal Karnataka | 96.5% plantation | ❌ Not covered |
| 1 | 16.5°N, 73.5°E | Goa-Karnataka border | 96.8% plantation | ❌ Not covered |

---

## ALTERNATIVE DATA SOURCES FOR ANALYSIS

Given the Core Stack API limitation, here are **high-quality alternative approaches** to answer the research question: *"Is changing crop intensity a risk to old-growth forests in Western Ghats?"*

### 🌟 **Option 1: Google Earth Engine (GEE) - RECOMMENDED**

**Advantages:**
- Already using GEE for forest typology analysis (proven workflow)
- Complete Western Ghats coverage
- High temporal resolution (2000-2024)
- Free for research use

**Available Datasets:**

#### 1. **Cropping Intensity (MODIS NDVI-based)**
- **Dataset:** MODIS/006/MOD13Q1 (250m, 16-day)
- **Time series:** 2000-2024
- **Method:** Calculate cropping cycles from NDVI peaks per year
  - 1 peak = single cropping
  - 2 peaks = double cropping
  - 3 peaks = triple cropping
- **Trend analysis:** Compare 2017-2023 with 2000-2010 baseline

#### 2. **Agricultural Intensity (Sentinel-2 NDVI)**
- **Dataset:** COPERNICUS/S2 (10m, 5-day)
- **Time series:** 2015-2024
- **Advantage:** Higher resolution than MODIS, better for plantation vs. agroforestry distinction
- **Method:** NDVI variance analysis
  - High variance = annual crops (intensive)
  - Low variance = perennial crops (sustainable agroforestry)

#### 3. **Water Balance Components**
- **Dataset:** TerraClimate (4km, monthly)
  - Precipitation, ET, runoff, soil moisture (1958-2023)
- **Dataset:** CHIRPS (Precipitation, 5km, daily, 1981-2024)
- **Dataset:** MODIS ET (MOD16A2, 500m, 8-day)
- **Analysis:** Calculate water deficit trends
  - Water deficit = Precipitation - (ET + Runoff)
  - Compare old-growth forest zones vs. plantation zones
  - Identify drought stress hotspots (2017-2023)

#### 4. **Land Use Intensity (Dynamic World)**
- **Dataset:** GOOGLE/DYNAMICWORLD/V1 (10m, 2015-2024)
- **Classes:** Crops, trees, grass, water, built, bare
- **Method:** Track transition patterns
  - Forest → Crops = direct conversion
  - Trees → Crops (within plantation zones) = intensification
  - Crop class probability trends = intensity changes

#### 5. **Irrigation Infrastructure (Surface Water Dynamics)**
- **Dataset:** JRC Global Surface Water (30m, 1984-2021)
- **Method:** Map waterbody expansion/decline
- **Hypothesis:** Waterbody expansion = irrigation investment = intensification
- **Link:** Waterbody proximity to old-growth forests = pressure indicator

---

### **Option 2: Indian Government Open Data**

#### 1. **Agriculture Census (agriccensus.nic.in)**
- **Data:** District-level cropping intensity (2015-16 census available)
- **Coverage:** All 87 Western Ghats districts
- **Metrics:**
  - Net sown area, gross cropped area
  - Cropping intensity = (Gross cropped / Net sown) × 100
  - Irrigation coverage (%)
  - Major crops by district
- **Analysis:** Compare high-intensity districts with forest loss data

#### 2. **FAOSTAT (Food and Agriculture Organization)**
- **Data:** State-level agricultural statistics (2000-2022)
- **Metrics:**
  - Crop production (tonnes)
  - Area harvested (hectares)
  - Yield (tonnes/ha)
- **States:** Karnataka, Kerala, Tamil Nadu, Maharashtra, Goa
- **Analysis:** Link production trends with forest loss in Western Ghats

#### 3. **India Water Resources Information System (WRIS)**
- **URL:** https://indiawris.gov.in/wris/
- **Data:** Watershed-level water balance
  - Precipitation, runoff, groundwater
  - Reservoir storage
  - Irrigation statistics
- **Coverage:** Western Ghats watersheds
- **Method:** Download basin reports, extract hydrological trends

#### 4. **Forest Survey of India (FSI) Reports**
- **Data:** State of Forest Reports (biennial, 2001-2023)
- **Coverage:** District-level forest cover change
- **Metrics:**
  - Very dense forest, moderately dense, open forest
  - Forest cover change (km² gain/loss)
- **Analysis:** Correlate with agricultural expansion

---

### **Option 3: Academic Datasets & Research Collaborations**

#### 1. **LDSF (Land Degradation Surveillance Framework)**
- **Source:** ICRAF (World Agroforestry Centre)
- **Coverage:** Sample-based field data in Western Ghats
- **Metrics:** Soil health, tree cover, crop diversity
- **Advantage:** Ground truth for agroforestry systems

#### 2. **GFSAD (Global Food Security-support Analysis Data)**
- **Source:** USGS/NASA
- **Dataset:** Global cropland extent (30m, 2015)
- **Advantage:** Distinguishes irrigated vs. rainfed croplands
- **Method:** Overlay with forest typology to identify intensive zones

#### 3. **Coffee Board of India Data**
- **Relevance:** Kodagu (Grid 12) is major coffee region
- **Data:** Plantation area, production statistics (1990-2023)
- **Method:** Track coffee intensification trends
  - Traditional shade-grown vs. sun coffee conversion
  - Link with old-growth forest proximity

---

## PROPOSED IMPLEMENTATION: GEE-BASED ANALYSIS

### **Phase 1: Cropping Intensity from MODIS NDVI (2000-2023)**

```javascript
// Google Earth Engine Script
var wg_boundary = ee.FeatureCollection('path/to/western_ghats_boundary');

// Load MODIS NDVI
var modis = ee.ImageCollection('MODIS/006/MOD13Q1')
  .filterBounds(wg_boundary)
  .select('NDVI')
  .filterDate('2017-01-01', '2023-12-31');

// Annual NDVI time series
var years = ee.List.sequence(2017, 2023);

var croppingIntensity = ee.ImageCollection.fromImages(
  years.map(function(year) {
    var annual = modis.filterDate(
      ee.Date.fromYMD(year, 1, 1),
      ee.Date.fromYMD(year, 12, 31)
    );
    
    // Count NDVI peaks (simplified: count values >6000)
    var peaks = annual.map(function(img) {
      return img.gt(6000);
    }).sum();
    
    // Classify: 1 peak = single, 2 = double, 3 = triple
    var intensity = peaks.clamp(1, 3);
    
    return intensity.set('year', year);
  })
);

// Export for analysis
Export.image.toDrive({
  image: croppingIntensity.mean(),
  description: 'WG_CroppingIntensity_2017_2023',
  scale: 250,
  region: wg_boundary,
  maxPixels: 1e13
});
```

### **Phase 2: Water Balance Analysis (TerraClimate)**

```javascript
// Load TerraClimate
var terraclimate = ee.ImageCollection('IDAHO_EPSCOR/TERRACLIMATE')
  .filterBounds(wg_boundary)
  .filterDate('2017-01-01', '2023-12-31');

// Calculate water deficit
var waterDeficit = terraclimate.map(function(img) {
  var precip = img.select('pr');
  var et = img.select('aet');
  var runoff = img.select('ro');
  var deficit = precip.subtract(et.add(runoff));
  return deficit.set('system:time_start', img.get('system:time_start'));
});

// Annual mean deficit
var annualDeficit = ee.ImageCollection.fromImages(
  years.map(function(year) {
    return waterDeficit.filterDate(
      ee.Date.fromYMD(year, 1, 1),
      ee.Date.fromYMD(year, 12, 31)
    ).mean().set('year', year);
  })
);

// Overlay with forest typology
var oldGrowth = ee.Image('path/to/old_growth_mask');
var plantations = ee.Image('path/to/plantation_mask');

// Compare water deficit: old-growth vs. plantation zones
var ogDeficit = annualDeficit.map(function(img) {
  return img.updateMask(oldGrowth);
});

var plantDeficit = annualDeficit.map(function(img) {
  return img.updateMask(plantations);
});
```

### **Phase 3: Agroforestry Classification (Sentinel-2 NDVI Variance)**

```javascript
// Load Sentinel-2
var s2 = ee.ImageCollection('COPERNICUS/S2_SR')
  .filterBounds(wg_boundary)
  .filterDate('2020-01-01', '2023-12-31')
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20));

// Calculate NDVI
var addNDVI = function(img) {
  var ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI');
  return img.addBands(ndvi);
};

var s2ndvi = s2.map(addNDVI).select('NDVI');

// NDVI variance (high = intensive annual crops, low = perennial/forest)
var ndviVariance = s2ndvi.reduce(ee.Reducer.stdDev());

// Classify:
// - Low variance (<0.1) + trees = shade-grown coffee/agroforestry
// - High variance (>0.2) + crops = intensive annual cropping
var sustainable = ndviVariance.lt(0.1);
var intensive = ndviVariance.gt(0.2);

// Overlay with forest proximity
// (Calculate distance to old-growth forests)
var oldGrowthDist = oldGrowth.fastDistanceTransform().sqrt()
  .multiply(ee.Image.pixelArea().sqrt());

// Risk zones: intensive cropping within 5 km of old-growth
var riskZone = intensive.and(oldGrowthDist.lt(5000));
```

---

## RESEARCH QUESTIONS - REVISED APPROACH

### **Q1: Do shade-grown regions maintain higher old-growth forest %?**

**Method (without Core Stack):**
1. Use Sentinel-2 NDVI variance to classify:
   - Low variance + high NDVI = shade-grown coffee/cardamom (sustainable)
   - High variance + seasonal NDVI = intensive annual crops
2. Overlay with forest typology (old-growth vs. plantation masks)
3. Calculate old-growth % in 5 km buffer around each classification
4. Statistical test: t-test comparing old-growth % between sustainable vs. intensive zones

**Expected finding:** Shade-grown zones have 20-30% higher old-growth forest retention

---

### **Q2: Is water balance more stable in sustainable agroforestry zones?**

**Method (without Core Stack):**
1. Use TerraClimate to calculate water deficit (2017-2023)
2. Overlay with agroforestry classification (sustainable vs. intensive)
3. Compare:
   - Mean water deficit (should be lower in sustainable zones)
   - Deficit variability (standard deviation - should be lower)
   - Trend (intensifying deficit indicates stress)

**Expected finding:** Sustainable zones have 15-25% lower water deficit and more stable inter-annual patterns

---

### **Q3: Does cropping intensification correlate with forest loss?**

**Method (without Core Stack):**
1. Calculate cropping intensity trends (2000-2023) from MODIS NDVI peaks
2. Identify areas with increasing intensity (2017-2023 > 2010-2016)
3. Overlay with Hansen forest loss (2017-2023)
4. Spatial correlation analysis:
   - Regions with +0.5 increase in cropping intensity
   - Forest loss within 10 km radius

**Expected finding:** 30-40% of forest loss occurs within 5 km of areas with increasing cropping intensity

---

### **Q4: Are there tangible benefits to sustainable practices?**

**Metrics for comparison:**

| **Metric** | **Shade-Grown (Expected)** | **Intensive (Expected)** | **Data Source** |
|------------|---------------------------|--------------------------|-----------------|
| Old-growth retention | 60-70% within 5 km | 30-40% within 5 km | Forest typology + buffer analysis |
| Water deficit | 50-100 mm/year | 150-250 mm/year | TerraClimate |
| Soil moisture | Higher (0.2-0.3) | Lower (0.1-0.2) | TerraClimate |
| NDVI stability (CV) | <15% | >25% | Sentinel-2 time series |
| Biodiversity proxy (tree cover density) | 60-80% | 20-40% | Dynamic World |

**Agricultural output (from govt data):**
- Coffee yield (Karnataka): Shade-grown ~800 kg/ha, intensive ~1200 kg/ha (short-term)
- Sustainability: Shade-grown maintains yield over decades, intensive shows decline after 10-15 years

---

## IMPLEMENTATION TIMELINE

### **Week 1: Data Acquisition & Processing**
- [ ] Export MODIS NDVI cropping intensity (2017-2023) from GEE
- [ ] Export TerraClimate water balance components (2017-2023)
- [ ] Export Sentinel-2 NDVI variance for agroforestry classification
- [ ] Download FSI district-level forest change data

### **Week 2: Spatial Analysis**
- [ ] Overlay cropping intensity with forest typology
- [ ] Calculate buffer zones (5 km, 10 km) around old-growth forests
- [ ] Classify sustainable vs. intensive agricultural zones
- [ ] Distance analysis (agriculture → forest edge)

### **Week 3: Statistical Analysis & Validation**
- [ ] Compare water balance: sustainable vs. intensive zones
- [ ] Correlation: cropping intensity change vs. forest loss (2017-2023)
- [ ] District-level aggregation (87 Western Ghats districts)
- [ ] Cross-validation with FSI data, Agriculture Census

### **Week 4: Visualization & Reporting**
- [ ] Risk maps (high-pressure zones)
- [ ] Time series charts (intensity, water deficit, forest loss)
- [ ] District rankings (conservation priority vs. intervention needed)
- [ ] Final report with policy recommendations

---

## EXPECTED DELIVERABLES

1. **Cropping Intensity Map (2017-2023)**
   - Raster: Single/double/triple cropping classification
   - Trend map: Areas with increasing intensity
   - Format: GeoTIFF, 250m resolution

2. **Water Balance Analysis**
   - Deficit maps (annual mean, 2017-2023)
   - Comparison charts: Old-growth vs. plantation zones
   - Drought stress hotspots

3. **Agroforestry Classification**
   - Shade-grown zones (sustainable)
   - Intensive annual crop zones (high pressure)
   - Transition/mixed zones

4. **Risk Assessment Map**
   - Combined: Cropping intensity + water stress + forest proximity
   - Color-coded: Green (low risk) → Red (high risk)
   - Districts prioritized for intervention

5. **Statistical Report**
   - T-tests: Sustainable vs. intensive zone comparisons
   - Correlation coefficients: Intensity vs. forest loss
   - Regression models: Water deficit ~ cropping intensity + forest cover

6. **Policy Brief**
   - Districts requiring buffer zone enforcement
   - Incentive programs for sustainable agroforestry
   - Water conservation priorities

---

## CONCLUSION

While the Core Stack API does not cover Western Ghats, **alternative data sources are sufficient and arguably superior** for answering the research questions:

**Advantages of GEE-based approach:**
- ✅ Complete Western Ghats coverage (109,065 km²)
- ✅ Higher spatial resolution (10-30m vs. MWS aggregates)
- ✅ Longer time series (2000-2024 vs. 2017-2023)
- ✅ Direct integration with existing forest typology analysis
- ✅ Free and reproducible

**Core Stack would have provided:**
- MWS-level aggregation (convenient but not essential)
- Pre-computed cropping intensity (can be calculated from NDVI)
- Waterbody metadata (available from JRC Global Surface Water)

**Recommendation:** Proceed with GEE-based analysis outlined above. This will provide comprehensive, high-resolution answers to all research questions while maintaining full control over methodology and data quality.

**Next steps:**
1. Confirm approach with user
2. Develop GEE scripts for cropping intensity and water balance
3. Run exports and begin spatial analysis
4. Generate preliminary findings within 1 week

---

**Analysis Status:** Core Stack API limitation documented, alternative approach designed and ready for implementation.
