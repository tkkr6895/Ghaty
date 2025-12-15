# QUICK START GUIDE - Western Ghats Visualization

## 🎯 YOUR TWO MAIN FILES

### 1. **Story Dashboard** (For Substack/Blog)
📄 `outputs/western_ghats_corrected_story_dashboard.html`

**To view:**
- Double-click the file in Windows Explorer
- OR right-click → Open with → Chrome/Firefox/Edge

**What you'll see:**
- ✅ Corrected statistics (4.0x built area, not 15x)
- ✅ Interactive charts you can screenshot
- ✅ Community impact analysis
- ✅ Action items for different stakeholders

**For Substack:**
- Screenshot the insight cards
- Export charts as images
- Copy text from impact sections
- Use action items as conclusion

---

### 2. **Interactive Map** (For Exploration)
📄 `outputs/interactive_map_viewer.html`

**To view:**
- Double-click the file
- Click hotspot buttons to jump to regions
- Change basemap to see satellite imagery
- Click anywhere to get coordinates

**Note:** Full GeoTIFF visualization requires QGIS (see below)

---

## 🗺️ FOR DETAILED SPATIAL ANALYSIS

### Install GDAL First
```powershell
# Option 1: If you have conda
conda install -c conda-forge gdal

# Option 2: If you have pip
pip install gdal

# Option 3: Download OSGeo4W installer
# https://trac.osgeo.org/osgeo4w/
```

### Then Run QGIS Generator
```powershell
cd "C:\Users\trkumar\OneDrive - Deloitte (O365D)\Documents\Research\Western Ghats"
python create_qgis_project.py
```

**This will:**
1. Merge 24 GeoTIFF tiles into 2 mosaics
2. Create QGIS project file (.qgz)
3. Generate visualization guide

### Then Open in QGIS
- Install QGIS: https://qgis.org/download/
- Double-click: `western_ghats_urbanization.qgz`
- Layers load automatically with proper styling

---

## 📊 KEY STATISTICS (CORRECTED)

### Historical Period (1987-2015, GLC-FCS30D)
- **Built Area:** 207.5 → 831.9 km² (**4.0x increase**)
- **Tree Cover:** 87,503.7 → 87,554.9 km² (+0.06%, stable)
- **Croplands:** 14,343.2 → 14,731.6 km² (+2.7%)
- **Water Bodies:** 1,146.5 → 1,317.5 km² (+15%)

### ⚠️ DO NOT USE
- ❌ "1500% increase" (dataset mixing artifact)
- ❌ "16x increase" (incorrect calculation)
- ❌ "Forest loss" (use "tree cover" instead)
- ❌ "Bangalore urbanization in Western Ghats" (city is outside boundary)

---

## 🎯 HOTSPOT COORDINATES

Copy these into Google Maps or QGIS:

- **Wayanad, Kerala:** 11.61°N, 76.08°E
- **Kodagu (Coorg), Karnataka:** 12.42°N, 75.74°E
- **Munnar, Kerala:** 10.09°N, 77.06°E
- **Nilgiris (Ooty), Tamil Nadu:** 11.41°N, 76.70°E
- **Goa Highlands:** 15.36°N, 74.12°E
- **Sahyadri, Maharashtra:** 18.00°N, 73.50°E

---

## 🔍 DATA QUALITY NOTES

### Why Dataset Discontinuity Matters
- GLC-FCS30D (1987-2015): Landsat 30m, conservative urban detection
- Dynamic World (2018-2025): Sentinel-2 10m, sensitive urban detection
- **Gap causes artificial 2.6x jump** in 2015→2018 (not real change!)

### Solution
- ✅ Use GLC-FCS30D for 1987-2015 trends
- ✅ Use Dynamic World for 2018-2025 trends  
- ✅ **DO NOT compare across datasets**
- ✅ Current ESRI analysis (2017-2023) avoids this issue

---

## 📝 FOR YOUR SUBSTACK POST

### Opening Hook
"Between 1987 and 2015, built-up areas in the Western Ghats increased fourfold—
from 207 to 832 square kilometers. But this isn't a story about statistics. 
It's about hill communities watching their watersheds change, wildlife corridors 
fragmenting, and the delicate balance between development and conservation."

### Key Data Points
1. **4x urban expansion** (not 16x—that's dataset mixing)
2. **Tree cover remained stable** (but plantations ≠ forests)
3. **Croplands shifted** (rice → coffee/tea cash crops)
4. **Water bodies increased 15%** (dams, not natural springs)

### Regional Focus
- Highlight **hill stations within Western Ghats**: Munnar, Ooty, Coorg, Wayanad
- Avoid **plains cities**: Bangalore, Mangalore, Kochi (mostly outside boundary)
- Emphasize **community impacts**: water security, landslides, biodiversity

### Action Section
Copy the action cards from dashboard for:
- Local administrators
- Civil society/NGOs
- Local communities
- Policy makers
- Researchers
- Tourists

---

## ✅ DELIVERABLES CHECKLIST

**Ready to Use:**
- [x] Corrected story dashboard (`western_ghats_corrected_story_dashboard.html`)
- [x] Interactive map viewer (`interactive_map_viewer.html`)
- [x] Data quality analysis (`corrected_metrics.json`)
- [x] GeoTIFF tiles (24 files downloaded)

**Requires GDAL Installation:**
- [ ] Merged mosaics (run `create_qgis_project.py`)
- [ ] QGIS project file (.qgz)
- [ ] Detailed spatial analysis

**Optional:**
- [ ] Time-series animations (requires additional GEE exports)
- [ ] Field validation in hotspots
- [ ] Substack publication

---

## 🆘 TROUBLESHOOTING

**"Charts not showing in dashboard"**
- Ensure JavaScript is enabled in browser
- Check console for errors (F12)
- Try different browser (Chrome recommended)

**"GDAL not found" when running QGIS script**
- Install via conda: `conda install gdal`
- OR download OSGeo4W: https://trac.osgeo.org/osgeo4w/
- Restart terminal after installation

**"Map shows wrong data"**
- Dashboard uses 1987-2015 data (GLC-FCS30D)
- Spatial exports use 2017-2023 data (ESRI)
- Both are valid for different time periods

**"Where is Bangalore in the analysis?"**
- Bangalore city is OUTSIDE Western Ghats boundary
- Only periphery/outskirts are included
- Focus on hill stations: Munnar, Coorg, Ooty, Wayanad

---

## 📧 FILE LOCATIONS

```
C:\Users\trkumar\OneDrive - Deloitte (O365D)\Documents\Research\Western Ghats\
├── outputs\
│   ├── western_ghats_corrected_story_dashboard.html  ← OPEN THIS FOR STORY
│   ├── interactive_map_viewer.html                   ← OPEN THIS FOR MAP
│   ├── corrected_metrics.json                        ← ACCURATE STATISTICS
│   ├── BuiltArea_Western_Ghats_Spatial_Analysis\     ← GEOTIFF TILES
│   └── BuiltHotspot_Western_Ghats_Spatial_Analysis\  ← GEOTIFF TILES
├── analyze_data_quality.py                           ← DATA VALIDATION
├── create_qgis_project.py                            ← MOSAIC GENERATOR
└── DELIVERABLES_SUMMARY.md                           ← FULL DOCUMENTATION
```

---

**Questions? Check `DELIVERABLES_SUMMARY.md` for detailed explanations.**

**Ready to publish? Use `western_ghats_corrected_story_dashboard.html` as your data source!**
