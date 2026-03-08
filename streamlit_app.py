import streamlit as st
import pandas as pd
import polars as pl
import altair as alt


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
    
# Convert polars summary to a pandas DataFrame
def convert_pl_to_pd(df_polars) -> pd.DataFrame:
    df_pandas = df_polars.to_pandas()
    return df_pandas

# Aggregate data and return summarized polars dataframe  
def aggregate_records(data, **kwargs) -> pd.DataFrame:
    col_name = kwargs.get('col_name') 
    col_name_alias = kwargs.get('col_name_alias') 
    group_by_key = kwargs.get('group_by_key') 
    sort_key = kwargs.get('sort_key') 

    df_polars = pl.from_pandas(data)

    df_agg_service_type_polars = df_polars.group_by([group_by_key, col_name]).agg(
                  pl.col(col_name).count().alias(col_name_alias),
              ).sort([sort_key], descending=[False])
    data = convert_pl_to_pd(df_agg_service_type_polars)
    return data



#############################################################################
# ETL pipeline                                                              #
#############################################################################
api_data = get_raw_data(API_ENDPOINT)

aggregated_data_service_type = aggregate_records(api_data, group_by_key="year", \
                                                 sort_key="year", \
                                                 col_name="service_type", \
                                                 col_name_alias="service_type_count")

aggregated_data_service_level = aggregate_records(api_data, group_by_key="year", \
                                                 sort_key="year", \
                                                 col_name="service_level", \
                                                 col_name_alias="service_level_count")



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
