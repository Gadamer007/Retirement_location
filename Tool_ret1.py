import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests
from io import BytesIO

# Load dataset
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Gadamer007/Retirement_location/main/Ret_data.xlsx"  # GitHub raw URL
    
    # Download the file content from GitHub
    response = requests.get(url)
    response.raise_for_status()  # Ensure we stop on bad responses (e.g., 404)

    # Load the Excel file into Pandas from the downloaded content
    df = pd.read_excel(BytesIO(response.content), sheet_name="Country")
    return df

# Load the data
data = load_data()
data['Country'] = data['Country'].str.strip().str.title()

# Standardize column names
column_mapping = {
    "Safety index_2025": "Safety",
    "Healthcare_2025": "Healthcare",
    "Political stability_2023": "Political Stability",
    "Pollution_2025": "Pollution",
    "Climate_2025": "Climate"
}
data = data.rename(columns=column_mapping)

# Define country-to-continent mapping
continent_mapping = {
    'United States': 'America', 'Canada': 'America', 'Mexico': 'America', 'Brazil': 'America',
    'Argentina': 'America', 'Chile': 'America', 'Colombia': 'America', 'Peru': 'America', 'Uruguay': 'America',
    'Costa Rica': 'America', 'Panama': 'America', 'Trinidad And Tobago': 'America', 'Puerto Rico': 'America',
    'Dominican Republic': 'America', 'Paraguay': 'America', 'Ecuador': 'America', 'Venezuela': 'America',
    'South Africa': 'Africa', 'Egypt': 'Africa', 'Nigeria': 'Africa', 'Kenya': 'Africa', 'Morocco': 'Africa',
    'Mauritius': 'Africa', 'Tunisia': 'Africa', 'Ghana': 'Africa', 'Uganda': 'Africa', 'Algeria': 'Africa',
    'Libya': 'Africa', 'Zimbabwe': 'Africa',
    'China': 'Asia', 'Japan': 'Asia', 'India': 'Asia', 'South Korea': 'Asia', 'Thailand': 'Asia',
    'Singapore': 'Asia', 'Malaysia': 'Asia', 'Israel': 'Asia', 'Taiwan': 'Asia', 'Jordan': 'Asia',
    'Kazakhstan': 'Asia', 'Lebanon': 'Asia', 'Armenia': 'Asia', 'Iraq': 'Asia', 'Uzbekistan': 'Asia',
    'Vietnam': 'Asia', 'Philippines': 'Asia', 'Kyrgyzstan': 'Asia', 'Bangladesh': 'Asia', 'Iran': 'Asia',
    'Nepal': 'Asia', 'Sri Lanka': 'Asia', 'Pakistan': 'Asia', 'Kuwait': 'Asia', 'Turkey': 'Asia',
    'Indonesia': 'Asia', 'United Arab Emirates': 'Asia', 'Saudi Arabia': 'Asia', 'Bahrain': 'Asia',
    'Qatar': 'Asia', 'Oman': 'Asia', 'Azerbaijan': 'Asia',
    'Germany': 'Europe', 'France': 'Europe', 'United Kingdom': 'Europe', 'Italy': 'Europe', 'Spain': 'Europe',
    'Netherlands': 'Europe', 'Sweden': 'Europe', 'Denmark': 'Europe', 'Norway': 'Europe', 'Ireland': 'Europe',
    'Finland': 'Europe', 'Belgium': 'Europe', 'Austria': 'Europe', 'Switzerland': 'Europe', 'Luxembourg': 'Europe',
    'Czech Republic': 'Europe', 'Slovenia': 'Europe', 'Estonia': 'Europe', 'Poland': 'Europe', 'Malta': 'Europe',
    'Croatia': 'Europe', 'Lithuania': 'Europe', 'Slovakia': 'Europe', 'Latvia': 'Europe', 'Portugal': 'Europe',
    'Bulgaria': 'Europe', 'Hungary': 'Europe', 'Romania': 'Europe', 'Greece': 'Europe', 'Montenegro': 'Europe',
    'Serbia': 'Europe', 'Bosnia And Herzegovina': 'Europe', 'North Macedonia': 'Europe', 'Albania': 'Europe',
    'Moldova': 'Europe', 'Belarus': 'Europe', 'Georgia': 'Europe', 'Ukraine': 'Europe', 'Russia': 'Europe',
    'Cyprus': 'Europe', 'Kosovo (Disputed Territory)': 'Europe', 'Australia': 'Oceania', 'New Zealand': 'Oceania'
}

# Assign continent
data['Continent'] = data['Country'].map(continent_mapping)

# **Rank Normalize Data (0-1)**
for var in column_mapping.values():
    if var in data.columns:
        data[var] = (data[var] - data[var].min()) / (data[var].max() - data[var].min())

# Sidebar Filters
st.sidebar.subheader("Select Variables for Retirement Suitability")
selected_vars = []
sliders = {}

for label in column_mapping.values():
    if st.sidebar.checkbox(label, value=True):
        sliders[label] = st.sidebar.slider(f"{label}", 0.0, 1.0, 1.0, step=0.05)
        selected_vars.append(label)

if selected_vars:
    df_selected = data[['Country', 'Col_2025', 'Continent'] + selected_vars].dropna()

    for var in selected_vars:
        max_value = sliders[var]
        df_selected = df_selected[df_selected[var] <= max_value]

    df_selected['Retirement Suitability'] = df_selected[selected_vars].mean(axis=1)

    # Scatter Plot
    fig_scatter = px.scatter(
        df_selected, x="Retirement Suitability", y="Col_2025", text="Country", color=df_selected['Continent'],
        title="Retirement Suitability vs Cost of Living",
        labels={
            "Col_2025": "Cost of Living (0 - 1)",
            "Retirement Suitability": "Retirement Suitability (0 - 1)"
        },
        template="plotly_dark",
        hover_data={var: ':.2f' for var in selected_vars}  # Show individual variable scores
    )

    fig_scatter.update_traces(marker=dict(size=6), textposition='top center')

    fig_scatter.update_layout(
        title=dict(text="Retirement Suitability vs Cost of Living", font=dict(color='white', size=24), x=0.5, xanchor="center"),
        xaxis=dict(
            title="Retirement Suitability (0 - 1)", range=[0, 1], linecolor='white', tickfont=dict(color='white'), 
            showgrid=True, gridcolor='rgba(255, 255, 255, 0.3)', gridwidth=1, griddash="dash"
        ),
        yaxis=dict(
            title="Cost of Living (0 - 1)", range=[0, 1], linecolor='white', tickfont=dict(color='white'), 
            showgrid=True, gridcolor='rgba(255, 255, 255, 0.3)', gridwidth=1, griddash="dash"
        ),
        legend=dict(font=dict(color="white")),
        paper_bgcolor='black', plot_bgcolor='black'
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

    # **Map Visualization**
    st.write("### Understand the spatial distribution of the variables that make up the Retirement Suitability")
    selected_map_var = st.selectbox("Select Variable to View on Map", selected_vars)
    
    fig_map = px.choropleth(
        df_selected, locations="Country", locationmode="country names", color=selected_map_var, 
        color_continuous_scale="RdYlGn", hover_data={selected_map_var: ':.2f'}
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
