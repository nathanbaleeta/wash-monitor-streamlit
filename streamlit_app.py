import streamlit as st
import pandas as pd
import altair as alt
import duckdb


st.title("WASH Global Monitor")
st.write("A global dashboard for tracking water, sanitation and hygiene (WASH) trends")

st.set_page_config(
    # Title and icon for the browser's tab bar:
    page_title="Global WASH Monitor",
    page_icon="🌦️",
    # Make the content take up the width of the page:
    layout="wide",
)

# Store the raw URL in a variable
API_ENDPOINT = 'https://raw.githubusercontent.com/nathanbaleeta/wash-monitor-streamlit/refs/heads/main/datasets/combined_service_level_data.csv'

# Function to fetch data from the API
# Cache the data to prevent re-fetching on every rerun
@st.cache_data 
def get_raw_data(url) -> pd.DataFrame:
    try:
        # Read the CSV data directly into a DataFrame
        data = pd.read_csv(url)
        
        # convert year into date like object
        data['date'] = pd.to_datetime(data['year'], format='%Y')
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Aggregate data and return summarized polars dataframe  
# def aggregate_service_type(data) -> pd.DataFrame:
#     return duckdb.query("""
#                               SELECT year, service_type, COUNT(service_type) AS service_type_count
#                               FROM data
#                               GROUP BY year, service_type
#                               ORDER BY year ASC
#                               -- LIMIT 100
#                               """).to_df()

# def aggregate_service_level(data) -> pd.DataFrame:
#     return duckdb.query("""
#                               SELECT year, service_level, COUNT(service_level) AS service_level_count
#                               FROM data
#                               GROUP BY year, service_level
#                               ORDER BY year ASC
#                               -- LIMIT 100
#                               """).to_df()

def aggregate_service_type(data) -> pd.DataFrame:
    result = (
        data.groupby(['year', 'service_type'])['service_type']
        .count()
        .reset_index(name='service_type_count')
        .sort_values(by='year', ascending=True)
    )
    return result

def aggregate_service_level(data) -> pd.DataFrame:
    result = (
        data.groupby(['year', 'service_level'])['service_level']
        .count()
        .reset_index(name='service_level_count')
        .sort_values(by='year', ascending=True)
    )
    return result

#############################################################################
# ETL pipeline                                                              #
#############################################################################
api_data = get_raw_data(API_ENDPOINT)

aggregated_data_service_type = aggregate_service_type(api_data)

aggregated_data_service_level = aggregate_service_level(api_data)



overview, country = st.tabs(["Overview", "Country"], on_change="rerun")

with overview:
    cols = st.columns([3, 2])

    with cols[0].container(border=True, height="stretch"):
        st.altair_chart(
            alt.Chart(aggregated_data_service_type).mark_bar(size=20).encode(
                x=alt.X('year', axis=alt.Axis(title='Year', format='d')),
                y='service_type_count',
                #color='service_type',
                color=alt.Color('service_type', legend=alt.Legend(title='Service type')),
            ).properties(
                width=1000,
                title='Service Type breakdown Totals Over Time (2000-2024)'
            ).configure_legend(orient="bottom")
        )

    with cols[1].container(border=True, height="stretch"):
        st.altair_chart(
            alt.Chart(aggregated_data_service_type).mark_line(size=1).encode(
                x=alt.X('year', axis=alt.Axis(title='Year', format='d')),
                y='service_type_count',
                color='service_type',
            ).properties(
                width=1000,
                title='Service Level Performance (2000-2024)'
            ).configure_legend(orient="bottom")
        )

    cols = st.columns([3, 2])

    with cols[0].container(border=True, height="stretch"):
        st.altair_chart(
            alt.Chart(aggregated_data_service_level).mark_bar(size=20).encode(
                x=alt.X('year', axis=alt.Axis(title='Year', format='d')),
                y='service_level_count',
                #color='service_level',
                color=alt.Color('service_level', legend=alt.Legend(title='Service level')),
            ).properties(
                width=1000,
                title='Service Type breakdown Totals Over Time (2000-2024)'
            ).configure_legend(orient="bottom")
        )

    with cols[1].container(border=True, height="stretch"):
        st.altair_chart(
            alt.Chart(aggregated_data_service_level).mark_line(size=1).encode(
                x=alt.X('year', axis=alt.Axis(title='Year', format='d')),
                y='service_level_count',
                color='service_level',
            ).properties(
                width=1000,
                title='Service Level Performance (2000-2024)'
            ).configure_legend(orient="bottom")
        )


with country:
    st.write("Coming soon")
    

if overview.open:
    options = []
    cat_color = st.sidebar.selectbox("Select Country?", options, disabled=True)
if country.open:
    options = ["Nigeria", "Uganda", "Zambia"]
    dog_color = st.sidebar.selectbox("Select Country?", options)