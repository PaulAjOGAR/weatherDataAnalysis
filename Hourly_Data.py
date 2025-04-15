import streamlit as st
import pandas as pd
import plotly.express as px
from functions import fetch_weather_data

# Page title
st.title("⏰ Hourly Weather Data")

# Ensure that we have a valid city selected
lat = st.session_state.get("latitude")
lon = st.session_state.get("longitude")

if lat and lon:
    # Fetch the data
    hourly_df, daily_df = fetch_weather_data(lat, lon)

    # Check if the DataFrame is valid and print the columns
    if isinstance(hourly_df, pd.DataFrame):
        st.write("Dataframe Structure:")
        st.write(hourly_df.head())  # Display the first few rows of the DataFrame for debugging
        st.write("Columns in hourly data:", hourly_df.columns)  # Show all columns in the DataFrame

        # Validate if necessary columns exist in the dataframe
        if "date" in hourly_df.columns and "temperature_2m" in hourly_df.columns and "precipitation" in hourly_df.columns:
            # Allow user to select parameters
            st.subheader("Select parameters to display:")

            # List of parameters to display
            parameters = ["temperature_2m", "precipitation"]
            selected_parameters = st.multiselect("Choose parameters", parameters, default=parameters)

            # Display the hourly data table with selected parameters
            selected_data = hourly_df[["date"] + selected_parameters]
            st.write("### Hourly Data Table", selected_data)

            # Plot if there are valid parameters selected
            if selected_parameters:
                try:
                    fig = px.scatter(selected_data, x="date", y=selected_parameters, title="Hourly Weather Trends")
                    st.plotly_chart(fig)
                except Exception as e:
                    st.error(f"Error plotting data: {e}")
        else:
            st.error("Missing required columns in hourly data. Expected columns: 'date', 'temperature_2m', and 'precipitation'.")
    else:
        st.error("Invalid data or failed to fetch hourly data.")
else:
    st.warning("Please select a city from the home page first.")
