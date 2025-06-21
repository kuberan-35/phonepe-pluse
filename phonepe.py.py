import streamlit as st
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import plotly.express as px

@st.cache_data
def load_data():
    return create_engine("postgresql+psycopg2://postgres:your_password@localhost:5432/project_phonepe")

st.set_page_config(page_title="📱 PhonePe Data Insights", layout="wide")
st.title("📊 PhonePe Data Insights Dashboard")

def datas():
    engine = load_data()
    df_top_user = pd.read_sql("SELECT * FROM df_top_user", engine)
    df_top_map = pd.read_sql("SELECT * FROM df_top_map", engine)
    df_top_insurance = pd.read_sql("SELECT * FROM df_top_insurance", engine)
    return df_top_user, df_top_map, df_top_insurance

df_top_user, df_top_map, df_top_insurance = datas()

st.sidebar.header("📌 Filters")
state_filter = st.sidebar.selectbox("Select State", sorted(df_top_user["state"].unique()))
year_filter = st.sidebar.selectbox("Select Year", sorted(df_top_user["year"].unique()))

st.subheader("1. 🧾 Transaction Dynamics by State, Quarter, and Category")
df_filtered = df_top_map[(df_top_map["state"] == state_filter) & (df_top_map["year"] == year_filter)]
trans_pivot = df_filtered.groupby(["quarter", "transaction_type"])["transaction_amount"].sum().unstack().fillna(0)
st.bar_chart(trans_pivot)

st.subheader("2. 📱 Device Dominance and User Engagement")
df_device = df_top_user[df_top_user["state"] == state_filter]
df_device_grouped = df_device.groupby("brand").agg({"registeredusers_count": "sum", "oppopens": "sum"})
st.dataframe(df_device_grouped.sort_values("registeredusers_count", ascending=False))

st.subheader("3. 🛡️ Insurance Penetration Analysis")
df_insurance_grouped = df_top_insurance[df_top_insurance["state"] == state_filter].groupby("year").agg({"count": "sum", "amount": "sum"})
st.line_chart(df_insurance_grouped)

st.subheader("4. 🌍 Market Expansion Transaction Trends")
df_market = df_top_map.groupby("state")["transaction_amount"].sum().sort_values(ascending=False).head(10)
st.bar_chart(df_market)

st.subheader("5. 🙋‍♂️ User Engagement Analysis")
df_engagement = df_top_user[df_top_user["state"] == state_filter].groupby("year").agg({"registeredusers": "sum", "oppopens": "sum"})
st.line_chart(df_engagement)

st.subheader("6. 🗺️ India-Wide Transaction Heatmap by State")
df_map_statewise = df_top_map.groupby("state")["transaction_amount"].sum().reset_index()
df_map_statewise["state"] = df_map_statewise["state"].str.title()

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

st.success("✅ Dashboard Loaded Successfully")