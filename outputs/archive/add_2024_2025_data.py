#!/usr/bin/env python3
"""
Add Dynamic World LULC analysis for 2024 and 2025
Extends the existing analysis with recent satellite observations
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
print("ADDING 2024 AND 2025 DYNAMIC WORLD DATA")
print("=" * 80)

# Initialize Earth Engine
print("\nInitializing Google Earth Engine...")
try:
    ee.Initialize(project='ee-tkkrfirst')
    print("Earth Engine initialized")
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
print(f"Boundary loaded")

# Calculate area for normalization
area_km2 = gdf.geometry.area.sum() / 1e6

# Load existing combined dataset
combined_csv = output_dir / "glc_fcs30d_combined_lulc_20251024_114642.csv"
existing_df = pd.read_csv(combined_csv)

print(f"\nExisting data: {len(existing_df)} years")
print(f"Year range: {existing_df['year'].min()} - {existing_df['year'].max()}")
print(f"Datasets: {existing_df['dataset'].unique().tolist()}")

# Dynamic World collection
dw_collection = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")

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

# Columns to match existing data structure
columns = ['year', 'dataset', 'Water', 'Trees', 'Grass', 'Flooded Vegetation', 
           'Crops', 'Shrub and Scrub', 'Built', 'Bare', 'Snow and ice']

new_data = []

for year in [2024, 2025]:
    print(f"\n{'=' * 80}")
    print(f"PROCESSING YEAR {year}")
    print(f"{'=' * 80}")
    
    # Check if data already exists
    if year in existing_df['year'].values:
        print(f"WARNING: Year {year} already exists in dataset. Will replace it.")
        existing_df = existing_df[existing_df['year'] != year]
    
    # Filter Dynamic World for this year
    start_date = f'{year}-01-01'
    end_date = f'{year}-12-31'
    
    print(f"\nFiltering Dynamic World: {start_date} to {end_date}")
    dw_year = dw_collection.filterDate(start_date, end_date).filterBounds(ee_boundary)
    
    # Check image count
    image_count = dw_year.size().getInfo()
    print(f"Available images: {image_count}")
    
    if image_count == 0:
        print(f"ERROR: No Dynamic World images available for {year}")
        continue
    
    # Get mode (most common class) for the year
    print(f"Computing mode classification...")
    lulc_mode = dw_year.select('label').mode().clip(ee_boundary)
    
    # Calculate area for each class
    print(f"Calculating area by class...")
    year_data = {'year': year, 'dataset': 'Dynamic World'}
    
    for class_id, class_name in DW_CLASSES.items():
        print(f"  Processing {class_name} (class {class_id})...")
        
        # Create binary mask for this class
        class_mask = lulc_mode.eq(class_id)
        
        # Calculate area in square meters
        area_image = class_mask.multiply(ee.Image.pixelArea())
        
        # Reduce to get total area
        area_stats = area_image.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=ee_boundary,
            scale=10,  # Dynamic World is 10m resolution
            maxPixels=1e10,  # Increased for 10m resolution
            bestEffort=True
        )
        
        area_m2 = area_stats.get('label').getInfo() or 0
        area_km2 = area_m2 / 1e6
        
        year_data[class_name] = area_km2
        print(f"    Area: {area_km2:.2f} km²")
    
    new_data.append(year_data)
    print(f"\n✓ Completed {year}")

# Create DataFrame from new data
if new_data:
    new_df = pd.DataFrame(new_data)
    
    # Combine with existing data
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    combined_df = combined_df.sort_values('year').reset_index(drop=True)
    
    # Save updated dataset
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_csv = output_dir / f"glc_fcs30d_combined_lulc_{timestamp}.csv"
    combined_df.to_csv(output_csv, index=False)
    
    print(f"\n{'=' * 80}")
    print(f"DATA SAVED")
    print(f"{'=' * 80}")
    print(f"Output file: {output_csv}")
    print(f"Total years: {len(combined_df)}")
    print(f"Year range: {combined_df['year'].min()} - {combined_df['year'].max()}")
    print(f"\nYear breakdown:")
    for dataset in combined_df['dataset'].unique():
        years = combined_df[combined_df['dataset'] == dataset]['year'].tolist()
        print(f"  {dataset}: {years}")
    
    # Summary statistics for new years
    print(f"\n{'=' * 80}")
    print(f"NEW DATA SUMMARY (2024-2025)")
    print(f"{'=' * 80}")
    
    for year in [2024, 2025]:
        if year in combined_df['year'].values:
            year_data = combined_df[combined_df['year'] == year].iloc[0]
            print(f"\nYear {year}:")
            print(f"  Dataset: {year_data['dataset']}")
            print(f"  Water: {year_data['Water']:.2f} km²")
            print(f"  Trees: {year_data['Trees']:.2f} km²")
            print(f"  Crops: {year_data['Crops']:.2f} km²")
            print(f"  Built: {year_data['Built']:.2f} km²")
            print(f"  Bare: {year_data['Bare']:.2f} km²")
    
    # Compare 2023 vs 2025
    if 2023 in combined_df['year'].values and 2025 in combined_df['year'].values:
        data_2023 = combined_df[combined_df['year'] == 2023].iloc[0]
        data_2025 = combined_df[combined_df['year'] == 2025].iloc[0]
        
        print(f"\n{'=' * 80}")
        print(f"CHANGE ANALYSIS: 2023 to 2025")
        print(f"{'=' * 80}")
        
        for col in ['Water', 'Trees', 'Crops', 'Built', 'Bare']:
            val_2023 = data_2023[col]
            val_2025 = data_2025[col]
            change = val_2025 - val_2023
            pct_change = (change / val_2023 * 100) if val_2023 > 0 else 0
            
            print(f"\n{col}:")
            print(f"  2023: {val_2023:.2f} km²")
            print(f"  2025: {val_2025:.2f} km²")
            print(f"  Change: {change:+.2f} km² ({pct_change:+.2f}%)")
    
    # Create metadata file
    metadata = {
        'created': datetime.now().isoformat(),
        'years_added': [2024, 2025],
        'total_years': len(combined_df),
        'year_range': f"{combined_df['year'].min()}-{combined_df['year'].max()}",
        'datasets': combined_df['dataset'].unique().tolist(),
        'dynamic_world_years': combined_df[combined_df['dataset'] == 'Dynamic World']['year'].tolist(),
        'glc_fcs30d_years': combined_df[combined_df['dataset'] == 'GLC-FCS30D']['year'].tolist(),
        'output_file': str(output_csv),
        'columns': list(combined_df.columns)
    }
    
    metadata_file = output_dir / f"update_metadata_{timestamp}.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nMetadata saved: {metadata_file}")
    
    print(f"\n{'=' * 80}")
    print(f"EXPORT TASKS FOR NEW YEARS")
    print(f"{'=' * 80}")
    print(f"\nTo export rasters and shapefiles for 2024 and 2025:")
    print(f"1. Update generate_lulc_layers_and_shapefiles.py to use {output_csv.name}")
    print(f"2. Run the export script")
    print(f"3. Monitor tasks at https://code.earthengine.google.com/tasks")
    
else:
    print(f"\nNo new data added. Check errors above.")

print(f"\n{'=' * 80}")
print(f"COMPLETE")
print(f"{'=' * 80}")
