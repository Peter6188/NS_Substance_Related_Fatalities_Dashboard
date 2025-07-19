import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load and process data
try:
    df = pd.read_csv('Numbers_and_rates_of_substance-related_fatalities_in_Nova_Scotia.csv')
    print("CSV loaded successfully")
    print(f"Shape: {df.shape}")
    
    # Clean and filter data
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=['Year', 'Health Zone of Residence'])
    
    # Get unique values for filters
    health_zones = sorted([zone for zone in df['Health Zone of Residence'].unique() 
                          if zone in ['Central', 'Eastern', 'Northern', 'Western', 'Nova Scotia']])
    
    # Test sex analysis function
    def test_sex_analysis(year_range, selected_zone, selected_drug):
        print(f"\nTesting: {selected_drug} in {selected_zone} for years {year_range}")
        
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
        
        print(f"Filtered data shape: {filtered_df.shape}")
        print(f"Available years: {sorted(filtered_df['Year'].unique()) if not filtered_df.empty else 'None'}")
        print(f"Available sexes: {filtered_df['Sex'].unique().tolist() if not filtered_df.empty else 'None'}")
        print(f"Sample data:")
        if not filtered_df.empty:
            print(filtered_df[['Year', 'Sex', 'Frequency']].head())
        else:
            print("No data found")
        
        return filtered_df
    
    print(f"Health Zones: {health_zones}")
    print(f"Available drug types: {df['Drug Type'].unique()}")
    
    # Test different scenarios
    test_cases = [
        ([2020, 2023], 'Nova Scotia', 'Cocaine'),
        ([2020, 2023], 'Central', 'Cocaine'),
        ([2020, 2023], 'Eastern', 'Cocaine'),
        ([2020, 2023], 'Central', 'Opioid - pharmaceutical'),
    ]
    
    for year_range, zone, drug in test_cases:
        test_sex_analysis(year_range, zone, drug)
        print("-" * 50)

except Exception as e:
    print(f"Error: {e}")
