#!/usr/bin/env python3
"""
Complete Historical Analysis: 1987-2025
Combines GLC-FCS30D (1987-2015) with Dynamic World (2018-2025)
Exports shapefiles for 5-year intervals and generates comprehensive dashboard
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
print("COMPLETE HISTORICAL LULC ANALYSIS (1987-2025)")
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
print(f"✓ Boundary loaded")

# Load existing datasets
print("\nLoading existing datasets...")
historical_csv = output_dir / "archive" / "glc_fcs30d_historical_lulc_20251024_114642.csv"
dynamic_csv = output_dir / "dynamic_world_lulc_january_2018_2025_20251026_153424.csv"

df_historical = pd.read_csv(historical_csv)
df_dynamic = pd.read_csv(dynamic_csv)

print(f"  Historical (GLC-FCS30D): {len(df_historical)} years")
print(f"    Years: {sorted(df_historical['year'].unique().tolist())}")
print(f"  Dynamic World: {len(df_dynamic)} years")
print(f"    Years: {sorted(df_dynamic['year'].unique().tolist())}")

# Standardize column names for merging
# Historical has lowercase 'vegetation', Dynamic has uppercase 'Vegetation'
historical_cols = ['year', 'dataset', 'Water', 'Trees', 'Grass', 'Flooded vegetation', 
                   'Crops', 'Shrub and scrub', 'Built', 'Bare', 'Snow and ice']
dynamic_cols_map = {
    'Flooded Vegetation': 'Flooded vegetation',
    'Shrub and Scrub': 'Shrub and scrub'
}

df_dynamic_clean = df_dynamic.copy()
df_dynamic_clean = df_dynamic_clean.rename(columns=dynamic_cols_map)
df_dynamic_clean = df_dynamic_clean[historical_cols]

df_historical_clean = df_historical[historical_cols].copy()

# Use GLC-FCS30D for 1987-2015, Dynamic World for 2018-2025
df_historical_filtered = df_historical_clean[df_historical_clean['year'] <= 2015].copy()

# Combine datasets
combined_df = pd.concat([df_historical_filtered, df_dynamic_clean], ignore_index=True)
combined_df = combined_df.sort_values('year').reset_index(drop=True)

print(f"\nCombined dataset:")
print(f"  Total years: {len(combined_df)}")
print(f"  Year range: {combined_df['year'].min()} - {combined_df['year'].max()}")
print(f"  Years: {combined_df['year'].tolist()}")

# Save combined dataset
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
combined_csv = output_dir / f"complete_lulc_1987_2025_{timestamp}.csv"
combined_df.to_csv(combined_csv, index=False)
print(f"\n✓ Combined dataset saved: {combined_csv}")

# Initialize datasets for export
dw_collection = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
glc_fcs_five_year = ee.ImageCollection("projects/sat-io/open-datasets/GLC-FCS30D/five-years-map")
glc_fcs_annual = ee.ImageCollection("projects/sat-io/open-datasets/GLC-FCS30D/annual")

# GLC-FCS30D to Dynamic World mapping
GLC_TO_DW_MAPPING = {
    10: 1, 20: 1, 51: 1, 52: 1, 61: 1, 62: 1, 71: 1, 72: 1, 81: 1, 82: 1,  # Trees
    90: 5, 100: 5, 110: 5, 120: 2, 121: 2, 122: 2, 130: 2,  # Shrub/Grass
    140: 3, 150: 3, 152: 3, 153: 3,  # Flooded/Wetlands
    11: 4, 12: 4, 13: 4,  # Crops
    190: 6, 200: 6,  # Built
    201: 7, 202: 7, 210: 7, 220: 8,  # Bare/Snow
    180: 0  # Water
}

def remap_glc_to_dw(image):
    """Remap GLC-FCS30D classes to Dynamic World classes"""
    return image.remap(
        list(GLC_TO_DW_MAPPING.keys()),
        list(GLC_TO_DW_MAPPING.values()),
        defaultValue=7
    )

# Export configuration
export_config = {
    'scale': 30,
    'region': ee_boundary,
    'maxPixels': 1e10,
    'crs': 'EPSG:4326'
}

# Years to export rasters and shapefiles
historical_years = [1987, 1992, 1997, 2000, 2005, 2010, 2015]
dynamic_years = [2018, 2020, 2022, 2025]  # Key Dynamic World years
all_export_years = historical_years + dynamic_years

export_tasks = []

print(f"\n{'=' * 80}")
print(f"EXPORTING RASTERS AND SHAPEFILES")
print(f"{'=' * 80}")
print(f"Years to export: {all_export_years}")

for year in all_export_years:
    print(f"\n{'=' * 80}")
    print(f"PROCESSING YEAR {year}")
    print(f"{'=' * 80}")
    
    try:
        if year <= 2015:
            # GLC-FCS30D data
            dataset_name = "GLC-FCS30D"
            
            if year <= 1999:
                if year <= 1989:
                    band, period = 'b1', '1985-1989'
                elif year <= 1994:
                    band, period = 'b2', '1990-1994'
                else:
                    band, period = 'b3', '1995-1999'
                glc_image = glc_fcs_five_year.select([band]).mosaic().clip(ee_boundary)
            else:
                band = f'b{year - 2000 + 1}'
                period = str(year)
                glc_image = glc_fcs_annual.select([band]).mosaic().clip(ee_boundary)
            
            lulc_image = remap_glc_to_dw(glc_image).rename('lulc').byte()
            
        else:
            # Dynamic World data (January only)
            dataset_name = "Dynamic World"
            start_date = f'{year}-01-01'
            end_date = f'{year}-01-31'
            
            dw_january = dw_collection.filterDate(start_date, end_date).filterBounds(ee_boundary)
            lulc_image = dw_january.select('label').mode().clip(ee_boundary).rename('lulc').byte()
        
        print(f"Dataset: {dataset_name}")
        
        # Export full LULC raster
        print(f"  Exporting full LULC raster...")
        task_raster = ee.batch.Export.image.toDrive(
            image=lulc_image,
            description=f'LULC_{year}_{dataset_name.replace(" ", "_")}',
            folder='Western_Ghats_Complete_Analysis',
            fileNamePrefix=f'lulc_{year}_{dataset_name.lower().replace(" ", "_")}',
            **export_config
        )
        task_raster.start()
        export_tasks.append({
            'year': year,
            'dataset': dataset_name,
            'type': 'full_lulc',
            'task_id': task_raster.id
        })
        print(f"    ✓ Task ID: {task_raster.id}")
        
        # Export tree cover layer
        print(f"  Exporting tree cover layer...")
        tree_mask = lulc_image.eq(1).selfMask()
        task_tree = ee.batch.Export.image.toDrive(
            image=tree_mask,
            description=f'Trees_{year}_{dataset_name.replace(" ", "_")}',
            folder='Western_Ghats_Complete_Analysis',
            fileNamePrefix=f'trees_{year}_{dataset_name.lower().replace(" ", "_")}',
            **export_config
        )
        task_tree.start()
        export_tasks.append({
            'year': year,
            'dataset': dataset_name,
            'type': 'trees',
            'task_id': task_tree.id
        })
        print(f"    ✓ Task ID: {task_tree.id}")
        
        # Export built area layer
        print(f"  Exporting built area layer...")
        built_mask = lulc_image.eq(6).selfMask()
        task_built = ee.batch.Export.image.toDrive(
            image=built_mask,
            description=f'Built_{year}_{dataset_name.replace(" ", "_")}',
            folder='Western_Ghats_Complete_Analysis',
            fileNamePrefix=f'built_{year}_{dataset_name.lower().replace(" ", "_")}',
            **export_config
        )
        task_built.start()
        export_tasks.append({
            'year': year,
            'dataset': dataset_name,
            'type': 'built',
            'task_id': task_built.id
        })
        print(f"    ✓ Task ID: {task_built.id}")
        
        # Export shapefiles for key classes
        for class_id, class_name in [(1, 'Trees'), (6, 'Built')]:
            print(f"  Exporting {class_name.lower()} shapefile...")
            
            class_mask = lulc_image.eq(class_id)
            vectors = class_mask.reduceToVectors(
                geometry=ee_boundary,
                scale=100,  # 100m for vectors
                maxPixels=1e10,
                geometryType='polygon'
            )
            
            task_vector = ee.batch.Export.table.toDrive(
                collection=vectors,
                description=f'{class_name}_{year}_Vector',
                folder='Western_Ghats_Shapefiles',
                fileNamePrefix=f'{class_name.lower()}_{year}',
                fileFormat='SHP'
            )
            task_vector.start()
            export_tasks.append({
                'year': year,
                'dataset': dataset_name,
                'type': f'{class_name.lower()}_shapefile',
                'task_id': task_vector.id
            })
            print(f"    ✓ Task ID: {task_vector.id}")
        
        print(f"✓ Completed {year} - {len([t for t in export_tasks if t['year'] == year])} tasks submitted")
        
    except Exception as e:
        print(f"ERROR processing {year}: {e}")
        continue

# Save export metadata
export_metadata = {
    'created': datetime.now().isoformat(),
    'years_exported': all_export_years,
    'historical_years': historical_years,
    'dynamic_world_years': dynamic_years,
    'total_tasks': len(export_tasks),
    'tasks_by_type': {
        'full_lulc': len([t for t in export_tasks if t['type'] == 'full_lulc']),
        'trees_raster': len([t for t in export_tasks if t['type'] == 'trees']),
        'built_raster': len([t for t in export_tasks if t['type'] == 'built']),
        'trees_shapefile': len([t for t in export_tasks if t['type'] == 'trees_shapefile']),
        'built_shapefile': len([t for t in export_tasks if t['type'] == 'built_shapefile'])
    },
    'tasks': export_tasks,
    'combined_csv': str(combined_csv),
    'google_drive_folders': {
        'rasters': 'Western_Ghats_Complete_Analysis',
        'shapefiles': 'Western_Ghats_Shapefiles'
    }
}

metadata_file = geospatial_dir / f"complete_export_metadata_{timestamp}.json"
with open(metadata_file, 'w') as f:
    json.dump(export_metadata, f, indent=2)

print(f"\n{'=' * 80}")
print(f"EXPORT SUMMARY")
print(f"{'=' * 80}")
print(f"Total tasks submitted: {len(export_tasks)}")
print(f"  Full LULC rasters: {export_metadata['tasks_by_type']['full_lulc']}")
print(f"  Tree cover rasters: {export_metadata['tasks_by_type']['trees_raster']}")
print(f"  Built area rasters: {export_metadata['tasks_by_type']['built_raster']}")
print(f"  Tree shapefiles: {export_metadata['tasks_by_type']['trees_shapefile']}")
print(f"  Built shapefiles: {export_metadata['tasks_by_type']['built_shapefile']}")
print(f"\nMetadata saved: {metadata_file}")
print(f"Combined CSV saved: {combined_csv}")
print(f"\nGoogle Drive folders:")
print(f"  - Western_Ghats_Complete_Analysis (rasters)")
print(f"  - Western_Ghats_Shapefiles (vectors)")
print(f"\nMonitor tasks: https://code.earthengine.google.com/tasks")

print(f"\n{'=' * 80}")
print(f"COMPLETE")
print(f"{'=' * 80}")
