import streamlit as st
import pandas as pd
import plotly.express as px
from functions import get_openmeteo_client, get_archive_hourly_weather

st.title("🕒 Hourly Weather Data (Archive)")

city_hourly = st.session_state.get("city")
lat = st.session_state.get("latitude")
lon = st.session_state.get("longitude")

if not city_hourly or not lat or not lon:
    st.warning("⚠️ Please select a location on the Home page first.")
    st.stop()

st.success(f"📍 Location: **{city_hourly}** ({lat:.2f}, {lon:.2f})")

mode = st.radio("Select Date Mode", ["Manual Range", "Search by Year"])

if mode == "Search by Year":
    selected_year = st.selectbox("Select Year", list(range(1940, pd.Timestamp.now().year + 1))[::-1])
    start_date = pd.to_datetime(f"{selected_year}-01-01")
    end_date = start_date + pd.Timedelta(days=30)
else:
    start_date = st.date_input("Start date", min_value=pd.to_datetime("1940-01-01"))
    end_date = st.date_input("End date", min_value=pd.to_datetime("1940-01-01"))

st.caption(f"📅 Requesting data from **{start_date}** to **{end_date}**")

if (end_date - start_date).days > 31:
    st.error("❌ Hourly archive data is limited to a 31-day range.")
    st.stop()

client = get_openmeteo_client()

try:
    df = get_archive_hourly_weather(lat, lon, start_date, end_date, client)
except Exception:
    st.error("🚫 Daily API request limit exceeded. Please try again tomorrow.")
    st.stop()

if df is not None and not df.empty:
    df["time"] = pd.to_datetime(df["time"])
    parameters = [col for col in df.columns if col != "time"]
    selected = st.multiselect("🧪 Parameters to Plot", parameters, default=["temperature_2m"])
    chart_type = st.radio("📈 Chart Type", ["line", "scatter"], horizontal=True)

    for param in selected:
        fig = px.line(df, x="time", y=param, title=f"{param} (Hourly)") if chart_type == "line" \
            else px.scatter(df, x="time", y=param, title=f"{param} (Hourly)")
        st.plotly_chart(fig, use_container_width=True)

    st.download_button("⬇️ Download CSV", df.to_csv(index=False), file_name="hourly_weather.csv")
else:
    st.warning("⚠️ No data available for this location and date range.\n\n"
               "✅ Try:\n"
               "- A different city\n"
               "- A date between 1980 and yesterday\n"
               "- A smaller or more recent range")
