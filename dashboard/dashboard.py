import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Set the default style for seaborn
sns.set(style='whitegrid')

# Load the datasets (update the paths if needed)
day_df = pd.read_csv("dashboard/day.csv")

# Convert the 'dteday' column to datetime
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

# Create helper functions to process data
def create_daily_rentals_df(df):
    """Create daily rental counts."""
    daily_rentals_df = df[['dteday', 'cnt']].groupby('dteday').sum().reset_index()
    daily_rentals_df.rename(columns={'cnt': 'total_rentals'}, inplace=True)
    return daily_rentals_df

def create_top_weather_conditions(df):
    """Get the top weather conditions based on the number of rentals."""
    top_weather_df = df.groupby('weathersit')['cnt'].sum().reset_index().sort_values(by='cnt', ascending=False)
    top_weather_df.rename(columns={'cnt': 'total_rentals'}, inplace=True)
    return top_weather_df

# Sidebar configuration with date filter
min_date = day_df['dteday'].min()
max_date = day_df['dteday'].max()

with st.sidebar:
    # Add a logo or image (optional)
    st.header('Hafizh Akbar Karimy')
    st.image("data/me.jpeg")
    
    # Date filter input
    start_date, end_date = st.date_input(
        label='Select Date Range',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter the dataframe based on the selected dates
main_df = day_df[(day_df['dteday'] >= pd.to_datetime(start_date)) & 
                 (day_df['dteday'] <= pd.to_datetime(end_date))]

# Create daily rentals dataframe for the selected date range
daily_rentals_df = create_daily_rentals_df(main_df)

# Create a summary for the entire period
total_rentals = daily_rentals_df['total_rentals'].sum()

# Header for the dashboard
st.header('Bike Sharing Data Dashboard 🚴‍♂️')

# -------------------- Correlation between Weather Conditions and Bike Usage across Seasons --------------------
st.subheader('How Correlation Across Seasons Helps Identify Bike Usage Trends Affected by Weather')
# Function to calculate correlation between weather variables and bike usage for each season
def calculate_correlations(df, season):
    """Calculate correlation between weather variables and bike usage for a given season."""
    season_data = df[df['season'] == season]
    correlations = season_data[['temp', 'hum', 'windspeed', 'cnt']].corr()['cnt'].drop('cnt')
    return correlations

# Define season mapping (assuming mapping of 1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter')
season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}

# Calculate correlations for each season
correlations_by_season = {}
for season_num, season_name in season_mapping.items():
    correlations_by_season[season_name] = calculate_correlations(day_df, season_num)

# Convert the dictionary to a DataFrame for better readability
correlations_df = pd.DataFrame(correlations_by_season)

# Transpose the correlation dataframe for better visualization (seasons as columns)
correlations_transposed = correlations_df.T

# Set up the figure for plotting
fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(
    correlations_transposed,
    annot=True,
    fmt=".2f",
    cmap="YlGnBu",
    center=0,
    linewidths=0.5,
    cbar_kws={'label': 'Correlation Coefficient'},
    ax=ax
)

# Add titles and labels
ax.set_title('Correlation between Weather Conditions and Bike Usage across Seasons', fontsize=16, fontweight='bold')
ax.set_xlabel('Weather Variables', fontsize=14)
ax.set_ylabel('Seasons', fontsize=14)

# Annotate interpretation guide
ax.text(
    3.5, -0.8, 
    "Interpretation:\n- Positive values: Higher weather variable values increase bike usage.\n"
    "- Negative values: Higher weather variable values decrease bike usage.", 
    fontsize=12, ha="center", color="gray", bbox=dict(boxstyle="round", facecolor="white", alpha=0.7)
)

# Adjust layout and show plot in Streamlit
plt.tight_layout()
st.pyplot(fig)
