# Forest Typology & Agricultural Pressure Analysis
## Core Stack API Integration Strategy

**Analysis Date:** December 14, 2024  
**Objective:** Link cropping intensity and agricultural trends with old-growth forest conservation risk

---

## PART 1: SPATIAL ANALYSIS SUMMARY

### Forest Type Distribution
- **Old-growth natural forests:** 18,226 km² (57.5% of forest)
- **Plantations:** 13,458 km² (42.5% of forest)  
- **Ratio:** 1.35:1 (old-growth : plantation)

### Key Regional Findings

#### 🌲 OLD-GROWTH FOREST HOTSPOTS (Priority Conservation Areas)
1. **Grid 22** (9.5°N, 77.5°E): 2,620 km² old-growth (84.7% of forest)
   - **Location:** Southern Western Ghats (Kerala-Tamil Nadu border)
   - **Status:** High old-growth concentration, low plantation pressure

2. **Grid 18** (10.5°N, 76.5°E): 2,331 km² old-growth (79.1% of forest)
   - **Location:** Central Kerala (Wayanad-Idukki region)
   - **Status:** Strong old-growth dominance

3. **Grid 13** (13.5°N, 75.5°E): 2,167 km² old-growth (45.8% of forest) 
   - **Location:** Karnataka-Kerala border (Kodagu-Kasaragod)
   - **Status:** ⚠️ **MIXED ZONE** - High plantation pressure (54.2%)

4. **Grid 12** (12.5°N, 75.5°E): 2,096 km² old-growth (38.7% of forest)
   - **Location:** Central Karnataka (Kodagu district)
   - **Status:** ⚠️ **HIGH RISK** - Plantation-dominated (61.3%)

5. **Grid 8** (14.5°N, 74.5°E): 1,801 km² old-growth (73.1% of forest)
   - **Location:** Northern Karnataka (Uttara Kannada)
   - **Status:** Relatively stable

#### 🌾 PLANTATION HOTSPOTS (High Agricultural Intensity)
1. **Grid 12** (12.5°N, 75.5°E): 3,325 km² plantation (61.3% of forest)
   - **Context:** Coffee estates in Kodagu, Karnataka
   - **Risk:** Intensifying agriculture adjacent to old-growth

2. **Grid 13** (13.5°N, 75.5°E): 2,561 km² plantation (54.2% of forest)
   - **Context:** Coffee, cardamom, rubber plantations
   - **Risk:** Expansion pressure on old-growth forests

3. **Grid 1** (16.5°N, 73.5°E): 551 km² plantation (96.8% of forest)
   - **Location:** Goa-Karnataka border
   - **Status:** Nearly complete conversion to plantations

4. **Grid 0** (15.5°N, 73.5°E): 535 km² plantation (96.5% of forest)
   - **Location:** Coastal Karnataka (Uttara Kannada)
   - **Status:** Heavily converted landscape

#### ⚠️ MIXED/TRANSITION ZONES (Critical Monitoring Areas)
1. **Grid 13** (13.5°N, 75.5°E): 4,727 km² forest (45.8% old-growth, 54.2% plantation)
   - **Risk Level:** HIGH - Active plantation expansion zone

2. **Grid 9** (15.5°N, 74.5°E): 1,092 km² forest (55.9% old-growth, 44.1% plantation)
   - **Risk Level:** MODERATE - Balanced but vulnerable

3. **Grid 20** (12.5°N, 76.5°E): 232 km² forest (44.4% old-growth, 55.6% plantation)
   - **Risk Level:** HIGH - Plantation-dominated transition

---

## PART 2: CORE STACK API CAPABILITIES

Based on API specification and example notebooks, the following data can be retrieved:

### Available APIs

#### 1. **MWS (Micro-Watershed) Identification**
- **Endpoint:** `/get_mwsid_by_latlon/`
- **Input:** Latitude, longitude
- **Output:** MWS ID, State, District, Tehsil (administrative hierarchy)
- **Use case:** Map forest grid cells to micro-watersheds for targeted analysis

#### 2. **Cropping Intensity Time Series (2017-2023)**
- **Endpoint:** `/get_mws_kyl_indicators/`
- **Available metrics:**
  - `cropping_intensity_trend`: Trend value over time
  - `cropping_intensity_avg`: Average cropping intensity (1.0 = single crop, 2.0 = double crop)
  - `avg_single_cropped`: % area under single cropping
  - `avg_double_cropped`: % area under double cropping  
  - `avg_triple_cropped`: % area under triple cropping
- **Use case:** Identify regions with intensifying agriculture near old-growth forests

#### 3. **Water Balance Components**
- **Endpoint:** `/get_mws_data/`
- **Time series data (2017-2024):**
  - `precipitation`: Rainfall (mm)
  - `et`: Evapotranspiration (mm)
  - `runoff`: Surface runoff (mm)
- **Use case:** Assess water stress in agricultural zones adjacent to forests

#### 4. **Hydrological Indicators**
- **Endpoint:** `/get_mws_kyl_indicators/`
- **Available metrics:**
  - `avg_precipitation`: Average precipitation
  - `avg_runoff`: Average runoff
  - `avg_number_dry_spell`: Number of dry spell events
- **Use case:** Link drought stress with plantation expansion pressure

#### 5. **Water Bodies Data**
- **Endpoint:** `/get_waterbodies_data_by_admin/`
- **Available metrics per waterbody:**
  - Water spread area by year (2017-2024)
  - Filling percentage (k_17-18, k_18-19, etc.)
  - Cropping intensity in Zone of Influence (ZOI)
  - NDVI time series in ZOI
- **Use case:** Track agricultural expansion around water bodies near forests

#### 6. **Generated Layers (GeoServer)**
- **Endpoint:** `/get_generated_layer_urls/`
- **Available layers:**
  - SOGE (Slope-Oriented Grid Elevation)
  - Drainage networks
  - Aquifer classification
  - GEE asset paths for analysis
- **Use case:** Environmental context for forest-agriculture interface

---

## PART 3: PROPOSED ANALYSIS STRATEGY

### 🎯 PRIMARY QUESTION:
**"Is changing (intensifying) crop intensity a potential risk to old-growth forests in the Western Ghats?"**

### Analysis Workflow

#### PHASE 1: Link Forest Grid Cells to Micro-Watersheds
**For each of the 26 grid cells:**
1. Extract centroid coordinates (lat/lon)
2. Query `/get_mwsid_by_latlon/` to get MWS IDs
3. Build spatial database: Grid Cell → MWS → State/District/Tehsil

**Priority grid cells for analysis:**
- High-risk transition zones: Grids 12, 13, 20 (mixed old-growth/plantation)
- Old-growth hotspots: Grids 22, 18, 21 (conservation monitoring)
- Plantation hotspots: Grids 1, 0, 14 (baseline for conversion)

#### PHASE 2: Retrieve Cropping Intensity Trends (2017-2023)
**For each MWS in priority grid cells:**
1. Query `/get_mws_kyl_indicators/` 
2. Extract time series:
   - `cropping_intensity_avg` (2017-2023)
   - `cropping_intensity_trend` (increasing/decreasing)
   - Breakdown: single/double/triple cropping %

**Key analysis:**
- **Intensification pressure:** MWS with increasing cropping intensity trend near old-growth
- **Conversion risk:** Areas shifting from single → double → triple cropping
- **Spatial correlation:** Distance from old-growth forests vs. cropping intensity

#### PHASE 3: Water Balance & Climate Stress
**For each MWS:**
1. Query `/get_mws_data/` for time series (2017-2024)
2. Calculate water stress indicators:
   - **Water deficit:** Precipitation - (ET + Runoff)
   - **Dry spell frequency:** From `/get_mws_kyl_indicators/`
   - **Trend analysis:** Declining precipitation, increasing ET

**Hypothesis:**
- Water-stressed agricultural zones may expand into forested watersheds
- Old-growth forests regulate local water balance (higher ET, stable runoff)
- Plantation conversion may alter hydrological regime

#### PHASE 4: Waterbody Dynamics & Agricultural Expansion
**For waterbodies near forest boundaries:**
1. Query `/get_waterbodies_data_by_admin/`
2. Analyze Zone of Influence (ZOI) metrics:
   - Cropping intensity trends in waterbody catchments (2017-2023)
   - NDVI time series (vegetation health)
   - Waterbody filling trends (k_17-18 to k_23-24)

**Risk indicators:**
- Declining waterbody levels + increasing cropping intensity = resource competition
- Expansion of cropland in forest-adjacent waterbody ZOIs

---

## PART 4: SPECIFIC ANALYSES WITH CORE STACK API

### Analysis 1: Cropping Intensity Gradient from Old-Growth to Plantation Zones

**Method:**
1. Select transect across Grid 13 (mixed zone: 45.8% old-growth, 54.2% plantation)
2. Sample 10-15 MWS points from old-growth core → plantation edge → agricultural matrix
3. Compare cropping intensity (2017-2023) along gradient

**Expected findings:**
- Higher cropping intensity in plantation zones vs. old-growth
- Increasing trend (2017→2023) strongest at forest-agriculture interface
- Triple-cropping concentration near plantation edges

**Risk assessment:**
- If cropping intensity increases sharply at boundary → expansion pressure
- If water balance deteriorates → resource competition

---

### Analysis 2: Coffee/Cardamom Plantation Intensification (Kodagu, Karnataka)

**Focus area:** Grids 12 & 13 (high plantation %, significant remaining old-growth)

**Method:**
1. Query all MWS in Kodagu district (lat/lon 12.5°N, 75.5°E region)
2. Retrieve cropping intensity indicators:
   - Average intensity 2017-2023
   - Trend (positive/negative)
   - Shift in cropping patterns (single → double)
3. Correlate with forest proximity:
   - MWS adjacent to old-growth forests
   - MWS in plantation-dominated areas
   - MWS in agricultural matrix

**Hypothesis:**
- Coffee estates traditionally under-cropped (perennial, shade-grown)
- Intensification = intercropping annuals, removing shade trees
- Risk: Conversion of forest buffer zones to intensive agriculture

**Indicators of concern:**
- Increasing cropping intensity trend in MWS bordering old-growth
- Declining precipitation + increasing cropping = water stress
- Waterbody levels declining in plantation zones

---

### Analysis 3: Coastal Plantation Belt (Uttara Kannada - Grids 0, 1)

**Context:** 96-97% plantation-dominated landscape (very little old-growth remaining)

**Method:**
1. Query MWS in Grids 0 & 1 (coastal Karnataka, 15.5-16.5°N, 73.5°E)
2. Compare with inland old-growth zones (Grids 8, 22)
3. Metrics:
   - Cropping intensity trends (coastal plantation vs. inland forest)
   - Water balance differences (ET, runoff, precipitation)
   - Dry spell frequency (climate stress)

**Expected findings:**
- Coastal zones: High cropping intensity, declining water availability
- Inland forests: Lower intensity, stable water balance
- Gradient of pressure: Coastal → inland migration of intensification

**Use case:** Predictive model for expansion pressure on remaining old-growth

---

### Analysis 4: Southern Old-Growth Stronghold (Kerala-TN Border - Grid 22)

**Context:** 2,620 km² old-growth (84.7% of forest) - best-preserved region

**Method:**
1. Query MWS in Grid 22 (9.5°N, 77.5°E - Idukki/Wayanad region)
2. Establish baseline:
   - Cropping intensity in forest-adjacent MWS (should be low)
   - Water balance in forested watersheds (high precipitation, stable runoff)
   - Protected area coverage (should be high)
3. Monitor for early warning signs:
   - Any MWS with increasing cropping intensity trend
   - Waterbodies showing declining levels
   - New agricultural expansion near forest edge

**Use case:** Conservation monitoring - detect threats early

---

### Analysis 5: Waterbody-Mediated Agricultural Expansion Risk

**Hypothesis:** Irrigation infrastructure (waterbodies) enables cropping intensification, which may drive forest conversion

**Method:**
1. Query `/get_waterbodies_data_by_admin/` for districts in mixed zones (Grid 13, 20)
2. For each waterbody:
   - Extract ZOI cropping intensity (2017-2023)
   - Compare waterbody filling trends (k_17-18 to k_23-24)
   - Analyze NDVI in ZOI (vegetation health)
3. Spatial analysis:
   - Distance from waterbody to nearest old-growth forest patch
   - Cropping intensity vs. forest distance

**Risk indicators:**
- Waterbodies with increasing ZOI cropping intensity near old-growth
- Declining waterbody levels (over-extraction for irrigation)
- Expansion of double/triple cropping in forest-adjacent areas

**Expected findings:**
- Waterbodies enable intensification → pressure on nearby forests for land/water
- Declining water availability may push agriculture into forested watersheds

---

## PART 5: ADDITIONAL VALUABLE ANALYSES (Beyond Cropping Intensity)

### 1. **Drought-Driven Forest Conversion Risk**
**Data:** `avg_number_dry_spell`, `avg_precipitation`, `avg_runoff`  
**Analysis:** Identify MWS with increasing dry spell frequency near old-growth forests  
**Hypothesis:** Climate stress → agricultural expansion into forested areas for better water retention

### 2. **Sacred Grove Identification via Waterbody Analysis**
**Data:** Waterbody metadata (small waterbodies <5,000 m² in forest zones)  
**Analysis:** Cross-reference with old-growth patches <0.5 km²  
**Use case:** Identify culturally protected forest fragments (sacred groves) for targeted conservation

### 3. **Agroforestry vs. Monoculture Plantation Distinction**
**Data:** NDVI time series in plantation zones, cropping intensity  
**Analysis:**  
- High NDVI + low cropping intensity = shade-grown coffee/cardamom (sustainable)
- Low NDVI + high cropping intensity = cleared monoculture (high risk)  
**Use case:** Differentiate forest-friendly plantations from intensive agriculture

### 4. **Aquifer Classification & Forest Recharge Zones**
**Data:** `aquifer_vector` from `/get_tehsil_data/`  
**Analysis:** Overlay aquifer types with old-growth forest locations  
**Hypothesis:** Old-growth forests on alluvial aquifers provide critical recharge function  
**Risk:** Conversion in recharge zones → regional water stress

### 5. **NDVI-Forest Degradation Correlation**
**Data:** Waterbody ZOI NDVI time series  
**Analysis:** Declining NDVI trends in areas classified as old-growth  
**Use case:** Detect forest degradation not captured by tree cover data (selective logging, understory loss)

### 6. **Temporal Analysis: 2017-2023 Agricultural Expansion**
**Data:** Year-by-year cropping intensity, waterbody area trends  
**Analysis:**  
- 2017 baseline vs. 2023 current state  
- Identify "hotspot years" of rapid intensification  
- Correlate with Hansen forest loss data (2017-2023)  
**Use case:** Quantify forest loss attributable to agricultural expansion

### 7. **Protected Area Effectiveness**
**Data:** MWS within protected areas (query by admin boundaries)  
**Analysis:**  
- Compare cropping intensity trends inside vs. outside PAs  
- Protected areas should show stable/low intensity  
- Buffer zones (5-10 km from PA boundary) = critical monitoring  
**Use case:** Assess whether PAs effectively buffer old-growth from agricultural pressure

---

## PART 6: DATA INTEGRATION & WORKFLOW

### Proposed Script Architecture

```python
# Step 1: Load forest grid analysis results
grid_df = pd.read_csv('outputs/forest_typology_corrected/regional_forest_comparison.csv')

# Step 2: Query Core Stack API for priority grids
api_key = '<your-api-key>'
priority_grids = [12, 13, 20, 22, 18]  # High-risk + high-value

for grid_id in priority_grids:
    grid_row = grid_df[grid_df['grid_id'] == grid_id].iloc[0]
    lat_center = (grid_row['lat_min'] + grid_row['lat_max']) / 2
    lon_center = (grid_row['lon_min'] + grid_row['lon_max']) / 2
    
    # Get MWS ID
    mws_response = requests.get(
        f"{base_url}/get_mwsid_by_latlon/",
        params={'latitude': lat_center, 'longitude': lon_center},
        headers={'X-API-Key': api_key}
    )
    mws_data = mws_response.json()
    
    # Get cropping intensity indicators
    kyl_response = requests.get(
        f"{base_url}/get_mws_kyl_indicators/",
        params={
            'state': mws_data['State'],
            'district': mws_data['District'],
            'tehsil': mws_data['Tehsil'],
            'mws_id': mws_data['uid']
        },
        headers={'X-API-Key': api_key}
    )
    kyl_data = kyl_response.json()
    
    # Extract cropping intensity trends
    cropping_intensity_trend = kyl_data[0]['cropping_intensity_trend']
    cropping_intensity_avg = kyl_data[0]['cropping_intensity_avg']
    
    # Get water balance time series
    ts_response = requests.get(
        f"{base_url}/get_mws_data/",
        params={
            'state': mws_data['State'],
            'district': mws_data['District'],
            'tehsil': mws_data['Tehsil'],
            'mws_id': mws_data['uid']
        },
        headers={'X-API-Key': api_key}
    )
    ts_data = ts_response.json()
    
    # Analyze time series (precipitation, ET, runoff trends)
    # Save results for each grid cell
```

### Output Deliverables

1. **CSV:** `forest_cropping_intensity_analysis.csv`
   - Columns: grid_id, lat, lon, forest_type, old_growth_km2, plantation_km2, mws_id, cropping_intensity_avg, cropping_intensity_trend, precipitation_avg, dry_spell_count

2. **Risk Map:** Grid cells colored by:
   - Green: Low risk (stable cropping intensity, high old-growth %)
   - Yellow: Moderate risk (increasing intensity, mixed forest)
   - Red: High risk (rapid intensification, <50% old-growth)

3. **Time Series Charts:**
   - Cropping intensity 2017-2023 for high-risk grids
   - Water balance trends (precipitation, ET, runoff)
   - Forest loss correlation with cropping intensity changes

4. **Summary Report:**
   - Districts with highest agricultural pressure on old-growth
   - MWS requiring urgent monitoring (intensification + proximity to forest)
   - Recommended conservation interventions (buffer zones, PAs, sustainable agriculture)

---

## PART 7: INTERPRETATION & CONSERVATION IMPLICATIONS

### Expected Findings

#### Scenario A: **Cropping Intensity IS a Risk Factor**
**Evidence:**
- MWS adjacent to old-growth show increasing cropping intensity trends (2017-2023)
- Mixed zones (Grids 12, 13) have higher intensity than old-growth cores
- Water balance deteriorating in intensifying zones (declining precipitation, increasing ET)
- Waterbodies in forest-adjacent areas showing declining levels

**Implications:**
- Agricultural expansion driven by intensification (more crops/year) → land demand
- Water stress in intensive zones → pressure on forested watersheds
- Plantations converting to annual crops (coffee → vegetables/rice)

**Recommended actions:**
- Establish buffer zones (5-10 km) around old-growth cores with restricted intensification
- Incentivize sustainable agroforestry (shade-grown coffee) over intensive monocultures
- Water conservation programs in high-intensity zones to reduce forest encroachment
- Protected area expansion in high-risk grids (12, 13, 20)

---

#### Scenario B: **Cropping Intensity is NOT a Direct Risk**
**Evidence:**
- Cropping intensity stable or declining in forest-adjacent MWS
- High-intensity zones spatially separated from old-growth forests
- Water balance stable in forested watersheds
- Plantation zones show low intensification (shade-grown perennials)

**Implications:**
- Forest loss driven by other factors (urbanization, logging, mining)
- Plantations coexist with old-growth (coffee estates provide buffer)
- Agricultural intensification contained within existing cropland

**Recommended actions:**
- Focus conservation efforts on non-agricultural threats (urban expansion, infrastructure)
- Support sustainable plantation practices (agroforestry certification)
- Monitor for future intensification trends (early warning system)

---

### Cross-Validation with Urbanization Hotspots

**Link with previous analysis (Pune, Raigarh, Thane):**
- Overlay forest grids with urbanization expansion zones
- Hypothesis: Urban expansion → agricultural land loss → pressure on forests for new cropland
- Combined threat: Urbanization (direct forest conversion) + agricultural displacement (indirect pressure)

**Expected finding:**
- Grids near Pune/Thane show both urban expansion AND agricultural intensification
- Forests in peri-urban zones face dual pressures: built-up growth + farming intensification

---

## PART 8: NEXT STEPS & DELIVERABLES

### Immediate Actions (Next 1-2 Days)

1. **API Key Validation**
   - Test example API calls with provided key (`rBKKRCKl.jsfeUjArYxscYFJZf4FY0L7NuddaSp5u`)
   - Verify access to all required endpoints

2. **Script Development**
   - Create `forest_agriculture_risk_analysis.py` 
   - Query MWS for priority grid cells (12, 13, 18, 20, 22)
   - Retrieve cropping intensity + water balance data

3. **Preliminary Analysis**
   - Generate time series plots (cropping intensity 2017-2023)
   - Calculate correlations (forest proximity vs. intensity)
   - Identify high-risk MWS for detailed study

### Medium-Term Deliverables (Next Week)

1. **Comprehensive Report**
   - District-level analysis (all 87 Western Ghats districts)
   - Cropping intensity trends by forest type (old-growth vs. plantation zones)
   - Water balance assessment (climate stress indicators)

2. **Interactive Dashboard**
   - Map: Grid cells with forest type + cropping intensity overlay
   - Time slider: 2017-2023 changes
   - Filter: By risk level, state, district

3. **Policy Recommendations**
   - Priority areas for intervention
   - Sustainable agriculture incentives
   - Conservation buffer zone proposals

---

## CONCLUSION

The Core Stack API provides rich agricultural and hydrological data that can directly answer:
- **Primary question:** Is changing crop intensity a risk to old-growth forests?
- **Mechanism:** Does intensification drive expansion into forested areas?
- **Context:** Water stress, climate trends, waterbody dynamics

**Key value-adds beyond cropping intensity:**
- Water balance analysis (drought risk)
- Waterbody monitoring (irrigation infrastructure)
- Aquifer classification (recharge zone importance)
- NDVI trends (forest degradation detection)
- Protected area effectiveness assessment

**Integration with existing work:**
- Combines forest typology (old-growth vs. plantation) with agricultural pressure data
- Links urbanization hotspots with agricultural displacement
- Provides temporal dimension (2017-2023 trends) to complement spatial analysis

**Expected outcome:** Comprehensive risk assessment identifying specific districts/MWS where agricultural intensification threatens old-growth forests, enabling targeted conservation interventions.
