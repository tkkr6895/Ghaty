"""
Download India Census 2011 District Boundaries from DataMeet

This script downloads the district shapefile and prepares it for upload to Google Earth Engine.
"""

import requests
import os
from pathlib import Path

print("="*80)
print("DOWNLOADING INDIA CENSUS 2011 DISTRICT BOUNDARIES")
print("="*80)

# Create output directory
output_dir = Path(r"C:\Users\trkumar\OneDrive - Deloitte (O365D)\Documents\Research\Western Ghats\data\district_boundaries")
output_dir.mkdir(parents=True, exist_ok=True)

# DataMeet GitHub URL
url = "https://github.com/datameet/maps/raw/master/Districts/Census_2011/2011_Dist.zip"
output_file = output_dir / "india_district_2011.zip"

print(f"\nDownloading from: {url}")
print(f"Saving to: {output_file}")

try:
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    block_size = 8192
    downloaded = 0
    
    with open(output_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=block_size):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\rProgress: {percent:.1f}% ({downloaded / 1024 / 1024:.1f} MB)", end='')
    
    print(f"\n\n✓ Download complete: {output_file}")
    print(f"  File size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Try to extract
    print("\nExtracting files...")
    import zipfile
    
    with zipfile.ZipFile(output_file, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    
    print("✓ Extraction complete")
    
    # List extracted files
    print("\nExtracted files:")
    for file in sorted(output_dir.glob("*")):
        if file.is_file() and file.suffix != '.zip':
            print(f"  - {file.name} ({file.stat().st_size / 1024:.1f} KB)")
    
    print("\n" + "="*80)
    print("NEXT STEPS: UPLOAD TO GOOGLE EARTH ENGINE")
    print("="*80)
    print("""
1. Go to: https://code.earthengine.google.com/

2. Click 'Assets' tab in left panel

3. Click 'NEW' → 'Shape files' (or 'Table upload')

4. Upload these files together:
   - 2011_Dist.shp
   - 2011_Dist.shx
   - 2011_Dist.dbf
   - 2011_Dist.prj
   
5. Name the asset: 'india_districts_2011'

6. Wait for processing to complete (may take 5-15 minutes)

7. Update spatial_analysis_comprehensive.py with your GEE asset path:
   Line ~170: districts = ee.FeatureCollection('users/YOUR_USERNAME/india_districts_2011')
   
8. Re-run the spatial analysis script to enable district-level analysis

Files are ready in: {output_dir}
""")
    
except requests.exceptions.RequestException as e:
    print(f"\n✗ Error downloading file: {e}")
    print("\nAlternative: Manual download")
    print("1. Visit: https://github.com/datameet/maps/tree/master/Districts/Census_2011")
    print("2. Download 2011_Dist.zip manually")
    print(f"3. Extract to: {output_dir}")
except Exception as e:
    print(f"\n✗ Unexpected error: {e}")

print("="*80)
