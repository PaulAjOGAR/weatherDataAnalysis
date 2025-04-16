import requests
import pandas as pd

def get_forecast_daily(lat, lon, start, end):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,"
        f"uv_index_max,rain_sum,precipitation_sum,windspeed_10m_max"
        f"&start_date={start}&end_date={end}&timezone=auto"
    )
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json().get("daily", {})
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"])
        return df
    return None

def get_archive_daily(lat, lon, start, end):
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&start_date={start}&end_date={end}"
        f"&daily=temperature_2m_max,temperature_2m_min,rain_sum,precipitation_sum,"
        f"wind_speed_10m_max,uv_index_max&timezone=auto"
    )
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json().get("daily", {})
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"])
        return df
    return None

def get_archive_hourly(lat, lon, start, end, client):
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": str(start),
        "end_date": str(end),
        "hourly": [
            "temperature_2m", "wind_speed_100m", "relative_humidity_2m", "dew_point_2m", "apparent_temperature",
            "rain", "precipitation", "snowfall", "snow_depth",
            "soil_temperature_0_to_7cm", "soil_temperature_7_to_28cm",
            "soil_temperature_28_to_100cm", "soil_temperature_100_to_255cm",
            "soil_moisture_0_to_7cm", "soil_moisture_7_to_28cm",
            "soil_moisture_28_to_100cm", "soil_moisture_100_to_255cm",
            "weather_code", "pressure_msl", "surface_pressure", "cloud_cover",
            "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high",
            "et0_fao_evapotranspiration", "vapour_pressure_deficit", "wind_speed_10m",
            "wind_direction_10m", "wind_direction_100m", "wind_gusts_10m"
        ]
    }
    response = client.weather_api("https://archive-api.open-meteo.com/v1/archive", params=params)
    return response[0] if response else None
