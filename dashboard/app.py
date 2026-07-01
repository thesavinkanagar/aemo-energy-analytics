import streamlit as st
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
import os
import plotly.express as px

load_dotenv()

st.set_page_config(page_title="AEMO Energy Analytics", layout="wide")

@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema="MARTS"
    )

@st.cache_data(ttl=3600)
def load_data():
    conn = get_connection()
    query = "SELECT * FROM ENERGY_DB.MARTS.MART_GENERATION_SUMMARY ORDER BY DATE_DAY"
    df = pd.read_sql(query, conn)
    return df

st.title("⚡ AEMO Energy Analytics Dashboard")
st.caption("Australian electricity market — demand & price analysis | Built with Snowflake + dbt + Streamlit")

df = load_data()

# --- Sidebar filters ---
st.sidebar.header("Filters")
regions = st.sidebar.multiselect(
    "Select regions",
    options=df["REGION"].unique(),
    default=df["REGION"].unique()
)
date_range = st.sidebar.date_input(
    "Date range",
    value=(df["DATE_DAY"].min(), df["DATE_DAY"].max())
)

filtered = df[
    (df["REGION"].isin(regions)) &
    (df["DATE_DAY"] >= pd.to_datetime(date_range[0])) &
    (df["DATE_DAY"] <= pd.to_datetime(date_range[1]))
]

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Demand (MW)", f"{filtered['AVG_DEMAND_MW'].mean():,.0f}")
col2.metric("Peak Demand (MW)", f"{filtered['PEAK_DEMAND_MW'].max():,.0f}")
col3.metric("Avg Price ($/MWh)", f"{filtered['AVG_PRICE_AUD_MWH'].mean():,.2f}")
col4.metric("Max Price ($/MWh)", f"{filtered['MAX_PRICE_AUD_MWH'].max():,.2f}")

st.divider()

# --- Demand trend ---
st.subheader("Demand Trend Over Time")
fig_demand = px.line(
    filtered, x="DATE_DAY", y="AVG_DEMAND_MW", color="REGION",
    labels={"AVG_DEMAND_MW": "Avg Demand (MW)", "DATE_DAY": "Date"}
)
st.plotly_chart(fig_demand, use_container_width=True)

# --- Price trend ---
st.subheader("Price Trend Over Time")
fig_price = px.line(
    filtered, x="DATE_DAY", y="AVG_PRICE_AUD_MWH", color="REGION",
    labels={"AVG_PRICE_AUD_MWH": "Avg Price ($/MWh)", "DATE_DAY": "Date"}
)
st.plotly_chart(fig_price, use_container_width=True)

# --- Regional comparison ---
st.subheader("Average Demand by Region")
region_summary = filtered.groupby("REGION_NAME", as_index=False)["AVG_DEMAND_MW"].mean()
fig_bar = px.bar(
    region_summary, x="REGION_NAME", y="AVG_DEMAND_MW",
    labels={"AVG_DEMAND_MW": "Avg Demand (MW)", "REGION_NAME": "Region"}
)
st.plotly_chart(fig_bar, use_container_width=True)

# --- Raw data ---
with st.expander("View raw data"):
    st.dataframe(filtered, use_container_width=True)