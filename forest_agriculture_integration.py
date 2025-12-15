"""
Forest-Agriculture Integration Analysis
Link old-growth forests with cropping intensity and water balance data via Core Stack API

Research Question: Is cropping intensity a risk factor for old-growth forests?
Focus: Shade-grown agroforestry vs. intensive cropping impacts

Created: December 14, 2024
NOTE: Requires config.py file with CORE_STACK_API_KEY defined
"""

import requests
import pandas as pd
import numpy as np
import json
import time
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Import API key from config
try:
    from config import CORE_STACK_API_KEY, CORE_STACK_BASE_URL
except ImportError:
    print("ERROR: config.py not found. Please copy config_template.py to config.py and add your API key.")
    exit(1)

# Configuration
BASE_URL = CORE_STACK_BASE_URL
HEADERS = {'X-API-Key': CORE_STACK_API_KEY}

# Output directory
OUTPUT_DIR = Path('outputs/forest_agriculture_analysis')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load forest grid analysis
print("=" * 80)
print("FOREST-AGRICULTURE INTEGRATION ANALYSIS")
print("Investigating shade-grown vs. intensive cropping impacts on old-growth forests")
print("=" * 80)
print()

print("Loading forest grid analysis results...")
grid_df = pd.read_csv('outputs/forest_typology_corrected/regional_forest_comparison.csv')
print(f"  Loaded {len(grid_df)} grid cells")
print()

# Priority grids for analysis (from plan)
priority_grids = {
    # High-risk transition zones (mixed old-growth/plantation)
    12: {'reason': 'High plantation pressure (61.3%), Kodagu coffee region', 'type': 'high_risk'},
    13: {'reason': 'Mixed zone (54.2% plantation), active expansion', 'type': 'high_risk'},
    20: {'reason': 'Plantation-dominated transition (55.6%)', 'type': 'high_risk'},
    
    # Old-growth hotspots (conservation monitoring)
    22: {'reason': 'Old-growth stronghold (84.7%), Kerala-TN border', 'type': 'conservation'},
    18: {'reason': 'Strong old-growth (79.1%), Wayanad-Idukki', 'type': 'conservation'},
    21: {'reason': 'High old-growth (85.2%), southern WG', 'type': 'conservation'},
    
    # Plantation hotspots (baseline for comparison)
    0: {'reason': 'Nearly complete conversion (96.5% plantation)', 'type': 'baseline_intensive'},
    1: {'reason': 'High conversion (96.8% plantation), Goa-Karnataka', 'type': 'baseline_intensive'},
}

print("PRIORITY GRID CELLS FOR ANALYSIS:")
print("-" * 80)
for grid_id, info in priority_grids.items():
    grid_row = grid_df[grid_df['grid_id'] == grid_id].iloc[0]
    lat = (grid_row['lat_min'] + grid_row['lat_max']) / 2
    lon = (grid_row['lon_min'] + grid_row['lon_max']) / 2
    print(f"Grid {grid_id:2d} ({lat:.2f}°N, {lon:.2f}°E): {info['reason']}")
    print(f"        Forest mix: {grid_row['old_growth_pct']:.1f}% old-growth, {grid_row['plantation_pct']:.1f}% plantation")
print()

# Helper functions for API calls
def get_mws_by_latlon(lat, lon, max_retries=3):
    """Get MWS ID and administrative details for a lat/lon point"""
    endpoint = f"{BASE_URL}/get_mwsid_by_latlon/"
    params = {'latitude': lat, 'longitude': lon}
    
    for attempt in range(max_retries):
        try:
            response = requests.get(endpoint, params=params, headers=HEADERS, timeout=30)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"    WARNING: Location ({lat:.4f}, {lon:.4f}) not in Core Stack coverage")
                return None
            else:
                print(f"    WARNING: API returned status {response.status_code}: {response.text}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return None
        except Exception as e:
            print(f"    ERROR: Error querying MWS: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return None
    return None

def get_kyl_indicators(state, district, tehsil, mws_id, max_retries=3):
    """Get cropping intensity and hydrological indicators for an MWS"""
    endpoint = f"{BASE_URL}/get_mws_kyl_indicators/"
    params = {
        'state': state,
        'district': district,
        'tehsil': tehsil,
        'mws_id': mws_id
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(endpoint, params=params, headers=HEADERS, timeout=30)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"    WARNING: No KYL data for {mws_id} in {district}, {state}")
                return None
            else:
                print(f"    WARNING: API returned status {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
        except Exception as e:
            print(f"    ERROR: Error querying KYL indicators: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return None
    return None

def get_mws_timeseries(state, district, tehsil, mws_id, max_retries=3):
    """Get water balance time series (precipitation, ET, runoff) for an MWS"""
    endpoint = f"{BASE_URL}/get_mws_data/"
    params = {
        'state': state,
        'district': district,
        'tehsil': tehsil,
        'mws_id': mws_id
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(endpoint, params=params, headers=HEADERS, timeout=30)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"    WARNING: No time series data for {mws_id}")
                return None
            else:
                print(f"    WARNING: API returned status {response.status_code}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
        except Exception as e:
            print(f"    ERROR: Error querying time series: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return None
    return None

# PHASE 1: Link Forest Grid Cells to Micro-Watersheds
print("PHASE 1: LINKING FOREST GRID CELLS TO MICRO-WATERSHEDS")
print("=" * 80)
print()

grid_mws_data = []

for grid_id in priority_grids.keys():
    grid_row = grid_df[grid_df['grid_id'] == grid_id].iloc[0]
    lat_center = (grid_row['lat_min'] + grid_row['lat_max']) / 2
    lon_center = (grid_row['lon_min'] + grid_row['lon_max']) / 2
    
    print(f"Grid {grid_id} ({lat_center:.2f}°N, {lon_center:.2f}°E): Querying MWS...")
    
    mws_data = get_mws_by_latlon(lat_center, lon_center)
    
    if mws_data:
        print(f"  SUCCESS: Found MWS: {mws_data['uid']}")
        print(f"    Admin: {mws_data['District']}, {mws_data['State']}")
        print(f"    Tehsil: {mws_data['Tehsil']}")
        
        grid_mws_data.append({
            'grid_id': grid_id,
            'grid_type': priority_grids[grid_id]['type'],
            'grid_reason': priority_grids[grid_id]['reason'],
            'lat': lat_center,
            'lon': lon_center,
            'old_growth_pct': grid_row['old_growth_pct'],
            'plantation_pct': grid_row['plantation_pct'],
            'old_growth_km2': grid_row['old_growth_km2'],
            'plantation_km2': grid_row['plantation_km2'],
            'mws_id': mws_data['uid'],
            'state': mws_data['State'],
            'district': mws_data['District'],
            'tehsil': mws_data['Tehsil']
        })
    else:
        print(f"  FAILED: No MWS data available for this location")
        # Still record grid data for reference
        grid_mws_data.append({
            'grid_id': grid_id,
            'grid_type': priority_grids[grid_id]['type'],
            'grid_reason': priority_grids[grid_id]['reason'],
            'lat': lat_center,
            'lon': lon_center,
            'old_growth_pct': grid_row['old_growth_pct'],
            'plantation_pct': grid_row['plantation_pct'],
            'old_growth_km2': grid_row['old_growth_km2'],
            'plantation_km2': grid_row['plantation_km2'],
            'mws_id': None,
            'state': None,
            'district': None,
            'tehsil': None
        })
    
    print()
    time.sleep(1)  # Rate limiting

grid_mws_df = pd.DataFrame(grid_mws_data)
print(f"Successfully linked {grid_mws_df['mws_id'].notna().sum()} grid cells to MWS")
print()

# Save intermediate results
grid_mws_output = OUTPUT_DIR / 'grid_mws_linkage.csv'
grid_mws_df.to_csv(grid_mws_output, index=False)
print(f"Saved grid-MWS linkage: {grid_mws_output}")
print()

# PHASE 2: Retrieve Cropping Intensity and Hydrological Indicators
print("=" * 80)
print("PHASE 2: RETRIEVING CROPPING INTENSITY & HYDROLOGICAL INDICATORS")
print("=" * 80)
print()

cropping_data = []

for idx, row in grid_mws_df[grid_mws_df['mws_id'].notna()].iterrows():
    print(f"Grid {int(row['grid_id'])} - MWS {row['mws_id']}: Querying KYL indicators...")
    
    kyl_data = get_kyl_indicators(row['state'], row['district'], row['tehsil'], row['mws_id'])
    
    if kyl_data and len(kyl_data) > 0:
        indicators = kyl_data[0]  # First element contains the data
        print(f"  SUCCESS: Retrieved cropping intensity data")
        print(f"    Avg cropping intensity: {indicators.get('cropping_intensity_avg', 'N/A'):.2f}")
        print(f"    Trend: {indicators.get('cropping_intensity_trend', 'N/A')}")
        print(f"    Avg precipitation: {indicators.get('avg_precipitation', 'N/A'):.1f} mm")
        print(f"    Avg runoff: {indicators.get('avg_runoff', 'N/A'):.1f} mm")
        print(f"    Dry spells: {indicators.get('avg_number_dry_spell', 'N/A'):.1f} events")
        
        # Extract key metrics
        cropping_data.append({
            'grid_id': row['grid_id'],
            'mws_id': row['mws_id'],
            'district': row['district'],
            'state': row['state'],
            'old_growth_pct': row['old_growth_pct'],
            'plantation_pct': row['plantation_pct'],
            'grid_type': row['grid_type'],
            
            # Cropping intensity metrics
            'cropping_intensity_avg': indicators.get('cropping_intensity_avg'),
            'cropping_intensity_trend': indicators.get('cropping_intensity_trend'),
            'avg_single_cropped': indicators.get('avg_single_cropped'),
            'avg_double_cropped': indicators.get('avg_double_cropped'),
            'avg_triple_cropped': indicators.get('avg_triple_cropped'),
            
            # Hydrological metrics
            'avg_precipitation': indicators.get('avg_precipitation'),
            'avg_runoff': indicators.get('avg_runoff'),
            'avg_number_dry_spell': indicators.get('avg_number_dry_spell'),
            
            # Additional indicators
            'terraincluster_id': indicators.get('terraincluster_id'),
        })
    else:
        print(f"  FAILED: No KYL data available")
        cropping_data.append({
            'grid_id': row['grid_id'],
            'mws_id': row['mws_id'],
            'district': row['district'],
            'state': row['state'],
            'old_growth_pct': row['old_growth_pct'],
            'plantation_pct': row['plantation_pct'],
            'grid_type': row['grid_type'],
            'cropping_intensity_avg': None,
        })
    
    print()
    time.sleep(1)

cropping_df = pd.DataFrame(cropping_data)
print(f"Retrieved cropping intensity data for {cropping_df['cropping_intensity_avg'].notna().sum()} MWS")
print()

# Save cropping intensity results
cropping_output = OUTPUT_DIR / 'cropping_intensity_analysis.csv'
cropping_df.to_csv(cropping_output, index=False)
print(f"Saved cropping intensity analysis: {cropping_output}")
print()

# PHASE 3: Analyze Patterns - Shade-grown vs. Intensive Cropping
print("=" * 80)
print("PHASE 3: SHADE-GROWN AGROFORESTRY VS. INTENSIVE CROPPING ANALYSIS")
print("=" * 80)
print()

# Filter valid data
valid_df = cropping_df[cropping_df['cropping_intensity_avg'].notna()].copy()

if len(valid_df) > 0:
    # Classification criteria:
    # - Shade-grown/sustainable: Low cropping intensity (<1.5) + high old-growth % (>70%)
    # - Intensive: High cropping intensity (>1.5) + low old-growth % (<50%)
    # - Transition: Mixed characteristics
    
    def classify_agroforestry_type(row):
        ci = row['cropping_intensity_avg']
        og_pct = row['old_growth_pct']
        
        if ci < 1.5 and og_pct > 70:
            return 'Shade-grown/Sustainable'
        elif ci > 1.5 and og_pct < 50:
            return 'Intensive Agriculture'
        else:
            return 'Transition/Mixed'
    
    valid_df['agroforestry_type'] = valid_df.apply(classify_agroforestry_type, axis=1)
    
    # Summary statistics by type
    print("AGROFORESTRY TYPE CLASSIFICATION:")
    print("-" * 80)
    
    for af_type in ['Shade-grown/Sustainable', 'Intensive Agriculture', 'Transition/Mixed']:
        subset = valid_df[valid_df['agroforestry_type'] == af_type]
        if len(subset) > 0:
            print(f"\n{af_type}: ({len(subset)} grid cells)")
            print(f"  Average cropping intensity: {subset['cropping_intensity_avg'].mean():.2f}")
            print(f"  Average old-growth %: {subset['old_growth_pct'].mean():.1f}%")
            print(f"  Average precipitation: {subset['avg_precipitation'].mean():.1f} mm")
            print(f"  Average runoff: {subset['avg_runoff'].mean():.1f} mm")
            print(f"  Average dry spells: {subset['avg_number_dry_spell'].mean():.1f} events")
            
            if 'avg_single_cropped' in subset.columns:
                print(f"  Single cropping: {subset['avg_single_cropped'].mean():.1f}%")
                print(f"  Double cropping: {subset['avg_double_cropped'].mean():.1f}%")
                print(f"  Triple cropping: {subset['avg_triple_cropped'].mean():.1f}%")
            
            print(f"\n  Grid cells:")
            for _, row in subset.iterrows():
                print(f"    - Grid {int(row['grid_id'])}: {row['district']}, {row['state']}")
    
    # Statistical comparison
    print("\n" + "=" * 80)
    print("STATISTICAL COMPARISON: SHADE-GROWN VS. INTENSIVE")
    print("=" * 80)
    print()
    
    shade_grown = valid_df[valid_df['agroforestry_type'] == 'Shade-grown/Sustainable']
    intensive = valid_df[valid_df['agroforestry_type'] == 'Intensive Agriculture']
    
    if len(shade_grown) > 0 and len(intensive) > 0:
        metrics = {
            'Cropping Intensity': ('cropping_intensity_avg', 'lower is sustainable'),
            'Old-growth Forest %': ('old_growth_pct', 'higher is better'),
            'Precipitation (mm)': ('avg_precipitation', 'higher indicates stability'),
            'Runoff (mm)': ('avg_runoff', 'stable runoff is healthy'),
            'Dry Spell Events': ('avg_number_dry_spell', 'lower is better'),
        }
        
        for metric_name, (col, interpretation) in metrics.items():
            if col in shade_grown.columns and shade_grown[col].notna().any():
                sg_mean = shade_grown[col].mean()
                int_mean = intensive[col].mean()
                diff = sg_mean - int_mean
                pct_diff = (diff / int_mean * 100) if int_mean != 0 else 0
                
                print(f"{metric_name}:")
                print(f"  Shade-grown: {sg_mean:.2f}")
                print(f"  Intensive: {int_mean:.2f}")
                print(f"  Difference: {diff:+.2f} ({pct_diff:+.1f}%)")
                print(f"  Interpretation: {interpretation}")
                print()
    elif len(shade_grown) > 0:
        print("SUCCESS: Shade-grown zones identified, but no intensive zones in dataset")
        print("  This suggests old-growth forests are primarily in sustainable agroforestry regions")
    elif len(intensive) > 0:
        print("WARNING: Intensive zones identified, but no shade-grown zones in dataset")
        print("  This indicates high conversion pressure throughout the study area")
    else:
        print("WARNING: Insufficient data for statistical comparison")
    
    # Save classified results
    classified_output = OUTPUT_DIR / 'agroforestry_classification.csv'
    valid_df.to_csv(classified_output, index=False)
    print(f"\nSaved agroforestry classification: {classified_output}")
    print()
    
else:
    print("WARNING: No valid cropping intensity data available for analysis")
    print("   Core Stack coverage may not extend to Western Ghats priority regions")
    print()

# PHASE 4: Time Series Analysis (for available MWS)
print("=" * 80)
print("PHASE 4: WATER BALANCE TIME SERIES ANALYSIS (2017-2024)")
print("=" * 80)
print()

timeseries_data = []

for idx, row in grid_mws_df[grid_mws_df['mws_id'].notna()].iterrows():
    print(f"Grid {int(row['grid_id'])} - MWS {row['mws_id']}: Querying time series...")
    
    ts_data = get_mws_timeseries(row['state'], row['district'], row['tehsil'], row['mws_id'])
    
    if ts_data and 'time_series' in ts_data:
        ts_records = ts_data['time_series']
        print(f"  SUCCESS: Retrieved {len(ts_records)} time series records")
        
        # Convert to DataFrame for analysis
        ts_df = pd.DataFrame(ts_records)
        ts_df['date'] = pd.to_datetime(ts_df['date'])
        
        # Calculate trends and summary stats
        if len(ts_df) > 0:
            summary = {
                'grid_id': row['grid_id'],
                'mws_id': row['mws_id'],
                'district': row['district'],
                'old_growth_pct': row['old_growth_pct'],
                'n_records': len(ts_df),
                'start_date': ts_df['date'].min(),
                'end_date': ts_df['date'].max(),
                'avg_precipitation': ts_df['precipitation'].mean(),
                'avg_et': ts_df['et'].mean(),
                'avg_runoff': ts_df['runoff'].mean(),
                'total_precipitation': ts_df['precipitation'].sum(),
                'total_et': ts_df['et'].sum(),
                'total_runoff': ts_df['runoff'].sum(),
            }
            
            # Calculate water deficit (simplified)
            ts_df['water_deficit'] = ts_df['precipitation'] - (ts_df['et'] + ts_df['runoff'])
            summary['avg_water_deficit'] = ts_df['water_deficit'].mean()
            
            timeseries_data.append(summary)
            
            # Save individual time series
            ts_output = OUTPUT_DIR / f'timeseries_grid{int(row["grid_id"])}_mws{row["mws_id"]}.csv'
            ts_df.to_csv(ts_output, index=False)
            print(f"    Saved to: {ts_output}")
    else:
        print(f"  FAILED: No time series data available")
    
    print()
    time.sleep(1)

if len(timeseries_data) > 0:
    ts_summary_df = pd.DataFrame(timeseries_data)
    ts_summary_output = OUTPUT_DIR / 'water_balance_summary.csv'
    ts_summary_df.to_csv(ts_summary_output, index=False)
    print(f"Saved water balance summary: {ts_summary_output}")
    print()

# Final Summary Report
print("=" * 80)
print("ANALYSIS COMPLETE - SUMMARY REPORT")
print("=" * 80)
print()

print(f"Grid cells analyzed: {len(grid_mws_df)}")
print(f"MWS successfully linked: {grid_mws_df['mws_id'].notna().sum()}")
print(f"Cropping intensity data retrieved: {len(cropping_df[cropping_df['cropping_intensity_avg'].notna()])}")
print(f"Time series data retrieved: {len(timeseries_data)}")
print()

print("OUTPUT FILES:")
print(f"  1. Grid-MWS linkage: {grid_mws_output}")
print(f"  2. Cropping intensity analysis: {cropping_output}")
if len(valid_df) > 0:
    print(f"  3. Agroforestry classification: {classified_output}")
if len(timeseries_data) > 0:
    print(f"  4. Water balance summary: {ts_summary_output}")
    print(f"  5. Individual time series: {len(timeseries_data)} files in {OUTPUT_DIR}")
print()

print("NEXT STEPS:")
print("  1. Review agroforestry classification results")
print("  2. Analyze time series trends (precipitation, ET, runoff)")
print("  3. Generate visualizations (cropping intensity vs. forest %, water balance charts)")
print("  4. Statistical testing (shade-grown vs. intensive impacts)")
print("  5. Spatial risk mapping (combine with Hansen forest loss data)")
print()

print("KEY RESEARCH QUESTIONS TO ANSWER:")
print("  - Do shade-grown regions maintain higher old-growth forest %?")
print("  - Is water balance more stable in sustainable agroforestry zones?")
print("  - Does cropping intensification correlate with forest loss?")
print("  - Are there tangible benefits to sustainable practices?")
print()
