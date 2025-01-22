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
                # Invert Pollution so lower values are better
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

# Instructions Section
st.write("### Instructions for Using the Tool")
instructions = """
- This tool aims to help users find the **most suitable country for retirement** abroad.  
- On the left panel, you can **select the key variables** that are most relevant to you. For instance, if pollution is not a factor you want to consider, then unclick it.  
- **Use the sliders to filter out** poor-performing countries for certain variables. For example, if we move Safety from 5 to 4, it will drop the worst-performing countries for this variable. If we move it all the way to 1, it will only keep a handful of extremely safe countries.  
- The tool calculates a **Retirement Suitability** score based on the average across the selected variables.  
- The **Figure plots the Retirement Suitability** score against **cost of living (COL)** to help users identify good candidate countries.    
- Hover over the top right of the figure and use the **zoom tool** (draw a square on the figure), zoom in/out, pan, and other functions to better visualize your countries of interest.
- Click on the **legend's continents** to remove groups of countries.
- **Example**: Imagine we want very strict criteria across most variariables, and set Safety (2), Healthcare (2), Political stability (2), Pollution (2), Climate (3). We have only 6 countries complying with this criteria. We can observe that Spain, Portugal, and Japan are good candidates under this criteria that also have a relatively low COL.
- The **map below** helps visualize how the different underlying variables of the Retirement Suitability score are distributed geographically. For example, how Safety or Healthcare compares across countries.
- **Data is from Numbeo (2025)**, with the exception of Political stability, which is an aggregate score of the World Bank's World Governance Indicators (2023): Voice and accountability; political stability and absence of violence/terrorism; government effectiveness; regulatory quality; rule of law; and control of corruption.
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
        title="Retirement Suitability vs Cost of Living", labels={"Col_2025": "Cost of Living", "Retirement Suitability": "Retirement Suitability"},
        template="plotly_dark", category_orders={"Continent": ["America", "Europe", "Asia", "Africa", "Oceania"]},
        hover_data={var: ':.2f' for var in selected_vars}
    )

    fig_scatter.update_traces(marker=dict(size=8), textposition='top center')

    fig_scatter.update_layout(
        title=dict(text="Retirement Suitability vs Cost of Living", font=dict(color='white', size=24), x=0.5, xanchor="center"),
        xaxis=dict(linecolor='white', tickfont=dict(color='white'), showgrid=True, 
           gridcolor='rgba(255, 255, 255, 0.3)', gridwidth=1, griddash="dash"),
        yaxis=dict(linecolor='white', tickfont=dict(color='white'), showgrid=True, 
           gridcolor='rgba(255, 255, 255, 0.3)', gridwidth=1, griddash="dash"),
        legend=dict(font=dict(color="white")),
        paper_bgcolor='black', plot_bgcolor='black'
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

    # Map Visualization
    st.write("### Understand the spatial distribution of the variables that make up the Retirement Suitability")
    selected_map_var = st.selectbox("", selected_vars)
    
    fig_map = px.choropleth(df_selected, locations="Country", locationmode="country names", color=selected_map_var, color_continuous_scale="RdYlGn")
    
    st.plotly_chart(fig_map, use_container_width=True)



