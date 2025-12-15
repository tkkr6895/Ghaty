#!/usr/bin/env python3
"""
Test GLC-FCS30D dataset structure to determine correct property names
"""

import ee

print("Initializing Earth Engine...")
try:
    ee.Initialize(project='ee-tkkrfirst')
    print("SUCCESS: Earth Engine initialized\n")
    
    # Test the dataset structure
    print("Testing GLC-FCS30D Five-Year Map collection...")
    glc_fcs_five_year = ee.ImageCollection("projects/sat-io/open-datasets/GLC-FCS30D/five-years-map")
    
    # Get collection info
    print("Getting collection size...")
    size = glc_fcs_five_year.size().getInfo()
    print(f"Collection contains {size} images\n")
    
    if size > 0:
        # Get first image
        print("Getting first image info...")
        first_image = glc_fcs_five_year.first()
        
        # Get band names
        bands = first_image.bandNames().getInfo()
        print(f"Band names: {bands}\n")
        
        # Get properties
        props = first_image.propertyNames().getInfo()
        print(f"Properties: {props}\n")
        
        # Get all properties
        all_props = first_image.toDictionary().getInfo()
        print("All properties:")
        for key, value in sorted(all_props.items()):
            if not key.startswith('system:'):
                print(f"  {key}: {value}")
        
        print("\n" + "="*70)
        print("Listing all images with their properties...")
        print("="*70)
        
        # Get all images
        image_list = glc_fcs_five_year.toList(glc_fcs_five_year.size())
        
        for i in range(min(10, size)):  # Limit to first 10
            img = ee.Image(image_list.get(i))
            img_props = img.toDictionary().getInfo()
            
            # Extract relevant properties
            year_prop = img_props.get('year', img_props.get('YEAR', img_props.get('time', 'N/A')))
            system_index = img_props.get('system:index', 'N/A')
            
            print(f"\nImage {i+1}:")
            print(f"  system:index: {system_index}")
            print(f"  year property: {year_prop}")
            
            # Check if there's a date property
            if 'system:time_start' in img_props:
                time_start = img_props['system:time_start']
                from datetime import datetime
                date = datetime.fromtimestamp(time_start / 1000)
                print(f"  Date: {date.year}-{date.month:02d}-{date.day:02d}")
    
    print("\n" + "="*70)
    print("Testing GLC-FCS30D Annual collection...")
    print("="*70)
    
    glc_fcs_annual = ee.ImageCollection("projects/sat-io/open-datasets/GLC-FCS30D/annual")
    annual_size = glc_fcs_annual.size().getInfo()
    print(f"Annual collection contains {annual_size} images")
    
    if annual_size > 0:
        first_annual = glc_fcs_annual.first()
        annual_props = first_annual.toDictionary().getInfo()
        print("\nFirst annual image properties:")
        for key, value in sorted(annual_props.items()):
            if not key.startswith('system:'):
                print(f"  {key}: {value}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
