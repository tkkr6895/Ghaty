# Western Ghats Forest Typology Analysis - Natural Forests vs. Plantations

## Project Status Update (December 14, 2025)

### Previous Work Completed ✅

1. **Tree Cover Analysis (1987-2025)**
   - GLC-FCS30D: 1987-2010 (6 time points)
   - Dynamic World: 2018-2025 (8 annual snapshots)
   - Key Finding: Overall tree cover remained stable (~85,000 km²)

2. **Urbanization Analysis**
   - Identified top 10 districts with built-up area growth
   - Created animations for top 3 hotspots (Pune, Raigarh, Thane)
   - Key Finding: 16.2x growth in built-up area (1987-2025)

### New Objective: Distinguish Natural Forests from Plantations

---

## Data Sources for Forest Typology

### 1. **Natural Forest Map 2020** (Primary Source)
- **Dataset**: Nature-Trace Natural Forest 2020 v1.0
- **GEE ID**: `projects/nature-trace/assets/forest_typology/natural_forest_2020_v1_0_collection`
- **Description**: Binary classification (natural forest vs. other)
- **Resolution**: 30m
- **Coverage**: Global
- **Use Case**: Primary distinction between natural and plantation forests

### 2. **Hansen Global Forest Change** (Validation & Historical Context)
- **GEE ID**: `UMD/hansen/global_forest_change_2023_v1_11`
- **Bands**:
  - `treecover2000`: Tree cover % in year 2000
  - `loss`: Forest loss 2000-2023
  - `gain`: Forest gain 2000-2012
  - `lossyear`: Year of forest loss
- **Resolution**: 30m
- **Use Case**: 
  - Identify plantation areas (recent gains)
  - Forest loss patterns
  - Age of forest stands

### 3. **Dynamic World** (Current Reference)
- **GEE ID**: `GOOGLE/DYNAMICWORLD/V1`
- **Classes**: Trees (includes natural + plantation)
- **Resolution**: 10m
- **Temporal**: 2015-present
- **Use Case**: Current tree cover extent

### 4. **GLC-FCS30D** (Historical Baseline)
- **GEE ID**: `projects/sat-io/open-datasets/GLC-FCS30D`
- **Classes**: Multiple forest types (deciduous, evergreen, etc.)
- **Resolution**: 30m
- **Temporal**: 1985-2022
- **Use Case**: Historical forest type context

---

## Analysis Strategy

### Phase 1: Natural Forest Identification (2020 Baseline)
1. Load Nature-Trace Natural Forest 2020
2. Clip to Western Ghats boundary
3. Calculate total natural forest area
4. Create natural forest mask

### Phase 2: Plantation Identification (Multi-source)
Identify plantations using combination of:

**Method A: Forest Gain Analysis (Hansen)**
- Areas with `gain=1` (2000-2012) → Likely plantations
- Areas with high tree cover in 2023 BUT not in Natural Forest 2020 → Plantations

**Method B: Temporal Pattern Analysis**
- Compare GLC-FCS30D (1987-2010) with Natural Forest 2020
- Areas that transitioned: Bare/Crop → Trees → Likely plantation
- Areas consistently forested → Likely natural

**Method C: Dynamic World Cross-validation**
- Current tree cover (DW 2023) NOT in Natural Forest 2020 → Plantations
- Consider species composition proxies (if available)

### Phase 3: Spatial Distribution
1. Create district-level statistics:
   - Natural forest area
   - Plantation area
   - Ratio (plantation vs. natural)
   - Loss/gain patterns

2. Hotspot identification:
   - Districts with highest plantation %
   - Districts with most natural forest loss
   - Overlap with urbanization hotspots

### Phase 4: Temporal Analysis
1. Natural forest loss (1987-2025):
   - Using Natural Forest 2020 as reference
   - Backtrack with Hansen loss data
   - Forward project with DW data

2. Plantation expansion:
   - Hansen gain areas
   - New tree cover NOT in historical natural forests
   - Correlation with agricultural areas

---

## Expected Outputs

### 1. Maps & Visualizations
- Natural forest distribution (2020)
- Plantation areas (multi-year)
- Change maps (natural → plantation, natural → other)
- District-level choropleth maps

### 2. Statistics & Reports
- CSV: District-wise breakdown (natural vs. plantation)
- CSV: Temporal trends (loss/gain by type)
- JSON: Metadata and methodology
- Dashboard: Interactive comparison

### 3. Animations
- Forest typology change (1987-2025)
- Hotspot evolution (natural forest loss)
- Plantation expansion patterns

---

## Technical Implementation

### Step 1: Data Preparation
```python
# Load datasets
natural_forest_2020 = ee.ImageCollection('projects/nature-trace/assets/forest_typology/natural_forest_2020_v1_0_collection')
hansen = ee.Image('UMD/hansen/global_forest_change_2023_v1_11')
dynamic_world = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
glc = ee.ImageCollection('projects/sat-io/open-datasets/GLC-FCS30D')
```

### Step 2: Classification Logic
```python
# Natural forest (2020 baseline)
natural_forest = natural_forest_2020.mosaic().clip(wg_boundary)

# Current tree cover (2023)
trees_2023 = dynamic_world.filter('2023').select('trees').mean().gt(0.5)

# Plantations (derived)
plantations = trees_2023.And(natural_forest.Not())

# Historical plantation expansion
forest_gain = hansen.select('gain').eq(1)
plantation_candidates = forest_gain.Or(plantations)
```

### Step 3: District-level Aggregation
```python
# For each district
district_stats = {
    'natural_forest_km2': ...,
    'plantation_km2': ...,
    'plantation_percentage': ...,
    'natural_loss_km2': ...,
    'plantation_gain_km2': ...
}
```

---

## Next Steps

1. **Immediate**: Create GEE script for natural forest analysis
2. **Week 1**: Generate 2020 baseline maps and statistics
3. **Week 2**: Temporal analysis (1987-2025 forest typology changes)
4. **Week 3**: District-level attribution and hotspot identification
5. **Week 4**: Integrate with urbanization data for comprehensive story

---

## Data Validation Approach

Given multiple sources, we'll use consensus method:
- **High Confidence Natural Forest**: Nature-Trace 2020 = Natural AND consistent in GLC historical
- **High Confidence Plantation**: Hansen gain = 1 OR (Current trees AND NOT in Nature-Trace 2020)
- **Uncertain**: Conflicting signals → Flag for manual review

---

## Attribution Framework (Future)

Once forest typology is established, link with:
1. **Administrative**: District boundaries (already have)
2. **Protected Areas**: Wildlife sanctuaries, national parks
3. **Elevation Zones**: Hill station vs. lowland patterns
4. **Proximity Analysis**: Distance to roads, cities, agricultural zones
5. **Community Data**: Tribal areas, forest-dependent communities

This will enable:
- Identifying which districts need intervention
- Understanding drivers of forest loss/conversion
- Community-specific conservation strategies
- Policy recommendations grounded in spatial data

---

*Created: December 14, 2025*  
*Workspace: Western Ghats Analysis*  
*Next: Implement GEE script for forest typology classification*
