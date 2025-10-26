#!/usr/bin/env python3
"""
Update LULC dataset:
- GLC-FCS30D: 1987-2017
- Dynamic World: 2018-2025 (only)
- 2024-2025: January only (avoid seasonal variations)
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
print("UPDATING LULC DATASET - CONSISTENT METHODOLOGY")
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

# Load existing combined dataset
combined_csv = output_dir / "glc_fcs30d_combined_lulc_20251024_114642.csv"
existing_df = pd.read_csv(combined_csv)

print(f"\nExisting data: {len(existing_df)} records")
print(f"Year range: {existing_df['year'].min()} - {existing_df['year'].max()}")

# Filter to keep only GLC-FCS30D data before 2018
glc_data = existing_df[
    (existing_df['dataset'] == 'GLC-FCS30D') & 
    (existing_df['year'] < 2018)
].copy()

print(f"\nRetaining GLC-FCS30D data: {len(glc_data)} years")
print(f"  Years: {sorted(glc_data['year'].tolist())}")

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

# Years to process with Dynamic World (2018-2025)
dw_years = list(range(2018, 2026))  # 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025

print(f"\nProcessing Dynamic World years: {dw_years}")

new_data = []

for year in dw_years:
    print(f"\n{'=' * 80}")
    print(f"PROCESSING YEAR {year}")
    print(f"{'=' * 80}")
    
    # For 2024 and 2025, use only January to avoid seasonal variations
    if year >= 2024:
        start_date = f'{year}-01-01'
        end_date = f'{year}-01-31'
        period_label = f'{year} (January only)'
    else:
        start_date = f'{year}-01-01'
        end_date = f'{year}-12-31'
        period_label = f'{year} (full year)'
    
    print(f"Period: {period_label}")
    print(f"Filtering Dynamic World: {start_date} to {end_date}")
    
    dw_year = dw_collection.filterDate(start_date, end_date).filterBounds(ee_boundary)
    
    # Check image count
    image_count = dw_year.size().getInfo()
    print(f"Available images: {image_count}")
    
    if image_count == 0:
        print(f"WARNING: No Dynamic World images available for {year}")
        continue
    
    # Get mode (most common class) for the period
    print(f"Computing mode classification...")
    lulc_mode = dw_year.select('label').mode().clip(ee_boundary)
    
    # Calculate area for each class
    print(f"Calculating area by class...")
    year_data = {'year': year, 'dataset': 'Dynamic World'}
    
    for class_id, class_name in DW_CLASSES.items():
        print(f"  Processing {class_name} (class {class_id})...", end=' ')
        
        # Create binary mask for this class
        class_mask = lulc_mode.eq(class_id)
        
        # Calculate area in square meters
        area_image = class_mask.multiply(ee.Image.pixelArea())
        
        # Reduce to get total area
        area_stats = area_image.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=ee_boundary,
            scale=30,  # Use 30m scale for consistency and speed
            maxPixels=1e10,
            bestEffort=True
        )
        
        area_m2 = area_stats.get('label').getInfo() or 0
        area_km2 = area_m2 / 1e6
        
        year_data[class_name] = area_km2
        print(f"{area_km2:.2f} km²")
    
    new_data.append(year_data)
    print(f"\n✓ Completed {year}")

# Create DataFrame from new data
if new_data:
    new_df = pd.DataFrame(new_data)
    
    # Combine GLC data (pre-2018) with new Dynamic World data (2018-2025)
    combined_df = pd.concat([glc_data, new_df], ignore_index=True)
    combined_df = combined_df.sort_values('year').reset_index(drop=True)
    
    # Save updated dataset
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_csv = output_dir / f"lulc_combined_consistent_{timestamp}.csv"
    combined_df.to_csv(output_csv, index=False)
    
    print(f"\n{'=' * 80}")
    print(f"DATA SAVED")
    print(f"{'=' * 80}")
    print(f"Output file: {output_csv}")
    print(f"Total years: {len(combined_df)}")
    print(f"Year range: {combined_df['year'].min()} - {combined_df['year'].max()}")
    
    print(f"\nDataset breakdown:")
    print(f"  GLC-FCS30D (1987-2017): {len(glc_data)} years")
    print(f"  Dynamic World (2018-2025): {len(new_df)} years")
    
    print(f"\nYears by dataset:")
    for dataset in combined_df['dataset'].unique():
        years = sorted(combined_df[combined_df['dataset'] == dataset]['year'].tolist())
        print(f"  {dataset}: {years}")
    
    # Summary statistics
    print(f"\n{'=' * 80}")
    print(f"SUMMARY STATISTICS")
    print(f"{'=' * 80}")
    
    # Show key metrics for selected years
    key_years = [1987, 2000, 2017, 2018, 2023, 2024, 2025]
    for year in key_years:
        if year in combined_df['year'].values:
            year_data = combined_df[combined_df['year'] == year].iloc[0]
            print(f"\n{year} ({year_data['dataset']}):")
            print(f"  Trees: {year_data['Trees']:.2f} km²")
            print(f"  Built: {year_data['Built']:.2f} km²")
            print(f"  Crops: {year_data['Crops']:.2f} km²")
            print(f"  Water: {year_data['Water']:.2f} km²")
    
    # Change analysis: 2017 to 2018 (dataset transition)
    if 2017 in combined_df['year'].values and 2018 in combined_df['year'].values:
        data_2017 = combined_df[combined_df['year'] == 2017].iloc[0]
        data_2018 = combined_df[combined_df['year'] == 2018].iloc[0]
        
        print(f"\n{'=' * 80}")
        print(f"DATASET TRANSITION: 2017 (GLC-FCS30D) to 2018 (Dynamic World)")
        print(f"{'=' * 80}")
        
        for col in ['Water', 'Trees', 'Crops', 'Built', 'Bare']:
            val_2017 = data_2017[col]
            val_2018 = data_2018[col]
            change = val_2018 - val_2017
            pct_change = (change / val_2017 * 100) if val_2017 > 0 else 0
            
            print(f"{col:20s}: {val_2017:8.2f} → {val_2018:8.2f} km² ({pct_change:+6.2f}%)")
    
    # Change analysis: 2023 to 2025
    if 2023 in combined_df['year'].values and 2025 in combined_df['year'].values:
        data_2023 = combined_df[combined_df['year'] == 2023].iloc[0]
        data_2025 = combined_df[combined_df['year'] == 2025].iloc[0]
        
        print(f"\n{'=' * 80}")
        print(f"RECENT CHANGE: 2023 to 2025 (January)")
        print(f"{'=' * 80}")
        
        for col in ['Water', 'Trees', 'Crops', 'Built', 'Bare']:
            val_2023 = data_2023[col]
            val_2025 = data_2025[col]
            change = val_2025 - val_2023
            pct_change = (change / val_2023 * 100) if val_2023 > 0 else 0
            
            print(f"{col:20s}: {val_2023:8.2f} → {val_2025:8.2f} km² ({pct_change:+6.2f}%)")
    
    # Create metadata
    metadata = {
        'created': datetime.now().isoformat(),
        'description': 'Consistent LULC dataset with single methodology per period',
        'methodology': {
            '1987-2017': 'GLC-FCS30D',
            '2018-2023': 'Dynamic World (full year)',
            '2024-2025': 'Dynamic World (January only to avoid seasonal variations)'
        },
        'total_years': len(combined_df),
        'year_range': f"{combined_df['year'].min()}-{combined_df['year'].max()}",
        'glc_fcs30d_years': sorted(glc_data['year'].tolist()),
        'dynamic_world_years': sorted(new_df['year'].tolist()),
        'output_file': str(output_csv),
        'columns': list(combined_df.columns),
        'notes': [
            'Removed GLC-FCS30D data for 2018-2020 to eliminate methodology inconsistency',
            '2024-2025 use January data only to avoid seasonal variations',
            'All Dynamic World data processed at 30m scale for consistency'
        ]
    }
    
    metadata_file = output_dir / f"lulc_metadata_{timestamp}.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nMetadata saved: {metadata_file}")
    
else:
    print(f"\nERROR: No Dynamic World data could be processed")

print(f"\n{'=' * 80}")
print(f"COMPLETE")
print(f"{'=' * 80}")
