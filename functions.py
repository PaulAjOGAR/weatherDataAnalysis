import pandas as pd
import plotly.express as px
import requests

def get_parameter_color(param):
    color_map = {
        "temperature_2m": "orangered",
        "precipitation": "royalblue",
        "humidity_2m": "mediumseagreen",
        "pressure_msl": "darkorchid",
        "wind_speed_10m": "darkcyan",
        "temperature_2m_max": "crimson",
        "temperature_2m_min": "lightskyblue",
        "rain_sum": "cornflowerblue",
        "precipitation_sum": "steelblue",
        "windspeed_10m_max": "teal",
        "uv_index_max": "gold",
    }
    return color_map.get(param, "gray")


def fetch_weather_data(latitude, longitude):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        f"&hourly=temperature_2m,precipitation,humidity_2m,pressure_msl,wind_speed_10m"
        f"&timezone=auto"
    )
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        hourly_data = pd.DataFrame(data['hourly'])
        hourly_data['date'] = pd.to_datetime(hourly_data['time'])
        return hourly_data, None
    return None, None


def get_daily_weather_data(location, start_date, end_date, latitude, longitude):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        f"&daily=temperature_2m_max,temperature_2m_min,uv_index_max,rain_sum,precipitation_sum,windspeed_10m_max"
        f"&start_date={start_date}&end_date={end_date}&timezone=auto"
    )
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        daily_data = data['daily']
        df = pd.DataFrame(daily_data)
        df['time'] = pd.to_datetime(df['time'])
        return df
    return None


def filter_data_by_date(df, start_date, end_date):
    df['time'] = pd.to_datetime(df['time'])
    return df[(df['time'] >= pd.to_datetime(start_date)) & (df['time'] <= pd.to_datetime(end_date))]


def plot_chart(df, x, y, title, chart_type="scatter"):
    color = get_parameter_color(y)
    if chart_type == "line":
        fig = px.line(df, x=x, y=y, title=title, color_discrete_sequence=[color])
    else:
        fig = px.scatter(df, x=x, y=y, title=title, color_discrete_sequence=[color])
    return fig
