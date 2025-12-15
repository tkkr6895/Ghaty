# Western Ghats Urbanization Analysis - Key Findings

## Executive Summary

Analysis of built-up area expansion in the Western Ghats region from 1987 to 2025 using:
- **GLC-FCS30D dataset** (1987-2010): 6 time points
- **Google Dynamic World** (2018-2025): 8 annual snapshots

---

## Overall Statistics

### Western Ghats Region (Full Extent)
- **1987 Baseline**: 242,121 built pixels
- **2025 Current**: 3,920,422 built pixels
- **New Built Area**: 3,738,105 pixels (95.4% of 2025 total)
- **Overall Growth**: **16.2x** (1,519% increase)

### Regional Breakdown

| Region | 1987 Built | 2025 Built | New Built | % of Total | Growth Factor |
|--------|------------|------------|-----------|------------|---------------|
| **North (Goa-Maharashtra)** | 95,802 | 1,497,144 | 1,427,359 | 38.2% | 15.6x |
| **Central (Karnataka)** | 85,215 | 1,316,071 | 1,253,437 | 33.5% | 15.4x |
| **South (Kerala-Tamil Nadu)** | 61,104 | 1,107,207 | 1,057,309 | 28.3% | **18.1x** |

**Key Finding**: Southern region shows highest growth rate (18.1x), indicating rapid urbanization pressure in Kerala and Tamil Nadu portions of the Western Ghats.

---

## Top 10 Districts by Urbanization Growth

Analysis of 87 districts intersecting the Western Ghats extent:

| Rank | District | State | 1987 Built | 2025 Built | New Built | Growth |
|------|----------|-------|------------|------------|-----------|--------|
| **1** | **Pune** | Maharashtra | 424 | 33,946 | 33,529 | **80.1x** |
| **2** | **Raigarh** | Maharashtra | 269 | 26,660 | 26,404 | **99.1x** |
| **3** | **Thane** | Maharashtra | 1,690 | 26,791 | 25,208 | **15.9x** |
| 4 | Ahmadnagar | Maharashtra | 894 | 24,954 | 24,093 | 27.9x |
| 5 | Nashik | Maharashtra | 1,645 | 19,581 | 18,045 | 11.9x |
| 6 | Shimoga | Karnataka | 1,025 | 17,958 | 16,999 | 17.5x |
| 7 | North Goa | Goa | 160 | 15,230 | 15,151 | 95.2x |
| 8 | Coimbatore | Tamil Nadu | 887 | 13,172 | 12,320 | 14.9x |
| 9 | South Goa | Goa | 331 | 12,166 | 11,975 | 36.8x |
| 10 | Uttara Kannada | Karnataka | 366 | 11,890 | 11,585 | 32.5x |

**Note**: Pixel counts based on 4x downsampled data; actual counts approximately 16x higher.

---

## Critical Findings - Top 3 Hotspots

### 🔴 1. Pune, Maharashtra
- **Location**: 18.57°N, 74.07°E
- **Growth**: 80.1x (from 424 to 33,946 pixels in downsampled data)
- **Actual Built Area (2025)**: ~828,905 pixels at full resolution
- **New Built**: ~801,604 pixels
- **Context**: Pune metropolitan expansion + IT corridor development
- **Critical Period**: Massive acceleration from 2010 (173,669 pixels) to 2018 (495,441 pixels)

### 🔴 2. Raigarh, Maharashtra  
- **Location**: 18.52°N, 73.21°E
- **Growth**: 99.1x (nearly 100x growth!)
- **Actual Built Area (2025)**: ~769,413 pixels
- **New Built**: ~744,011 pixels
- **Context**: Mumbai Metropolitan Region spillover, industrial development
- **Critical Period**: 2010-2018 jump from 161,853 to 471,550 pixels

### 🔴 3. Thane, Maharashtra
- **Location**: 19.60°N, 73.15°E  
- **Growth**: 15.9x (started from higher baseline)
- **Actual Built Area (2025)**: ~560,309 pixels
- **New Built**: ~512,262 pixels
- **Context**: Mumbai suburban expansion, satellite city development
- **Pattern**: Steady growth with acceleration post-2018

---

## Spatial Hotspot Grid Analysis

Using 100x100 grid cell analysis across the entire Western Ghats:

### Top 5 Hotspot Cells

| Rank | Grid Cell | Location | New Built Pixels | Baseline | Growth Factor |
|------|-----------|----------|------------------|----------|---------------|
| 1 | (3,14) | North-West | 32,907 | 12,389 | 2.7x |
| 2 | (13,13) | North-West | 31,064 | 2,962 | 10.5x |
| 3 | (14,14) | North-West | 30,583 | 904 | **33.8x** |
| 4 | (14,13) | North-West | 27,979 | 499 | **56.1x** |
| 5 | (39,15) | Central-West | 27,757 | 1,479 | 18.8x |

**Pattern**: Highest concentration in North-West (Pune-Mumbai-Goa corridor) and Central-West (Bangalore periphery).

---

## Visualization Outputs

### 1. District Analysis
- **Chart**: `outputs/district_analysis/top10_districts_chart.png`
- **Data**: `outputs/district_analysis/district_urbanization_analysis.csv` (87 districts)
- **Metadata**: `outputs/district_analysis/top3_hotspots.json`

### 2. Hotspot Grid Maps
- **Overview**: `outputs/animations/hotspot_grid_map.png` - 100x100 heatmap
- **Comparison**: `outputs/animations/clear_before_after_comparison.png` - 1987 vs 2025

### 3. Hotspot Animations (1987-2025, 14 frames each)
- **Pune**: `outputs/hotspot_animations/hotspot_1_pune_1987_2025.gif` (2.40 MB)
  - Comparison: `hotspot_1_pune_comparison.png`
- **Raigarh**: `outputs/hotspot_animations/hotspot_2_raigarh_1987_2025.gif` (2.68 MB)
  - Comparison: `hotspot_2_raigarh_comparison.png`
- **Thane**: `outputs/hotspot_animations/hotspot_3_thane_1987_2025.gif` (2.54 MB)
  - Comparison: `hotspot_3_thane_comparison.png`

---

## Key Insights for "Bettada Jeeva" Story

### 1. **Urbanization is Concentrated**
- Top 10 districts account for disproportionate share of growth
- Maharashtra dominates (7 of top 10 districts)
- Coastal and metropolitan periphery areas most affected

### 2. **Acceleration Pattern**
- Moderate growth 1987-2010 (GLC era)
- **Explosive growth 2010-2025** (especially post-2018)
- Some districts show 80-100x growth!

### 3. **Geographic Pattern**
- **North**: Goa-Pune-Mumbai corridor - tourism + metro expansion
- **Central**: Bangalore periphery, Karnataka hill stations
- **South**: Tamil Nadu (Coimbatore) + Kerala hill stations

### 4. **Ecological Implications**
- Rapid urbanization in biodiversity hotspot
- Pressure on endemic species habitats
- Hill station development (Coorg, Wayanad, Munnar, Nilgiris areas)
- Protected area peripheries at risk

---

## Data Sources & Methods

### Datasets
1. **GLC-FCS30D** (1987-2010): 30m resolution global land cover, reclassified to built areas
2. **Google Dynamic World** (2018-2025): 10m resolution near-real-time land cover
3. **District Boundaries**: Census 2011 from DataMeet repository

### Analysis Approach
- Full resolution raster analysis (45,325 x 18,594 pixels)
- District-level aggregation using spatial overlay
- Hotspot identification using spatial binning (100x100 grid)
- Change detection: 2025 built area NOT present in 1987
- Memory-efficient processing due to large data volumes

### Limitations
- Dataset methodology switch between 2015-2018 (GLC → Dynamic World)
- Different spatial resolutions (30m vs 10m)
- District analysis used downsampled data (4x) due to memory constraints
- Bounding box approximation for district overlap

---

## Recommendations for Conservation/Planning

### Immediate Attention Needed
1. **Pune-Raigarh-Thane corridor**: Establish green belts, enforce protected area buffers
2. **Goa districts**: Tourism vs. conservation balance
3. **Shimoga & Uttara Kannada**: Monitor forest fragmentation

### Priority Actions
- Detailed hotspot surveys in top 10 districts
- Compare with protected area boundaries
- Monitor connectivity corridors between forest patches
- Assess impact on Western Ghats endemic species

### Data Gaps
- Need higher temporal resolution (annual) for 2010-2018 period
- District-level validation with ground truth
- Correlation with protected areas, forest cover, elevation zones

---

## Next Steps

1. ✅ District-level analysis complete
2. ✅ Top 10 hotspots identified
3. ✅ Top 3 animations created
4. ⏳ Overlay with protected area boundaries
5. ⏳ Elevation gradient analysis
6. ⏳ Distance-to-city gradient analysis
7. ⏳ Integrate into Substack story with narrative

---

*Generated: November 2, 2025*  
*Analysis: Western Ghats Built-Up Area Expansion (1987-2025)*  
*For: "Bettada Jeeva or The Life of the Hills" - Substack Story*
