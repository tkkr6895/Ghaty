# Current Status: Interactive Map with Year/Class Layers

## Question: Which HTML file allows toggling between years/classes for side-by-side analysis?

### Answer: No such file currently exists

The current HTML files only contain:

1. **lulc_statistics_dashboard_20251025_160437.html**
   - Statistics tables and charts only
   - No map layers
   - No spatial visualization
   - Year selector shows numbers, not maps

2. **interactive_lulc_comparison_20251024_115233.html**
   - Shows boundary polygon only
   - No LULC raster layers
   - No year toggle functionality

3. **final_interactive_lulc_map_20251025_153550.html**
   - Similar to above
   - Boundary visualization only

## Why the Layers Are Missing

The script `create_complete_interactive_map.py` was designed to:
1. Download LULC images from Earth Engine
2. Embed them as base64 in HTML
3. Create toggleable layers

However, it failed due to SSL/network issues when connecting to Earth Engine API.

## Solution: Generate LULC Layers via Earth Engine Tasks

### Option 1: GeoTIFF Rasters (For QGIS)

The script `generate_lulc_layers_and_shapefiles.py` submits Earth Engine tasks to export:

**Raster Files** (13 files, one per year):
- lulc_1987_GLC_FCS30D.tif
- lulc_1992_GLC_FCS30D.tif
- lulc_1997_GLC_FCS30D.tif
- lulc_2000_GLC_FCS30D.tif
- lulc_2005_GLC_FCS30D.tif
- lulc_2010_GLC_FCS30D.tif
- lulc_2015_GLC_FCS30D.tif
- lulc_2018_Dynamic_World.tif
- lulc_2019_Dynamic_World.tif
- lulc_2020_GLC_FCS30D.tif
- lulc_2021_Dynamic_World.tif
- lulc_2022_Dynamic_World.tif
- lulc_2023_Dynamic_World.tif

**Location**: Google Drive > Western_Ghats_LULC folder

**Properties**:
- Format: GeoTIFF
- Resolution: 30 meters
- CRS: EPSG:4326 (WGS84)
- Pixel values: 0-8 (LULC class codes)

**Use in QGIS**:
1. Download files from Google Drive
2. Layer > Add Layer > Add Raster Layer
3. Select file
4. Style > Paletted/Unique values
5. Classify with color ramp
6. Load multiple years as separate layers
7. Toggle visibility to compare

### Option 2: Shapefiles (Vector Polygons)

**Class-Specific Shapefiles** (52 files total):
- For each year: water, trees, crops, built polygons
- Example: water_1987_GLC_FCS30D.shp, trees_1987_GLC_FCS30D.shp

**Location**: Google Drive > Western_Ghats_LULC_Vectors folder

**Properties**:
- Format: Shapefile (.shp, .shx, .dbf, .prj)
- Scale: 100 meters (vectorized from raster)
- CRS: EPSG:4326

**Use in QGIS**:
1. Download shapefiles from Google Drive
2. Layer > Add Layer > Add Vector Layer
3. Select .shp file
4. Style by class
5. Compare years by overlaying layers

### Option 3: Upload to Google Earth Engine

**For GEE Code Editor**:
1. Go to https://code.earthengine.google.com
2. Assets > NEW > Upload
3. Select GeoTIFF files from Google Drive
4. Once uploaded, use in GEE scripts:
   ```javascript
   var lulc1987 = ee.Image('users/YOUR_USERNAME/lulc_1987_GLC_FCS30D');
   var lulc2023 = ee.Image('users/YOUR_USERNAME/lulc_2023_Dynamic_World');
   
   Map.addLayer(lulc1987, {min: 0, max: 8, palette: [colors]}, 'LULC 1987');
   Map.addLayer(lulc2023, {min: 0, max: 8, palette: [colors]}, 'LULC 2023');
   ```

## Checking Export Task Status

1. Visit: https://code.earthengine.google.com/tasks
2. Look for tasks named:
   - LULC_1987_GLC_FCS30D
   - LULC_2023_Dynamic_World
   - water_1987_GLC_FCS30D
   - trees_2023_Dynamic_World
   etc.

3. Tasks will show:
   - READY: Waiting to start
   - RUNNING: Currently processing
   - COMPLETED: Check Google Drive
   - FAILED: Check error message

## Timeline

- Export tasks typically take: 5-30 minutes per file
- Total processing time: 2-6 hours for all files
- Files appear in Google Drive as they complete

## File Sizes (Estimated)

- Raster GeoTIFF: 5-20 MB per file
- Shapefile (per class): 2-10 MB
- Total download: ~500 MB - 1 GB

## Next Steps

1. **Monitor Earth Engine Tasks**
   - Check task manager for completion status

2. **Download from Google Drive**
   - Once tasks complete, files will be in Drive folders

3. **Load in QGIS**
   - Import rasters or shapefiles
   - Apply styling
   - Create side-by-side comparison layouts

4. **Conduct Analysis**
   - Overlay layers to identify change areas
   - Calculate area differences
   - Identify spatial patterns of change

## LULC Class Codes

| Code | Class | Color (Hex) |
|------|-------|-------------|
| 0 | Water | #419BDF |
| 1 | Trees | #397D49 |
| 2 | Grass | #88B053 |
| 3 | Flooded vegetation | #7A87C6 |
| 4 | Crops | #E49635 |
| 5 | Shrub and scrub | #DFC35A |
| 6 | Built | #C4281B |
| 7 | Bare | #A59B8F |
| 8 | Snow and ice | #B39FE1 |

## Reproducibility

All exports use:
- Original CEPF boundary shapefile
- GLC-FCS30D: Band-based selection with mosaic
- Dynamic World: Annual mode composite
- Same class harmonization mapping used in analysis
- Documented in: `outputs/geospatial/export_metadata_*.json`

## Files Generated

Check `outputs/geospatial/` folder for:
- `export_tasks_*.json` - Raster export task IDs
- `vector_export_tasks_*.json` - Shapefile export task IDs
- `export_metadata_*.json` - Complete export configuration

These files allow others to verify exactly what was exported and how.
