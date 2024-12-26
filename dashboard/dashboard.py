import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import os

# Set the default style for seaborn
sns.set(style='ticks')

# ----- Pastikan Path File Benar -----
file_path = "dashboard/day.csv"  # Update path jika file berada di lokasi berbeda
if not os.path.exists(file_path):
    st.error(f"File tidak ditemukan di path: {file_path}")
    raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

# Load the datasets
day_df = pd.read_csv(file_path)

# Convert the 'dteday' column to datetime
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

# Create helper functions to process data
def create_daily_rentals_df(df):
    """Create daily rental counts."""
    daily_rentals_df = df[['dteday', 'cnt']].groupby('dteday').sum().reset_index()
    daily_rentals_df.rename(columns={'cnt': 'total_rentals'}, inplace=True)
    return daily_rentals_df

# Sidebar configuration with date filter
min_date = day_df['dteday'].min()
max_date = day_df['dteday'].max()

with st.sidebar:
    st.subheader('Galvin Suryo Asmoro')
    st.header('Bike Sharing Dashboard')
    st.markdown("""
    **Explore bike-sharing data** with insights on seasonality, weather effects, and trends over time.
    """)

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
st.title('Bike Sharing Dashboard 🚲')
st.markdown("""
Discover insights on bike-sharing trends, seasonality effects, and weather influences using this interactive dashboard.
""")

# -------------------- Average Bike Use Across Seasons --------------------
st.subheader('1. Average Bike Usage Across Seasons')
seasonal_usage = day_df.groupby('season')['cnt'].mean().reset_index()

fig, ax = plt.subplots(figsize=(8, 6))
palette = sns.color_palette("mako", len(seasonal_usage))
sns.barplot(x='season', y='cnt', data=seasonal_usage, palette=palette, ax=ax)
ax.set_xlabel('Season', fontsize=14)
ax.set_ylabel('Average Rentals', fontsize=14)
ax.set_title('Average Rentals by Season', fontsize=16, fontweight='bold')
for container in ax.containers:
    ax.bar_label(container, fmt='%.0f', padding=5, fontsize=10, color='black')
sns.despine()
st.pyplot(fig)

# -------------------- Correlation between Weather Conditions and Bike Usage across Seasons --------------------
def calculate_correlations(df, season):
    """Calculate correlations for a given season."""
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
st.subheader('2. Correlation between Weather and Rentals by Season')
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(correlations_transposed, annot=True, cmap="viridis", linewidths=0.5, ax=ax)
ax.set_title('Weather and Rentals Correlation by Season', fontsize=16, fontweight='bold')
ax.set_xlabel('Weather Variables', fontsize=14)
ax.set_ylabel('Seasons', fontsize=14)
plt.tight_layout()
st.pyplot(fig)

# Descriptive Text Below Heatmap
st.markdown("""
**Interpretation:**
- Positive correlations indicate that higher values of the weather variable lead to higher rentals.
- Negative correlations suggest the opposite.
""")
