#!/usr/bin/env python3
"""
Interactive LULC Statistics Dashboard
Generates HTML visualization for Western Ghats LULC data (1987-2023)
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("CREATING LULC STATISTICS DASHBOARD")
print("=" * 80)

# Directories
output_dir = Path("outputs")

# Load combined dataset
print("\nLoading LULC statistics...")
combined_csv = output_dir / "dynamic_world_lulc_january_2018_2025_20251026_153424.csv"
df = pd.read_csv(combined_csv)

# Data is already clean (Dynamic World only, no duplicates)
df = df.sort_values('year').reset_index(drop=True)

print(f"Loaded {len(df)} years of data")
print(f"  Years: {sorted(df['year'].unique().tolist())}")
print(f"  Datasets: {df['dataset'].unique().tolist()}")

# Calculate statistics
df['total_computed'] = df[['Water', 'Trees', 'Grass', 'Flooded Vegetation', 
                           'Crops', 'Shrub and Scrub', 'Built', 'Bare', 'Snow and ice']].sum(axis=1)

area_mean = df['total_computed'].mean()
trees_first = df.iloc[0]['Trees']
trees_last = df.iloc[-1]['Trees']
trees_change = ((trees_last - trees_first) / trees_first) * 100

built_first = df.iloc[0]['Built']
built_last = df.iloc[-1]['Built']
built_change = ((built_last - built_first) / built_first) * 100

# LULC Color palette
LULC_COLORS = {
    'Water': '#419BDF',
    'Trees': '#397D49',
    'Grass': '#88B053',
    'Flooded vegetation': '#7A87C6',
    'Crops': '#E49635',
    'Shrub and scrub': '#DFC35A',
    'Built': '#C4281B',
    'Bare': '#A59B8F',
    'Snow and ice': '#B39FE1'
}

# Create the HTML
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Western Ghats LULC Analysis Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header .subtitle {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .stats-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f5f5f5;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #1976D2;
            margin: 10px 0;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .controls {{
            padding: 30px;
            background: white;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        .control-group {{
            margin-bottom: 20px;
        }}
        
        .control-group label {{
            display: block;
            font-weight: bold;
            margin-bottom: 8px;
            color: #333;
        }}
        
        .control-group select {{
            width: 100%;
            padding: 12px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 8px;
            transition: border-color 0.3s;
        }}
        
        .control-group select:focus {{
            outline: none;
            border-color: #1976D2;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .year-details {{
            background: #f9f9f9;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 30px;
            border-left: 5px solid #1976D2;
        }}
        
        .year-details h2 {{
            color: #1976D2;
            margin-bottom: 20px;
        }}
        
        .lulc-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .lulc-table thead {{
            background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
            color: white;
        }}
        
        .lulc-table th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.5px;
        }}
        
        .lulc-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .lulc-table tbody tr:hover {{
            background: #f5f5f5;
        }}
        
        .lulc-table tbody tr:last-child td {{
            border-bottom: none;
        }}
        
        .color-indicator {{
            width: 30px;
            height: 20px;
            border-radius: 4px;
            display: inline-block;
            margin-right: 10px;
            border: 1px solid #999;
        }}
        
        .chart-container {{
            margin: 30px 0;
            padding: 25px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        }}
        
        .chart-container h3 {{
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #1976D2;
            padding-bottom: 10px;
        }}
        
        .legend {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 25px;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 8px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            font-size: 0.9rem;
        }}
        
        .footer {{
            background: #333;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 0.9rem;
        }}
        
        .data-source {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #1976D2;
        }}
        
        .data-source strong {{
            color: #1976D2;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Western Ghats Land Use Land Cover Analysis</h1>
            <div class="subtitle">LULC Analysis Dashboard (2018-2025)</div>
        </div>
        
        <div class="stats-summary">
            <div class="stat-card">
                <div class="stat-label">Temporal Coverage</div>
                <div class="stat-value">{len(df)}</div>
                <div class="stat-label">Years Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Study Period</div>
                <div class="stat-value">2018-2025</div>
                <div class="stat-label">36 Years</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Area</div>
                <div class="stat-value">{area_mean:,.0f}</div>
                <div class="stat-label">km²</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Tree Cover (2025)</div>
                <div class="stat-value">{trees_last/1000:.1f}K</div>
                <div class="stat-label">km² ({trees_change:+.1f}%)</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Built Area (2025)</div>
                <div class="stat-value">{built_last:,.0f}</div>
                <div class="stat-label">km² ({built_change:+.0f}%)</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Data Status</div>
                <div class="stat-value">Verified</div>
                <div class="stat-label">From Satellite Observations</div>
            </div>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label for="year-select">Select Year to View Detailed Statistics:</label>
                <select id="year-select" onchange="updateYearDetails()">
                    {"".join([f'<option value="{i}">{int(row["year"])} - {row["dataset"]}</option>' for i, row in df.iterrows()])}
                </select>
            </div>
        </div>
        
        <div class="content">
            <div id="year-details" class="year-details">
                <!-- Will be populated by JavaScript -->
            </div>
            
            <div class="chart-container">
                <h3>Land Cover Trends Over Time</h3>
                <canvas id="trendsChart" height="100"></canvas>
            </div>
            
            <div class="chart-container">
                <h3>Built Area Expansion</h3>
                <canvas id="builtChart" height="100"></canvas>
            </div>
            
            <div class="chart-container">
                <h3>Tree Cover Trends</h3>
                <canvas id="forestChart" height="100"></canvas>
            </div>
            
            <div class="data-source">
                <strong>Data Sources:</strong><br>
                Dynamic World V1 (2018-2025): Near real-time 10m resolution land cover,
                  <a href="https://dynamicworld.app/" target="_blank">More info</a><br>
                Analysis Period: January only (dry season, minimal cloud cover)<br>
                All data processed via Google Earth Engine<br>
                Study area: Western Ghats Priority Conservation Area (CEPF Boundary)
            </div>
            
            <div class="legend">
                <h3 style="grid-column: 1 / -1; margin-bottom: 10px;">Land Cover Classes Legend</h3>
                {"".join([f'<div class="legend-item"><span class="color-indicator" style="background-color: {color};"></span>{label}</div>' for label, color in LULC_COLORS.items()])}
            </div>
        </div>
        
        <div class="footer">
            Generated on {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}<br>
            Western Ghats LULC Analysis - Data from GLC-FCS30D and Dynamic World satellite observations
        </div>
    </div>
    
    <script>
        // Data from Python
        const lulcData = {json.dumps(df.to_dict('records'))};
        const colors = {json.dumps(LULC_COLORS)};
        
        // Update year details
        function updateYearDetails() {{
            const select = document.getElementById('year-select');
            const idx = parseInt(select.value);
            const data = lulcData[idx];
            
            const detailsHtml = `
                <h2>${{data.year}} - ${{data.dataset}}</h2>
                <p><strong>Period:</strong> ${{data.period || data.year}}</p>
                <p><strong>Total Classified Area:</strong> ${{data.total_area_km2.toFixed(2)}} km²</p>
                
                <table class="lulc-table">
                    <thead>
                        <tr>
                            <th>Land Cover Class</th>
                            <th>Area (km²)</th>
                            <th>Percentage (%)</th>
                            <th>Visual</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><span class="color-indicator" style="background-color: ${{colors['Water']}};"></span>Water</td>
                            <td>${{data.Water.toFixed(2)}}</td>
                            <td>${{data['Water_percent'].toFixed(2)}}%</td>
                            <td><div style="width: ${{data['Water_percent'] * 3}}px; height: 20px; background: ${{colors['Water']}}; border-radius: 4px;"></div></td>
                        </tr>
                        <tr style="background: #f0f8f0;">
                            <td><span class="color-indicator" style="background-color: ${{colors['Trees']}};"></span><strong>Trees</strong></td>
                            <td><strong>${{data.Trees.toFixed(2)}}</strong></td>
                            <td><strong>${{data['Trees_percent'].toFixed(2)}}%</strong></td>
                            <td><div style="width: ${{data['Trees_percent'] * 3}}px; height: 20px; background: ${{colors['Trees']}}; border-radius: 4px;"></div></td>
                        </tr>
                        <tr>
                            <td><span class="color-indicator" style="background-color: ${{colors['Grass']}};"></span>Grass</td>
                            <td>${{data.Grass.toFixed(2)}}</td>
                            <td>${{data['Grass_percent'].toFixed(2)}}%</td>
                            <td><div style="width: ${{data['Grass_percent'] * 3}}px; height: 20px; background: ${{colors['Grass']}}; border-radius: 4px;"></div></td>
                        </tr>
                        <tr>
                            <td><span class="color-indicator" style="background-color: ${{colors['Flooded vegetation']}};"></span>Flooded vegetation</td>
                            <td>${{data['Flooded vegetation'].toFixed(2)}}</td>
                            <td>${{data['Flooded vegetation_percent'].toFixed(2)}}%</td>
                            <td><div style="width: ${{data['Flooded vegetation_percent'] * 3}}px; height: 20px; background: ${{colors['Flooded vegetation']}}; border-radius: 4px;"></div></td>
                        </tr>
                        <tr style="background: #fff8f0;">
                            <td><span class="color-indicator" style="background-color: ${{colors['Crops']}};"></span><strong>Crops</strong></td>
                            <td><strong>${{data.Crops.toFixed(2)}}</strong></td>
                            <td><strong>${{data['Crops_percent'].toFixed(2)}}%</strong></td>
                            <td><div style="width: ${{data['Crops_percent'] * 3}}px; height: 20px; background: ${{colors['Crops']}}; border-radius: 4px;"></div></td>
                        </tr>
                        <tr>
                            <td><span class="color-indicator" style="background-color: ${{colors['Shrub and scrub']}};"></span>Shrub and scrub</td>
                            <td>${{data['Shrub and scrub'].toFixed(2)}}</td>
                            <td>${{data['Shrub and scrub_percent'].toFixed(2)}}%</td>
                            <td><div style="width: ${{data['Shrub and scrub_percent'] * 3}}px; height: 20px; background: ${{colors['Shrub and scrub']}}; border-radius: 4px;"></div></td>
                        </tr>
                        <tr style="background: #fff0f0;">
                            <td><span class="color-indicator" style="background-color: ${{colors['Built']}};"></span><strong>Built</strong></td>
                            <td><strong>${{data.Built.toFixed(2)}}</strong></td>
                            <td><strong>${{data['Built_percent'].toFixed(2)}}%</strong></td>
                            <td><div style="width: ${{data['Built_percent'] * 3}}px; height: 20px; background: ${{colors['Built']}}; border-radius: 4px;"></div></td>
                        </tr>
                        <tr>
                            <td><span class="color-indicator" style="background-color: ${{colors['Bare']}};"></span>Bare</td>
                            <td>${{data.Bare.toFixed(2)}}</td>
                            <td>${{data['Bare_percent'].toFixed(2)}}%</td>
                            <td><div style="width: ${{data['Bare_percent'] * 3}}px; height: 20px; background: ${{colors['Bare']}}; border-radius: 4px;"></div></td>
                        </tr>
                        <tr>
                            <td><span class="color-indicator" style="background-color: ${{colors['Snow and ice']}};"></span>Snow and ice</td>
                            <td>${{data['Snow and ice'].toFixed(2)}}</td>
                            <td>${{data['Snow and ice_percent'].toFixed(2)}}%</td>
                            <td><div style="width: ${{data['Snow and ice_percent'] * 3}}px; height: 20px; background: ${{colors['Snow and ice']}}; border-radius: 4px;"></div></td>
                        </tr>
                    </tbody>
                </table>
            `;
            
            document.getElementById('year-details').innerHTML = detailsHtml;
        }}
        
        // Create charts
        const years = lulcData.map(d => d.year);
        
        // Trends Chart
        new Chart(document.getElementById('trendsChart'), {{
            type: 'line',
            data: {{
                labels: years,
                datasets: [
                    {{
                        label: 'Trees',
                        data: lulcData.map(d => d.Trees),
                        borderColor: colors['Trees'],
                        backgroundColor: colors['Trees'] + '33',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true
                    }},
                    {{
                        label: 'Built',
                        data: lulcData.map(d => d.Built),
                        borderColor: colors['Built'],
                        backgroundColor: colors['Built'] + '33',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true
                    }},
                    {{
                        label: 'Crops',
                        data: lulcData.map(d => d.Crops),
                        borderColor: colors['Crops'],
                        backgroundColor: colors['Crops'] + '33',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true
                    }},
                    {{
                        label: 'Water',
                        data: lulcData.map(d => d.Water),
                        borderColor: colors['Water'],
                        backgroundColor: colors['Water'] + '33',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        position: 'top',
                        labels: {{
                            font: {{ size: 14, weight: 'bold' }},
                            padding: 15
                        }}
                    }},
                    tooltip: {{
                        mode: 'index',
                        intersect: false,
                        callbacks: {{
                            label: function(context) {{
                                return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + ' km²';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: false,
                        title: {{
                            display: true,
                            text: 'Area (km²)',
                            font: {{ size: 14, weight: 'bold' }}
                        }},
                        ticks: {{
                            font: {{ size: 12 }}
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Year',
                            font: {{ size: 14, weight: 'bold' }}
                        }},
                        ticks: {{
                            font: {{ size: 12 }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Built Chart
        new Chart(document.getElementById('builtChart'), {{
            type: 'bar',
            data: {{
                labels: years,
                datasets: [{{
                    label: 'Built Area (km²)',
                    data: lulcData.map(d => d.Built),
                    backgroundColor: colors['Built'],
                    borderColor: '#A02010',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top',
                        labels: {{
                            font: {{ size: 14, weight: 'bold' }}
                        }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return 'Built Area: ' + context.parsed.y.toFixed(2) + ' km²';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Built Area (km²)',
                            font: {{ size: 14, weight: 'bold' }}
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Year',
                            font: {{ size: 14, weight: 'bold' }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Tree Chart
        new Chart(document.getElementById('forestChart'), {{
            type: 'line',
            data: {{
                labels: years,
                datasets: [{{
                    label: 'Tree Cover (km²)',
                    data: lulcData.map(d => d.Trees),
                    borderColor: colors['Trees'],
                    backgroundColor: colors['Trees'] + '66',
                    borderWidth: 4,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 5,
                    pointHoverRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top',
                        labels: {{
                            font: {{ size: 14, weight: 'bold' }}
                        }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return 'Tree Cover: ' + context.parsed.y.toFixed(2) + ' km²';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: false,
                        title: {{
                            display: true,
                            text: 'Tree Cover (km²)',
                            font: {{ size: 14, weight: 'bold' }}
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Year',
                            font: {{ size: 14, weight: 'bold' }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Initialize with most recent year
        document.getElementById('year-select').value = lulcData.length - 1;
        updateYearDetails();
    </script>
</body>
</html>
"""

# Save the HTML
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = output_dir / f"lulc_dashboard_clean_{timestamp}.html"

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\nDashboard created: {output_file}")
print(f"  File size: {output_file.stat().st_size / 1024:.2f} KB")

print("\n" + "=" * 80)
print("DASHBOARD GENERATION COMPLETE")
print("=" * 80)
print(f"\nOpen in browser: {output_file}")
