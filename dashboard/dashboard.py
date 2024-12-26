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
    st.header('Galvin Suryo Asmoro')
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

# -------------------- Average Bike Use Across Seasons --------------------
st.subheader('Average Bike Usage Across Seasons')
seasonal_usage = day_df.groupby('season')['cnt'].mean().reset_index()

fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(x='season', y='cnt', data=seasonal_usage, palette="Blues_d", ax=ax)
ax.set_xlabel('Season', fontsize=14)
ax.set_ylabel('Average Bike Usage', fontsize=14)
ax.set_title('Average Bike Usage Across Seasons', fontsize=16, fontweight='bold')
ax.bar_label(ax.containers[0], label_type='edge', padding=3)
ax.grid(axis='y')
st.pyplot(fig)


# -------------------- Correlation between Weather Conditions and Bike Usage across Seasons --------------------
# Function to calculate correlation between weather variables and bike usage for each season
def calculate_correlations(df, season):
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

# Plot the heatmap
st.subheader('Correlation between Weather Conditions and Bike Usage across Seasons')
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(correlations_transposed, annot=True, cmap="coolwarm", center=0, linewidths=0.5, ax=ax)

# Add titles and labels
ax.set_title('Correlation between Weather Conditions and Bike Usage across Seasons', fontsize=14)
ax.set_xlabel('Weather Conditions', fontsize=12)
ax.set_ylabel('Seasons', fontsize=12)
plt.tight_layout()

# Display the heatmap in Streamlit
st.pyplot(fig)
