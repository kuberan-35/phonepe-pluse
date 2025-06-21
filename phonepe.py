import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
from sqlalchemy import create_engine

# ------------------------ DATABASE CONNECTION ------------------------ #
def get_engine():
     return psycopg2.connect(
        host="localhost", database="project phonepe", user="postgres", password="63693103k@"
    )
engine = get_engine()

# ------------------------ PAGE SETUP ------------------------ #
st.set_page_config(page_title="📱 PhonePe Data Insights", layout="wide")
st.title("📊 PhonePe Data Insights Dashboard")

# ------------------------ FILTERS ------------------------ #     host="localhost", database="project phonepe", user="postgres", password="63693103k@

@st.cache_data
def get_filter_options():
    df_states = pd.read_sql("SELECT DISTINCT state FROM df_agg_user", engine)
    df_years = pd.read_sql("SELECT DISTINCT year FROM df_agg_user", engine)
    df_years = pd.read_sql("SELECT DISTINCT year FROM df_top_insurance", engine)
    return sorted(df_states['state']), sorted(df_years['year'])

states, years = get_filter_options()
state_filter = st.sidebar.selectbox("Select State", states)
year_filter = st.sidebar.selectbox("Select Year", years)

# ------------------------ QUERIES ------------------------ #
@st.cache_data
def query_transaction_dynamics(state, year):
    query = f"""
        SELECT quater, transaction_type, SUM(transaction_amount) AS total_amount
        FROM df_top_map
        WHERE state = '{state}' AND year = {year}
        GROUP BY quater, transaction_type
        ORDER BY quater;
    """
    return pd.read_sql(query, engine)

@st.cache_data
def query_device_engagement(state):
    query = f"""
        SELECT brand, SUM(registeredusers_count) AS users, SUM(app_opens) AS opens
        FROM df_agg_user
        WHERE state = '{state}'
        GROUP BY brand;
    """
    return pd.read_sql(query, engine)

@st.cache_data
def query_insurance(state):
    query = f"""
        SELECT year, SUM(transaction_count) AS policies, SUM(transaction_amount) AS premium
        FROM df_top_insurance
        WHERE state = '{state}'
        GROUP BY year;
    """
    return pd.read_sql(query, engine)

@st.cache_data
def query_top_states():
    query = """
        SELECT state, SUM(transaction_amount) AS total
        FROM df_top_insurance
        GROUP BY state
        ORDER BY total DESC
        LIMIT 10;
    """
    return pd.read_sql(query, engine)

@st.cache_data
def query_user_engagement(state):
    query = f"""
        SELECT year, SUM(registered_users) AS users, SUM(app_opens) AS opens
        FROM df_agg_user
        WHERE state = '{state}'
        GROUP BY year;
    """
    return pd.read_sql(query, engine)

@st.cache_data
def query_map():
    query = """
        SELECT state, SUM(transaction_amount) AS transaction_amount
        FROM df_agg_transaction
        GROUP BY state;
    """
    df = pd.read_sql(query, engine)
    df['state'] = df['state'].str.title()
    return df

# ------------------------ 1. TRANSACTION DYNAMICS ------------------------ #
st.subheader("1. 🧾 Transaction Dynamics by State, Quater, and Category")
df_dynamics = query_transaction_dynamics(state_filter, year_filter)
trans_pivot = df_dynamics.pivot(index='quater', columns='transaction_type', values='total_amount').fillna(0)
st.bar_chart(trans_pivot)

# ------------------------ 2. DEVICE DOMINANCE ------------------------ #
st.subheader("2. 📱 Device Dominance and User Engagement")
df_device = query_device_engagement(state_filter)
st.dataframe(df_device.sort_values("users", ascending=False))

# ------------------------ 3. INSURANCE PENETRATION ------------------------ #
st.subheader("3. 🛡️ Insurance Penetration Analysis")
df_insurance = query_insurance(state_filter)
st.line_chart(df_insurance.set_index('year'))

# ------------------------ 4. TRANSACTION ANALYSIS ------------------------ #
st.subheader("4. 🌍 Market Expansion Transaction Trends")
df_market = query_top_states()
st.bar_chart(df_market.set_index('state'))

# ------------------------ 5. USER ENGAGEMENT ------------------------ #
st.subheader("5. 🙋‍♂️ User Engagement Analysis")
df_engagement = query_user_engagement(state_filter)
st.line_chart(df_engagement.set_index('year'))

# ------------------------ 6. INDIA TRANSACTION MAP ------------------------ #
st.subheader("6. 🗺️ India-Wide Transaction Heatmap by State")
df_map_statewise = query_map()
geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"

fig = px.choropleth(
    df_map_statewise,
    geojson=geojson_url,
    featureidkey="properties.ST_NM",
    locations="state",
    color="transaction_amount",
    color_continuous_scale="Purples",
    title="Total Transactions Across Indian States"
)
fig.update_geos(fitbounds="locations", visible=False)
st.plotly_chart(fig, use_container_width=True)

#st.success("✅ Dashboard Loaded Successfully")
