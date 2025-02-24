import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import base64
from functions import fetch_weather_data, calc_variance, calc_std_deviation

st.title("3-Day Weather Forecast")

city = st.text_input("Enter city name:", "London")


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

        # Calculate Variance and Standard Deviation using the imported functions
        var_temp_max = calc_variance(df["Max Temp (°C)"])
        var_temp_min = calc_variance(df["Min Temp (°C)"])
        var_temp_avg = calc_variance(df["Avg Temp (°C)"])
        var_wind_speed = calc_variance(df["Wind Speed (km/h)"])

        std_dev_temp_max = calc_std_deviation(df["Max Temp (°C)"])
        std_dev_temp_min = calc_std_deviation(df["Min Temp (°C)"])
        std_dev_temp_avg = calc_std_deviation(df["Avg Temp (°C)"])
        std_dev_wind_speed = calc_std_deviation(df["Wind Speed (km/h)"])

        st.subheader("Statistical Analysis")
        st.write(f"**Variance of Max Temp (°C):** {var_temp_max:.2f}")
        st.write(f"**Variance of Min Temp (°C):** {var_temp_min:.2f}")
        st.write(f"**Variance of Avg Temp (°C):** {var_temp_avg:.2f}")
        st.write(f"**Variance of Wind Speed (km/h):** {var_wind_speed:.2f}")

        st.write(f"**Standard Deviation of Max Temp (°C):** {std_dev_temp_max:.2f}")
        st.write(f"**Standard Deviation of Min Temp (°C):** {std_dev_temp_min:.2f}")
        st.write(f"**Standard Deviation of Avg Temp (°C):** {std_dev_temp_avg:.2f}")
        st.write(f"**Standard Deviation of Wind Speed (km/h):** {std_dev_wind_speed:.2f}")

        # Plot Temperature Trends
        st.subheader("Temperature Trends")
        fig, ax = plt.subplots(figsize=(16, 8))
        ax.plot(df["Date"], df["Max Temp (°C)"], label="Max Temp", color="red", marker="o")
        ax.plot(df["Date"], df["Min Temp (°C)"], label="Min Temp", color="blue", marker="o")
        ax.plot(df["Date"], df["Avg Temp (°C)"], label="Avg Temp", color="green", linestyle="--")
        ax.set_xlabel("Date")
        ax.set_ylabel("Temperature (°C)")
        ax.set_xticks(range(len(df["Date"])))
        ax.set_xticklabels(df["Date"], rotation=45)
        ax.legend()
        st.pyplot(fig)

        # Wind Speed Graph
        st.subheader("Wind Speed Trend")
        fig, ax = plt.subplots(figsize=(16, 8))
        ax.plot(df["Date"], df["Wind Speed (km/h)"], label="Wind Speed", color="purple", marker="s")
        ax.set_xlabel("Date")
        ax.set_ylabel("Wind Speed (km/h)")
        ax.set_xticks(range(len(df["Date"])))
        ax.set_xticklabels(df["Date"], rotation=45)
        ax.legend()
        st.pyplot(fig)

        # Box Plots
        st.subheader("Box Plots")
        fig, ax = plt.subplots(figsize=(16, 8))
        # Box plot for temperature data
        temp_data = [df["Max Temp (°C)"], df["Min Temp (°C)"], df["Avg Temp (°C)"]]
        bp = ax.boxplot(temp_data, patch_artist=True, labels=["Max Temp", "Min Temp", "Avg Temp"])
        ax.set_title("Temperature Distribution")
        ax.set_ylabel("Temperature (°C)")
        st.pyplot(fig)

        # Box plot for Wind Speed
        st.subheader("Wind Speed Distribution")
        fig, ax = plt.subplots(figsize=(16, 8))
        bp = ax.boxplot(df["Wind Speed (km/h)"], patch_artist=True)
        ax.set_title("Wind Speed Distribution")
        ax.set_ylabel("Wind Speed (km/h)")
        st.pyplot(fig)

        # Scatter Plot
        st.subheader("Scatterplot: Avg Temp vs Wind Speed")
        fig, ax = plt.subplots(figsize=(16, 8))
        ax.scatter(df["Avg Temp (°C)"], df["Wind Speed (km/h)"], color="magenta", marker="o")
        ax.set_xlabel("Avg Temperature (°C)")
        ax.set_ylabel("Wind Speed (km/h)")
        ax.set_title("Avg Temp vs Wind Speed")
        st.pyplot(fig)

    else:
        st.error("No data found. Try a different city.")
