import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import base64
from functions import fetch_weather_data

st.title("3-Day Weather Forecast")

city = st.text_input("Enter city name:", "London")

fetch_weather_data(city)

def set_png_as_page_bg(image_file):
    with open(image_file, "rb") as f:
        bin_str = base64.b64encode(f.read()).decode()

    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Set the background image
set_png_as_page_bg("background2.png")  # Change this to your image file name


if st.button("Get Weather Data"):
    with st.spinner("Fetching weather data..."):
        df = fetch_weather_data(city)

    if df is not None:
        st.success(f"Weather forecast for {city}")

        st.subheader("Weather Data (3 Days)")
        st.dataframe(df.drop(columns=["Humidity (%)"]))

        # ✅ Calculate Standard Deviation and Variance
        std_dev_temp_max = np.std(df["Max Temp (°C)"])
        std_dev_temp_min = np.std(df["Min Temp (°C)"])
        std_dev_temp_avg = np.std(df["Avg Temp (°C)"])
        std_dev_wind_speed = np.std(df["Wind Speed (km/h)"])

        var_temp_max = np.var(df["Max Temp (°C)"])
        var_temp_min = np.var(df["Min Temp (°C)"])
        var_temp_avg = np.var(df["Avg Temp (°C)"])
        var_wind_speed = np.var(df["Wind Speed (km/h)"])

        # Plot Temperature Trends
        st.subheader("Temperature Trends")
        fig, ax = plt.subplots(figsize=(16,8 ))
        ax.plot(df["Date"], df["Max Temp (°C)"], label="Max Temp", color="red", marker="o")
        ax.plot(df["Date"], df["Min Temp (°C)"], label="Min Temp", color="blue", marker="o")
        ax.plot(df["Date"], df["Avg Temp (°C)"], label="Avg Temp", color="green", linestyle="--")

        ax.set_xlabel("Date")
        ax.set_ylabel("Temperature (°C)")
        ax.set_xticklabels(df["Date"], rotation=45)
        ax.legend()
        st.pyplot(fig)

        # Wind Speed Graph
        st.subheader("Wind Speed Trend")
        fig, ax = plt.subplots(figsize=(16, 8))
        ax.plot(df["Date"], df["Wind Speed (km/h)"], label="Wind Speed", color="purple", marker="s")

        ax.set_xlabel("Date")
        ax.set_ylabel("Wind Speed (km/h)")
        ax.set_xticklabels(df["Date"], rotation=45)
        ax.legend()
        st.pyplot(fig)


    else:
        st.error("No data found. Try a different city.")

