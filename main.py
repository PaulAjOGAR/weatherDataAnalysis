import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

WEATHERAPI_KEY = "c7a754bf38384796ad2214825250802"

def fetch_weather_data(city, api_key=WEATHERAPI_KEY):
    url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=7"
    response = requests.get(url)

    if response.status_code != 200:
        st.error(f"Error fetching data: {response.text}")
        return None

    data = response.json()
    records = []

    if "forecast" in data and "forecastday" in data["forecast"]:
        for day in data["forecast"]["forecastday"]:
            date_obj = datetime.strptime(day["date"], "%Y-%m-%d")
            formatted_date = date_obj.strftime("%A, %d %B")

            records.append({
                "Date": formatted_date,
                "Max Temp (°C)": day["day"]["maxtemp_c"],
                "Min Temp (°C)": day["day"]["mintemp_c"],
                "Avg Temp (°C)": day["day"]["avgtemp_c"],
                "Humidity (%)": day["day"]["avghumidity"],
                "Wind Speed (km/h)": day["day"]["maxwind_kph"],
                "UV Index": day["day"]["uv"],
                "Condition": day["day"]["condition"]["text"]
            })

    return pd.DataFrame(records) if records else None

st.title("3-Day Weather Forecast")

city = st.text_input("Enter city name:", "London")

if st.button("Get Weather Data"):
    with st.spinner("Fetching weather data..."):
        df = fetch_weather_data(city)

    if df is not None:
        st.success(f"Weather forecast for {city}")

        st.subheader("3-Day Weather Data")
        st.dataframe(df.head(3).drop(columns=["Humidity (%)"]))

        st.subheader("Temperature Trends")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df["Date"], df["Max Temp (°C)"], label="Max Temp", color="red", marker="o")
        ax.plot(df["Date"], df["Min Temp (°C)"], label="Min Temp", color="blue", marker="o")
        ax.plot(df["Date"], df["Avg Temp (°C)"], label="Avg Temp", color="green", linestyle="--")

        ax.set_xlabel("Date")
        ax.set_ylabel("Temperature (°C)")
        ax.set_xticklabels(df["Date"], rotation=45)
        ax.legend()
        st.pyplot(fig)

        st.subheader("Wind Speed Trend")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df["Date"], df["Wind Speed (km/h)"], label="Wind Speed", color="purple", marker="s")

        ax.set_xlabel("Date")
        ax.set_ylabel("Wind Speed (km/h)")
        ax.set_xticklabels(df["Date"], rotation=45)
        ax.legend()
        st.pyplot(fig)

        st.subheader("UV Index Trend")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df["Date"], df["UV Index"], label="UV Index", color="orange", marker="D")

        ax.set_xlabel("Date")
        ax.set_ylabel("UV Index")
        ax.set_xticklabels(df["Date"], rotation=45)
        ax.legend()
        st.pyplot(fig)

    else:
        st.error("No data found. Try a different city.")
