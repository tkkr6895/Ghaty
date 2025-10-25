#!/usr/bin/env python3
"""
Interactive LULC Comparison Tool and Statistical Analysis
Generates comprehensive HTML visualization and statistical reports for Western Ghats LULC data
"""

import pandas as pd
import numpy as np
import json
import folium
from folium import plugins
import base64
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

print("=" * 80)
print("WESTERN GHATS LULC COMPREHENSIVE ANALYSIS")
print("=" * 80)
print("\nLoading data...")

# Load all available LULC data
output_dir = Path("outputs")

# Load Dynamic World data
dw_file = output_dir / "western_ghats_lulc_analysis_results_20250928_203521.csv"
dw_df = pd.read_csv(dw_file)
print(f"Loaded Dynamic World data: {len(dw_df)} years ({dw_df['year'].min():.0f}-{dw_df['year'].max():.0f})")

# Check for historical data
historical_files = list(output_dir.glob("western_ghats_historical_lulc_*.csv"))
combined_files = list(output_dir.glob("western_ghats_combined_lulc_*.csv"))

if combined_files:
    # Use the most recent combined file
    combined_file = sorted(combined_files)[-1]
    combined_df = pd.read_csv(combined_file)
    print(f"Loaded combined dataset: {len(combined_df)} years ({combined_df['year'].min():.0f}-{combined_df['year'].max():.0f})")
elif historical_files:
    # Combine manually
    historical_file = sorted(historical_files)[-1]
    hist_df = pd.read_csv(historical_file)
    dw_df['dataset'] = 'Dynamic World'
    combined_df = pd.concat([hist_df, dw_df], ignore_index=True)
    combined_df = combined_df.sort_values('year').reset_index(drop=True)
    print(f"Combined historical and Dynamic World data: {len(combined_df)} years")
else:
    # Use only Dynamic World
    combined_df = dw_df.copy()
    combined_df['dataset'] = 'Dynamic World'
    print("Using Dynamic World data only (2018-2023)")

# Load boundary
boundary_file = output_dir / "western_ghats_boundary_20250928_203521.geojson"
import geopandas as gpd
boundary_gdf = gpd.read_file(boundary_file)
print(f"Loaded boundary: {len(boundary_gdf)} polygons")

# Define land cover classes
LULC_CLASSES = {
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

# Class colors
CLASS_COLORS = {
    'Water': '#1976D2',
    'Trees': '#2E7D32',
    'Grass': '#689F38',
    'Flooded vegetation': '#00796B',
    'Crops': '#F57C00',
    'Shrub and scrub': '#795548',
    'Built': '#D32F2F',
    'Bare': '#757575',
    'Snow and ice': '#E0E0E0'
}

print("\n" + "=" * 80)
print("1. GENERATING COMPREHENSIVE STATISTICAL ANALYSIS")
print("=" * 80)

# Overall statistics
print("\nOVERALL SUMMARY")
print("-" * 80)
years_analyzed = sorted(combined_df['year'].unique())
print(f"Analysis period: {int(min(years_analyzed))}-{int(max(years_analyzed))}")
print(f"Total years analyzed: {len(years_analyzed)}")
print(f"Years: {', '.join([str(int(y)) for y in years_analyzed])}")

if 'dataset' in combined_df.columns:
    datasets = combined_df['dataset'].unique()
    print(f"Datasets: {', '.join(datasets)}")

# Calculate study area
if 'total_area_km2' in combined_df.columns:
    study_area = combined_df['total_area_km2'].mean()
else:
    # Calculate from class areas
    class_cols = [col for col in combined_df.columns if col in LULC_CLASSES.values()]
    study_area = combined_df[class_cols].sum(axis=1).mean()

print(f"Study area: {study_area:.0f} km²")

# Land cover statistics by class
print("\nLAND COVER STATISTICS BY CLASS")
print("-" * 80)

stats_by_class = {}
for class_name in LULC_CLASSES.values():
    if class_name in combined_df.columns:
        first_year_data = combined_df.iloc[0]
        last_year_data = combined_df.iloc[-1]
        
        area_change = last_year_data[class_name] - first_year_data[class_name]
        
        if f'{class_name}_percent' in combined_df.columns:
            pct_first = first_year_data[f'{class_name}_percent']
            pct_last = last_year_data[f'{class_name}_percent']
            pct_change = pct_last - pct_first
        else:
            pct_first = (first_year_data[class_name] / study_area) * 100
            pct_last = (last_year_data[class_name] / study_area) * 100
            pct_change = pct_last - pct_first
        
        relative_change = (area_change / first_year_data[class_name] * 100) if first_year_data[class_name] > 0 else 0
        
        stats_by_class[class_name] = {
            'initial_year': int(first_year_data['year']),
            'final_year': int(last_year_data['year']),
            'initial_area_km2': float(first_year_data[class_name]),
            'final_area_km2': float(last_year_data[class_name]),
            'initial_percent': float(pct_first),
            'final_percent': float(pct_last),
            'absolute_change_km2': float(area_change),
            'percentage_point_change': float(pct_change),
            'relative_change_percent': float(relative_change)
        }
        
        print(f"\n{class_name}:")
        print(f"   {int(first_year_data['year'])}: {first_year_data[class_name]:.1f} km² ({pct_first:.1f}%)")
        print(f"   {int(last_year_data['year'])}: {last_year_data[class_name]:.1f} km² ({pct_last:.1f}%)")
        print(f"   Change: {area_change:+.1f} km² ({pct_change:+.1f} percentage points, {relative_change:+.1f}%)")

# Temporal trends
print("\nTEMPORAL TRENDS")
print("-" * 80)

temporal_trends = {}
key_classes = ['Trees', 'Built', 'Crops', 'Bare']

for class_name in key_classes:
    if class_name in combined_df.columns:
        # Calculate year-over-year changes
        if f'{class_name}_percent' in combined_df.columns:
            pct_col = f'{class_name}_percent'
        else:
            combined_df[f'{class_name}_percent'] = (combined_df[class_name] / study_area) * 100
            pct_col = f'{class_name}_percent'
        
        combined_df[f'{class_name}_change'] = combined_df[pct_col].diff()
        
        mean_change = combined_df[f'{class_name}_change'].mean()
        std_change = combined_df[f'{class_name}_change'].std()
        max_increase = combined_df[f'{class_name}_change'].max()
        max_decrease = combined_df[f'{class_name}_change'].min()
        
        temporal_trends[class_name] = {
            'mean_annual_change': float(mean_change) if not np.isnan(mean_change) else 0,
            'std_deviation': float(std_change) if not np.isnan(std_change) else 0,
            'max_increase': float(max_increase) if not np.isnan(max_increase) else 0,
            'max_decrease': float(max_decrease) if not np.isnan(max_decrease) else 0
        }
        
        print(f"\n{class_name}:")
        print(f"   Mean annual change: {mean_change:+.3f} percentage points/year")
        print(f"   Std deviation: {std_change:.3f}")
        print(f"   Maximum increase: {max_increase:+.3f} percentage points")
        print(f"   Maximum decrease: {max_decrease:+.3f} percentage points")

# Save comprehensive statistics
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
stats_summary = {
    'analysis_info': {
        'analysis_date': datetime.now().isoformat(),
        'study_area_km2': float(study_area),
        'years_analyzed': [int(y) for y in years_analyzed],
        'temporal_range': f"{int(min(years_analyzed))}-{int(max(years_analyzed))}",
        'total_years': len(years_analyzed)
    },
    'land_cover_statistics': stats_by_class,
    'temporal_trends': temporal_trends
}

stats_file = output_dir / f'comprehensive_statistics_{timestamp}.json'
with open(stats_file, 'w') as f:
    json.dump(stats_summary, f, indent=2)

print(f"\nStatistics saved: {stats_file}")

# Export detailed CSV
detailed_csv = output_dir / f'detailed_lulc_statistics_{timestamp}.csv'
combined_df.to_csv(detailed_csv, index=False)
print(f"Detailed CSV saved: {detailed_csv}")

print("\n" + "=" * 80)
print("2. CREATING INTERACTIVE HTML COMPARISON TOOL")
print("=" * 80)

# Create the interactive map
center_lat = boundary_gdf.geometry.centroid.y.mean()
center_lon = boundary_gdf.geometry.centroid.x.mean()

# Create base map
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=7,
    tiles=None,
    control_scale=True
)

# Add multiple basemaps
folium.TileLayer('OpenStreetMap', name='OpenStreetMap', overlay=False, control=True).add_to(m)
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Satellite Imagery',
    overlay=False,
    control=True
).add_to(m)

# Add boundary
folium.GeoJson(
    boundary_gdf,
    name='Western Ghats Boundary',
    style_function=lambda x: {
        'fillColor': 'none',
        'color': '#FF5722',
        'weight': 3,
        'fillOpacity': 0
    }
).add_to(m)

# Add title and instructions
title_html = '''
<div style="position: fixed; 
            top: 10px; left: 50px; width: 400px; height: auto;
            background-color: white; z-index:9999; font-size:14px;
            border:2px solid grey; border-radius: 5px; padding: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
    <h3 style="margin: 0 0 10px 0; color: #1976D2;">Western Ghats LULC Analysis</h3>
    <p style="margin: 5px 0;"><strong>Period:</strong> ''' + f"{int(min(years_analyzed))}-{int(max(years_analyzed))}" + '''</p>
    <p style="margin: 5px 0;"><strong>Years available:</strong> ''' + ', '.join([str(int(y)) for y in years_analyzed]) + '''</p>
    <p style="margin: 5px 0; font-size: 12px;">Use the layer control to toggle different years and basemaps.</p>
</div>
'''
m.get_root().html.add_child(folium.Element(title_html))

# Add layer control
folium.LayerControl(position='topright', collapsed=False).add_to(m)

# Add fullscreen button
plugins.Fullscreen(position='topleft').add_to(m)

# Add measure control
plugins.MeasureControl(position='bottomleft', primary_length_unit='kilometers').add_to(m)

# Save map
html_file = output_dir / f'interactive_lulc_comparison_{timestamp}.html'
m.save(str(html_file))
print(f"Interactive HTML map saved: {html_file}")
print(f"File size: {html_file.stat().st_size / 1024:.1f} KB")

print("\n" + "=" * 80)
print("3. CREATING COMPREHENSIVE VISUALIZATIONS")
print("=" * 80)

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Create comprehensive figure
fig = plt.figure(figsize=(20, 12))

# 1. Long-term trends
ax1 = plt.subplot(2, 3, 1)
for class_name in ['Trees', 'Built', 'Crops']:
    if class_name in combined_df.columns:
        pct_col = f'{class_name}_percent' if f'{class_name}_percent' in combined_df.columns else class_name
        ax1.plot(combined_df['year'], combined_df[pct_col], 
                marker='o', linewidth=2, markersize=6, label=class_name,
                color=CLASS_COLORS.get(class_name, '#000000'))

ax1.set_title('Land Cover Trends Over Time', fontweight='bold', fontsize=12)
ax1.set_xlabel('Year')
ax1.set_ylabel('Percentage of Total Area (%)')
ax1.legend(loc='best')
ax1.grid(True, alpha=0.3)

# 2. Built-up area expansion
ax2 = plt.subplot(2, 3, 2)
if 'Built' in combined_df.columns:
    ax2.bar(combined_df['year'], combined_df['Built'], 
           color=CLASS_COLORS['Built'], alpha=0.7, width=0.8)
    ax2.set_title('Built-up Area Expansion', fontweight='bold', fontsize=12)
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Built-up Area (km²)')
    ax2.grid(True, alpha=0.3, axis='y')

# 3. Forest cover trends
ax3 = plt.subplot(2, 3, 3)
if 'Trees' in combined_df.columns:
    ax3.plot(combined_df['year'], combined_df['Trees'], 
            marker='o', color=CLASS_COLORS['Trees'], linewidth=2, markersize=6)
    ax3.fill_between(combined_df['year'], combined_df['Trees'], alpha=0.3, color=CLASS_COLORS['Trees'])
    ax3.set_title('Forest Cover Over Time', fontweight='bold', fontsize=12)
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Forest Area (km²)')
    ax3.grid(True, alpha=0.3)

# 4. Change rates
ax4 = plt.subplot(2, 3, 4)
if len(combined_df) > 1:
    changes_df = combined_df[['year'] + [f'{c}_change' for c in key_classes if f'{c}_change' in combined_df.columns]].dropna()
    if len(changes_df) > 0:
        width = 0.2
        x = np.arange(len(changes_df))
        colors = [CLASS_COLORS.get(c, '#000000') for c in key_classes if f'{c}_change' in combined_df.columns]
        
        for i, class_name in enumerate([c for c in key_classes if f'{c}_change' in combined_df.columns]):
            ax4.bar(x + i*width, changes_df[f'{class_name}_change'], 
                   width, label=class_name, color=CLASS_COLORS.get(class_name, '#000000'), alpha=0.7)
        
        ax4.set_title('Year-over-Year Changes', fontweight='bold', fontsize=12)
        ax4.set_xlabel('Year')
        ax4.set_ylabel('Change (percentage points)')
        ax4.set_xticks(x)
        ax4.set_xticklabels([int(y) for y in changes_df['year']], rotation=45)
        ax4.legend()
        ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax4.grid(True, alpha=0.3)

# 5. Latest composition
ax5 = plt.subplot(2, 3, 5)
latest = combined_df.iloc[-1]
classes_to_plot = [c for c in LULC_CLASSES.values() if c in combined_df.columns and latest[c] > 0.1]
areas = [latest[c] for c in classes_to_plot]
colors = [CLASS_COLORS.get(c, '#000000') for c in classes_to_plot]

if areas:
    wedges, texts, autotexts = ax5.pie(areas, labels=classes_to_plot, autopct='%1.1f%%',
                                       colors=colors, startangle=90)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_weight('bold')
    ax5.set_title(f'Land Cover Composition {int(latest["year"])}', fontweight='bold', fontsize=12)

# 6. Cumulative change
ax6 = plt.subplot(2, 3, 6)
baseline = combined_df.iloc[0]
for class_name in ['Trees', 'Built', 'Crops']:
    if class_name in combined_df.columns:
        cumulative = combined_df[class_name] - baseline[class_name]
        ax6.plot(combined_df['year'], cumulative, 
                marker='o', linewidth=2, markersize=6, label=class_name,
                color=CLASS_COLORS.get(class_name, '#000000'))

ax6.set_title(f'Cumulative Change from {int(baseline["year"])} Baseline', fontweight='bold', fontsize=12)
ax6.set_xlabel('Year')
ax6.set_ylabel('Change in Area (km²)')
ax6.legend()
ax6.axhline(y=0, color='black', linestyle='--', linewidth=0.5)
ax6.grid(True, alpha=0.3)

plt.tight_layout()

viz_file = output_dir / f'comprehensive_analysis_visualization_{timestamp}.png'
plt.savefig(viz_file, dpi=300, bbox_inches='tight')
print(f"Comprehensive visualization saved: {viz_file}")

plt.close()

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print("\nGenerated files:")
print(f"1. Statistics (JSON): {stats_file.name}")
print(f"2. Detailed data (CSV): {detailed_csv.name}")
print(f"3. Interactive map (HTML): {html_file.name}")
print(f"4. Visualizations (PNG): {viz_file.name}")
print("\nAll outputs saved in 'outputs' directory")
