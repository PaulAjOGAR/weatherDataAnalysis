import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta
import time
from functions import get_archive_daily_weather, plot_chart

# Page config
st.set_page_config(page_title="Daily Weather Data", page_icon="📊", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        color: #1976D2;
        font-weight: 700;
    }
    .data-metrics {
        background-color: #f0f7ff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stProgress > div > div > div > div {
        background-color: #1976D2;
    }
    .metric-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
    }
    .metric-title {
        font-size: 0.9rem;
        color: #616161;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<div class="main-header">📊 Daily Weather Data Explorer</div>', unsafe_allow_html=True)

# Sidebar for location info and filters
with st.sidebar:
    st.image("https://cdn.pixabay.com/photo/2018/04/21/19/12/weather-3339347_640.png", width=80)
    st.title("Location Details")

    # Check if location is set in session state
    city_daily = st.session_state.get("city")
    lat = st.session_state.get("latitude")
    lon = st.session_state.get("longitude")

    if not city_daily or not lat or not lon:
        st.warning("⚠️ No location selected")
        st.button("🏠 Return to Home", on_click=lambda: st.switch_page("main.py"))
        st.stop()

    st.success(f"📍 Location: **{city_daily}**")
    st.text(f"Coordinates: {lat:.4f}, {lon:.4f}")

    st.markdown("---")

    # Navigation buttons
    st.subheader("Navigation")
    if st.button("🏠 Home"):
        st.switch_page("main.py")

    if st.button("📊 Switch to Daily View"):
        st.switch_page("pages/Daily_Data.py")

    st.markdown("---")
    st.markdown("### About Daily Data")
    st.markdown("""
    This page displays daily aggregated weather data including:
    - Max/min temperatures
    - Precipitation and rainfall
    - Wind speeds
    - UV index

    Data availability varies by location and time period.
    """)

# Main content
st.subheader(f"Historical Weather Data for {city_daily}")

# Date selection with improved UI
date_col1, date_col2 = st.columns(2)
with date_col1:
    mode = st.radio("Select Date Mode", ["Search by Year", "Manual Range"])

with date_col2:
    if mode == "Search by Year":
        current_year = pd.Timestamp.now().year
        available_years = list(range(1940, current_year + 1))[::-1]
        selected_year = st.selectbox("Select Year", available_years)
        start_date = pd.to_datetime(f"{selected_year}-01-01")
        end_date = pd.to_datetime(f"{selected_year}-12-31")

        # Show month range slider for more precise filtering
        months = list(range(1, 13))
        month_range = st.select_slider(
            "Narrow down to specific months",
            options=months,
            value=(1, 12),
            format_func=lambda x: pd.Timestamp(2000, x, 1).strftime("%B")
        )

        if month_range != (1, 12):
            start_date = pd.to_datetime(f"{selected_year}-{month_range[0]:02d}-01")
            # Last day of end month
            if month_range[1] == 12:
                end_date = pd.to_datetime(f"{selected_year}-12-31")
            else:
                next_month = pd.to_datetime(f"{selected_year}-{month_range[1]:02d}-01") + pd.DateOffset(months=1)
                end_date = next_month - pd.DateOffset(days=1)
    else:
        max_date = pd.Timestamp.now().date() - timedelta(days=1)  # Yesterday
        min_date = pd.Timestamp("1940-01-01").date()

        start_date = st.date_input("Start date",
                                   value=max_date - timedelta(days=30),
                                   min_value=min_date,
                                   max_value=max_date)

        end_date = st.date_input("End date",
                                 value=max_date,
                                 min_value=start_date,
                                 max_value=max_date)

st.caption(f"📅 Requesting data from **{start_date.strftime('%B %d, %Y')}** to **{end_date.strftime('%B %d, %Y')}**")

# Date range warning
date_diff = (end_date - start_date).days
if date_diff > 365 * 5:
    st.warning(f"⚠️ You've selected a large date range ({date_diff} days). This might affect performance.")

# Data loading with progress indicator
try:
    with st.spinner("Loading weather data..."):
        progress_bar = st.progress(0)
        for i in range(100):
            # Simulate progress while data loads
            time.sleep(0.01)
            progress_bar.progress(i + 1)

        df = get_archive_daily_weather(lat, lon, start_date, end_date)
        progress_bar.empty()

        if df is None or df.empty:
            st.error("❌ No data available for this location and date range.")
            st.markdown("""
            **Possible solutions:**
            - Try a more recent date range
            - Select a different location
            - Reduce the date range size
            """)
            st.stop()

        # Process dataframe
        df["time"] = pd.to_datetime(df["time"])
        if "Wind Speed 10m Max" in df.columns:
            df.rename(columns={"Wind Speed 10m Max": "wind_speed_10m_max"}, inplace=True)

        # Data quality check
        missing_data_pct = df.isna().sum().sum() / (df.shape[0] * df.shape[1]) * 100
        if missing_data_pct > 20:
            st.warning(f"⚠️ This dataset has {missing_data_pct:.1f}% missing values which might affect analysis.")

except Exception as e:
    st.error(f"🚫 Failed to load data: {str(e)}")
    st.markdown("""
    **This might happen because:**
    - API request limit exceeded
    - Network connectivity issues
    - Invalid date range for this location

    Please try again later or with a different configuration.
    """)
    st.stop()

# Success message and data overview
st.success(f"✅ Successfully loaded data for {date_diff + 1} days")

# Display key metrics in nice format
st.markdown("### 📈 Key Statistics")

metrics_expander = st.expander("View Key Weather Metrics", expanded=True)
with metrics_expander:
    metrics_cols = st.columns(4)

    # Calculate key metrics
    avg_temp_max = df["temperature_2m_max"].mean()
    avg_temp_min = df["temperature_2m_min"].mean()
    total_rain = df["rain_sum"].sum()
    max_uv = df["uv_index_max"].max() if "uv_index_max" in df.columns else 0

    with metrics_cols[0]:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{avg_temp_max:.1f}°C</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-title">Average Max Temp</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with metrics_cols[1]:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{avg_temp_min:.1f}°C</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-title">Average Min Temp</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with metrics_cols[2]:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{total_rain:.1f}mm</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-title">Total Rainfall</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with metrics_cols[3]:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{max_uv:.1f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-title">Max UV Index</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Raw data table with download option
with st.expander("📋 View Raw Data Table", expanded=False):
    st.dataframe(df, use_container_width=True)
    st.download_button(
        "⬇️ Download Raw Data as CSV",
        df.to_csv(index=False),
        file_name=f"weather_daily_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# Main visualization section
st.markdown("### 📊 Visualize Weather Parameters")

# Parameter selection with better formatting
param_map = {
    "Max Temperature (°C)": "temperature_2m_max",
    "Min Temperature (°C)": "temperature_2m_min",
    "Rain (mm)": "rain_sum",
    "Precipitation (mm)": "precipitation_sum",
    "Max Wind Speed (km/h)": "wind_speed_10m_max",
    "Max UV Index": "uv_index_max"
}

viz_col1, viz_col2 = st.columns([3, 1])

with viz_col2:
    st.markdown("#### Chart Options")
    selected_param = st.selectbox("Choose Parameter", list(param_map.keys()))
    y_col = param_map[selected_param]

    chart_type = st.radio("Chart Type", ["Line", "Area", "Bar", "Scatter"], format_func=lambda x: f"{x} Chart")

    aggregation = st.radio("Aggregate Data By", ["Daily", "Weekly", "Monthly"])

    show_trendline = st.checkbox("Show Trendline", value=True)

    color_theme = st.selectbox(
        "Color Theme",
        ["Blues", "Reds", "Greens", "Purples", "Oranges"],
        index=0 if "Temperature" in selected_param else
        2 if "Rain" in selected_param or "Precipitation" in selected_param else 0
    )

# Process data based on aggregation
with viz_col1:
    if aggregation != "Daily":
        if aggregation == "Weekly":
            df["period"] = df["time"].dt.to_period("W")
        else:  # Monthly
            df["period"] = df["time"].dt.to_period("M")

        df_agg = df.groupby("period").agg({
            y_col: "mean",
            "time": "min"  # Keep the first date of each period
        }).reset_index(drop=True)

        chart_df = df_agg
    else:
        chart_df = df

    # Create appropriate chart based on user selection
    if chart_type == "Line":
        fig = px.line(
            chart_df,
            x="time",
            y=y_col,
            title=f"{selected_param} ({aggregation})",
            color_discrete_sequence=px.colors.sequential.__getattribute__(color_theme)
        )

        # Add trendline if requested (as a separate trace for line charts)
        if show_trendline:
            import numpy as np
            from scipy import stats

            # Calculate trendline
            x_numeric = np.arange(len(chart_df))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, chart_df[y_col])
            trendline_y = intercept + slope * x_numeric

            # Add trendline as a separate trace
            fig.add_trace(
                go.Scatter(
                    x=chart_df["time"],
                    y=trendline_y,
                    mode="lines",
                    name="Trend",
                    line=dict(color="red", dash="dash"),
                )
            )

    elif chart_type == "Area":
        fig = px.area(
            chart_df,
            x="time",
            y=y_col,
            title=f"{selected_param} ({aggregation})",
            color_discrete_sequence=px.colors.sequential.__getattribute__(color_theme)
        )
    elif chart_type == "Bar":
        fig = px.bar(
            chart_df,
            x="time",
            y=y_col,
            title=f"{selected_param} ({aggregation})",
            color_discrete_sequence=px.colors.sequential.__getattribute__(color_theme)
        )
    else:  # Scatter
        # Scatter plots do support trendline parameter directly
        fig = px.scatter(
            chart_df,
            x="time",
            y=y_col,
            title=f"{selected_param} ({aggregation})",
            color_discrete_sequence=px.colors.sequential.__getattribute__(color_theme),
            trendline="ols" if show_trendline else None,
            trendline_color_override="red"
        )

    # Enhance chart formatting
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=selected_param,
        plot_bgcolor="white",
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Download chart option
    st.download_button(
        "⬇️ Download Chart as HTML",
        fig.to_html(include_plotlyjs="cdn"),
        file_name=f"{y_col}_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.html",
        mime="text/html"
    )

# Enhanced statistics section with box plot
st.markdown("### 📊 Statistical Analysis")

stat_col1, stat_col2 = st.columns([1, 1])

with stat_col1:
    st.markdown("#### Summary Statistics")
    st.dataframe(df[[y_col]].describe().round(2), use_container_width=True)

    # Monthly breakdown if data spans multiple months
    if (end_date.year - start_date.year) * 12 + end_date.month - start_date.month > 0:
        st.markdown("#### Monthly Averages")
        monthly_data = df.set_index("time").resample("M")[y_col].mean().reset_index()
        monthly_data["Month"] = monthly_data["time"].dt.strftime("%b %Y")
        st.dataframe(
            monthly_data[["Month", y_col]].rename(columns={y_col: selected_param}),
            use_container_width=True
        )

with stat_col2:
    st.markdown("#### Distribution")
    fig = px.box(
        df,
        y=y_col,
        title=f"Distribution of {selected_param}",
        color_discrete_sequence=px.colors.sequential.__getattribute__(color_theme)
    )
    fig.update_layout(height=300, yaxis_title=selected_param)
    st.plotly_chart(fig, use_container_width=True)

# Temperature Range Analysis (if applicable)
if "temperature_2m_max" in df.columns and "temperature_2m_min" in df.columns:
    st.markdown("### 🌡️ Temperature Range Analysis")

    # Calculate temperature range
    df["temp_range"] = df["temperature_2m_max"] - df["temperature_2m_min"]

    temp_fig = go.Figure()

    # Add range as a filled area
    temp_fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["temperature_2m_max"],
        fill=None,
        mode='lines',
        line_color='crimson',
        name='Max Temperature'
    ))

    temp_fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["temperature_2m_min"],
        fill='tonexty',
        mode='lines',
        line_color='royalblue',
        name='Min Temperature'
    ))

    temp_fig.update_layout(
        title="Temperature Range Over Time",
        xaxis_title="Date",
        yaxis_title="Temperature (°C)",
        plot_bgcolor="white",
        height=400
    )

    st.plotly_chart(temp_fig, use_container_width=True)

    # Temperature range statistics
    temp_stats = st.columns(3)
    with temp_stats[0]:
        st.metric("Average Daily Range", f"{df['temp_range'].mean():.1f}°C")
    with temp_stats[1]:
        st.metric("Maximum Range", f"{df['temp_range'].max():.1f}°C")
    with temp_stats[2]:
        st.metric("Minimum Range", f"{df['temp_range'].min():.1f}°C")

# Footer
st.markdown("---")
st.caption("© 2025 Weather Analytics App | Data Source: Open-Meteo")