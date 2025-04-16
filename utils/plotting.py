import plotly.express as px

def get_parameter_color(param):
    color_map = {
        "temperature_2m": "orangered", "precipitation": "royalblue",
        "humidity_2m": "mediumseagreen", "pressure_msl": "darkorchid",
        "wind_speed_10m": "darkcyan", "temperature_2m_max": "crimson",
        "temperature_2m_min": "lightskyblue", "rain_sum": "cornflowerblue",
        "precipitation_sum": "steelblue", "wind_speed_10m_max": "teal",
        "uv_index_max": "gold"
    }
    return color_map.get(param, "gray")

def plot_chart(df, x, y, title, chart_type="line"):
    color = get_parameter_color(y)
    if chart_type == "line":
        return px.line(df, x=x, y=y, title=title, color_discrete_sequence=[color])
    return px.scatter(df, x=x, y=y, title=title, color_discrete_sequence=[color])
