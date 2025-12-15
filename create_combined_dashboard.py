#!/usr/bin/env python3
"""
Create Complete Dashboard: 1987-2025
Combines GLC-FCS30D (1987-2015) with Dynamic World (2018-2025)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("CREATING COMPLETE LULC DASHBOARD (1987-2025)")
print("=" * 80)

output_dir = Path("outputs")

# Load datasets
print("\nLoading datasets...")
historical_csv = output_dir / "archive" / "glc_fcs30d_historical_lulc_20251024_114642.csv"
dynamic_csv = output_dir / "dynamic_world_lulc_january_2018_2025_20251026_153424.csv"

df_historical = pd.read_csv(historical_csv)
df_dynamic = pd.read_csv(dynamic_csv)

print(f"  Historical (GLC-FCS30D): {len(df_historical)} years - {sorted(df_historical['year'].unique().tolist())}")
print(f"  Dynamic World: {len(df_dynamic)} years - {sorted(df_dynamic['year'].unique().tolist())}")

# Standardize column names
historical_cols = ['year', 'dataset', 'Water', 'Trees', 'Grass', 'Flooded vegetation', 
                   'Crops', 'Shrub and scrub', 'Built', 'Bare', 'Snow and ice']

# Fix column name differences
df_dynamic_clean = df_dynamic.copy()
df_dynamic_clean = df_dynamic_clean.rename(columns={
    'Flooded Vegetation': 'Flooded vegetation',
    'Shrub and Scrub': 'Shrub and scrub'
})
df_dynamic_clean = df_dynamic_clean[historical_cols]
df_historical_clean = df_historical[historical_cols].copy()

# Use GLC-FCS30D for 1987-2015, Dynamic World for 2018-2025
df_historical_filtered = df_historical_clean[df_historical_clean['year'] <= 2015].copy()

# Combine
combined_df = pd.concat([df_historical_filtered, df_dynamic_clean], ignore_index=True)
combined_df = combined_df.sort_values('year').reset_index(drop=True)

print(f"\nCombined dataset: {len(combined_df)} years ({combined_df['year'].min()}-{combined_df['year'].max()})")
print(f"  Years: {combined_df['year'].tolist()}")

# Save combined CSV
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
combined_csv = output_dir / f"complete_lulc_1987_2025_{timestamp}.csv"
combined_df.to_csv(combined_csv, index=False)
print(f"\n✓ Saved: {combined_csv}")

# Calculate statistics
df = combined_df.copy()
df['total_computed'] = df[['Water', 'Trees', 'Grass', 'Flooded vegetation', 
                           'Crops', 'Shrub and scrub', 'Built', 'Bare', 'Snow and ice']].sum(axis=1)

area_mean = df['total_computed'].mean()
trees_first = df.iloc[0]['Trees']
trees_last = df.iloc[-1]['Trees']
trees_change = ((trees_last - trees_first) / trees_first) * 100

built_first = df.iloc[0]['Built']
built_last = df.iloc[-1]['Built']
built_change = ((built_last - built_first) / built_first) * 100

year_first = int(df.iloc[0]['year'])
year_last = int(df.iloc[-1]['year'])

print(f"\n{'=' * 80}")
print(f"SUMMARY STATISTICS ({year_first}-{year_last})")
print(f"{'=' * 80}")
print(f"Tree Cover:")
print(f"  {year_first}: {trees_first:,.2f} km²")
print(f"  {year_last}: {trees_last:,.2f} km²")
print(f"  Change: {trees_change:+.2f}% ({trees_last - trees_first:+,.2f} km²)")
print(f"\nBuilt Area:")
print(f"  {year_first}: {built_first:,.2f} km²")
print(f"  {year_last}: {built_last:,.2f} km²")
print(f"  Change: {built_change:+.2f}% ({built_last - built_first:+,.2f} km²)")

# LULC Colors
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

# Create HTML dashboard
print(f"\n{'=' * 80}")
print(f"GENERATING HTML DASHBOARD")
print(f"{'=' * 80}")

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Western Ghats LULC Analysis (1987-2025)</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%);
            color: white;
            padding: 40px;
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
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 10px;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #2E7D32;
        }}
        
        .stat-change {{
            font-size: 0.9rem;
            margin-top: 5px;
        }}
        
        .stat-change.positive {{
            color: #2E7D32;
        }}
        
        .stat-change.negative {{
            color: #C62828;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .year-selector {{
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .year-selector label {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-right: 15px;
        }}
        
        .year-selector select {{
            padding: 10px 20px;
            font-size: 1rem;
            border: 2px solid #2E7D32;
            border-radius: 5px;
            cursor: pointer;
        }}
        
        .data-table {{
            width: 100%;
            margin: 20px 0;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .data-table table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .data-table th {{
            background: #2E7D32;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        .data-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        
        .data-table tr:hover {{
            background: #f5f5f5;
        }}
        
        .color-box {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 3px;
            margin-right: 10px;
            vertical-align: middle;
        }}
        
        .chart-container {{
            margin: 30px 0;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .chart-title {{
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
        }}
        
        .info-section {{
            margin: 30px 0;
            padding: 20px;
            background: #e8f5e9;
            border-left: 4px solid #2E7D32;
            border-radius: 5px;
        }}
        
        .info-section h3 {{
            color: #2E7D32;
            margin-bottom: 10px;
        }}
        
        .info-section p {{
            line-height: 1.6;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Western Ghats Land Cover Analysis</h1>
            <div class="subtitle">Complete Historical Analysis (1987-2025)</div>
        </div>
        
        <div class="stats-summary">
            <div class="stat-card">
                <div class="stat-label">Time Period</div>
                <div class="stat-value">{year_first}-{year_last}</div>
                <div class="stat-change">{year_last - year_first} years</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Study Area</div>
                <div class="stat-value">{area_mean/1000:.1f}K</div>
                <div class="stat-change">km²</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Tree Cover ({year_last})</div>
                <div class="stat-value">{trees_last/1000:.1f}K</div>
                <div class="stat-change {'positive' if trees_change > 0 else 'negative'}">{trees_change:+.1f}% change</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Built Area ({year_last})</div>
                <div class="stat-value">{built_last:,.0f}</div>
                <div class="stat-change positive">{built_change:+.1f}% change</div>
            </div>
        </div>
        
        <div class="content">
            <div class="info-section">
                <h3>Data Sources</h3>
                <p>
                  <strong>Historical Baseline (1987-2015):</strong> GLC-FCS30D 30m resolution global land cover dataset<br>
                  <strong>Recent Analysis (2018-2025):</strong> Dynamic World 10m resolution near real-time land cover (January data only to avoid seasonal variations)<br>
                  <strong>Study Area:</strong> Western Ghats biodiversity hotspot across 6 states
                </p>
            </div>
            
            <div class="year-selector">
                <label for="yearSelect">Select Year:</label>
                <select id="yearSelect" onchange="updateYearData()">
"""

# Add year options
for year in df['year'].values:
    html_content += f'                    <option value="{int(year)}">{int(year)}</option>\n'

html_content += """                </select>
            </div>
            
            <div class="data-table">
                <h3 style="padding: 15px; background: #f8f9fa; margin: 0;">Land Cover Statistics for <span id="selectedYear"></span></h3>
                <table>
                    <thead>
                        <tr>
                            <th>Land Cover Class</th>
                            <th>Area (km²)</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody id="dataTableBody">
                    </tbody>
                </table>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Long-term Land Cover Trends (1987-2025)</div>
                <canvas id="trendsChart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Built Area Expansion</div>
                <canvas id="builtChart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Tree Cover Trends</div>
                <canvas id="treesChart"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        // Data
        const data = """

# Add JavaScript data
html_content += "{\n"
for idx, row in df.iterrows():
    year = int(row['year'])
    html_content += f"    {year}: {{\n"
    for col in ['Water', 'Trees', 'Grass', 'Flooded vegetation', 'Crops', 'Shrub and scrub', 'Built', 'Bare']:
        html_content += f"        '{col}': {row[col]:.2f},\n"
    total = row['total_computed']
    html_content += f"        'Total': {total:.2f},\n"
    html_content += f"        'Dataset': '{row['dataset']}'\n"
    html_content += "    },\n"
html_content += "};\n"

html_content += f"""
        const colors = {{
            'Water': '{LULC_COLORS['Water']}',
            'Trees': '{LULC_COLORS['Trees']}',
            'Grass': '{LULC_COLORS['Grass']}',
            'Flooded vegetation': '{LULC_COLORS['Flooded vegetation']}',
            'Crops': '{LULC_COLORS['Crops']}',
            'Shrub and scrub': '{LULC_COLORS['Shrub and scrub']}',
            'Built': '{LULC_COLORS['Built']}',
            'Bare': '{LULC_COLORS['Bare']}'
        }};
        
        function updateYearData() {{
            const year = document.getElementById('yearSelect').value;
            document.getElementById('selectedYear').textContent = year;
            
            const yearData = data[year];
            const tbody = document.getElementById('dataTableBody');
            tbody.innerHTML = '';
            
            const classes = ['Water', 'Trees', 'Grass', 'Flooded vegetation', 'Crops', 'Shrub and scrub', 'Built', 'Bare'];
            
            classes.forEach(cls => {{
                const area = yearData[cls];
                const pct = (area / yearData['Total']) * 100;
                
                const row = `<tr>
                    <td><span class="color-box" style="background: ${{colors[cls]}}"></span>${{cls}}</td>
                    <td>${{area.toFixed(2).toLocaleString()}}</td>
                    <td>${{pct.toFixed(1)}}%</td>
                </tr>`;
                tbody.innerHTML += row;
            }});
        }}
        
        // Initialize with first year
        document.getElementById('yearSelect').value = {year_first};
        updateYearData();
        
        // Trends Chart
        const years = {df['year'].tolist()};
        const trendsCtx = document.getElementById('trendsChart').getContext('2d');
        new Chart(trendsCtx, {{
            type: 'line',
            data: {{
                labels: years,
                datasets: [
                    {{
                        label: 'Trees',
                        data: {df['Trees'].tolist()},
                        borderColor: colors['Trees'],
                        backgroundColor: colors['Trees'] + '20',
                        tension: 0.4
                    }},
                    {{
                        label: 'Built',
                        data: {df['Built'].tolist()},
                        borderColor: colors['Built'],
                        backgroundColor: colors['Built'] + '20',
                        tension: 0.4
                    }},
                    {{
                        label: 'Crops',
                        data: {df['Crops'].tolist()},
                        borderColor: colors['Crops'],
                        backgroundColor: colors['Crops'] + '20',
                        tension: 0.4
                    }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'top'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Area (km²)'
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Year'
                        }}
                    }}
                }}
            }}
        }});
        
        // Built Area Chart
        const builtCtx = document.getElementById('builtChart').getContext('2d');
        new Chart(builtCtx, {{
            type: 'bar',
            data: {{
                labels: years,
                datasets: [{{
                    label: 'Built Area',
                    data: {df['Built'].tolist()},
                    backgroundColor: colors['Built']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Area (km²)'
                        }}
                    }}
                }}
            }}
        }});
        
        // Trees Chart
        const treesCtx = document.getElementById('treesChart').getContext('2d');
        new Chart(treesCtx, {{
            type: 'line',
            data: {{
                labels: years,
                datasets: [{{
                    label: 'Tree Cover',
                    data: {df['Trees'].tolist()},
                    borderColor: colors['Trees'],
                    backgroundColor: colors['Trees'] + '40',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: false,
                        title: {{
                            display: true,
                            text: 'Area (km²)'
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

# Save dashboard
dashboard_file = output_dir / f"complete_lulc_dashboard_1987_2025_{timestamp}.html"
with open(dashboard_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✓ Dashboard created: {dashboard_file}")
print(f"  File size: {dashboard_file.stat().st_size / 1024:.2f} KB")

print(f"\n{'=' * 80}")
print(f"COMPLETE")
print(f"{'=' * 80}")
print(f"\nFiles created:")
print(f"  1. {combined_csv}")
print(f"  2. {dashboard_file}")
print(f"\nOpen dashboard in browser to view complete 1987-2025 analysis")
