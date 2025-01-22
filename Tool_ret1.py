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

# Categorize each variable into percentiles (quintiles)
def categorize_percentiles(df, variables):
    for var in variables:
        if var in df.columns:
            if var == "Pollution":
                df[f"{var}_Category"] = pd.qcut(
                    df[var].rank(method='min', ascending=False, na_option='bottom'),
                    5, labels=[5, 4, 3, 2, 1]  # 1 = Cleanest, 5 = Most Polluted
                )
            else:
                df[f"{var}_Category"] = pd.qcut(
                    df[var].rank(method='first', ascending=True, na_option='bottom'),
                    5, labels=[5, 4, 3, 2, 1]  # 1 = Best, 5 = Worst
                )
    return df

data = categorize_percentiles(data, list(column_mapping.values()))

# Title for the Tool
st.title("Best Countries for Early Retirement: Where to Retire Abroad?")

# ✅ **Instructions**
st.write("### Instructions for Using the Tool")
instructions = """
- This tool helps users find the **most suitable country for retirement** abroad.  
- On the left panel, select the key **variables** that are most relevant to you.  
- **Use the sliders** to filter out poor-performing countries. Moving from 5 to 1 removes the worst-performing ones.  
- The **Retirement Suitability score** is based on the selected variables.  
- The **figure plots Suitability vs. Cost of Living (COL)** to help find good candidate countries.  
- **Use the map below** to explore how different variables are distributed geographically.  
- **Data is from Numbeo (2025)**, except Political Stability, sourced from the **World Bank Governance Indicators (2023)**.
"""
st.write(instructions)

# Sidebar Filters
st.sidebar.subheader("Select Variables for Retirement Suitability")
selected_vars = []
sliders = {}
variables = list(column_mapping.values())

for label in variables:
    if st.sidebar.checkbox(label, value=True):
        sliders[label] = st.sidebar.slider(f"{label}", 1, 5, 5, format=None)
        selected_vars.append(label)

if selected_vars:
    df_selected = data[['Country', 'Col_2025', 'Continent'] + selected_vars + [f"{var}_Category" for var in selected_vars]].dropna()

    for var in selected_vars:
        max_category = sliders[var]  
        df_selected = df_selected[df_selected[f"{var}_Category"].astype(int) <= max_category]

    df_selected['Retirement Suitability'] = df_selected[selected_vars].mean(axis=1)

    # Scatter Plot
    fig_scatter = px.scatter(
        df_selected, x="Retirement Suitability", y="Col_2025", text="Country", color=df_selected['Continent'],
        title="Retirement Suitability vs Cost of Living", template="plotly_dark"
    )

    fig_scatter.update_traces(marker=dict(size=11), textposition='top center')

    st.plotly_chart(fig_scatter, use_container_width=True)

    # Map
    st.write("### Geographic Distribution of Retirement Suitability")
    selected_map_var = st.selectbox("", selected_vars)
    fig_map = px.choropleth(df_selected, locations="Country", locationmode="country names", color=selected_map_var)
    st.plotly_chart(fig_map, use_container_width=True)



