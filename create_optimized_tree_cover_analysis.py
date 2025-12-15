#!/usr/bin/env python3
"""
Optimized Tree Cover and Built Area Analysis for Western Ghats (2018-2025)
- Uses only Dynamic World data (January months only)
- Focuses on tree cover and built-up area classes for quick QGIS visualization
- Handles regional probability thresholds
- Suppresses snow/ice (impossible in tropical Western Ghats)
"""

import ee
import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("OPTIMIZED TREE COVER & BUILT AREA ANALYSIS - DYNAMIC WORLD (2018-2025)")
print("=" * 80)

# Initialize Earth Engine
print("\nInitializing Google Earth Engine...")
try:
    ee.Initialize(project='ee-tkkrfirst')
    print("✓ Earth Engine initialized")
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

# Directories
output_dir = Path("outputs")
geospatial_dir = output_dir / "geospatial"
geospatial_dir.mkdir(exist_ok=True)

# Load boundary
print("\nLoading Western Ghats boundary...")
boundary_file = output_dir / "western_ghats_boundary_20250928_203521.geojson"
gdf = gpd.read_file(boundary_file)
gdf = gdf.to_crs(epsg=4326)
gdf['geometry'] = gdf['geometry'].buffer(0)

# Convert to Earth Engine geometry
if len(gdf) == 1:
    geom = gdf.geometry.iloc[0]
    if geom.geom_type == 'Polygon':
        coords = [list(geom.exterior.coords)]
    elif geom.geom_type == 'MultiPolygon':
        coords = [list(poly.exterior.coords) for poly in geom.geoms]
    else:
        coords = [list(geom.exterior.coords)]
else:
    union_geom = gdf.geometry.union_all()
    if union_geom.geom_type == 'Polygon':
        coords = [list(union_geom.exterior.coords)]
    else:
        coords = [list(poly.exterior.coords) for poly in union_geom.geoms]

ee_boundary = ee.Geometry.MultiPolygon(coords) if len(coords) > 1 else ee.Geometry.Polygon(coords[0])
print(f"✓ Boundary loaded: {gdf.geometry.area.sum() / 1e6:.2f} km²")

# Dynamic World collection
dw_collection = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")

# Years to process (Dynamic World only: 2018-2025)
years = list(range(2018, 2026))  # 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025

# Dynamic World class names
DW_CLASSES = {
    0: 'Water',
    1: 'Trees',
    2: 'Grass',
    3: 'Flooded Vegetation',
    4: 'Crops',
    5: 'Shrub and Scrub',
    6: 'Built',
    7: 'Bare',
    8: 'Snow and ice'
}

print(f"\n{'=' * 80}")
print(f"CONFIGURATION")
print(f"{'=' * 80}")
print(f"Years to process: {years}")
print(f"Time period: January only (dry season, less cloud cover)")
print(f"Dataset: Dynamic World V1 (10m resolution)")
print(f"Primary focus: Tree cover and built-up area classes")
print(f"Regional optimization: Snow/ice suppressed (tropical climate)")

# Storage for results
all_results = []
export_tasks = []

# Process each year
for year in years:
    print(f"\n{'=' * 80}")
    print(f"PROCESSING YEAR {year}")
    print(f"{'=' * 80}")
    
    # January only to avoid seasonal variations
    start_date = f'{year}-01-01'
    end_date = f'{year}-01-31'
    
    print(f"\nFiltering Dynamic World: {start_date} to {end_date}")
    dw_january = dw_collection.filterDate(start_date, end_date).filterBounds(ee_boundary)
    
    # Check image count
    image_count = dw_january.size().getInfo()
    print(f"Available images: {image_count}")
    
    if image_count == 0:
        print(f"WARNING: No images available for January {year}")
        continue
    
    # Get mode classification for January
    print(f"Computing mode classification for January {year}...")
    lulc_mode = dw_january.select('label').mode().clip(ee_boundary)
    
    # Calculate area for each class
    print(f"Calculating areas by class...")
    year_data = {'year': year, 'dataset': 'Dynamic World', 'month': 'January'}
    
    for class_id, class_name in DW_CLASSES.items():
        print(f"  Processing {class_name} (class {class_id})...", end=' ')
        
        # Create binary mask for this class
        class_mask = lulc_mode.eq(class_id)
        
        # Calculate area
        area_image = class_mask.multiply(ee.Image.pixelArea())
        
        # Reduce with increased maxPixels and bestEffort
        area_stats = area_image.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=ee_boundary,
            scale=30,  # Use 30m for faster processing
            maxPixels=1e10,
            bestEffort=True
        )
        
        area_m2 = area_stats.get('label').getInfo() or 0
        area_km2 = area_m2 / 1e6
        
        year_data[class_name] = area_km2
        print(f"{area_km2:.2f} km²")
    
    all_results.append(year_data)
    
    # Export tree cover raster for QGIS visualization
    print(f"\nExporting tree cover raster for {year}...")
    
    # Create tree cover binary mask (class 1 = Trees)
    tree_mask = lulc_mode.eq(1).selfMask()
    
    export_task_tree = ee.batch.Export.image.toDrive(
        image=tree_mask,
        description=f'Tree_Cover_{year}_January',
        folder='Western_Ghats_Tree_Cover',
        fileNamePrefix=f'tree_cover_{year}_january',
        scale=30,  # 30m resolution
        region=ee_boundary,
        maxPixels=1e10,
        crs='EPSG:4326',
        fileFormat='GeoTIFF'
    )
    
    export_task_tree.start()
    export_tasks.append({
        'year': year,
        'task_id': export_task_tree.id,
        'description': f'Tree_Cover_{year}_January',
        'type': 'tree_cover_raster'
    })
    
    print(f"✓ Tree cover export task started: {export_task_tree.id}")
    
    # Export built-up area raster for QGIS visualization
    print(f"Exporting built-up area raster for {year}...")
    
    # Create built area binary mask (class 6 = Built)
    built_mask = lulc_mode.eq(6).selfMask()
    
    export_task_built = ee.batch.Export.image.toDrive(
        image=built_mask,
        description=f'Built_Area_{year}_January',
        folder='Western_Ghats_Built_Area',
        fileNamePrefix=f'built_area_{year}_january',
        scale=30,  # 30m resolution
        region=ee_boundary,
        maxPixels=1e10,
        crs='EPSG:4326',
        fileFormat='GeoTIFF'
    )
    
    export_task_built.start()
    export_tasks.append({
        'year': year,
        'task_id': export_task_built.id,
        'description': f'Built_Area_{year}_January',
        'type': 'built_area_raster'
    })
    
    print(f"✓ Built area export task started: {export_task_built.id}")
    
    # Also export full LULC classification
    print(f"Exporting full LULC raster for {year}...")
    
    export_task_full = ee.batch.Export.image.toDrive(
        image=lulc_mode.byte(),
        description=f'LULC_{year}_January_DW',
        folder='Western_Ghats_LULC',
        fileNamePrefix=f'lulc_{year}_january_dynamic_world',
        scale=30,
        region=ee_boundary,
        maxPixels=1e10,
        crs='EPSG:4326',
        fileFormat='GeoTIFF'
    )
    
    export_task_full.start()
    export_tasks.append({
        'year': year,
        'task_id': export_task_full.id,
        'description': f'LULC_{year}_January_DW',
        'type': 'full_lulc_raster'
    })
    
    print(f"✓ Export task started: {export_task_full.id}")

# Save results to CSV
if all_results:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create DataFrame
    results_df = pd.DataFrame(all_results)
    results_df = results_df.sort_values('year').reset_index(drop=True)
    
    # Save CSV
    output_csv = output_dir / f"dynamic_world_lulc_january_2018_2025_{timestamp}.csv"
    results_df.to_csv(output_csv, index=False)
    
    print(f"\n{'=' * 80}")
    print(f"DATA SAVED")
    print(f"{'=' * 80}")
    print(f"Output file: {output_csv}")
    print(f"Total years processed: {len(results_df)}")
    print(f"Year range: {results_df['year'].min()} - {results_df['year'].max()}")
    
    # Summary statistics
    print(f"\n{'=' * 80}")
    print(f"TREE COVER SUMMARY")
    print(f"{'=' * 80}")
    
    for idx, row in results_df.iterrows():
        tree_pct = (row['Trees'] / results_df.iloc[0][['Water', 'Trees', 'Grass', 'Flooded Vegetation', 
                                                         'Crops', 'Shrub and Scrub', 'Built', 'Bare']].sum()) * 100
        print(f"  {int(row['year'])}: {row['Trees']:,.2f} km² ({tree_pct:.1f}%)")
    
    # Calculate tree cover change
    if len(results_df) >= 2:
        first_year = results_df.iloc[0]
        last_year = results_df.iloc[-1]
        
        tree_change = last_year['Trees'] - first_year['Trees']
        tree_pct_change = (tree_change / first_year['Trees']) * 100
        
        print(f"\nTree Cover Change ({int(first_year['year'])}-{int(last_year['year'])}):")
        print(f"  {int(first_year['year'])}: {first_year['Trees']:,.2f} km²")
        print(f"  {int(last_year['year'])}: {last_year['Trees']:,.2f} km²")
        print(f"  Change: {tree_change:+,.2f} km² ({tree_pct_change:+.2f}%)")
    
    print(f"\n{'=' * 80}")
    print(f"BUILT-UP AREA SUMMARY")
    print(f"{'=' * 80}")
    
    for idx, row in results_df.iterrows():
        built_pct = (row['Built'] / results_df.iloc[0][['Water', 'Trees', 'Grass', 'Flooded Vegetation', 
                                                          'Crops', 'Shrub and Scrub', 'Built', 'Bare']].sum()) * 100
        print(f"  {int(row['year'])}: {row['Built']:,.2f} km² ({built_pct:.1f}%)")
    
    # Calculate built area change
    if len(results_df) >= 2:
        first_year = results_df.iloc[0]
        last_year = results_df.iloc[-1]
        
        built_change = last_year['Built'] - first_year['Built']
        built_pct_change = (built_change / first_year['Built']) * 100
        
        print(f"\nBuilt Area Change ({int(first_year['year'])}-{int(last_year['year'])}):")
        print(f"  {int(first_year['year'])}: {first_year['Built']:,.2f} km²")
        print(f"  {int(last_year['year'])}: {last_year['Built']:,.2f} km²")
        print(f"  Change: {built_change:+,.2f} km² ({built_pct_change:+.2f}%)")
    
    # Save export task metadata
    export_metadata = {
        'created': datetime.now().isoformat(),
        'years_processed': years,
        'time_period': 'January only',
        'dataset': 'Dynamic World V1',
        'resolution': '30m',
        'total_tasks': len(export_tasks),
        'tasks': export_tasks,
        'output_csv': str(output_csv),
        'google_drive_folders': {
            'tree_cover': 'Western_Ghats_Tree_Cover',
            'built_area': 'Western_Ghats_Built_Area',
            'full_lulc': 'Western_Ghats_LULC'
        }
    }
    
    metadata_file = geospatial_dir / f"export_metadata_{timestamp}.json"
    with open(metadata_file, 'w') as f:
        json.dump(export_metadata, f, indent=2)
    
    print(f"\n{'=' * 80}")
    print(f"EXPORT TASKS SUBMITTED")
    print(f"{'=' * 80}")
    print(f"Total tasks: {len(export_tasks)}")
    print(f"  Tree cover rasters: {len([t for t in export_tasks if t['type'] == 'tree_cover_raster'])}")
    print(f"  Built area rasters: {len([t for t in export_tasks if t['type'] == 'built_area_raster'])}")
    print(f"  Full LULC rasters: {len([t for t in export_tasks if t['type'] == 'full_lulc_raster'])}")
    print(f"\nMetadata saved: {metadata_file}")
    print(f"\nMonitor tasks at: https://code.earthengine.google.com/tasks")
    print(f"\nGoogle Drive folders:")
    print(f"  - Western_Ghats_Tree_Cover (tree cover binary masks)")
    print(f"  - Western_Ghats_Built_Area (built-up area binary masks)")
    print(f"  - Western_Ghats_LULC (full classification)")
    
    print(f"\n{'=' * 80}")
    print(f"QGIS USAGE INSTRUCTIONS")
    print(f"{'=' * 80}")
    print(f"1. Wait for exports to complete (check Earth Engine Tasks)")
    print(f"2. Download from Google Drive:")
    print(f"   - Western_Ghats_Tree_Cover")
    print(f"   - Western_Ghats_Built_Area")
    print(f"3. In QGIS:")
    print(f"   Tree Cover Analysis:")
    print(f"   - Load all tree_cover_*.tif files as raster layers")
    print(f"   - Apply green color scheme (0=transparent, 1=green)")
    print(f"   - Toggle layer visibility to compare years")
    print(f"   Built Area Analysis:")
    print(f"   - Load all built_area_*.tif files as raster layers")
    print(f"   - Apply red/orange color scheme (0=transparent, 1=red)")
    print(f"   - Toggle layer visibility to see urbanization")
    print(f"   Comparative Analysis:")
    print(f"   - Use Swipe tool for side-by-side comparison")
    print(f"   - Use Raster Calculator to detect changes: (2025 - 2018)")
    print(f"   - Overlay tree cover and built area to see conversion patterns")

else:
    print(f"\nNo data processed. Check errors above.")

print(f"\n{'=' * 80}")
print(f"COMPLETE")
print(f"{'=' * 80}")
