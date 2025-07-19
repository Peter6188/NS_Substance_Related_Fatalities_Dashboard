import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
# import geopandas as gpd
# import folium
# from folium import plugins
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
    # gdf = gpd.read_file('Nova Scotia Health Authority Management Zones.geojson')
    print("GeoJSON loaded successfully")
    print(f"GeoJSON features: {len(geojson_data['features'])}")
except Exception as e:
    print(f"Error loading GeoJSON: {e}")
    geojson_data = None
    # gdf = gpd.GeoDataFrame()

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
    
    # Get drug types and exclude aggregated categories
    excluded_drug_categories = [
        'Opioid - total',
        'Total - all substances', 
        'Nonpharmaceutical drug (any)'
    ]
    all_drug_types = df['Drug Type'].unique()
    drug_types = sorted([drug for drug in all_drug_types if drug not in excluded_drug_categories])
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
    
    # Main layout with sidebar
    dbc.Row([
        # Left sidebar - Control Panel
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Control Panel", style={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'}),
                dbc.CardBody([
                    html.Label("Year Range:", className="font-weight-bold mb-2"),
                    dcc.RangeSlider(
                        id='year-slider',
                        min=min(years) if years else 2009,
                        max=max(years) if years else 2025,
                        value=[min(years) if years else 2009, max(years) if years else 2025],
                        marks={year: str(year) for year in range(min(years) if years else 2009, 
                                                               max(years) + 1 if years else 2026, 3)},
                        step=1,
                        vertical=False
                    ),
                    html.Hr(),
                    
                    html.Label("Health Zone:", className="font-weight-bold mb-2"),
                    dcc.Dropdown(
                        id='zone-dropdown',
                        options=[{'label': zone, 'value': zone} for zone in health_zones],
                        value='Nova Scotia',
                        clearable=False,
                        className="mb-3"
                    ),
                    
                    html.Label("Drug Type:", className="font-weight-bold mb-2"),
                    dcc.Dropdown(
                        id='drug-dropdown',
                        options=[{'label': drug, 'value': drug} for drug in drug_types],
                        value='Cocaine' if 'Cocaine' in drug_types else (drug_types[0] if drug_types else 'Cocaine'),
                        clearable=False,
                        className="mb-3"
                    )
                ], style={'padding': '20px'})
            ], style={'position': 'sticky', 'top': '20px'})
        ], width=3, className="mb-4"),
        
        # Right content area
        dbc.Col([
    
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
                    html.Div(id='drug-distribution-table', style={'height': '400px', 'overflow-y': 'auto'})
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Sex of Death Analysis"),
                dbc.CardBody([
                    dcc.Graph(id='sex-death-chart', style={'height': '400px'})
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
                    dcc.Graph(id='map', style={'height': '700px'})
                ])
            ])
        ])
    ], className="mb-4"),
        ], width=9)  # Close right content column
    ])  # Close main row
    
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

# Callback for drug distribution table
@app.callback(
    Output('drug-distribution-table', 'children'),
    [Input('year-slider', 'value'),
     Input('zone-dropdown', 'value')]
)
def update_drug_distribution(year_range, selected_zone):
    if df.empty:
        return html.P("No data available")
    
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
        return html.P("No data available for selected filters")
    
    # Group by drug type and filter out aggregated categories
    drug_data = filtered_df.groupby('Drug Type')['Frequency'].sum().reset_index()
    drug_data['Rate'] = filtered_df.groupby('Drug Type')['Rate'].mean().values
    
    # Remove aggregated/total categories
    excluded_categories = [
        'Opioid - total',
        'Total - all substances', 
        'Nonpharmaceutical drug (any)'
    ]
    drug_data = drug_data[~drug_data['Drug Type'].isin(excluded_categories)]
    
    drug_data = drug_data.sort_values('Frequency', ascending=False).head(15)
    
    # Calculate percentages
    total_deaths = drug_data['Frequency'].sum()
    drug_data['Percentage'] = (drug_data['Frequency'] / total_deaths * 100).round(1)
    
    # Create table
    table_header = [
        html.Thead([
            html.Tr([
                html.Th("Rank", style={'text-align': 'center', 'width': '10%'}),
                html.Th("Drug Type", style={'text-align': 'left', 'width': '50%'}),
                html.Th("Deaths", style={'text-align': 'center', 'width': '15%'}),
                html.Th("Rate per 100k", style={'text-align': 'center', 'width': '15%'}),
                html.Th("Percentage", style={'text-align': 'center', 'width': '10%'})
            ])
        ], style={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'})
    ]
    
    table_body = [
        html.Tbody([
            html.Tr([
                html.Td(str(i+1), style={'text-align': 'center', 'fontWeight': 'bold'}),
                html.Td(row['Drug Type'], style={'text-align': 'left'}),
                html.Td(f"{int(row['Frequency']):,}", style={'text-align': 'center'}),
                html.Td(f"{row['Rate']:.1f}", style={'text-align': 'center'}),
                html.Td(f"{row['Percentage']:.1f}%", style={'text-align': 'center'})
            ], style={'borderBottom': '1px solid #dee2e6'}) 
            for i, (_, row) in enumerate(drug_data.iterrows())
        ])
    ]
    
    return [
        html.H6(f"Drug Type Distribution - {selected_zone} ({year_range[0]}-{year_range[1]})", 
               className="text-center mb-3"),
        dbc.Table(
            table_header + table_body,
            bordered=True,
            hover=True,
            responsive=True,
            striped=True,
            style={'fontSize': '0.9rem'}
        )
    ]

# Callback for sex of death chart
@app.callback(
    Output('sex-death-chart', 'figure'),
    [Input('year-slider', 'value'),
     Input('zone-dropdown', 'value'),
     Input('drug-dropdown', 'value')]
)
def update_sex_death(year_range, selected_zone, selected_drug):
    if df.empty:
        return go.Figure()
    
    # Filter data for sex analysis
    sexes = ['Male', 'Female']
    filtered_df = df[
        (df['Year'] >= year_range[0]) & 
        (df['Year'] <= year_range[1]) &
        (df['Health Zone of Residence'] == selected_zone) &
        (df['Drug Type'] == selected_drug) &
        (df['Quarter'] == 'All') &
        (df['Manner of Death'] == 'All manners') &
        (df['Sex'].isin(sexes))
    ]
    
    if filtered_df.empty:
        return go.Figure()
    
    sex_data = filtered_df.groupby(['Year', 'Sex'])['Frequency'].sum().reset_index()
    
    fig = px.line(
        sex_data,
        x='Year',
        y='Frequency',
        color='Sex',
        title=f"Deaths by Sex Over Time - {selected_drug} in {selected_zone}",
        markers=True,
        color_discrete_map={'Male': '#1f77b4', 'Female': '#ff7f0e'}
    )
    
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Deaths",
        template='plotly_white'
    )
    
    return fig

# Callback for map
@app.callback(
    Output('map', 'figure'),
    [Input('year-slider', 'value'),
     Input('drug-dropdown', 'value')]
)
def update_map(year_range, selected_drug):
    if df.empty:
        return go.Figure()
    
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
        return go.Figure()
    
    # Aggregate data by zone
    zone_data = filtered_df.groupby('Health Zone of Residence').agg({
        'Frequency': 'sum',
        'Rate': 'mean'
    }).reset_index()
    
    # Create Plotly choropleth map using the GeoJSON data
    if geojson_data is not None:
        # Create a mapping from zone names to match GeoJSON properties
        zone_name_mapping = {
            'Central': 'Central',
            'Eastern': 'Eastern', 
            'Northern': 'Northern',
            'Western': 'Western'
        }
        
        # Prepare data for choropleth
        locations = []
        z_values = []
        hover_text = []
        
        for _, row in zone_data.iterrows():
            zone_name = row['Health Zone of Residence']
            if zone_name in zone_name_mapping:
                locations.append(zone_name_mapping[zone_name])
                z_values.append(row['Rate'])
                hover_text.append(f"<b>{zone_name}</b><br>Total Deaths: {row['Frequency']}<br>Rate per 100k: {row['Rate']:.1f}")
        
        # Create choropleth figure
        fig = go.Figure(go.Choroplethmapbox(
            geojson=geojson_data,
            locations=locations,
            z=z_values,
            colorscale='YlOrRd',
            hovertemplate='%{hovertext}<extra></extra>',
            hovertext=hover_text,
            marker_opacity=0.7,
            marker_line_width=1,
            featureidkey="properties.name"
        ))
        
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox=dict(
                center=go.layout.mapbox.Center(lat=45.0, lon=-63.0),
                zoom=6
            ),
            margin={"r":0,"t":0,"l":0,"b":0},
            title=f'{selected_drug} Rate per 100k Population ({year_range[0]}-{year_range[1]})',
            title_x=0.5
        )
        
        return fig
    else:
        # Fallback to bar chart if no geojson
        fig = px.bar(
            zone_data,
            x='Health Zone of Residence',
            y='Rate',
            title=f"{selected_drug} Rate by Health Zone ({year_range[0]}-{year_range[1]})",
            color='Rate',
            color_continuous_scale='YlOrRd'
        )
        fig.update_layout(
            xaxis_title="Health Zone",
            yaxis_title="Rate per 100k Population"
        )
        return fig

if __name__ == '__main__':
    print("Starting Nova Scotia Substance-Related Fatalities Dashboard...")
    print("Open your web browser and go to: http://127.0.0.1:8059")
    app.run(debug=True, host='0.0.0.0', port=8059)
