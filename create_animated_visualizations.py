"""
Create Animated GIF Time-Series of Western Ghats LULC Changes (1987-2025)

This script generates:
1. Annual LULC maps for all years
2. Animated GIF showing temporal changes
3. Side-by-side comparison animations
4. Before/After specific location zooms

Prerequisites:
- Install: pip install imageio pillow
- Ensure GEE exports have completed and downloaded to Google Drive

Author: Western Ghats LULC Analysis
Date: November 1, 2025
"""

import ee
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio
from datetime import datetime
import os
from pathlib import Path
import geopandas as gpd
import json

# Initialize Earth Engine
ee.Initialize(project='ee-tkkrfirst')

print("="*80)
print("WESTERN GHATS ANIMATED TIME-SERIES GENERATOR")
print("="*80)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Western Ghats boundary - Load from local GeoJSON
boundary_file = r"C:\Users\trkumar\OneDrive - Deloitte (O365D)\Documents\Research\Western Ghats\western_ghats_boundary_20250928_203521.geojson"
gdf = gpd.read_file(boundary_file)
geojson = json.loads(gdf.to_json())
cepf_boundary = ee.FeatureCollection(geojson)

# All years for animation
YEARS = list(range(1987, 2026))  # 1987-2025 (39 frames)

# Class mapping (same as before)
GLC_TO_DW_MAPPING = {
    10: 4, 20: 1, 51: 0, 52: 3, 61: 7, 62: 7, 71: 2, 72: 8,
    80: 6, 81: 6, 82: 2, 90: 5, 100: 3, 110: 2, 120: 5,
    121: 5, 122: 2, 130: 2, 140: 2, 150: 2, 152: 5, 153: 2,
    200: 7, 201: 7, 202: 7
}

# Colors
CLASS_COLORS = {
    0: '#419BDF', 1: '#397D49', 2: '#88B053', 3: '#7A87C6',
    4: '#E49635', 5: '#DFC35A', 6: '#C4281B', 7: '#A59B8F',
    8: '#B39FE1'
}

CLASS_NAMES = {
    0: 'Water', 1: 'Trees', 2: 'Grass', 3: 'Flooded vegetation',
    4: 'Crops', 5: 'Shrub and scrub', 6: 'Built', 7: 'Bare',
    8: 'Snow/ice'
}

# Output directory
output_dir = Path(r"C:\Users\trkumar\OneDrive - Deloitte (O365D)\Documents\Research\Western Ghats\outputs\animations")
output_dir.mkdir(parents=True, exist_ok=True)

# Specific hotspot locations for zoomed animations
HOTSPOTS = {
    'Wayanad': {
        'coords': [11.61, 76.08],
        'zoom_buffer': 0.3,  # degrees
        'description': 'Wayanad District, Kerala - Tourism & Development Hotspot'
    },
    'Kodagu': {
        'coords': [12.42, 75.74],
        'zoom_buffer': 0.3,
        'description': 'Kodagu District, Karnataka - Coffee Estates & Real Estate'
    },
    'Goa': {
        'coords': [15.36, 74.12],
        'zoom_buffer': 0.4,
        'description': 'Goa - Mining & Tourism Impact'
    },
    'Bangalore_Periphery': {
        'coords': [12.80, 77.30],
        'zoom_buffer': 0.5,
        'description': 'Bangalore Periphery - Urban Sprawl'
    },
    'Munnar': {
        'coords': [10.09, 77.06],
        'zoom_buffer': 0.25,
        'description': 'Munnar, Kerala - Plantation & Tourism Zone'
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_glc_fcs30d(year):
    """Get GLC-FCS30D classification for a given year"""
    if year < 2000:
        if year >= 1985 and year < 1990:
            band_name = 'b1'
        elif year >= 1990 and year < 1995:
            band_name = 'b2'
        elif year >= 1995 and year < 2000:
            band_name = 'b3'
        else:
            return None
        
        glc_fcs_five_year = ee.Image('users/potapovpeter/Global_land_cover_FCS30D/FCS_1985_2000')
        classification = glc_fcs_five_year.select(band_name)
    else:
        glc_fcs_annual = ee.ImageCollection('users/potapovpeter/Global_land_cover_FCS30D')
        classification = glc_fcs_annual.filterDate(f'{year}-01-01', f'{year}-12-31').first()
    
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

def create_visualization(lulc_image, title="", year=None):
    """Create RGB visualization with title overlay"""
    # Remap classes to color indices
    vis_image = lulc_image.remap(
        list(CLASS_COLORS.keys()),
        list(range(len(CLASS_COLORS)))
    ).visualize(
        min=0,
        max=8,
        palette=list(CLASS_COLORS.values())
    )
    
    return vis_image

def create_zoom_region(coords, buffer_deg):
    """Create bounding box for hotspot zoom"""
    lon, lat = coords
    return ee.Geometry.Rectangle([
        lon - buffer_deg,
        lat - buffer_deg,
        lon + buffer_deg,
        lat + buffer_deg
    ])

# ============================================================================
# EXPORT TASKS FOR ANIMATION FRAMES
# ============================================================================

print("\n" + "="*80)
print("EXPORTING ANIMATION FRAMES")
print("="*80)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Track export tasks
export_tasks = []

# 1. Full Western Ghats extent for each year
print("\n1. Exporting full Western Ghats frames...")
for year in YEARS:
    try:
        lulc = get_lulc_for_year(year)
        vis_image = create_visualization(lulc, year=year)
        
        task = ee.batch.Export.image.toDrive(
            image=vis_image,
            description=f'wg_full_{year}_{timestamp}',
            folder='Western_Ghats_Animations',
            fileNamePrefix=f'frame_full_{year:04d}',
            region=cepf_boundary.geometry(),
            scale=100,  # 100m for faster processing
            maxPixels=1e10,
            fileFormat='GeoTIFF'
        )
        task.start()
        export_tasks.append(f'frame_full_{year:04d}')
        print(f"  ✓ Exported: {year}")
    except Exception as e:
        print(f"  ✗ Failed: {year} - {e}")

print(f"\nTotal full frames exported: {len(export_tasks)}")

# 2. Hotspot zoom frames
print("\n2. Exporting hotspot zoom frames...")
hotspot_tasks = []

for hotspot_name, hotspot_data in HOTSPOTS.items():
    print(f"\n  Processing: {hotspot_data['description']}")
    
    zoom_region = create_zoom_region(
        hotspot_data['coords'],
        hotspot_data['zoom_buffer']
    )
    
    for year in [1987, 1995, 2000, 2005, 2010, 2015, 2018, 2020, 2022, 2025]:  # Key years only
        try:
            lulc = get_lulc_for_year(year)
            vis_image = create_visualization(lulc, year=year)
            
            task = ee.batch.Export.image.toDrive(
                image=vis_image,
                description=f'{hotspot_name}_{year}_{timestamp}',
                folder='Western_Ghats_Animations',
                fileNamePrefix=f'hotspot_{hotspot_name}_{year:04d}',
                region=zoom_region,
                scale=30,  # Higher resolution for zoomed views
                maxPixels=1e10,
                fileFormat='GeoTIFF'
            )
            task.start()
            hotspot_tasks.append(f'hotspot_{hotspot_name}_{year:04d}')
            print(f"    ✓ {year}")
        except Exception as e:
            print(f"    ✗ {year} - {e}")

print(f"\nTotal hotspot frames exported: {len(hotspot_tasks)}")

# 3. Change intensity maps (highlighting areas of change)
print("\n3. Exporting change intensity maps...")

# Calculate change for every 5-year period
change_tasks = []
base_years = list(range(1987, 2026, 5))

for i in range(len(base_years) - 1):
    year_start = base_years[i]
    year_end = base_years[i + 1]
    
    try:
        lulc_start = get_lulc_for_year(year_start)
        lulc_end = get_lulc_for_year(year_end)
        
        # Areas where class changed
        changed = lulc_start.neq(lulc_end)
        
        # Specifically highlight forest loss
        forest_start = lulc_start.eq(1)
        forest_end = lulc_end.eq(1)
        forest_loss = forest_start.And(forest_end.Not())
        
        # Built area gain
        built_start = lulc_start.eq(6)
        built_end = lulc_end.eq(6)
        built_gain = built_end.And(built_start.Not())
        
        # Composite: Red = forest loss, Yellow = built gain, Gray = other change
        change_vis = ee.Image.rgb(
            forest_loss.multiply(255),  # Red channel
            built_gain.multiply(200),    # Green channel (red+green=yellow)
            changed.multiply(100)        # Blue channel (subdued other changes)
        )
        
        task = ee.batch.Export.image.toDrive(
            image=change_vis,
            description=f'change_{year_start}_{year_end}_{timestamp}',
            folder='Western_Ghats_Animations',
            fileNamePrefix=f'change_{year_start}_to_{year_end}',
            region=cepf_boundary.geometry(),
            scale=100,
            maxPixels=1e10,
            fileFormat='GeoTIFF'
        )
        task.start()
        change_tasks.append(f'change_{year_start}_to_{year_end}')
        print(f"  ✓ Change map: {year_start} → {year_end}")
    except Exception as e:
        print(f"  ✗ Failed: {year_start} → {year_end} - {e}")

print(f"\nTotal change maps exported: {len(change_tasks)}")

# ============================================================================
# LOCAL PROCESSING SCRIPT (to run after downloads)
# ============================================================================

print("\n" + "="*80)
print("CREATING LOCAL ANIMATION SCRIPT")
print("="*80)

animation_script = '''
"""
Process downloaded frames into animated GIFs

Run this after downloading all frames from Google Drive

Prerequisites: pip install imageio pillow numpy
"""

import imageio
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pathlib import Path
import glob

print("Creating animated GIFs from exported frames...")

# Input directory (update this to your Google Drive download location)
input_dir = Path("path/to/downloaded/Western_Ghats_Animations")
output_dir = Path("outputs/animations")
output_dir.mkdir(parents=True, exist_ok=True)

# Animation parameters
fps = 2  # Frames per second
duration_per_frame = 0.5  # seconds

# 1. Create full Western Ghats animation
print("\\n1. Creating full Western Ghats time-lapse...")
full_frames = sorted(glob.glob(str(input_dir / "frame_full_*.tif")))

if full_frames:
    images = []
    for frame_path in full_frames:
        img = Image.open(frame_path)
        
        # Extract year from filename
        year = int(Path(frame_path).stem.split('_')[-1])
        
        # Add year label
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Add semi-transparent background for text
        text = f"Year: {year}"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        padding = 20
        bg_bbox = [
            padding,
            padding,
            padding + text_width + 2*padding,
            padding + text_height + 2*padding
        ]
        
        # Draw background
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(bg_bbox, fill=(0, 0, 0, 180))
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        
        # Draw text
        draw = ImageDraw.Draw(img)
        draw.text((padding*2, padding*2), text, fill=(255, 255, 255), font=font)
        
        images.append(np.array(img.convert('RGB')))
    
    # Save as GIF
    output_path = output_dir / "western_ghats_1987_2025.gif"
    imageio.mimsave(output_path, images, duration=duration_per_frame, loop=0)
    print(f"  ✓ Saved: {output_path}")
    print(f"    Frames: {len(images)}, Size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
else:
    print("  ✗ No full frames found")

# 2. Create hotspot animations
print("\\n2. Creating hotspot animations...")
hotspots = ['Wayanad', 'Kodagu', 'Goa', 'Bangalore_Periphery', 'Munnar']

for hotspot in hotspots:
    hotspot_frames = sorted(glob.glob(str(input_dir / f"hotspot_{hotspot}_*.tif")))
    
    if hotspot_frames:
        images = []
        for frame_path in hotspot_frames:
            img = Image.open(frame_path)
            year = int(Path(frame_path).stem.split('_')[-1])
            
            # Add labels
            draw = ImageDraw.Draw(img)
            try:
                font_title = ImageFont.truetype("arial.ttf", 30)
                font_year = ImageFont.truetype("arial.ttf", 50)
            except:
                font_title = font_year = ImageFont.load_default()
            
            # Add title and year
            img_rgba = img.convert('RGBA')
            overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Background for title
            overlay_draw.rectangle([10, 10, 500, 80], fill=(0, 0, 0, 180))
            img_rgba = Image.alpha_composite(img_rgba, overlay)
            
            draw = ImageDraw.Draw(img_rgba)
            draw.text((20, 20), hotspot.replace('_', ' '), fill=(255, 255, 255), font=font_title)
            draw.text((20, 50), f"Year: {year}", fill=(255, 255, 0), font=font_year)
            
            images.append(np.array(img_rgba.convert('RGB')))
        
        output_path = output_dir / f"hotspot_{hotspot}.gif"
        imageio.mimsave(output_path, images, duration=duration_per_frame * 2, loop=0)
        print(f"  ✓ {hotspot}: {len(images)} frames, {output_path.stat().st_size / 1024:.0f} KB")
    else:
        print(f"  ✗ {hotspot}: No frames found")

# 3. Create change intensity animation
print("\\n3. Creating change intensity animation...")
change_frames = sorted(glob.glob(str(input_dir / "change_*.tif")))

if change_frames:
    images = []
    for frame_path in change_frames:
        img = Image.open(frame_path)
        
        # Extract years from filename (e.g., change_1987_to_1992.tif)
        parts = Path(frame_path).stem.split('_')
        year_start = parts[1]
        year_end = parts[3]
        
        # Add legend
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 25)
        except:
            font = ImageFont.load_default()
        
        img_rgba = img.convert('RGBA')
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Legend background
        overlay_draw.rectangle([10, 10, 400, 140], fill=(0, 0, 0, 200))
        img_rgba = Image.alpha_composite(img_rgba, overlay)
        
        draw = ImageDraw.Draw(img_rgba)
        draw.text((20, 20), f"Changes: {year_start} → {year_end}", fill=(255, 255, 255), font=font)
        draw.text((20, 55), "■ Forest Loss", fill=(255, 0, 0), font=font)
        draw.text((20, 85), "■ Urban Growth", fill=(255, 255, 0), font=font)
        draw.text((20, 115), "■ Other Changes", fill=(150, 150, 150), font=font)
        
        images.append(np.array(img_rgba.convert('RGB')))
    
    output_path = output_dir / "change_intensity_1987_2025.gif"
    imageio.mimsave(output_path, images, duration=1.0, loop=0)
    print(f"  ✓ Saved: {output_path}")
else:
    print("  ✗ No change frames found")

print("\\n" + "="*80)
print("ANIMATION GENERATION COMPLETE!")
print("="*80)
print(f"\\nOutput directory: {output_dir}")
print("\\nGenerated files:")
for gif_file in sorted(output_dir.glob("*.gif")):
    print(f"  - {gif_file.name} ({gif_file.stat().st_size / 1024 / 1024:.1f} MB)")
'''

# Save the local processing script
local_script_path = output_dir / 'create_gifs_from_exports.py'
with open(local_script_path, 'w') as f:
    f.write(animation_script)

print(f"\n✓ Local animation script created: {local_script_path}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*80)
print("EXPORT TASKS SUBMITTED")
print("="*80)

total_tasks = len(export_tasks) + len(hotspot_tasks) + len(change_tasks)

print(f"""
Total tasks submitted: {total_tasks}

BREAKDOWN:
  - Full Western Ghats frames: {len(export_tasks)}
  - Hotspot zoom frames: {len(hotspot_tasks)}
  - Change intensity maps: {len(change_tasks)}

All exports will be saved to Google Drive folder: Western_Ghats_Animations/

NEXT STEPS:

1. Monitor tasks at: https://code.earthengine.google.com/tasks
   (This may take 2-4 hours depending on queue)

2. Download all frames from Google Drive to your local machine

3. Update the path in the local processing script:
   {local_script_path}
   
4. Install required Python packages:
   pip install imageio pillow numpy

5. Run the local script to generate GIFs:
   python {local_script_path}

6. Use the GIFs in your Substack story!

HOTSPOTS ANALYZED:
""")

for name, data in HOTSPOTS.items():
    print(f"  - {name}: {data['description']}")

print("\n" + "="*80)
print("All animation export tasks started!")
print("="*80)
