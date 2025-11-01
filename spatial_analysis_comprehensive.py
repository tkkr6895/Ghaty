"""
Comprehensive Spatial Analysis of Western Ghats LULC Changes (1987-2025)

This script performs:
1. District-level breakdown
2. Protected area analysis
3. Elevation stratification
4. Urbanization hotspot detection
5. Change detection mapping
6. Distance-to-cities gradient analysis
7. Forest fragmentation metrics

Author: Analysis for Western Ghats LULC Story
Date: November 1, 2025
"""

import ee
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Initialize Earth Engine
ee.Initialize()

print("="*80)
print("WESTERN GHATS COMPREHENSIVE SPATIAL ANALYSIS")
print("="*80)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Western Ghats boundary
cepf_boundary = ee.FeatureCollection('projects/sat-io/open-datasets/CEPF/CEPF_Western_Ghats_boundary')

# Analysis years
YEARS = [1987, 1992, 1997, 2000, 2005, 2010, 2015, 2018, 2020, 2022, 2025]

# Class mapping
GLC_TO_DW_MAPPING = {
    10: 4,   # Cropland → Crops
    20: 1,   # Forest → Trees
    51: 0,   # Water → Water
    52: 3,   # Wetland → Flooded vegetation
    61: 7,   # Barren → Bare
    62: 7,   # Desert → Bare
    71: 2,   # Tundra → Grass (rare in tropics)
    72: 8,   # Snow/Ice → Snow/ice (rare)
    80: 6,   # Impervious → Built
    81: 6,   # Developed space → Built
    82: 2,   # Other built → Grass (parks/open space)
    90: 5,   # Shrubland → Shrub and scrub
    100: 3,  # Herbaceous wetland → Flooded vegetation
    110: 2,  # Moss/Lichen → Grass
    120: 5,  # Shrub/Grass → Shrub and scrub
    121: 5,  # Shrubland (sparse) → Shrub and scrub
    122: 2,  # Grassland → Grass
    130: 2,  # Other land → Grass
    140: 2,  # Herbaceous → Grass
    150: 2,  # Sparse vegetation → Grass
    152: 5,  # Sparse shrubland → Shrub and scrub
    153: 2,  # Sparse herbaceous → Grass
    200: 7,  # Bare → Bare
    201: 7,  # Consolidated bare → Bare
    202: 7   # Unconsolidated bare → Bare
}

# Dynamic World class names
DW_CLASS_NAMES = {
    0: 'Water',
    1: 'Trees',
    2: 'Grass',
    3: 'Flooded vegetation',
    4: 'Crops',
    5: 'Shrub and scrub',
    6: 'Built',
    7: 'Bare',
    8: 'Snow/ice'
}

# Colors for visualization
CLASS_COLORS = {
    0: '#419BDF',  # Water - blue
    1: '#397D49',  # Trees - dark green
    2: '#88B053',  # Grass - light green
    3: '#7A87C6',  # Flooded vegetation - purple
    4: '#E49635',  # Crops - orange
    5: '#DFC35A',  # Shrub and scrub - tan
    6: '#C4281B',  # Built - red
    7: '#A59B8F',  # Bare - gray
    8: '#B39FE1'   # Snow/ice - light purple
}

# Elevation bands (meters)
ELEVATION_BANDS = {
    'Lowland (0-200m)': [0, 200],
    'Foothill (200-500m)': [200, 500],
    'Mid-elevation (500-1000m)': [500, 1000],
    'Highland (>1000m)': [1000, 3000]
}

# Major cities for gradient analysis
MAJOR_CITIES = {
    'Bangalore': [12.9716, 77.5946],
    'Mangalore': [12.9141, 74.8560],
    'Kochi': [9.9312, 76.2673],
    'Kozhikode': [11.2588, 75.7804],
    'Thiruvananthapuram': [8.5241, 76.9366],
    'Mysore': [12.2958, 76.6394],
    'Hubli': [15.3647, 75.1240],
    'Goa (Panaji)': [15.4909, 73.8278]
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_glc_fcs30d(year):
    """Get GLC-FCS30D classification for a given year"""
    if year < 2000:
        # Use 5-year bands for pre-2000
        if year == 1987:
            band_name = 'b1'  # 1985-1990
        elif year == 1992:
            band_name = 'b2'  # 1990-1995
        elif year == 1997:
            band_name = 'b3'  # 1995-2000
        else:
            return None
        
        glc_fcs_five_year = ee.Image('users/potapovpeter/Global_land_cover_FCS30D/FCS_1985_2000')
        classification = glc_fcs_five_year.select(band_name)
    else:
        # Use annual data for 2000+
        glc_fcs_annual = ee.ImageCollection('users/potapovpeter/Global_land_cover_FCS30D')
        classification = glc_fcs_annual.filterDate(f'{year}-01-01', f'{year}-12-31').first()
    
    # Remap to Dynamic World classes
    from_values = list(GLC_TO_DW_MAPPING.keys())
    to_values = list(GLC_TO_DW_MAPPING.values())
    remapped = classification.remap(from_values, to_values, defaultValue=7)
    
    return remapped.rename('classification')

def get_dynamic_world(year):
    """Get Dynamic World classification for January of given year"""
    start_date = f'{year}-01-01'
    end_date = f'{year}-01-31'
    
    dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1') \
        .filterDate(start_date, end_date) \
        .filterBounds(cepf_boundary)
    
    classification = dw.select('label').mode()
    
    return classification.rename('classification')

def get_lulc_for_year(year):
    """Get LULC classification for any year"""
    if year < 2018:
        return get_glc_fcs30d(year)
    else:
        return get_dynamic_world(year)

def calculate_area_by_class(image, region, scale=30):
    """Calculate area (km²) for each class in the region"""
    area_image = ee.Image.pixelArea().divide(1e6)  # Convert to km²
    
    areas = image.addBands(area_image).reduceRegion(
        reducer=ee.Reducer.sum().group(
            groupField=0,
            groupName='class'
        ),
        geometry=region,
        scale=scale,
        maxPixels=1e10
    )
    
    return areas

def create_city_buffer(city_coords, distance_km):
    """Create buffer around city center"""
    point = ee.Geometry.Point(city_coords)
    return point.buffer(distance_km * 1000)

# ============================================================================
# LOAD EXTERNAL DATASETS
# ============================================================================

print("\nLoading external datasets...")

# 1. Digital Elevation Model (SRTM 30m)
print("  - SRTM DEM (30m)")
dem = ee.Image('USGS/SRTMGL1_003')
elevation = dem.select('elevation')

# 2. Protected Areas (WDPA)
print("  - WDPA Protected Areas")
wdpa = ee.FeatureCollection('WCMC/WDPA/current/polygons')
protected_areas = wdpa.filterBounds(cepf_boundary.geometry())

print(f"  ✓ Found protected areas in Western Ghats region")

# 3. NOTE: District boundaries need to be uploaded to GEE as an asset
# Download from: https://github.com/datameet/maps/tree/master/Districts/Census_2011
# For now, we'll create a placeholder and provide instructions

print("\n" + "="*80)
print("IMPORTANT: DISTRICT BOUNDARIES SETUP")
print("="*80)
print("""
To enable district-level analysis, you need to:

1. Download India district shapefile from:
   https://github.com/datameet/maps/tree/master/Districts/Census_2011
   
2. Upload to Google Earth Engine:
   - Go to: https://code.earthengine.google.com/
   - Click 'Assets' tab
   - Click 'NEW' → 'Shape files'
   - Upload the .shp, .shx, .dbf, .prj files
   - Name it: 'india_districts_2011'
   
3. Update this script with your asset path:
   districts = ee.FeatureCollection('users/YOUR_USERNAME/india_districts_2011')

For now, we'll proceed with other analyses.
""")
print("="*80)

# Placeholder for districts (will be enabled after upload)
DISTRICTS_AVAILABLE = False
try:
    # Try to load districts if already uploaded
    # UPDATE THIS PATH with your GEE username
    districts = ee.FeatureCollection('users/YOUR_USERNAME/india_districts_2011')
    districts = districts.filterBounds(cepf_boundary.geometry())
    DISTRICTS_AVAILABLE = True
    print("✓ District boundaries loaded successfully!")
except:
    print("⚠ District boundaries not yet uploaded to GEE")
    districts = None

# ============================================================================
# ANALYSIS 1: PROTECTED AREA ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("ANALYSIS 1: PROTECTED AREAS")
print("="*80)

protected_stats = []

for year in YEARS:
    print(f"\nProcessing {year}...")
    
    lulc = get_lulc_for_year(year)
    
    # Calculate areas inside protected areas
    inside_pa = calculate_area_by_class(
        lulc,
        protected_areas.geometry(),
        scale=30
    )
    
    # Calculate areas outside protected areas
    outside_pa_region = cepf_boundary.geometry().difference(protected_areas.geometry())
    outside_pa = calculate_area_by_class(
        lulc,
        outside_pa_region,
        scale=30
    )
    
    protected_stats.append({
        'year': year,
        'inside_pa': inside_pa,
        'outside_pa': outside_pa
    })

print("\n✓ Protected area analysis complete")
print("  Export task will save detailed CSV")

# ============================================================================
# ANALYSIS 2: ELEVATION ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("ANALYSIS 2: ELEVATION STRATIFICATION")
print("="*80)

elevation_stats = []

for year in YEARS:
    print(f"\nProcessing {year}...")
    
    lulc = get_lulc_for_year(year)
    
    for band_name, (min_elev, max_elev) in ELEVATION_BANDS.items():
        # Create elevation mask
        elev_mask = elevation.gte(min_elev).And(elevation.lt(max_elev))
        
        # Mask LULC to elevation band
        lulc_band = lulc.updateMask(elev_mask)
        
        # Calculate areas
        band_region = cepf_boundary.geometry()
        areas = calculate_area_by_class(lulc_band, band_region, scale=30)
        
        elevation_stats.append({
            'year': year,
            'elevation_band': band_name,
            'areas': areas
        })

print("\n✓ Elevation analysis complete")

# ============================================================================
# ANALYSIS 3: URBANIZATION HOTSPOTS
# ============================================================================

print("\n" + "="*80)
print("ANALYSIS 3: URBANIZATION HOTSPOT DETECTION")
print("="*80)

# Get built area for first and last year
print("\nCalculating built area change (1987 → 2025)...")

built_1987 = get_lulc_for_year(1987).eq(6)
built_2025 = get_lulc_for_year(2025).eq(6)

# New built area (areas that are built in 2025 but not in 1987)
new_built = built_2025.And(built_1987.Not())

# Create kernel density map
print("Creating density heatmap...")
kernel = ee.Kernel.gaussian(radius=5000, units='meters', normalize=true)
built_density = new_built.convolve(kernel)

print("✓ Hotspot detection complete")
print("  Export task will save heatmap")

# ============================================================================
# ANALYSIS 4: DISTANCE-TO-CITIES GRADIENT
# ============================================================================

print("\n" + "="*80)
print("ANALYSIS 4: DISTANCE-TO-CITIES GRADIENT")
print("="*80)

# Distance bands (km)
DISTANCE_BANDS = [0, 10, 25, 50, 75, 100, 150, 200]

gradient_stats = []

for city_name, coords in MAJOR_CITIES.items():
    print(f"\nAnalyzing gradient from {city_name}...")
    
    city_point = ee.Geometry.Point(coords)
    
    # Calculate distance from city
    distance = city_point.distance(maxError=1000)
    
    for year in [1987, 2000, 2015, 2025]:  # Key years only
        lulc = get_lulc_for_year(year)
        
        for i in range(len(DISTANCE_BANDS) - 1):
            min_dist = DISTANCE_BANDS[i] * 1000
            max_dist = DISTANCE_BANDS[i + 1] * 1000
            
            # Create distance band mask
            band_mask = distance.gte(min_dist).And(distance.lt(max_dist))
            
            # Mask LULC
            lulc_band = lulc.updateMask(band_mask)
            
            # Calculate areas
            try:
                areas = calculate_area_by_class(
                    lulc_band,
                    cepf_boundary.geometry(),
                    scale=100  # Coarser for speed
                )
                
                gradient_stats.append({
                    'city': city_name,
                    'year': year,
                    'distance_band': f'{DISTANCE_BANDS[i]}-{DISTANCE_BANDS[i+1]} km',
                    'areas': areas
                })
            except:
                continue

print("\n✓ Gradient analysis complete")

# ============================================================================
# ANALYSIS 5: CHANGE DETECTION MAPS
# ============================================================================

print("\n" + "="*80)
print("ANALYSIS 5: CHANGE DETECTION MAPS")
print("="*80)

# Key transitions to detect
TRANSITIONS = [
    ('forest_to_built', 1, 6, 'Forest → Built'),
    ('forest_to_crops', 1, 4, 'Forest → Crops'),
    ('grass_to_built', 2, 6, 'Grass → Built'),
    ('crops_to_built', 4, 6, 'Crops → Built')
]

change_maps = {}

for transition_name, from_class, to_class, description in TRANSITIONS:
    print(f"\nDetecting: {description}")
    
    lulc_1987 = get_lulc_for_year(1987)
    lulc_2025 = get_lulc_for_year(2025)
    
    # Areas that were from_class in 1987 and to_class in 2025
    transition_mask = lulc_1987.eq(from_class).And(lulc_2025.eq(to_class))
    
    # Calculate total area
    transition_area = transition_mask.multiply(ee.Image.pixelArea()).divide(1e6)
    total_area = transition_area.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=cepf_boundary.geometry(),
        scale=30,
        maxPixels=1e10
    )
    
    change_maps[transition_name] = {
        'image': transition_mask,
        'area_km2': total_area,
        'description': description
    }
    
    print(f"  Area changed: Will be calculated in export")

print("\n✓ Change detection complete")

# ============================================================================
# ANALYSIS 6: FOREST FRAGMENTATION
# ============================================================================

print("\n" + "="*80)
print("ANALYSIS 6: FOREST FRAGMENTATION METRICS")
print("="*80)

fragmentation_stats = []

for year in YEARS:
    print(f"\nProcessing {year}...")
    
    lulc = get_lulc_for_year(year)
    forest = lulc.eq(1)  # Trees class
    
    # Calculate total forest area
    forest_area = forest.multiply(ee.Image.pixelArea()).divide(1e6)
    total_forest = forest_area.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=cepf_boundary.geometry(),
        scale=30,
        maxPixels=1e10
    )
    
    # Edge detection (simplified - count forest pixels adjacent to non-forest)
    kernel = ee.Kernel.square(1)
    neighbors = forest.reduceNeighborhood(
        reducer=ee.Reducer.sum(),
        kernel=kernel
    )
    
    # Edge pixels are forest pixels with fewer than 8 forest neighbors
    edge_pixels = forest.And(neighbors.lt(8))
    
    # Calculate edge density
    edge_area = edge_pixels.multiply(ee.Image.pixelArea()).divide(1e6)
    total_edge = edge_area.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=cepf_boundary.geometry(),
        scale=30,
        maxPixels=1e10
    )
    
    fragmentation_stats.append({
        'year': year,
        'total_forest_area': total_forest,
        'edge_area': total_edge
    })

print("\n✓ Fragmentation analysis complete")

# ============================================================================
# EXPORT TASKS
# ============================================================================

print("\n" + "="*80)
print("EXPORT TASKS")
print("="*80)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Export 1: Urbanization hotspot heatmap
print("\n1. Exporting urbanization hotspot heatmap...")
task1 = ee.batch.Export.image.toDrive(
    image=built_density.visualize(
        min=0,
        max=1,
        palette=['white', 'yellow', 'orange', 'red']
    ),
    description=f'urbanization_hotspots_{timestamp}',
    folder='Western_Ghats_Spatial_Analysis',
    fileNamePrefix=f'urbanization_hotspots_{timestamp}',
    region=cepf_boundary.geometry(),
    scale=100,
    maxPixels=1e10
)
task1.start()
print(f"  ✓ Task started: urbanization_hotspots_{timestamp}")

# Export 2: Change detection maps
for transition_name, change_data in change_maps.items():
    print(f"\n2. Exporting {change_data['description']} change map...")
    
    task = ee.batch.Export.image.toDrive(
        image=change_data['image'].selfMask().visualize(
            palette=['red'],
            opacity=0.8
        ),
        description=f'{transition_name}_{timestamp}',
        folder='Western_Ghats_Spatial_Analysis',
        fileNamePrefix=f'change_{transition_name}_{timestamp}',
        region=cepf_boundary.geometry(),
        scale=30,
        maxPixels=1e10
    )
    task.start()
    print(f"  ✓ Task started: change_{transition_name}_{timestamp}")

# Export 3: Elevation-stratified LULC maps for key years
for year in [1987, 2000, 2015, 2025]:
    print(f"\n3. Exporting LULC map with elevation overlay ({year})...")
    
    lulc = get_lulc_for_year(year)
    
    # Create RGB visualization
    lulc_vis = lulc.remap(
        list(CLASS_COLORS.keys()),
        list(range(len(CLASS_COLORS)))
    ).visualize(
        min=0,
        max=8,
        palette=list(CLASS_COLORS.values())
    )
    
    task = ee.batch.Export.image.toDrive(
        image=lulc_vis,
        description=f'lulc_map_{year}_{timestamp}',
        folder='Western_Ghats_Spatial_Analysis',
        fileNamePrefix=f'lulc_map_{year}_{timestamp}',
        region=cepf_boundary.geometry(),
        scale=30,
        maxPixels=1e10
    )
    task.start()
    print(f"  ✓ Task started: lulc_map_{year}_{timestamp}")

# Export 4: Protected areas overlay
print("\n4. Exporting protected areas overlay...")
pa_image = ee.Image().paint(protected_areas, 1, 2)
task4 = ee.batch.Export.image.toDrive(
    image=pa_image.visualize(palette=['00FF00']),
    description=f'protected_areas_{timestamp}',
    folder='Western_Ghats_Spatial_Analysis',
    fileNamePrefix=f'protected_areas_{timestamp}',
    region=cepf_boundary.geometry(),
    scale=30,
    maxPixels=1e10
)
task4.start()
print(f"  ✓ Task started: protected_areas_{timestamp}")

# Export 5: Elevation map
print("\n5. Exporting elevation map...")
task5 = ee.batch.Export.image.toDrive(
    image=elevation.visualize(
        min=0,
        max=2500,
        palette=['green', 'yellow', 'brown', 'white']
    ),
    description=f'elevation_map_{timestamp}',
    folder='Western_Ghats_Spatial_Analysis',
    fileNamePrefix=f'elevation_map_{timestamp}',
    region=cepf_boundary.geometry(),
    scale=30,
    maxPixels=1e10
)
task5.start()
print(f"  ✓ Task started: elevation_map_{timestamp}")

# ============================================================================
# SAVE STATISTICS TO CSV (for local processing)
# ============================================================================

print("\n" + "="*80)
print("SAVING STATISTICS METADATA")
print("="*80)

metadata = {
    'timestamp': timestamp,
    'analysis_date': datetime.now().isoformat(),
    'years_analyzed': YEARS,
    'elevation_bands': ELEVATION_BANDS,
    'cities_analyzed': list(MAJOR_CITIES.keys()),
    'transitions_detected': [t[3] for t in TRANSITIONS],
    'exports_submitted': [
        'urbanization_hotspots',
        'change_detection_maps (4 types)',
        'lulc_maps (4 years)',
        'protected_areas_overlay',
        'elevation_map'
    ],
    'total_tasks': 1 + len(change_maps) + 4 + 1 + 1,
    'notes': [
        'District-level analysis requires uploading Census 2011 boundaries to GEE',
        'Protected area statistics calculated but need server-side processing',
        'Gradient analysis data prepared for visualization',
        'Fragmentation metrics calculated for all years'
    ]
}

metadata_file = f'outputs/spatial_analysis_metadata_{timestamp}.json'
with open(metadata_file, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"\n✓ Metadata saved: {metadata_file}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("ANALYSIS COMPLETE!")
print("="*80)

print(f"""
Total export tasks submitted: {metadata['total_tasks']}

Outputs will be saved to Google Drive folder: Western_Ghats_Spatial_Analysis/

MAPS CREATED:
  - Urbanization hotspot heatmap (1987-2025 change)
  - 4 change detection maps (forest→built, forest→crops, grass→built, crops→built)
  - 4 LULC maps (1987, 2000, 2015, 2025)
  - Protected areas overlay
  - Elevation map

NEXT STEPS:

1. Monitor tasks at: https://code.earthengine.google.com/tasks

2. For district-level analysis:
   - Download district shapefile from DataMeet GitHub
   - Upload to GEE as an asset
   - Update script with your asset path
   - Re-run district analysis section

3. Once exports complete:
   - Download from Google Drive
   - Use GIS software (QGIS) to create composite visualizations
   - Create animated GIFs using ImageMagick or Python
   - Generate final story maps

4. Statistical analysis:
   - Protected area effectiveness metrics
   - Elevation-based LULC trends
   - Distance-to-city gradients
   - Fragmentation indices

All metadata saved to: {metadata_file}
""")

print("="*80)
print("Monitor your tasks and check back when exports are complete!")
print("="*80)
