import streamlit as st
from functions import get_daily_weather_data, filter_data_by_date, plot_chart
import pandas as pd

st.title(" Daily Weather Data")

location = st.text_input("Enter city name:", "London")
start_date = st.date_input("Start date")
end_date = st.date_input("End date")

lat = st.session_state.get("latitude")
lon = st.session_state.get("longitude")

if lat and lon:
    df = get_daily_weather_data(location, start_date, end_date, lat, lon)
    if df is not None:
        param_map = {
            "Max Temperature": "temperature_2m_max",
            "Min Temperature": "temperature_2m_min",
            "Rain": "rain_sum",
            "Precipitation": "precipitation_sum",
            "Max Wind Speed": "windspeed_10m_max",
            "Max UV Index": "uv_index_max"
        }

        selected_param = st.selectbox("Choose Parameter", list(param_map.keys()))
        chart_type = st.radio("Select Chart Type", ["scatter", "line"])

        y_col = param_map[selected_param]
        fig = plot_chart(df, x="time", y=y_col, title=selected_param, chart_type=chart_type)
        st.plotly_chart(fig)

        st.markdown("### Summary Statistics")
        st.write(df[[y_col]].describe())

        st.markdown("#### Download")
        st.download_button(" Download CSV", df.to_csv(index=False), file_name="daily_data.csv")
        st.download_button("Download Chart", fig.to_html(), file_name="daily_chart.html")
    else:
        st.error("Failed to retrieve data.")
else:
    st.warning("Please set a location on the Home page.")
