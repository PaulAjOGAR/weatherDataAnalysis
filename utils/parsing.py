import pandas as pd

def parse_hourly_response(response):
    try:
        hourly = response.Hourly()
        time_range = pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()), inclusive="left"
        )

        variable_names = [
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

        hourly_data = {"time": time_range}
        for i, name in enumerate(variable_names):
            hourly_data[name] = hourly.Variables(i).ValuesAsNumpy()

        return pd.DataFrame(hourly_data)
    except Exception as e:
        print("Parsing error:", e)
        return None
