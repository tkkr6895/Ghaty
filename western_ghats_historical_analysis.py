#!/usr/bin/env python
# coding: utf-8

# # Western Ghats Historical LULC Analysis (1985-2020)
# 
# **Objective**: Analyze long-term land use and land cover changes in the Western Ghats using Google Earth Engine's GLC-FCS30D dataset at 5-year intervals.
# 
# **Key Features**:
# - Historical analysis from 1985 to 2020
# - 5-year interval data for long-term trend detection
# - 30-meter resolution global land cover dataset
# - Comprehensive temporal analysis spanning 35 years
# - Integration with Dynamic World results for complete picture
# 
# **Technical Approach**:
# - GLC-FCS30D dataset from Google Earth Engine
# - 5-year composite analysis (1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020)
# - Area calculations and change detection
# - Statistical analysis and visualization
# - Export capabilities for further analysis

# In[ ]:


# SETUP AND IMPORTS
import ee
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import json
import time

print("Initializing Google Earth Engine...")
try:
    # Initialize Earth Engine
    ee.Initialize(project='ee-tkkrfirst')
    print("SUCCESS: Earth Engine initialized")

    # Load GLC-FCS30D dataset
    glc_fcs_annual = ee.ImageCollection("projects/sat-io/open-datasets/GLC-FCS30D/annual")
    glc_fcs_five_year = ee.ImageCollection("projects/sat-io/open-datasets/GLC-FCS30D/five-years-map")

    print("SUCCESS: GLC-FCS30D dataset loaded")

    # Define GLC-FCS30D land cover classes
    # Based on GLC-FCS30D classification scheme
    GLC_CLASSES = {
        10: 'Rainfed cropland',
        11: 'Herbaceous cover cropland',
        12: 'Tree or shrub cover cropland',
        20: 'Irrigated cropland',
        51: 'Open evergreen broadleaved forest',
        52: 'Closed evergreen broadleaved forest',
        61: 'Open deciduous broadleaved forest',
        62: 'Closed deciduous broadleaved forest',
        71: 'Open evergreen needle-leaved forest',
        72: 'Closed evergreen needle-leaved forest',
        81: 'Open deciduous needle-leaved forest',
        82: 'Closed deciduous needle-leaved forest',
        91: 'Open mixed leaf forest',
        92: 'Closed mixed leaf forest',
        120: 'Shrubland',
        121: 'Evergreen shrubland',
        122: 'Deciduous shrubland',
        130: 'Grassland',
        140: 'Lichens and mosses',
        150: 'Sparse vegetation',
        152: 'Sparse shrubland',
        153: 'Sparse herbaceous',
        181: 'Swamp',
        182: 'Marsh',
        183: 'Flooded flat',
        184: 'Saline',
        185: 'Mangrove',
        186: 'Salt marsh',
        187: 'Tidal flat',
        190: 'Impervious surfaces',
        200: 'Bare areas',
        201: 'Consolidated bare areas',
        202: 'Unconsolidated bare areas',
        210: 'Water body',
        220: 'Permanent ice and snow'
    }

    print(f"GLC-FCS30D classes loaded: {len(GLC_CLASSES)} categories")

except Exception as e:
    print(f"ERROR: {e}")
    print("Please run: ee.Authenticate() first if not authenticated")


# In[ ]:


# LOAD STUDY AREA BOUNDARY
shapefile_path = "CEPF Content/data/commondata/fwdcepfwesternghatsprioritizationdatalayers/cepfbnd_prj.shp"

print("Loading Western Ghats boundary...")
try:
    # Load boundary shapefile
    western_ghats = gpd.read_file(shapefile_path)
    print(f"Loaded {western_ghats.shape[0]} polygon(s)")
    print(f"Original CRS: {western_ghats.crs}")

    # Convert to WGS84 for Earth Engine compatibility
    western_ghats_wgs84 = western_ghats.to_crs('EPSG:4326')

    # Calculate area for verification
    area_km2 = western_ghats.to_crs('EPSG:3857').area.sum() / 1e6
    print(f"Total study area: {area_km2:.0f} km²")

    # Convert to Earth Engine geometry
    def convert_to_ee_geometry(gdf):
        """Convert GeoDataFrame to Earth Engine MultiPolygon"""
        gdf_buffered = gdf.buffer(0.0001).buffer(-0.0001)
        union_geom = gdf_buffered.unary_union

        if union_geom.geom_type == 'Polygon':
            coords = [list(union_geom.exterior.coords)]
            return ee.Geometry.Polygon(coords)
        elif union_geom.geom_type == 'MultiPolygon':
            polygons = []
            for polygon in union_geom.geoms:
                coords = [list(polygon.exterior.coords)]
                polygons.append(coords)
            return ee.Geometry.MultiPolygon(polygons)

    # Convert to Earth Engine geometry
    western_ghats_ee = convert_to_ee_geometry(western_ghats_wgs84)

    # Verify Earth Engine geometry
    ee_area = western_ghats_ee.area().getInfo() / 1e6
    print(f"Earth Engine area: {ee_area:.0f} km²")

    area_diff_percent = abs(ee_area - area_km2) / area_km2 * 100
    if area_diff_percent < 5:
        print(f"SUCCESS: Geometry conversion successful (difference: {area_diff_percent:.1f}%)")
        STUDY_AREA_KM2 = ee_area
    else:
        print(f"WARNING: Significant area difference: {area_diff_percent:.1f}%)")
        STUDY_AREA_KM2 = ee_area

except Exception as e:
    print(f"ERROR loading boundary: {e}")


# In[ ]:


# MAP GLC-FCS30D CLASSES TO SIMPLIFIED CATEGORIES

def map_glc_to_simplified_classes(glc_value):
    """Map GLC-FCS30D detailed classes to simplified LULC categories"""

    # Forest classes (50-92)
    if glc_value in [51, 52, 61, 62, 71, 72, 81, 82, 91, 92]:
        return 1  # Trees/Forest

    # Cropland classes (10-20)
    elif glc_value in [10, 11, 12, 20]:
        return 4  # Crops

    # Shrubland classes (120-122)
    elif glc_value in [120, 121, 122]:
        return 5  # Shrub and scrub

    # Grassland (130)
    elif glc_value == 130:
        return 2  # Grass

    # Sparse vegetation (150-153)
    elif glc_value in [150, 152, 153]:
        return 7  # Bare

    # Wetlands/Flooded vegetation (181-187)
    elif glc_value in [181, 182, 183, 184, 185, 186, 187]:
        return 3  # Flooded vegetation

    # Urban/Built (190)
    elif glc_value == 190:
        return 6  # Built

    # Bare areas (200-202)
    elif glc_value in [200, 201, 202]:
        return 7  # Bare

    # Water body (210)
    elif glc_value == 210:
        return 0  # Water

    # Lichen/mosses (140)
    elif glc_value == 140:
        return 2  # Grass (closest match)

    # Snow/ice (220) - should not occur in Western Ghats
    elif glc_value == 220:
        return 8  # Snow and ice

    else:
        return 7  # Default to Bare for unknown classes

# Create mapping dictionary for Earth Engine
GLC_TO_SIMPLIFIED = {
    # Forest
    51: 1, 52: 1, 61: 1, 62: 1, 71: 1, 72: 1, 81: 1, 82: 1, 91: 1, 92: 1,
    # Crops
    10: 4, 11: 4, 12: 4, 20: 4,
    # Shrub
    120: 5, 121: 5, 122: 5,
    # Grass
    130: 2, 140: 2,
    # Flooded vegetation
    181: 3, 182: 3, 183: 3, 184: 3, 185: 3, 186: 3, 187: 3,
    # Built
    190: 6,
    # Bare
    150: 7, 152: 7, 153: 7, 200: 7, 201: 7, 202: 7,
    # Water
    210: 0,
    # Snow/ice
    220: 8
}

# Simplified class names (matching Dynamic World)
SIMPLIFIED_CLASSES = {
    0: 'Water',
    1: 'Trees',
    2: 'Grass',
    3: 'Flooded vegetation',
    4: 'Crops',
    5: 'Shrub and scrub',
    6: 'Built',
    7: 'Bare',
    8: 'Snow and ice'
}

print("Class mapping defined")
print(f"Simplified to {len(SIMPLIFIED_CLASSES)} categories")


# In[ ]:


# HISTORICAL LULC ANALYSIS FUNCTION

def analyze_historical_lulc(year, region_ee):
    """
    Analyze historical LULC using GLC-FCS30D dataset

    Parameters:
    - year: Analysis year (1985-2020, preferably 5-year intervals)
    - region_ee: Earth Engine geometry for Western Ghats

    Returns:
    - Dictionary with area statistics for each land cover class
    """

    print(f"\n{'='*70}")
    print(f"ANALYZING HISTORICAL LULC FOR {year}")
    print(f"{'='*70}")

    start_time = time.time()

    try:
        # Get GLC-FCS30D image for the year
        print(f"Loading GLC-FCS30D data for {year}...")

        # Use 5-year collection for better temporal coverage
        glc_image = glc_fcs_five_year.filter(ee.Filter.eq('year', year)).first()

        # If not found in 5-year collection, try annual
        if glc_image is None:
            print(f"   Trying annual collection...")
            glc_image = glc_fcs_annual.filter(ee.Filter.eq('year', year)).first()

        if glc_image is None:
            print(f"ERROR: No data found for {year}")
            return None

        # Get the land cover band
        lc_band = glc_image.select('b1')  # Main classification band

        # Clip to study region
        lc_clipped = lc_band.clip(region_ee)

        print(f"   Data loaded successfully")

        # Remap GLC classes to simplified categories
        print(f"   Remapping {len(GLC_TO_SIMPLIFIED)} GLC classes to simplified categories...")

        from_values = list(GLC_TO_SIMPLIFIED.keys())
        to_values = list(GLC_TO_SIMPLIFIED.values())

        lc_simplified = lc_clipped.remap(from_values, to_values, 7)  # Default to Bare (7)

        # Calculate areas for each simplified class
        print(f"   Calculating areas for all land cover classes...")

        results = {'year': year, 'dataset': 'GLC-FCS30D'}
        pixel_area = ee.Image.pixelArea()

        for class_id, class_name in SIMPLIFIED_CLASSES.items():
            try:
                # Create mask for this class
                class_mask = lc_simplified.eq(class_id)

                # Calculate area
                area_m2 = pixel_area.updateMask(class_mask).reduceRegion(
                    reducer=ee.Reducer.sum(),
                    geometry=region_ee,
                    scale=30,  # 30m resolution for GLC-FCS30D
                    maxPixels=1e10,
                    bestEffort=True
                ).getInfo()

                # Convert to km²
                area_km2 = area_m2.get('area', 0) / 1e6
                results[class_name] = area_km2

                if area_km2 > 0.1:
                    percentage = (area_km2 / STUDY_AREA_KM2) * 100
                    print(f"      {class_name}: {area_km2:.1f} km² ({percentage:.1f}%)")

            except Exception as e:
                print(f"      ERROR calculating {class_name}: {e}")
                results[class_name] = 0

        # Calculate total area and percentages
        total_area = sum([v for k, v in results.items() 
                         if k not in ['year', 'dataset'] and isinstance(v, (int, float))])
        results['total_area_km2'] = total_area

        # Add percentage calculations
        for class_name in SIMPLIFIED_CLASSES.values():
            if class_name in results and total_area > 0:
                percentage = (results[class_name] / total_area) * 100
                results[f'{class_name}_percent'] = percentage

        # Summary
        elapsed = (time.time() - start_time) / 60
        print(f"SUCCESS: {year} analysis completed in {elapsed:.1f} minutes")
        print(f"Total classified area: {total_area:.1f} km² ({(total_area/STUDY_AREA_KM2)*100:.1f}% of study area)")

        return results

    except Exception as e:
        elapsed = (time.time() - start_time) / 60
        print(f"ERROR: {year} analysis FAILED after {elapsed:.1f} minutes")
        print(f"Error details: {e}")
        return None

print("Historical LULC analysis function ready")


# In[ ]:


# RUN HISTORICAL ANALYSIS FOR 5-YEAR INTERVALS (1985-2020)

# Define analysis years (5-year intervals)
historical_years = [1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020]

print(f"Starting historical analysis for {len(historical_years)} years...")
print(f"Years: {historical_years}")
print("This may take 30-60 minutes depending on Earth Engine quota")

historical_results = []

for year in historical_years:
    result = analyze_historical_lulc(year, western_ghats_ee)
    if result:
        historical_results.append(result)
        print(f"SUCCESS: {year} analysis complete")
    else:
        print(f"FAILED: {year} analysis failed")

    # Brief pause between requests
    time.sleep(5)

if historical_results:
    # Convert to DataFrame
    historical_df = pd.DataFrame(historical_results)

    print(f"\nHistorical analysis complete for {len(historical_results)} years")
    print("\nKey results:")
    display(historical_df[['year', 'Trees', 'Built', 'Crops', 'total_area_km2']].round(1))

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'outputs/western_ghats_historical_lulc_{timestamp}.csv'
    historical_df.to_csv(output_file, index=False)
    print(f"\nResults saved: {output_file}")

else:
    print("\nNo results obtained - check Earth Engine connection and data availability")


# In[ ]:


# LOAD AND COMBINE WITH DYNAMIC WORLD RESULTS

print("Loading Dynamic World results for comprehensive analysis...")

try:
    # Load Dynamic World results
    dw_files = [f for f in os.listdir('outputs') 
                if 'lulc_analysis_results' in f and f.endswith('.csv')]

    if dw_files:
        dw_df = pd.read_csv(f'outputs/{sorted(dw_files)[-1]}')
        dw_df['dataset'] = 'Dynamic World'
        print(f"Loaded Dynamic World results: {len(dw_df)} years")
        print(f"Years: {sorted(dw_df['year'].unique())}")

        # Combine datasets
        combined_df = pd.concat([historical_df, dw_df], ignore_index=True)
        combined_df = combined_df.sort_values('year').reset_index(drop=True)

        print(f"\nCombined dataset: {len(combined_df)} years total")
        print(f"Year range: {int(combined_df['year'].min())}-{int(combined_df['year'].max())}")

        # Save combined results
        combined_file = f'outputs/western_ghats_combined_lulc_{timestamp}.csv'
        combined_df.to_csv(combined_file, index=False)
        print(f"Combined results saved: {combined_file}")

    else:
        print("No Dynamic World results found")
        combined_df = historical_df.copy()

except Exception as e:
    print(f"Error loading Dynamic World results: {e}")
    combined_df = historical_df.copy()


# In[ ]:


# COMPREHENSIVE STATISTICAL ANALYSIS

print("COMPREHENSIVE STATISTICAL ANALYSIS")
print("=" * 80)

# Overall statistics
print("\n1. OVERALL SUMMARY")
print("-" * 80)
print(f"Analysis period: {int(combined_df['year'].min())}-{int(combined_df['year'].max())}")
print(f"Total years analyzed: {len(combined_df)}")
print(f"Datasets used: {combined_df['dataset'].unique()}")
print(f"Study area: {STUDY_AREA_KM2:.0f} km²")

# Land cover statistics by class
print("\n2. LAND COVER STATISTICS BY CLASS")
print("-" * 80)

for class_name in SIMPLIFIED_CLASSES.values():
    if class_name in combined_df.columns and f'{class_name}_percent' in combined_df.columns:

        # Get first and last year data
        first_year = combined_df.iloc[0]
        last_year = combined_df.iloc[-1]

        # Calculate changes
        area_change = last_year[class_name] - first_year[class_name]
        pct_point_change = last_year[f'{class_name}_percent'] - first_year[f'{class_name}_percent']

        if first_year[class_name] > 0:
            relative_change = (area_change / first_year[class_name]) * 100
        else:
            relative_change = 0

        print(f"\n{class_name}:")
        print(f"   {int(first_year['year'])}: {first_year[class_name]:.1f} km² ({first_year[f'{class_name}_percent']:.1f}%)")
        print(f"   {int(last_year['year'])}: {last_year[class_name]:.1f} km² ({last_year[f'{class_name}_percent']:.1f}%)")
        print(f"   Change: {area_change:+.1f} km² ({pct_point_change:+.1f} percentage points)")
        print(f"   Relative change: {relative_change:+.1f}%")

# Temporal trends
print("\n3. TEMPORAL TRENDS")
print("-" * 80)

# Calculate annual rates of change for key classes
key_classes = ['Trees', 'Built', 'Crops', 'Bare']

for class_name in key_classes:
    if f'{class_name}_percent' in combined_df.columns:

        # Calculate year-over-year changes
        combined_df[f'{class_name}_change'] = combined_df[f'{class_name}_percent'].diff()

        # Statistics
        mean_change = combined_df[f'{class_name}_change'].mean()
        std_change = combined_df[f'{class_name}_change'].std()
        max_increase = combined_df[f'{class_name}_change'].max()
        max_decrease = combined_df[f'{class_name}_change'].min()

        print(f"\n{class_name}:")
        print(f"   Mean annual change: {mean_change:+.3f} percentage points/year")
        print(f"   Std deviation: {std_change:.3f}")
        print(f"   Maximum increase: {max_increase:+.3f} percentage points")
        print(f"   Maximum decrease: {max_decrease:+.3f} percentage points")

# Dataset comparison (overlap years)
print("\n4. DATASET COMPARISON")
print("-" * 80)

overlap_years = [2018, 2019, 2020]
print(f"Comparing datasets for overlap years: {overlap_years}")

for year in overlap_years:
    year_data = combined_df[combined_df['year'] == year]
    if len(year_data) > 0:
        print(f"\n{int(year)}:")
        for class_name in key_classes:
            if class_name in year_data.columns:
                values = year_data[class_name].values
                print(f"   {class_name}: {values[0]:.1f} km²")

# Save statistical summary
stats_summary = {
    'analysis_info': {
        'analysis_date': datetime.now().isoformat(),
        'study_area_km2': float(STUDY_AREA_KM2),
        'years_analyzed': combined_df['year'].tolist(),
        'datasets': combined_df['dataset'].unique().tolist(),
        'temporal_range': f"{int(combined_df['year'].min())}-{int(combined_df['year'].max())}"
    },
    'land_cover_changes': {}
}

for class_name in SIMPLIFIED_CLASSES.values():
    if class_name in combined_df.columns:
        first_year = combined_df.iloc[0]
        last_year = combined_df.iloc[-1]

        stats_summary['land_cover_changes'][class_name] = {
            'initial_area_km2': float(first_year[class_name]),
            'final_area_km2': float(last_year[class_name]),
            'absolute_change_km2': float(last_year[class_name] - first_year[class_name]),
            'percentage_point_change': float(last_year[f'{class_name}_percent'] - first_year[f'{class_name}_percent']) if f'{class_name}_percent' in combined_df.columns else None
        }

stats_file = f'outputs/western_ghats_statistical_summary_{timestamp}.json'
with open(stats_file, 'w') as f:
    json.dump(stats_summary, f, indent=2)

print(f"\nStatistical summary saved: {stats_file}")


# In[ ]:


# CREATE COMPREHENSIVE VISUALIZATIONS

print("Creating comprehensive visualizations...")

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Create figure with multiple subplots
fig = plt.figure(figsize=(20, 12))

# 1. Long-term trends for key classes
ax1 = plt.subplot(2, 3, 1)
for class_name in ['Trees', 'Built', 'Crops']:
    if f'{class_name}_percent' in combined_df.columns:
        ax1.plot(combined_df['year'], combined_df[f'{class_name}_percent'], 
                marker='o', linewidth=2, markersize=6, label=class_name)

ax1.set_title('Long-term Land Cover Trends (1985-2023)', fontweight='bold', fontsize=12)
ax1.set_xlabel('Year')
ax1.set_ylabel('Percentage of Total Area (%)')
ax1.legend(loc='best')
ax1.grid(True, alpha=0.3)

# 2. Built-up area expansion
ax2 = plt.subplot(2, 3, 2)
if 'Built' in combined_df.columns:
    bars = ax2.bar(combined_df['year'], combined_df['Built'], 
                   color='#D32F2F', alpha=0.7, width=1.5)
    ax2.set_title('Built-up Area Expansion', fontweight='bold', fontsize=12)
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Built-up Area (km²)')
    ax2.grid(True, alpha=0.3, axis='y')

# 3. Forest cover trends
ax3 = plt.subplot(2, 3, 3)
if 'Trees' in combined_df.columns:
    ax3.plot(combined_df['year'], combined_df['Trees'], 
            marker='o', color='#2E7D32', linewidth=2, markersize=6)
    ax3.fill_between(combined_df['year'], combined_df['Trees'], alpha=0.3, color='#2E7D32')
    ax3.set_title('Forest Cover Over Time', fontweight='bold', fontsize=12)
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Forest Area (km²)')
    ax3.grid(True, alpha=0.3)

# 4. Rate of change analysis
ax4 = plt.subplot(2, 3, 4)
if 'Built_change' in combined_df.columns:
    changes = combined_df[['year', 'Trees_change', 'Built_change', 'Crops_change']].dropna()
    width = 0.25
    x = np.arange(len(changes))

    ax4.bar(x - width, changes['Trees_change'], width, label='Trees', color='#2E7D32', alpha=0.7)
    ax4.bar(x, changes['Built_change'], width, label='Built', color='#D32F2F', alpha=0.7)
    ax4.bar(x + width, changes['Crops_change'], width, label='Crops', color='#F57C00', alpha=0.7)

    ax4.set_title('Year-over-Year Changes', fontweight='bold', fontsize=12)
    ax4.set_xlabel('Year')
    ax4.set_ylabel('Change (percentage points)')
    ax4.set_xticks(x[::2])
    ax4.set_xticklabels(changes['year'].astype(int).values[::2], rotation=45)
    ax4.legend()
    ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax4.grid(True, alpha=0.3)

# 5. Land cover composition (latest year)
ax5 = plt.subplot(2, 3, 5)
latest = combined_df.iloc[-1]
classes_to_plot = ['Trees', 'Crops', 'Built', 'Shrub and scrub', 'Water', 'Grass', 'Bare']
areas = [latest.get(cls, 0) for cls in classes_to_plot]
colors_plot = ['#2E7D32', '#F57C00', '#D32F2F', '#795548', '#1976D2', '#689F38', '#757575']

# Filter out zero values
non_zero = [(cls, area, col) for cls, area, col in zip(classes_to_plot, areas, colors_plot) if area > 0]
if non_zero:
    classes_filtered, areas_filtered, colors_filtered = zip(*non_zero)
    wedges, texts, autotexts = ax5.pie(areas_filtered, labels=classes_filtered, autopct='%1.1f%%',
                                       colors=colors_filtered, startangle=90)
    ax5.set_title(f'Land Cover Composition {int(latest["year"])}', fontweight='bold', fontsize=12)

# 6. Cumulative change from baseline
ax6 = plt.subplot(2, 3, 6)
baseline = combined_df.iloc[0]
for class_name in ['Trees', 'Built', 'Crops']:
    if class_name in combined_df.columns:
        cumulative_change = combined_df[class_name] - baseline[class_name]
        ax6.plot(combined_df['year'], cumulative_change, 
                marker='o', linewidth=2, markersize=6, label=class_name)

ax6.set_title('Cumulative Change from 1985 Baseline', fontweight='bold', fontsize=12)
ax6.set_xlabel('Year')
ax6.set_ylabel('Change in Area (km²)')
ax6.legend()
ax6.axhline(y=0, color='black', linestyle='--', linewidth=0.5)
ax6.grid(True, alpha=0.3)

plt.tight_layout()

# Save comprehensive visualization
viz_file = f'outputs/western_ghats_comprehensive_analysis_{timestamp}.png'
plt.savefig(viz_file, dpi=300, bbox_inches='tight')
plt.show()

print(f"Comprehensive visualization saved: {viz_file}")


# ## Analysis Complete
# 
# The historical LULC analysis has been completed successfully. Key outputs:
# 
# 1. **Historical LULC data (1985-2020)** at 5-year intervals using GLC-FCS30D
# 2. **Combined dataset** integrating GLC-FCS30D and Dynamic World results
# 3. **Comprehensive statistical analysis** with detailed change metrics
# 4. **Visualizations** showing long-term trends and patterns
# 
# Next steps:
# - Generate interactive HTML comparison tool
# - Create detailed statistical reports
# - Prepare outputs for presentation
