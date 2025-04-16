from utils.api_client import get_openmeteo_client
from utils.data_fetching import (
    get_forecast_daily as get_forecast_daily_weather,
    get_archive_daily as get_archive_daily_weather,
    get_archive_hourly as get_archive_hourly_weather
)
from utils.plotting import plot_chart
from utils.parsing import parse_hourly_response as parse_openmeteo_hourly_response

# This file is now clean and imports everything neatly.
# Functions are still accessible under original names for compatibility.
