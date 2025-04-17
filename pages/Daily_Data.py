import streamlit as st
import pandas as pd
from jupyter_server.base.handlers import APIHandler

from functions import get_archive_daily_weather, plot_chart

st.title("📘 Daily Weather Data Explorer")

city_daily = st.session_state.get("city")
lat = st.session_state.get("latitude")
lon = st.session_state.get("longitude")

if not city_daily or not lat or not lon:
    st.warning("⚠️ Please select a location on the Home page first.")
    st.stop()

st.success(f"📍 Location: **{city_daily}** ({lat:.2f}, {lon:.2f})")

mode = st.radio("Select Date Mode", ["Manual Range", "Search by Year"])

if mode == "Search by Year":
    selected_year = st.selectbox("Select Year", list(range(1940, pd.Timestamp.now().year + 1))[::-1])
    start_date = pd.to_datetime(f"{selected_year}-01-01")
    end_date = pd.to_datetime(f"{selected_year}-12-31")  # FULL YEAR RANGE
else:
    start_date = st.date_input("Start date", min_value=pd.to_datetime("1940-01-01"))
    end_date = st.date_input("End date", min_value=pd.to_datetime("1940-01-01"))

st.caption(f"📅 Requesting data from **{start_date}** to **{end_date}**")

try:
    df = get_archive_daily_weather(lat, lon, start_date, end_date)
    st.write("📄 Raw Daily Weather Data:")
    st.dataframe(df, use_container_width=True)  # DISPLAY RAW DATAFRAME
except Exception:
    st.error("🚫 Daily API request limit exceeded. Please try again tomorrow.")
    st.stop()

if df is not None and not df.empty:
    df["time"] = pd.to_datetime(df["time"])
    df.rename(columns={"windspeed_10m_max": "wind_speed_10m_max"}, inplace=True)

    param_map = {
        "Max Temperature": "temperature_2m_max",
        "Min Temperature": "temperature_2m_min",
        "Rain": "rain_sum",
        "Precipitation": "precipitation_sum",
        "Max Wind Speed": "wind_speed_10m_max",
        "Max UV Index": "uv_index_max"
    }

    selected_param = st.selectbox("📊 Choose Parameter", list(param_map.keys()))
    y_col = param_map[selected_param]
    chart_type = st.radio("📈 Chart Type", ["line", "scatter"], horizontal=True)
    aggregation = st.radio("📅 Aggregate By", ["Daily", "Monthly", "Yearly"], horizontal=True)

    if aggregation != "Daily":
        df = df.groupby(df["time"].dt.to_period("M" if aggregation == "Monthly" else "Y")).mean(numeric_only=True).reset_index()
        df["time"] = df["time"].dt.to_timestamp()

    fig = plot_chart(df, x="time", y=y_col, title=f"{selected_param} ({aggregation})", chart_type=chart_type)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📊 Summary Statistics")
    st.dataframe(df[[y_col]].describe(), use_container_width=True)

    st.download_button("⬇️ Download CSV", df.to_csv(index=False), file_name="daily_weather.csv")
    st.download_button("⬇️ Download Chart", fig.to_html(), file_name="daily_chart.html")
else:
    st.warning("⚠️ No data available for this location and date range.\n\n"
               "✅ Try:\n"
               "- A different city\n"
               "- A date between 1980 and yesterday\n"
               "- A smaller or more recent range")
