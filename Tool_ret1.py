import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Load dataset
@st.cache_data
def load_data():
    file_path = "/Users/David/Dropbox/Mac/Desktop/Personal/Blog/Tool/Retire_country/Ret_data.xlsx"
    xls = pd.ExcelFile(file_path)
    df = pd.read_excel(xls, sheet_name="Country")
    return df

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
            df[f"{var}_Category"] = pd.qcut(df[var].rank(method='min', na_option='bottom'), 5, labels=[1, 2, 3, 4, 5])
    return df

data = categorize_percentiles(data, list(column_mapping.values()))

# Title for the Tool
st.title("Best Countries for Early Retirement: Where to Retire Abroad?")

# Instructions Section
st.write("### Instructions for Using the Tool")
instructions = """
- This tool aims to help users find the **most suitable country for retirement** abroad.  
- On the left panel, you can **select the key variables** that are most relevant to you. For instance, if pollution is not a factor you want to consider, then unclick it.  
- **Use the sliders to filter out** poor-performing countries for certain variables. Moving from 5 to 1 removes the lowest-ranked countries in the selected criteria.  
- The tool calculates a **Retirement Suitability** score based on the average across the selected variables.  
- The **Figure plots the Retirement Suitability** score against **cost of living (COL)** to help users identify good candidate countries.  
- The **map below** helps visualize how the different underlying variables of the Retirement Suitability index are distributed geographically.  
- **Data is from Numbeo (2025)**, with the exception of Political Stability, which is an aggregate score of the World Bank's Governance Indicators.
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

    # Reorder hover data so "Country" appears first
    hover_data = {"Country": True, "Retirement Suitability": ':.2f', "Col_2025": ':.2f'}
    hover_data.update({var: ':.2f' for var in selected_vars})

    # Scatter Plot
    fig_scatter = px.scatter(
        df_selected, x="Retirement Suitability", y="Col_2025", text="Country", color=df_selected['Continent'],
        title="Retirement Suitability vs Cost of Living", labels={"Col_2025": "Cost of Living", "Retirement Suitability": "Retirement Suitability"},
        template="plotly_dark", category_orders={"Continent": ["America", "Europe", "Asia", "Africa", "Oceania"]},
        hover_data=hover_data
    )

    fig_scatter.update_traces(marker=dict(size=9), textposition='top center')

    fig_scatter.update_layout(
        title=dict(
            text="Retirement Suitability vs Cost of Living",
            font=dict(color='white', size=24),
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(linecolor='white', showgrid=True, gridcolor='rgba(255, 255, 255, 0.3)', gridwidth=1, mirror=False, showline=True, zeroline=False),
        yaxis=dict(linecolor='white', showgrid=True, gridcolor='rgba(255, 255, 255, 0.3)', gridwidth=1, mirror=False, showline=True, zeroline=False),
        legend=dict(font=dict(color="white")),
        paper_bgcolor='black',
        plot_bgcolor='black'
    )

    # Restore dashed gridlines
    fig_scatter.update_xaxes(showgrid=True, gridcolor='rgba(255, 255, 255, 0.3)', gridwidth=1, dash='dash')
    fig_scatter.update_yaxes(showgrid=True, gridcolor='rgba(255, 255, 255, 0.3)', gridwidth=1, dash='dash')

    st.plotly_chart(fig_scatter, use_container_width=True)

    # Restore the map
    st.write("### Understand the spatial distribution of the variables that make up the Retirement Suitability")
    selected_map_var = st.selectbox("", selected_vars)
    
    fig_map = px.choropleth(df_selected, locations="Country", locationmode="country names", color=selected_map_var,
                            color_continuous_scale="RdYlGn", hover_data={selected_map_var: ':.2f'})

    st.plotly_chart(fig_map, use_container_width=True)

