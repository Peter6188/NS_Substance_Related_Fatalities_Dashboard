import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd
import folium
from folium import plugins
import json
import dash_bootstrap_components as dbc
from datetime import datetime
import numpy as np

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Nova Scotia Substance-Related Fatalities Dashboard"

# Load CSV data
try:
    df = pd.read_csv('Numbers_and_rates_of_substance-related_fatalities_in_Nova_Scotia.csv', encoding='utf-8-sig')
    print("CSV loaded successfully")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Shape: {df.shape}")
except Exception as e:
    print(f"Error loading CSV: {e}")
    df = pd.DataFrame()

# Load GeoJSON data
try:
    with open('Nova Scotia Health Authority Management Zones.geojson', 'r') as f:
        geojson_data = json.load(f)
    gdf = gpd.read_file('Nova Scotia Health Authority Management Zones.geojson')
    print("GeoJSON loaded successfully")
    print(f"GeoJSON features: {len(geojson_data['features'])}")
except Exception as e:
    print(f"Error loading GeoJSON: {e}")
    geojson_data = None
    gdf = gpd.GeoDataFrame()

# Data preprocessing
if not df.empty:
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Handle the rate column with special characters
    rate_col = 'Rate per 100,000 population (annualized for quarterly data)'
    if rate_col in df.columns:
        df['Rate'] = pd.to_numeric(df[rate_col], errors='coerce')
    
    # Convert Year to numeric
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df['Frequency'] = pd.to_numeric(df['Frequency'], errors='coerce')
    
    # Filter out rows with missing essential data
    df = df.dropna(subset=['Year', 'Health Zone of Residence'])
    
    # Get unique values for filters
    health_zones = sorted([zone for zone in df['Health Zone of Residence'].unique() 
                          if zone in ['Central', 'Eastern', 'Northern', 'Western', 'Nova Scotia']])
    drug_types = sorted(df['Drug Type'].unique())
    years = sorted(df['Year'].unique())
    
    print(f"Health Zones: {health_zones}")
    print(f"Years range: {min(years)} - {max(years)}")
    print(f"Drug Types: {len(drug_types)}")

# Define colors for health zones
zone_colors = {
    'Central': '#1f77b4',
    'Eastern': '#ff7f0e', 
    'Northern': '#2ca02c',
    'Western': '#d62728',
    'Nova Scotia': '#9467bd'
}

# App layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Nova Scotia Substance-Related Fatalities Dashboard", 
                   className="text-center mb-4",
                   style={'color': '#2c3e50', 'margin-top': '20px'}),
            html.P("Interactive visualization of substance-related fatalities in Nova Scotia health zones (2009-2025)",
                  className="text-center text-muted mb-4")
        ])
    ]),
    
    # Control Panel
    dbc.Card([
        dbc.CardHeader("Control Panel"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Year Range:", className="font-weight-bold"),
                    dcc.RangeSlider(
                        id='year-slider',
                        min=min(years) if years else 2009,
                        max=max(years) if years else 2025,
                        value=[min(years) if years else 2009, max(years) if years else 2025],
                        marks={year: str(year) for year in range(min(years) if years else 2009, 
                                                               max(years) + 1 if years else 2026, 2)},
                        step=1
                    )
                ], width=6),
                
                dbc.Col([
                    html.Label("Health Zone:", className="font-weight-bold"),
                    dcc.Dropdown(
                        id='zone-dropdown',
                        options=[{'label': zone, 'value': zone} for zone in health_zones],
                        value='Nova Scotia',
                        clearable=False
                    )
                ], width=3),
                
                dbc.Col([
                    html.Label("Drug Type:", className="font-weight-bold"),
                    dcc.Dropdown(
                        id='drug-dropdown',
                        options=[{'label': drug, 'value': drug} for drug in drug_types],
                        value=drug_types[0] if drug_types else 'Opioid - total',
                        clearable=False
                    )
                ], width=3),
            ])
        ])
    ], className="mb-4"),
    
    # Key Statistics Cards
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="total-deaths", className="text-primary"),
                    html.P("Total Deaths", className="mb-0")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="avg-rate", className="text-success"),
                    html.P("Average Rate per 100k", className="mb-0")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="peak-year", className="text-warning"),
                    html.P("Peak Year", className="mb-0")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="trend-direction", className="text-info"),
                    html.P("Recent Trend", className="mb-0")
                ])
            ])
        ], width=3),
    ], className="mb-4"),
    
    # Main Charts Row 1
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Time Series - Deaths by Year"),
                dbc.CardBody([
                    dcc.Graph(id='time-series-chart', style={'height': '400px'})
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Health Zone Comparison"),
                dbc.CardBody([
                    dcc.Graph(id='zone-comparison-chart', style={'height': '400px'})
                ])
            ])
        ], width=6),
    ], className="mb-4"),
    
    # Main Charts Row 2
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Drug Type Distribution"),
                dbc.CardBody([
                    dcc.Graph(id='drug-distribution-chart', style={'height': '400px'})
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Manner of Death Analysis"),
                dbc.CardBody([
                    dcc.Graph(id='manner-death-chart', style={'height': '400px'})
                ])
            ])
        ], width=6),
    ], className="mb-4"),
    
    # Geographic Visualization
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Geographic Distribution - Choropleth Map"),
                dbc.CardBody([
                    html.Div(id='map-container', children=[
                        html.Iframe(id='map', width='100%', height='500'),
                    ])
                ])
            ])
        ])
    ], className="mb-4"),
    
    # Data Table
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Detailed Data View"),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='data-table',
                        columns=[
                            {"name": "Year", "id": "Year"},
                            {"name": "Health Zone", "id": "Health Zone of Residence"},
                            {"name": "Drug Type", "id": "Drug Type"},
                            {"name": "Manner of Death", "id": "Manner of Death"},
                            {"name": "Sex", "id": "Sex"},
                            {"name": "Deaths", "id": "Frequency"},
                            {"name": "Rate per 100k", "id": "Rate", "type": "numeric", "format": {"specifier": ".1f"}},
                        ],
                        style_cell={'textAlign': 'left', 'padding': '10px'},
                        style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
                        style_data={'backgroundColor': '#ffffff'},
                        page_size=10,
                        sort_action="native",
                        filter_action="native"
                    )
                ])
            ])
        ])
    ], className="mb-4"),
    
], fluid=True)

# Callback for updating key statistics
@app.callback(
    [Output('total-deaths', 'children'),
     Output('avg-rate', 'children'),
     Output('peak-year', 'children'),
     Output('trend-direction', 'children')],
    [Input('year-slider', 'value'),
     Input('zone-dropdown', 'value'),
     Input('drug-dropdown', 'value')]
)
def update_key_stats(year_range, selected_zone, selected_drug):
    if df.empty:
        return "No data", "No data", "No data", "No data"
    
    # Filter data
    filtered_df = df[
        (df['Year'] >= year_range[0]) & 
        (df['Year'] <= year_range[1]) &
        (df['Health Zone of Residence'] == selected_zone) &
        (df['Drug Type'] == selected_drug) &
        (df['Quarter'] == 'All') &
        (df['Manner of Death'] == 'All manners') &
        (df['Sex'] == 'Total')
    ]
    
    if filtered_df.empty:
        return "0", "0.0", "N/A", "N/A"
    
    total_deaths = filtered_df['Frequency'].sum()
    avg_rate = filtered_df['Rate'].mean()
    
    # Find peak year
    yearly_deaths = filtered_df.groupby('Year')['Frequency'].sum()
    peak_year = yearly_deaths.idxmax() if not yearly_deaths.empty else "N/A"
    
    # Calculate trend (last 3 years vs previous 3 years)
    recent_years = filtered_df[filtered_df['Year'] >= max(filtered_df['Year']) - 2]['Frequency'].sum()
    earlier_years = filtered_df[
        (filtered_df['Year'] >= max(filtered_df['Year']) - 5) & 
        (filtered_df['Year'] < max(filtered_df['Year']) - 2)
    ]['Frequency'].sum()
    
    if earlier_years > 0:
        trend = "↑ Increasing" if recent_years > earlier_years else "↓ Decreasing"
    else:
        trend = "→ Stable"
    
    return f"{total_deaths:,.0f}", f"{avg_rate:.1f}", str(int(peak_year)) if peak_year != "N/A" else "N/A", trend

# Callback for time series chart
@app.callback(
    Output('time-series-chart', 'figure'),
    [Input('year-slider', 'value'),
     Input('zone-dropdown', 'value'),
     Input('drug-dropdown', 'value')]
)
def update_time_series(year_range, selected_zone, selected_drug):
    if df.empty:
        return go.Figure()
    
    # Filter data for time series
    filtered_df = df[
        (df['Year'] >= year_range[0]) & 
        (df['Year'] <= year_range[1]) &
        (df['Health Zone of Residence'] == selected_zone) &
        (df['Drug Type'] == selected_drug) &
        (df['Quarter'] == 'All') &
        (df['Manner of Death'] == 'All manners') &
        (df['Sex'] == 'Total')
    ]
    
    if filtered_df.empty:
        return go.Figure()
    
    yearly_data = filtered_df.groupby('Year').agg({
        'Frequency': 'sum',
        'Rate': 'mean'
    }).reset_index()
    
    fig = go.Figure()
    
    # Add deaths line
    fig.add_trace(go.Scatter(
        x=yearly_data['Year'],
        y=yearly_data['Frequency'],
        mode='lines+markers',
        name='Deaths',
        line=dict(color=zone_colors.get(selected_zone, '#1f77b4'), width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title=f"{selected_drug} Deaths Over Time - {selected_zone}",
        xaxis_title="Year",
        yaxis_title="Number of Deaths",
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

# Callback for zone comparison chart
@app.callback(
    Output('zone-comparison-chart', 'figure'),
    [Input('year-slider', 'value'),
     Input('drug-dropdown', 'value')]
)
def update_zone_comparison(year_range, selected_drug):
    if df.empty:
        return go.Figure()
    
    # Filter data for zone comparison
    zones = ['Central', 'Eastern', 'Northern', 'Western']
    filtered_df = df[
        (df['Year'] >= year_range[0]) & 
        (df['Year'] <= year_range[1]) &
        (df['Health Zone of Residence'].isin(zones)) &
        (df['Drug Type'] == selected_drug) &
        (df['Quarter'] == 'All') &
        (df['Manner of Death'] == 'All manners') &
        (df['Sex'] == 'Total')
    ]
    
    if filtered_df.empty:
        return go.Figure()
    
    zone_data = filtered_df.groupby('Health Zone of Residence').agg({
        'Frequency': 'sum',
        'Rate': 'mean'
    }).reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=zone_data['Health Zone of Residence'],
        y=zone_data['Frequency'],
        name='Total Deaths',
        marker_color=[zone_colors.get(zone, '#1f77b4') for zone in zone_data['Health Zone of Residence']]
    ))
    
    fig.update_layout(
        title=f"{selected_drug} Deaths by Health Zone ({year_range[0]}-{year_range[1]})",
        xaxis_title="Health Zone",
        yaxis_title="Total Deaths",
        template='plotly_white'
    )
    
    return fig

# Callback for drug distribution chart
@app.callback(
    Output('drug-distribution-chart', 'figure'),
    [Input('year-slider', 'value'),
     Input('zone-dropdown', 'value')]
)
def update_drug_distribution(year_range, selected_zone):
    if df.empty:
        return go.Figure()
    
    # Filter data for drug distribution
    filtered_df = df[
        (df['Year'] >= year_range[0]) & 
        (df['Year'] <= year_range[1]) &
        (df['Health Zone of Residence'] == selected_zone) &
        (df['Quarter'] == 'All') &
        (df['Manner of Death'] == 'All manners') &
        (df['Sex'] == 'Total')
    ]
    
    if filtered_df.empty:
        return go.Figure()
    
    drug_data = filtered_df.groupby('Drug Type')['Frequency'].sum().reset_index()
    drug_data = drug_data.sort_values('Frequency', ascending=False).head(10)
    
    fig = px.pie(
        drug_data,
        values='Frequency',
        names='Drug Type',
        title=f"Drug Type Distribution - {selected_zone} ({year_range[0]}-{year_range[1]})"
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(template='plotly_white')
    
    return fig

# Callback for manner of death chart
@app.callback(
    Output('manner-death-chart', 'figure'),
    [Input('year-slider', 'value'),
     Input('zone-dropdown', 'value'),
     Input('drug-dropdown', 'value')]
)
def update_manner_death(year_range, selected_zone, selected_drug):
    if df.empty:
        return go.Figure()
    
    # Filter data for manner of death
    manners = ['Accident', 'Suicide', 'All manners']
    filtered_df = df[
        (df['Year'] >= year_range[0]) & 
        (df['Year'] <= year_range[1]) &
        (df['Health Zone of Residence'] == selected_zone) &
        (df['Drug Type'] == selected_drug) &
        (df['Quarter'] == 'All') &
        (df['Manner of Death'].isin(manners)) &
        (df['Sex'] == 'Total')
    ]
    
    if filtered_df.empty:
        return go.Figure()
    
    manner_data = filtered_df.groupby(['Year', 'Manner of Death'])['Frequency'].sum().reset_index()
    
    fig = px.line(
        manner_data,
        x='Year',
        y='Frequency',
        color='Manner of Death',
        title=f"Deaths by Manner Over Time - {selected_drug} in {selected_zone}",
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Deaths",
        template='plotly_white'
    )
    
    return fig

# Callback for map
@app.callback(
    Output('map', 'srcDoc'),
    [Input('year-slider', 'value'),
     Input('drug-dropdown', 'value')]
)
def update_map(year_range, selected_drug):
    if df.empty or geojson_data is None:
        return ""
    
    # Filter data for map
    zones = ['Central', 'Eastern', 'Northern', 'Western']
    filtered_df = df[
        (df['Year'] >= year_range[0]) & 
        (df['Year'] <= year_range[1]) &
        (df['Health Zone of Residence'].isin(zones)) &
        (df['Drug Type'] == selected_drug) &
        (df['Quarter'] == 'All') &
        (df['Manner of Death'] == 'All manners') &
        (df['Sex'] == 'Total')
    ]
    
    if filtered_df.empty:
        return ""
    
    # Aggregate data by zone
    zone_data = filtered_df.groupby('Health Zone of Residence').agg({
        'Frequency': 'sum',
        'Rate': 'mean'
    }).reset_index()
    
    # Create folium map centered on Nova Scotia
    m = folium.Map(location=[45.0, -63.0], zoom_start=7, tiles='OpenStreetMap')
    
    # Create choropleth
    folium.Choropleth(
        geo_data=geojson_data,
        name='choropleth',
        data=zone_data,
        columns=['Health Zone of Residence', 'Frequency'],
        key_on='feature.properties.name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f'{selected_drug} Deaths ({year_range[0]}-{year_range[1]})'
    ).add_to(m)
    
    # Add markers with additional information
    for _, row in zone_data.iterrows():
        zone_name = row['Health Zone of Residence']
        deaths = row['Frequency']
        rate = row['Rate']
        
        # Calculate centroid from GeoJSON data
        zone_centroid = None
        if not gdf.empty:
            zone_geom = gdf[gdf['name'] == zone_name]
            if not zone_geom.empty:
                centroid = zone_geom.geometry.centroid.iloc[0]
                zone_centroid = [centroid.y, centroid.x]  # [lat, lon]
        
        # Fallback to improved approximate coordinates if centroid calculation fails
        if zone_centroid is None:
            zone_coords = {
                'Central': [44.65, -63.60],  # Halifax area
                'Eastern': [45.70, -61.40],  # Sydney/Cape Breton area
                'Northern': [46.10, -60.80],  # Northern Cape Breton/Ingonish area
                'Western': [44.25, -65.80]   # Yarmouth/Digby area
            }
            zone_centroid = zone_coords.get(zone_name)
        
        if zone_centroid:
            folium.Marker(
                location=zone_centroid,
                popup=f"""
                <b>{zone_name} Zone</b><br>
                Total Deaths: {deaths}<br>
                Average Rate: {rate:.1f} per 100k<br>
                Period: {year_range[0]}-{year_range[1]}
                """,
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
    
    folium.LayerControl().add_to(m)
    
    return m._repr_html_()

# Callback for data table
@app.callback(
    Output('data-table', 'data'),
    [Input('year-slider', 'value'),
     Input('zone-dropdown', 'value'),
     Input('drug-dropdown', 'value')]
)
def update_data_table(year_range, selected_zone, selected_drug):
    if df.empty:
        return []
    
    # Filter data for table
    filtered_df = df[
        (df['Year'] >= year_range[0]) & 
        (df['Year'] <= year_range[1]) &
        (df['Health Zone of Residence'] == selected_zone) &
        (df['Drug Type'] == selected_drug)
    ].copy()
    
    if filtered_df.empty:
        return []
    
    # Select relevant columns and sort
    table_data = filtered_df[['Year', 'Health Zone of Residence', 'Drug Type', 
                             'Manner of Death', 'Sex', 'Frequency', 'Rate']].copy()
    table_data = table_data.sort_values(['Year', 'Manner of Death', 'Sex'], ascending=[False, True, True])
    
    return table_data.to_dict('records')

if __name__ == '__main__':
    print("Starting Nova Scotia Substance-Related Fatalities Dashboard...")
    print("Open your web browser and go to: http://127.0.0.1:8052")
    app.run(debug=True, host='0.0.0.0', port=8052)
