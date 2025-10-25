#!/usr/bin/env python3
"""
Understand GLC-FCS30D band structure for year extraction
"""

import ee

print("Initializing Earth Engine...")
ee.Initialize(project='ee-tkkrfirst')

# Load the dataset
glc_fcs_five_year = ee.ImageCollection("projects/sat-io/open-datasets/GLC-FCS30D/five-years-map")
glc_fcs_annual = ee.ImageCollection("projects/sat-io/open-datasets/GLC-FCS30D/annual")

print("\n" + "="*70)
print("GLC-FCS30D Five-Year Map Collection")
print("="*70)

# Get a sample image
sample_five_year = glc_fcs_five_year.first()
bands = sample_five_year.bandNames().getInfo()
print(f"Bands: {bands}")
print(f"Number of bands: {len(bands)}")

# The 5-year map should have 3 bands for 1985, 1990, 1995, 2000
# Let's check what each band represents
for i, band in enumerate(bands):
    print(f"\nBand {i+1}: {band}")

# Get a sample tile ID to understand structure
id_no = sample_five_year.get('id_no').getInfo()
print(f"\nSample tile ID: {id_no}")

print("\n" + "="*70)
print("GLC-FCS30D Annual Collection")
print("="*70)

sample_annual = glc_fcs_annual.first()
annual_bands = sample_annual.bandNames().getInfo()
print(f"Number of bands: {len(annual_bands)}")
print("Bands represent years 2000-2022 (23 years)")

for i, band in enumerate(annual_bands[:5]):  # Show first 5
    print(f"Band {i+1}: {band} (likely year {2000+i})")

print("\n" + "="*70)
print("Testing mosaic approach for specific years")
print("="*70)

# The correct approach: mosaic all tiles for a specific band/year
# For 5-year map: bands are b1 (1985-1989), b2 (1990-1994), b3 (1995-1999)
# For annual: bands are b1 (2000), b2 (2001), ..., b23 (2022)

print("\nCreating mosaics for specific years...")

# Test with 5-year collection - these should be composite periods
five_year_periods = {
    'b1': '1985-1989',
    'b2': '1990-1994',
    'b3': '1995-1999'
}

print("\nFive-year collection periods:")
for band, period in five_year_periods.items():
    print(f"  {band}: {period}")
    mosaic = glc_fcs_five_year.select([band]).mosaic()
    # Check if mosaic has data
    try:
        # Get a sample point
        test_point = ee.Geometry.Point([75.0, 15.0])
        value = mosaic.sample(test_point, 30).first().get(band).getInfo()
        print(f"    Sample value at test point: {value}")
    except Exception as e:
        print(f"    Error sampling: {e}")

# Test with annual collection
print("\nAnnual collection - testing years 2000, 2005, 2010, 2015, 2020:")
test_years = [2000, 2005, 2010, 2015, 2020]
for year in test_years:
    band_index = year - 2000 + 1  # b1 = 2000, b2 = 2001, etc.
    band_name = f'b{band_index}'
    
    if band_index <= len(annual_bands):
        print(f"\n  Year {year} (band {band_name}):")
        mosaic = glc_fcs_annual.select([band_name]).mosaic()
        try:
            test_point = ee.Geometry.Point([75.0, 15.0])
            value = mosaic.sample(test_point, 30).first().get(band_name).getInfo()
            print(f"    Sample value at test point: {value}")
        except Exception as e:
            print(f"    Error sampling: {e}")

print("\n" + "="*70)
print("CONCLUSION")
print("="*70)
print("The GLC-FCS30D dataset is organized as:")
print("1. Multiple tiles covering the globe")
print("2. Each tile has multiple bands representing different years")
print("3. Five-year collection: 3 bands for 1985-1989, 1990-1994, 1995-1999")
print("4. Annual collection: 23 bands for 2000-2022")
print("\nTo use: Select specific band, mosaic all tiles, then analyze")
