import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta, datetime
import time

from functions import get_openmeteo_client, get_archive_hourly_weather, parse_openmeteo_hourly_response

# Page configuration
st.set_page_config(page_title="Hourly Weather Data", page_icon="🕒", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        color: #1976D2;
        font-weight: 700;
    }
    .data-card {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        margin-bottom: 1rem;
    }
    .info-text {
        color: #546E7A;
        margin-bottom: 1rem;
    }
    .highlight-box {
        background-color: #E3F2FD;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .stProgress > div > div > div > div {
        background-color: #1976D2;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<div class="main-header">🕒 Hourly Weather Data Explorer</div>', unsafe_allow_html=True)

# Sidebar for location info and navigation
with st.sidebar:
    st.image("https://cdn.pixabay.com/photo/2018/04/21/19/12/weather-3339347_640.png", width=80)
    st.title("Location Details")

    # Check if location is set in session state
    city_hourly = st.session_state.get("city")
    lat = st.session_state.get("latitude")
    lon = st.session_state.get("longitude")

    if not city_hourly or not lat or not lon:
        st.warning("⚠️ No location selected")
        st.button("🏠 Return to Home", on_click=lambda: st.switch_page("main.py"))
        st.stop()

    st.success(f"📍 Location: **{city_hourly}**")
    st.text(f"Coordinates: {lat:.4f}, {lon:.4f}")

    st.markdown("---")

    # Navigation buttons
    st.subheader("Navigation")
    st.button("🏠 Home", on_click=lambda: st.switch_page("main.py"))
    st.button("📊 Switch to Daily View", on_click=lambda: st.switch_page("pages/Daily_Data.py"))

    st.markdown("---")
    st.markdown("### About Hourly Data")
    st.markdown("""
    This page displays hourly weather data including:
    - Temperature
    - Precipitation
    - Humidity
    - Wind speed and direction
    - Cloud cover
    - And many more parameters

    Note: Hourly data is limited to a 31-day period.
    """)

# Main content
st.subheader(f"Hourly Weather Analysis for {city_hourly}")

st.markdown("""
<div class="highlight-box">
⚠️ <b>Important:</b> Hourly archive data is limited to a maximum of 31 days per request. 
For longer periods, please use the Daily Data view.
</div>
""", unsafe_allow_html=True)

# Date selection with enhanced UI
date_col1, date_col2 = st.columns(2)

with date_col1:
    mode = st.radio("Select Date Mode", ["Last Few Days", "Search by Month", "Manual Range"])

with date_col2:
    max_date = pd.Timestamp.now().date() - timedelta(days=1)  # Yesterday
    min_date = pd.Timestamp("1940-01-01").date()

    if mode == "Last Few Days":
        days_ago = st.slider("Days to show", min_value=1, max_value=31, value=7)
        end_date = max_date
        start_date = end_date - timedelta(days=days_ago - 1)

    elif mode == "Search by Month":
        # Get year options
        current_year = datetime.now().year
        year_options = list(range(1940, current_year + 1))[::-1]
        selected_year = st.selectbox("Select Year", year_options)

        # Month selection
        month_options = list(range(1, 13))
        selected_month = st.selectbox(
            "Select Month",
            month_options,
            format_func=lambda x: datetime(2000, x, 1).strftime("%B")
        )

        # Calculate first and last day of month
        if selected_year == current_year and selected_month == datetime.now().month:
            # Current month - show up to yesterday
            start_date = pd.to_datetime(f"{selected_year}-{selected_month:02d}-01")
            end_date = pd.Timestamp.now().date() - timedelta(days=1)
        else:
            # Calculate days in month
            if selected_month == 12:
                next_month = pd.to_datetime(f"{selected_year + 1}-01-01")
            else:
                next_month = pd.to_datetime(f"{selected_year}-{selected_month + 1:02d}-01")

            start_date = pd.to_datetime(f"{selected_year}-{selected_month:02d}-01")
            end_date = next_month - timedelta(days=1)

        # Ensure we don't exceed 31 days
        date_range = (end_date - start_date).days + 1
        if date_range > 31:
            end_date = start_date + timedelta(days=30)  # Limit to 31 days
            st.info(f"📅 Limited to first 31 days of {datetime(selected_year, selected_month, 1).strftime('%B %Y')}")
    else:
        # Manual date range
        start_date = st.date_input("Start date",
                                   value=max_date - timedelta(days=7),
                                   min_value=min_date,
                                   max_value=max_date)

        # Calculate max end date (start_date + 30 days or yesterday, whichever is sooner)
        max_end = min(start_date + timedelta(days=30), max_date)

        end_date = st.date_input("End date",
                                 value=min(start_date + timedelta(days=7), max_date),
                                 min_value=start_date,
                                 max_value=max_end)

# Validate date range
date_diff = (end_date - start_date).days
if date_diff > 31:
    st.error(f"❌ Selected range is {date_diff} days. Hourly data is limited to 31 days maximum.")
    st.stop()

st.caption(
    f"📅 Requesting hourly data from **{start_date.strftime('%B %d, %Y')}** to **{end_date.strftime('%B %d, %Y')}** ({date_diff + 1} days)")

# Initialize Open-Meteo client
client = get_openmeteo_client()

# Data loading with progress indicator
try:
    with st.spinner("Loading hourly weather data..."):
        progress_bar = st.progress(0)
        for i in range(100):
            # Simulate progress while data loads
            time.sleep(0.01)
            progress_bar.progress(i + 1)

        response = get_archive_hourly_weather(lat, lon, start_date, end_date, client)
        df = parse_openmeteo_hourly_response(response)
        progress_bar.empty()

        if df is None or df.empty:
            st.error("❌ No hourly data available for this location and date range.")
            st.markdown("""
            **Possible solutions:**
            - Try a more recent date range
            - Select a different location
            - Check the daily data view instead
            """)
            st.stop()

        # Process dataframe
        df["time"] = pd.to_datetime(df["time"])

        # Data quality check
        missing_data_pct = df.isna().sum().sum() / (df.shape[0] * df.shape[1]) * 100
        if missing_data_pct > 20:
            st.warning(f"⚠️ This dataset has {missing_data_pct:.1f}% missing values which might affect analysis.")

except Exception as e:
    st.error(f"🚫 Failed to load hourly data: {str(e)}")
    st.markdown("""
    **This might happen because:**
    - API request limit exceeded
    - Network connectivity issues
    - Invalid date range for this location

    Please try again later or with a different configuration.
    """)
    st.stop()

# Success message with data overview
st.success(f"✅ Successfully loaded {len(df)} hourly records ({date_diff + 1} days)")

# Create parameter groups for better organization
parameter_groups = {
    "Temperature": ["temperature_2m", "apparent_temperature", "dew_point_2m"],
    "Precipitation": ["rain", "precipitation", "snowfall", "snow_depth"],
    "Wind": ["wind_speed_10m", "wind_speed_100m", "wind_direction_10m", "wind_direction_100m", "wind_gusts_10m"],
    "Atmospheric": ["pressure_msl", "surface_pressure", "vapour_pressure_deficit"],
    "Humidity & Cloud": ["relative_humidity_2m", "cloud_cover", "cloud_cover_low", "cloud_cover_mid",
                         "cloud_cover_high"],
    "Soil Data": ["soil_temperature_0_to_7cm", "soil_temperature_7_to_28cm", "soil_temperature_28_to_100cm",
                  "soil_moisture_0_to_7cm", "soil_moisture_7_to_28cm", "soil_moisture_28_to_100cm"],
    "Other": ["weather_code", "et0_fao_evapotranspiration"]
}

# Create a flat list of all parameters
all_parameters = []
for group, params in parameter_groups.items():
    all_parameters.extend(params)

# Filter to only include parameters available in the data
available_parameters = [param for param in all_parameters if param in df.columns]

# Tab layout for better organization
st.markdown("### 📊 Analyze Weather Parameters")

tab1, tab2, tab3 = st.tabs(["📈 Interactive Charts", "🔄 Time Analysis", "📋 Raw Data"])

with tab1:
    # Parameter selection with grouped categories
    selected_group = st.selectbox(
        "Select Parameter Group",
        list(parameter_groups.keys()),
        index=0
    )

    # Get parameters in this group that are available in the data
    group_params = [p for p in parameter_groups[selected_group] if p in df.columns]

    if not group_params:
        st.warning(f"No parameters available in the '{selected_group}' group for this date range.")
    else:
        selected_params = st.multiselect(
            "Select Parameters to Plot",
            group_params,
            default=[group_params[0]]
        )

        if not selected_params:
            st.info("Please select at least one parameter to plot.")
        else:
            # Chart options
            chart_col1, chart_col2, chart_col3 = st.columns(3)

            with chart_col1:
                chart_type = st.radio("Chart Type", ["Line", "Scatter", "Area"])

            with chart_col2:
                time_resolution = st.radio(
                    "Time Resolution",
                    ["Hourly", "3-Hour", "6-Hour", "12-Hour"],
                    index=0
                )

            with chart_col3:
                show_trend = st.checkbox("Show Trend Line", value=False)

            # Process data based on time resolution
            if time_resolution != "Hourly":
                if time_resolution == "3-Hour":
                    freq = "3H"
                elif time_resolution == "6-Hour":
                    freq = "6H"
                else:  # 12-Hour
                    freq = "12H"

                # Resample data
                df_resampled = df.set_index("time").resample(freq).mean().reset_index()
            else:
                df_resampled = df

            # Create charts for each selected parameter
            for param in selected_params:
                # Get human-readable parameter name
                param_name = param.replace("_", " ").title()

                # Set color based on parameter type
                if "temperature" in param:
                    color_scheme = "Reds"
                elif "rain" in param or "precipitation" in param or "snow" in param:
                    color_scheme = "Blues"
                elif "humidity" in param or "moisture" in param:
                    color_scheme = "Greens"
                elif "wind" in param:
                    color_scheme = "Purples"
                elif "cloud" in param:
                    color_scheme = "Greys"
                else:
                    color_scheme = "Oranges"

                # Create appropriate chart
                if chart_type == "Line":
                    fig = px.line(
                        df_resampled,
                        x="time",
                        y=param,
                        title=f"{param_name} ({time_resolution})",
                        color_discrete_sequence=px.colors.sequential.__getattribute__(color_scheme)
                    )

                elif chart_type == "Scatter":
                    fig = px.scatter(
                        df_resampled,
                        x="time",
                        y=param,
                        title=f"{param_name} ({time_resolution})",
                        color_discrete_sequence=px.colors.sequential.__getattribute__(color_scheme)
                    )

                else:  # Area
                    fig = px.area(
                        df_resampled,
                        x="time",
                        y=param,
                        title=f"{param_name} ({time_resolution})",
                        color_discrete_sequence=px.colors.sequential.__getattribute__(color_scheme)
                    )

                # Add trendline separately if required (using statsmodels manually)
                if show_trend:
                    try:
                        import statsmodels.api as sm
                        import numpy as np

                        # Convert datetime to numeric values for regression
                        x_numeric = np.array([(t - pd.Timestamp('1970-01-01')) // pd.Timedelta('1s')
                                              for t in df_resampled['time']])

                        # Prepare the data, removing any NaN values
                        mask = ~np.isnan(df_resampled[param])
                        if sum(mask) > 1:  # Need at least 2 points for regression
                            X = sm.add_constant(x_numeric[mask])
                            y = df_resampled[param][mask]

                            # Fit the model
                            model = sm.OLS(y, X).fit()

                            # Predict values for all points
                            X_all = sm.add_constant(x_numeric)
                            predictions = model.predict(X_all)

                            # Add trend line to the figure
                            fig.add_trace(go.Scatter(
                                x=df_resampled['time'],
                                y=predictions,
                                mode='lines',
                                name='Trend',
                                line=dict(color='rgba(255, 0, 0, 0.7)', width=2, dash='dash')
                            ))
                    except (ImportError, Exception) as e:
                        st.warning(f"Could not generate trendline: {str(e)}")

                # Enhance chart appearance
                fig.update_layout(
                    xaxis_title="Time",
                    yaxis_title=param_name,
                    height=400,
                    hovermode="x unified",
                    plot_bgcolor="white"
                )

                st.plotly_chart(fig, use_container_width=True)

                # Statistics for this parameter
                stat_cols = st.columns(4)
                with stat_cols[0]:
                    st.metric("Average", f"{df_resampled[param].mean():.2f}")
                with stat_cols[1]:
                    st.metric("Minimum", f"{df_resampled[param].min():.2f}")
                with stat_cols[2]:
                    st.metric("Maximum", f"{df_resampled[param].max():.2f}")
                with stat_cols[3]:
                    st.metric("Standard Dev", f"{df_resampled[param].std():.2f}")

with tab2:
    st.markdown("### 🔄 Cyclical Patterns Analysis")

    # Select a parameter for time analysis
    time_param = st.selectbox(
        "Select Parameter for Time Analysis",
        available_parameters,
        index=0 if "temperature_2m" in available_parameters else 0
    )

    time_param_name = time_param.replace("_", " ").title()

    # Add time properties
    df["hour"] = df["time"].dt.hour
    df["day"] = df["time"].dt.day
    df["dayofweek"] = df["time"].dt.dayofweek
    df["date"] = df["time"].dt.date

    # Create hourly pattern analysis
    st.subheader("Hourly Pattern")

    hourly_avg = df.groupby("hour")[time_param].mean().reset_index()

    hourly_fig = px.line(
        hourly_avg,
        x="hour",
        y=time_param,
        title=f"Average {time_param_name} by Hour of Day",
        markers=True
    )

    hourly_fig.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=2
        ),
        xaxis_title="Hour of Day",
        yaxis_title=time_param_name,
        plot_bgcolor="white"
    )

    st.plotly_chart(hourly_fig, use_container_width=True)

    # Daily pattern if we have multiple days
    if date_diff > 1:
        st.subheader("Daily Pattern")

        daily_avg = df.groupby("date")[time_param].mean().reset_index()

        daily_fig = px.bar(
            daily_avg,
            x="date",
            y=time_param,
            title=f"Average {time_param_name} by Date",
            color_discrete_sequence=["#1976D2"]
        )

        daily_fig.update_layout(
            xaxis_title="Date",
            yaxis_title=f"Average {time_param_name}",
            plot_bgcolor="white"
        )

        st.plotly_chart(daily_fig, use_container_width=True)

    # Heatmap of hour x day if range is long enough
    if date_diff > 3:
        st.subheader("Hour × Day Heatmap")

        # Create pivot table: days vs hours
        pivot_df = df.pivot_table(
            values=time_param,
            index="day",
            columns="hour",
            aggfunc="mean"
        )

        heatmap_fig = px.imshow(
            pivot_df,
            title=f"{time_param_name} Heatmap (Day × Hour)",
            color_continuous_scale="Viridis"
        )

        heatmap_fig.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Day of Month"
        )

        st.plotly_chart(heatmap_fig, use_container_width=True)

with tab3:
    st.markdown("### 📋 Raw Data Table")

    # Column selection
    selected_columns = st.multiselect(
        "Select Columns to View",
        ["time"] + available_parameters,
        default=["time", "temperature_2m", "relative_humidity_2m", "precipitation"]
        if "precipitation" in available_parameters else ["time", "temperature_2m", "relative_humidity_2m"]
    )

    if not selected_columns:
        st.info("Please select at least one column to display.")
    else:
        # Display filtered dataframe
        df_display = df[selected_columns]
        st.dataframe(df_display, use_container_width=True)

        # Download options
        st.markdown("### 📥 Download Options")

        download_col1, download_col2 = st.columns(2)

        with download_col1:
            st.download_button(
                "⬇️ Download Selected Columns",
                df_display.to_csv(index=False),
                file_name=f"hourly_weather_selected_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

        with download_col2:
            st.download_button(
                "⬇️ Download All Data",
                df.to_csv(index=False),
                file_name=f"hourly_weather_full_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# Footer
st.markdown("---")
st.caption("© 2025 Weather Analytics App | Data Source: Open-Meteo")