import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import os

# Set the default style for seaborn
sns.set(style='ticks')

# Mendapatkan path direktori saat ini
current_dir = os.path.dirname(os.path.abspath(__file__))

# Menggabungkan path dengan nama file
file_path = os.path.join(current_dir, 'day.csv')

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

# -------------------- How Correlation Across Seasons Helps Identify Bike Usage Trends --------------------
st.subheader('1.  Visualisasi korelasi antar musim membantu mengidentifikasi tren penggunaan sepeda yang dipengaruhi cuaca')

# Define season mapping (assuming mapping of 1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter')
season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}

# Function to calculate correlation between weather variables and bike usage for each season
def calculate_correlations(df, season):
    """Calculate correlation between weather variables and bike usage for a given season."""
    season_data = df[df['season'] == season]
    correlations = season_data[['temp', 'hum', 'windspeed', 'cnt']].corr()['cnt'].drop('cnt')
    return correlations

# Calculate correlations for each season
correlations_by_season = {}
for season_num, season_name in season_mapping.items():
    correlations_by_season[season_name] = calculate_correlations(day_df, season_num)

# Convert the dictionary to a DataFrame for better readability
correlations_df = pd.DataFrame(correlations_by_season)

# Transpose the correlation dataframe for better visualization (seasons as columns)
correlations_transposed = correlations_df.T


# -------------------- How Does Bike Usage Vary Across Seasons --------------------
st.subheader('2. Pola penggunaan sepeda di setiap musim')

# Plot the results using Streamlit
fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(x='season_name', y='cnt', data=average_usage_by_season, palette='viridis', ax=ax)


ax.set_title('Average Bike Usage by Season', fontsize=16, fontweight='bold')
ax.set_xlabel('Season', fontsize=14)
ax.set_ylabel('Average Bike Usage', fontsize=14)

# Show values on top of the bars
for i, value in enumerate(average_usage_by_season['cnt']):
    ax.text(i, value + 50, f'{value:.0f}', ha='center', fontsize=12)

# Adjust layout and show the plot in Streamlit
plt.tight_layout()
st.pyplot(fig)


# Plot the heatmap
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

# Define the season mapping
season_mapping = {1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'}

# Add a column for season names
day_df['season_name'] = day_df['season'].replace(season_mapping)

# Group the data by season and calculate the average bike usage
average_usage_by_season = day_df.groupby('season_name')['cnt'].mean().reset_index()

# Sort the seasons in order (if needed)
season_order = ['Winter', 'Spring', 'Summer', 'Fall']
average_usage_by_season['season_name'] = pd.Categorical(average_usage_by_season['season_name'], categories=season_order, ordered=True)
average_usage_by_season = average_usage_by_season.sort_values('season_name')



