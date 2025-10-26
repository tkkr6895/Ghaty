#!/usr/bin/env python3
"""
CORRECTED Western Ghats Historical LULC Analysis using GLC-FCS30D
Fixed to properly handle the tile-based structure with band-per-year
"""

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

print("=" * 80)
print("WESTERN GHATS HISTORICAL LULC ANALYSIS (1985-2022)")
print("Using GLC-FCS30D Dataset - CORRECTED VERSION")
print("=" * 80)

# Initialize Earth Engine
print("\nInitializing Google Earth Engine...")
try:
    ee.Initialize(project='ee-tkkrfirst')
    print("SUCCESS: Earth Engine initialized")
    
    # Load GLC-FCS30D datasets
    glc_fcs_five_year = ee.ImageCollection("projects/sat-io/open-datasets/GLC-FCS30D/five-years-map")
    glc_fcs_annual = ee.ImageCollection("projects/sat-io/open-datasets/GLC-FCS30D/annual")
    
    print("SUCCESS: GLC-FCS30D datasets loaded")
    
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

# Load study area boundary
shapefile_path = "CEPF Content/data/commondata/fwdcepfwesternghatsprioritizationdatalayers/cepfbnd_prj.shp"

print("\nLoading Western Ghats boundary...")
western_ghats = gpd.read_file(shapefile_path)
print(f"Loaded {western_ghats.shape[0]} polygon(s)")

# Convert to WGS84
western_ghats_wgs84 = western_ghats.to_crs('EPSG:4326')
area_km2 = western_ghats.to_crs('EPSG:3857').area.sum() / 1e6
print(f"Total study area: {area_km2:.0f} km²")

# Convert to Earth Engine geometry
def convert_to_ee_geometry(gdf):
    """Convert GeoDataFrame to Earth Engine Geometry"""
    # Fix invalid geometries with buffer
    gdf_fixed = gdf.copy()
    gdf_fixed['geometry'] = gdf_fixed.geometry.buffer(0)
    geom = gdf_fixed.geometry.union_all()
    
    if geom.geom_type == 'Polygon':
        coords = [list(geom.exterior.coords)]
        return ee.Geometry.Polygon(coords)
    elif geom.geom_type == 'MultiPolygon':
        polygons = []
        for polygon in geom.geoms:
            coords = [list(polygon.exterior.coords)]
            polygons.append(coords)
        return ee.Geometry.MultiPolygon(polygons)

western_ghats_ee = convert_to_ee_geometry(western_ghats_wgs84)
STUDY_AREA_KM2 = western_ghats_ee.area().getInfo() / 1e6
print(f"Earth Engine area: {STUDY_AREA_KM2:.0f} km²")

# Define class mappings
GLC_TO_SIMPLIFIED = {
    # Forest (51-92)
    51: 1, 52: 1, 61: 1, 62: 1, 71: 1, 72: 1, 81: 1, 82: 1, 91: 1, 92: 1,
    # Crops (10-20)
    10: 4, 11: 4, 12: 4, 20: 4,
    # Shrub (120-122)
    120: 5, 121: 5, 122: 5,
    # Grass (130, 140)
    130: 2, 140: 2,
    # Flooded vegetation (181-187)
    181: 3, 182: 3, 183: 3, 184: 3, 185: 3, 186: 3, 187: 3,
    # Built (190)
    190: 6,
    # Bare (150-153, 200-202)
    150: 7, 152: 7, 153: 7, 200: 7, 201: 7, 202: 7,
    # Water (210)
    210: 0,
    # Snow/ice (220)
    220: 8
}

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

print(f"\nClass mapping: {len(GLC_TO_SIMPLIFIED)} GLC classes -> {len(SIMPLIFIED_CLASSES)} simplified classes")

def analyze_glc_year(year, region_ee, use_midpoint=True):
    """
    Analyze GLC-FCS30D for a specific year
    
    Parameters:
    - year: Year to analyze (1985-2022)
    - region_ee: Earth Engine geometry
    - use_midpoint: For 5-year periods, use midpoint year (e.g., 1987 for 1985-1989)
    
    Returns:
    - Dictionary with results
    """
    
    print(f"\n{'='*70}")
    print(f"ANALYZING YEAR {year}")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    try:
        # Determine which collection and band to use
        if year <= 1999:
            # Use five-year collection
            if 1985 <= year <= 1989:
                band = 'b1'
                period = '1985-1989'
                representative_year = 1987 if use_midpoint else year
            elif 1990 <= year <= 1994:
                band = 'b2'
                period = '1990-1994'
                representative_year = 1992 if use_midpoint else year
            elif 1995 <= year <= 1999:
                band = 'b3'
                period = '1995-1999'
                representative_year = 1997 if use_midpoint else year
            else:
                print(f"ERROR: Year {year} not available in five-year collection")
                return None
            
            print(f"Using five-year collection, period: {period}, band: {band}")
            lc_image = glc_fcs_five_year.select([band]).mosaic()
            band_to_analyze = band
            
        else:
            # Use annual collection (2000-2022)
            if 2000 <= year <= 2022:
                band_index = year - 2000 + 1
                band = f'b{band_index}'
                period = str(year)
                representative_year = year
                
                print(f"Using annual collection, year: {year}, band: {band}")
                lc_image = glc_fcs_annual.select([band]).mosaic()
                band_to_analyze = band
            else:
                print(f"ERROR: Year {year} not available (range: 1985-2022)")
                return None
        
        # Clip to study region
        lc_clipped = lc_image.clip(region_ee)
        
        # Remap to simplified classes
        print(f"Remapping GLC classes to simplified categories...")
        from_values = list(GLC_TO_SIMPLIFIED.keys())
        to_values = list(GLC_TO_SIMPLIFIED.values())
        
        lc_simplified = lc_clipped.select([band_to_analyze]).remap(
            from_values, to_values, 
            defaultValue=7  # Default to Bare
        )
        
        # Calculate areas
        print(f"Calculating areas for each land cover class...")
        results = {
            'year': representative_year,
            'period': period,
            'dataset': 'GLC-FCS30D'
        }
        
        pixel_area = ee.Image.pixelArea()
        
        for class_id, class_name in SIMPLIFIED_CLASSES.items():
            try:
                # Create mask for this class
                class_mask = lc_simplified.eq(class_id)
                
                # Calculate area
                area_m2 = pixel_area.updateMask(class_mask).reduceRegion(
                    reducer=ee.Reducer.sum(),
                    geometry=region_ee,
                    scale=30,  # 30m resolution
                    maxPixels=1e10,
                    bestEffort=True
                ).getInfo()
                
                # Convert to km²
                area_km2 = area_m2.get('area', 0) / 1e6
                results[class_name] = area_km2
                
                if area_km2 > 0.1:
                    percentage = (area_km2 / STUDY_AREA_KM2) * 100
                    print(f"   {class_name}: {area_km2:.1f} km² ({percentage:.1f}%)")
                    
            except Exception as e:
                print(f"   ERROR calculating {class_name}: {e}")
                results[class_name] = 0
        
        # Calculate totals and percentages
        total_area = sum([v for k, v in results.items() 
                         if k not in ['year', 'period', 'dataset'] and isinstance(v, (int, float))])
        results['total_area_km2'] = total_area
        
        for class_name in SIMPLIFIED_CLASSES.values():
            if class_name in results and total_area > 0:
                percentage = (results[class_name] / total_area) * 100
                results[f'{class_name}_percent'] = percentage
        
        elapsed = (time.time() - start_time) / 60
        print(f"SUCCESS: Completed in {elapsed:.1f} minutes")
        print(f"Total classified area: {total_area:.1f} km² ({(total_area/STUDY_AREA_KM2)*100:.1f}% of study area)")
        
        return results
        
    except Exception as e:
        elapsed = (time.time() - start_time) / 60
        print(f"ERROR: Analysis FAILED after {elapsed:.1f} minutes")
        print(f"Error details: {e}")
        import traceback
        traceback.print_exc()
        return None

# Define years to analyze
# Use midpoint years for 5-year periods, then annual from 2000
historical_years = [
    1987,  # Represents 1985-1989
    1992,  # Represents 1990-1994
    1997,  # Represents 1995-1999
    2000, 2005, 2010, 2015, 2020  # Annual years
]

print(f"\nStarting analysis for {len(historical_years)} years...")
print(f"Years: {historical_years}")
print("This may take 30-60 minutes...\n")

historical_results = []

for year in historical_years:
    result = analyze_glc_year(year, western_ghats_ee, use_midpoint=True)
    if result:
        historical_results.append(result)
        print(f"✓ {year} complete")
    else:
        print(f"✗ {year} failed")
    
    # Pause between requests
    time.sleep(3)

# Convert to DataFrame and save
if historical_results:
    historical_df = pd.DataFrame(historical_results)
    
    print(f"\n{'='*70}")
    print(f"HISTORICAL ANALYSIS COMPLETE")
    print(f"{'='*70}")
    print(f"\nAnalyzed {len(historical_results)} time periods")
    print("\nKey results:")
    print(historical_df[['year', 'period', 'Trees', 'Built', 'Crops', 'total_area_km2']].round(1).to_string(index=False))
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'outputs/glc_fcs30d_historical_lulc_{timestamp}.csv'
    historical_df.to_csv(output_file, index=False)
    print(f"\nResults saved: {output_file}")
    
    # Try to load and combine with Dynamic World data
    try:
        print("\nLoading Dynamic World data...")
        dw_file = 'outputs/western_ghats_lulc_analysis_results_20250928_203521.csv'
        dw_df = pd.read_csv(dw_file)
        dw_df['dataset'] = 'Dynamic World'
        dw_df['period'] = dw_df['year'].astype(str)
        
        # Combine datasets
        combined_df = pd.concat([historical_df, dw_df], ignore_index=True)
        combined_df = combined_df.sort_values('year').reset_index(drop=True)
        
        print(f"Combined dataset: {len(combined_df)} years")
        print(f"Year range: {int(combined_df['year'].min())}-{int(combined_df['year'].max())}")
        
        # Save combined results
        combined_file = f'outputs/glc_fcs30d_combined_lulc_{timestamp}.csv'
        combined_df.to_csv(combined_file, index=False)
        print(f"Combined results saved: {combined_file}")
        
        # Generate statistics
        print(f"\n{'='*70}")
        print("COMPREHENSIVE STATISTICS")
        print(f"{'='*70}")
        
        print(f"\nTemporal coverage:")
        print(f"  Historical (GLC-FCS30D): {len(historical_df)} periods")
        print(f"  Recent (Dynamic World): {len(dw_df)} years")
        print(f"  Total: {len(combined_df)} time periods")
        
        # Land cover changes
        print(f"\nMajor land cover changes:")
        for class_name in ['Trees', 'Built', 'Crops']:
            if class_name in combined_df.columns:
                first_val = combined_df.iloc[0][class_name]
                last_val = combined_df.iloc[-1][class_name]
                change = last_val - first_val
                change_pct = (change / first_val * 100) if first_val > 0 else 0
                
                print(f"  {class_name}:")
                print(f"    {int(combined_df.iloc[0]['year'])}: {first_val:.1f} km²")
                print(f"    {int(combined_df.iloc[-1]['year'])}: {last_val:.1f} km²")
                print(f"    Change: {change:+.1f} km² ({change_pct:+.1f}%)")
        
    except Exception as e:
        print(f"\nCould not combine with Dynamic World data: {e}")
        combined_df = historical_df
    
else:
    print("\nNo results obtained - check Earth Engine connection")

print(f"\n{'='*70}")
print("ANALYSIS COMPLETE")
print(f"{'='*70}")
