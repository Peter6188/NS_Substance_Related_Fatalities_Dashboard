# Nova Scotia Substance-Related Fatalities Dashboard

This interactive dashboard provides comprehensive visualizations of substance-related fatalities data in Nova Scotia from 2009 to 2025, using data from the Nova Scotia Medical Examiner Service.

## Features

### 1. Interactive Controls
- **Year Range Slider**: Select the time period for analysis
- **Health Zone Dropdown**: Choose specific zones (Central, Eastern, Northern, Western, or Nova Scotia overall)
- **Drug Type Dropdown**: Select specific substance types for focused analysis

### 2. Key Statistics Cards
- **Total Deaths**: Aggregate count for selected filters
- **Average Rate per 100k**: Population-adjusted rate
- **Peak Year**: Year with highest death count
- **Recent Trend**: Direction of change in recent years

### 3. Visualizations

#### Time Series Chart
- Shows deaths over time for selected parameters
- Helps identify trends and patterns
- Interactive with hover information

#### Health Zone Comparison
- Bar chart comparing total deaths across health zones
- Color-coded by zone for easy identification
- Useful for understanding geographic distribution

#### Drug Type Distribution
- Pie chart showing breakdown by substance type
- Top 10 drug types displayed
- Percentages and labels for clear understanding

#### Manner of Death Analysis
- Line chart showing trends by manner (Accident, Suicide, All manners)
- Helps understand the nature of fatalities over time

#### Geographic Choropleth Map
- Interactive map showing geographic distribution
- Color intensity represents death counts
- Popup markers with detailed zone information
- Built using Folium for rich interactivity

#### Detailed Data Table
- Filterable and sortable data view
- Export functionality for further analysis
- Shows all relevant columns with proper formatting

### 4. Data Sources

1. **CSV Data**: `Numbers_and_rates_of_substance-related_fatalities_in_Nova_Scotia.csv`
   - Contains detailed fatality records with demographics, substances, and rates
   - Data current as of July 1, 2025
   - Includes both confirmed and probable toxicity deaths

2. **Geographic Data**: `Nova Scotia Health Authority Management Zones.geojson`
   - Boundary data for the four health management zones
   - Used for choropleth mapping and geographic analysis

### 5. Technical Implementation

- **Framework**: Dash with Bootstrap components for responsive design
- **Visualization**: Plotly for interactive charts
- **Mapping**: Folium for geographic visualizations
- **Data Processing**: Pandas for data manipulation
- **Geographic Processing**: GeoPandas for spatial data

### 6. Running the Dashboard

1. Install required packages:
   ```bash
   pip install dash plotly pandas folium geopandas dash-bootstrap-components geojson
   ```

2. Run the application:
   ```bash
   python dashboard.py
   ```

3. Open your web browser and navigate to: `http://127.0.0.1:8050`

### 7. Data Considerations

- Data are provisional and subject to change
- Some case investigations remain ongoing
- Probable deaths may be reclassified in future releases
- Substance categories are not mutually exclusive
- Geographic coding may result in zone reclassifications
- Population data updated with latest Statistics Canada figures

### 8. Usage Tips

- Use the time slider to focus on specific periods
- Compare zones using the zone comparison chart
- Examine drug-specific trends by changing the drug type filter
- Hover over chart elements for detailed information
- Use the data table for detailed examination of specific records
- The map provides geographic context for the data patterns

This dashboard enables public health officials, researchers, and policymakers to explore patterns in substance-related fatalities and make data-driven decisions for intervention and prevention strategies.
# NS_Substance_Related_Fatalities_Dashboard
