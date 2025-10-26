#!/usr/bin/env python3
"""
Generate LULC raster layers and shapefiles for each year
Creates reproducible outputs for QGIS and GEE analysis
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
print("GENERATING LULC LAYERS AND SHAPEFILES")
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
    # Multiple features - union them
    union_geom = gdf.geometry.union_all()
    if union_geom.geom_type == 'Polygon':
        coords = [list(union_geom.exterior.coords)]
    else:
        coords = [list(poly.exterior.coords) for poly in union_geom.geoms]

ee_boundary = ee.Geometry.MultiPolygon(coords) if len(coords) > 1 else ee.Geometry.Polygon(coords[0])

print(f"Boundary loaded")
bounds = gdf.total_bounds

# Load combined dataset for year information
combined_csv = output_dir / "glc_fcs30d_combined_lulc_20251024_114642.csv"
df = pd.read_csv(combined_csv)
df = df[~((df['year'] == 2020) & (df['dataset'] == 'Dynamic World'))]
df = df.sort_values('year').reset_index(drop=True)

print(f"Years to process: {df['year'].tolist()}")

# GLC-FCS30D to Dynamic World class mapping
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

# Initialize datasets
dw_collection = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
glc_fcs_five_year = ee.ImageCollection("projects/sat-io/open-datasets/GLC-FCS30D/five-years-map")
glc_fcs_annual = ee.ImageCollection("projects/sat-io/open-datasets/GLC-FCS30D/annual")

# LULC class names
LULC_CLASSES = {
    0: 'water',
    1: 'trees',
    2: 'grass',
    3: 'flooded_vegetation',
    4: 'crops',
    5: 'shrub_and_scrub',
    6: 'built',
    7: 'bare',
    8: 'snow_and_ice'
}

print("\n" + "=" * 80)
print("EXPORTING LULC RASTERS TO GOOGLE DRIVE")
print("=" * 80)

# Export configuration
export_config = {
    'scale': 30,  # 30m resolution (GLC-FCS30D native)
    'region': ee_boundary,
    'maxPixels': 1e9,
    'crs': 'EPSG:4326'
}

tasks_started = []

for idx, row in df.iterrows():
    year = int(row['year'])
    dataset = row['dataset']
    
    print(f"\n[{idx+1}/{len(df)}] Processing {year} ({dataset})...")
    
    try:
        if dataset == 'GLC-FCS30D':
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
            
            lulc_image = remap_glc_to_dw(glc_image).rename('lulc')
        
        else:  # Dynamic World
            start_date = f'{year}-01-01'
            end_date = f'{year}-12-31'
            dw_year = dw_collection.filterDate(start_date, end_date).filterBounds(ee_boundary)
            lulc_image = dw_year.select('label').mode().clip(ee_boundary).rename('lulc')
        
        # Export to Google Drive
        task = ee.batch.Export.image.toDrive(
            image=lulc_image,
            description=f'LULC_{year}_{dataset.replace(" ", "_").replace("-", "_")}',
            folder='Western_Ghats_LULC',
            fileNamePrefix=f'lulc_{year}_{dataset.replace(" ", "_").replace("-", "_")}',
            scale=export_config['scale'],
            region=export_config['region'],
            maxPixels=export_config['maxPixels'],
            crs=export_config['crs'],
            fileFormat='GeoTIFF'
        )
        
        task.start()
        tasks_started.append({
            'year': year,
            'dataset': dataset,
            'task_id': task.id,
            'description': task.config['description']
        })
        
        print(f"  Export task started: {task.id}")
    
    except Exception as e:
        print(f"  ERROR: {e}")
        continue

print(f"\n{len(tasks_started)} export tasks started")
print("Tasks will export to Google Drive > Western_Ghats_LULC folder")
print("Note: Tasks may take several minutes to hours to complete")

# Save task information
tasks_file = geospatial_dir / f"export_tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(tasks_file, 'w') as f:
    json.dump(tasks_started, f, indent=2)

print(f"\nTask information saved: {tasks_file}")

# Generate class-specific shapefiles for each year
print("\n" + "=" * 80)
print("GENERATING CLASS-SPECIFIC SHAPEFILES")
print("=" * 80)

print("\nCreating vectorized polygons for each LULC class per year...")
print("This creates shapefiles that can be loaded into QGIS/GEE")

# Create a summary of what needs to be done
vector_tasks = []

for idx, row in df.iterrows():
    year = int(row['year'])
    dataset = row['dataset']
    
    print(f"\n[{idx+1}/{len(df)}] Setting up vector export for {year} ({dataset})...")
    
    try:
        if dataset == 'GLC-FCS30D':
            if year <= 1999:
                if year <= 1989:
                    band = 'b1'
                elif year <= 1994:
                    band = 'b2'
                else:
                    band = 'b3'
                glc_image = glc_fcs_five_year.select([band]).mosaic().clip(ee_boundary)
            else:
                band = f'b{year - 2000 + 1}'
                glc_image = glc_fcs_annual.select([band]).mosaic().clip(ee_boundary)
            
            lulc_image = remap_glc_to_dw(glc_image).rename('lulc')
        
        else:  # Dynamic World
            start_date = f'{year}-01-01'
            end_date = f'{year}-12-31'
            dw_year = dw_collection.filterDate(start_date, end_date).filterBounds(ee_boundary)
            lulc_image = dw_year.select('label').mode().clip(ee_boundary).rename('lulc')
        
        # Export vectors for each major class
        for class_id in [0, 1, 4, 6]:  # Water, Trees, Crops, Built
            class_name = LULC_CLASSES[class_id]
            
            # Create binary mask for this class
            class_mask = lulc_image.eq(class_id)
            
            # Vectorize
            vectors = class_mask.selfMask().reduceToVectors(
                geometry=ee_boundary,
                scale=100,  # 100m for reasonable polygon size
                geometryType='polygon',
                eightConnected=False,
                maxPixels=1e9
            )
            
            # Export to Drive
            task = ee.batch.Export.table.toDrive(
                collection=vectors,
                description=f'{class_name}_{year}_{dataset.replace(" ", "_")}',
                folder='Western_Ghats_LULC_Vectors',
                fileNamePrefix=f'{class_name}_{year}_{dataset.replace(" ", "_").replace("-", "_")}',
                fileFormat='SHP'
            )
            
            task.start()
            vector_tasks.append({
                'year': year,
                'dataset': dataset,
                'class': class_name,
                'class_id': class_id,
                'task_id': task.id
            })
            
            print(f"  {class_name.capitalize()}: Task started ({task.id})")
    
    except Exception as e:
        print(f"  ERROR: {e}")
        continue

print(f"\n{len(vector_tasks)} vector export tasks started")
print("Shapefiles will export to Google Drive > Western_Ghats_LULC_Vectors folder")

# Save vector task information
vector_tasks_file = geospatial_dir / f"vector_export_tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(vector_tasks_file, 'w') as f:
    json.dump(vector_tasks, f, indent=2)

print(f"\nVector task information saved: {vector_tasks_file}")

# Create metadata file
metadata = {
    'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'study_area': 'Western Ghats Priority Conservation Area',
    'boundary_file': str(boundary_file),
    'years_processed': df['year'].tolist(),
    'datasets_used': df['dataset'].unique().tolist(),
    'raster_exports': {
        'count': len(tasks_started),
        'format': 'GeoTIFF',
        'resolution': '30m',
        'crs': 'EPSG:4326',
        'destination': 'Google Drive/Western_Ghats_LULC',
        'tasks': tasks_started
    },
    'vector_exports': {
        'count': len(vector_tasks),
        'format': 'Shapefile',
        'classes_exported': ['water', 'trees', 'crops', 'built'],
        'scale': '100m',
        'destination': 'Google Drive/Western_Ghats_LULC_Vectors',
        'tasks': vector_tasks
    },
    'lulc_classes': LULC_CLASSES,
    'class_mapping': GLC_TO_DW_MAPPING,
    'usage_instructions': {
        'raster_files': 'Load GeoTIFF files in QGIS or upload to GEE as assets',
        'vector_files': 'Shapefiles can be directly opened in QGIS or uploaded to GEE',
        'qgis': 'Layer > Add Layer > Add Raster Layer (for GeoTIFF) or Add Vector Layer (for SHP)',
        'gee': 'Assets > NEW > Upload > Select files from Google Drive'
    }
}

metadata_file = geospatial_dir / f"export_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(metadata_file, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"\nExport metadata saved: {metadata_file}")

print("\n" + "=" * 80)
print("EXPORT TASKS SUBMITTED")
print("=" * 80)
print(f"\nRaster exports: {len(tasks_started)}")
print(f"Vector exports: {len(vector_tasks)}")
print(f"Total tasks: {len(tasks_started) + len(vector_tasks)}")
print("\nMonitor task progress:")
print("1. Visit: https://code.earthengine.google.com/tasks")
print("2. Check your Google Drive folders:")
print("   - Western_Ghats_LULC (raster GeoTIFF files)")
print("   - Western_Ghats_LULC_Vectors (shapefiles)")
print("\nTasks will complete in background. Check GEE Task Manager for status.")
