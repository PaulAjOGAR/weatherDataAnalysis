from datetime import datetime

import pandas as pd
import requests
import streamlit as st

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
def calc_variance():
    return None

def calc_std_deviation():
    return None
