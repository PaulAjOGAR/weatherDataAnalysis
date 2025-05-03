import streamlit as st
from streamlit_searchbox import st_searchbox
import requests
import pandas as pd
import time

# Page configuration with custom theme
st.set_page_config(
    page_title="Weather Archive Explorer",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #424242;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
    }
    .stButton button {
        background-color: #1E88E5;
        color: white;
        font-weight: 500;
    }
    .tip-box {
        padding: 0.8rem;
        background-color: #E3F2FD;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<div class="main-header">🌍 Historical Weather Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Analyze weather trends with accurate historical data</div>',
            unsafe_allow_html=True)

# Create sidebar for app navigation and info
with st.sidebar:
    st.image("https://cdn.pixabay.com/photo/2018/04/21/19/12/weather-3339347_640.png", width=100)
    st.title("Navigation")
    st.markdown("---")

    if "latitude" in st.session_state and "longitude" in st.session_state:
        st.success(f"📍 Location set: {st.session_state.get('city', 'Custom location')}")
        st.markdown("---")

    st.markdown("### About this app")
    st.markdown("""
    This application allows you to:
    - Search for any global location
    - View historical weather data
    - Analyze daily or hourly metrics
    - Download data for your own analysis
    """)

    st.markdown("---")
    st.caption("Data provided by Open-Meteo API")


# --- Autocomplete Location Search ---
@st.cache_data(ttl=3600, show_spinner=False)
def search_locations(query):
    if not query or len(query) < 3:
        return []

    url = f"https://nominatim.openstreetmap.org/search?format=json&q={query}"
    headers = {"User-Agent": "weather-archive-app/1.0"}

    try:
        res = requests.get(url, headers=headers, timeout=5).json()
        return [f"{item['display_name']}|{item['lat']}|{item['lon']}" for item in res[:8]]
    except Exception:
        return []


st.markdown("### 🔍 Find your location")
with st.container():
    st.markdown('<div class="tip-box">Start by searching for a city, region or landmark</div>', unsafe_allow_html=True)

    # --- Autocomplete UI with improved loading indicator ---
    selection = st_searchbox(
        search_locations,
        key="city_search",
        placeholder="🔍 Start typing a location name (min 3 characters)",
        label="Search for a location"
    )

# --- Location Selected Logic ---
if selection:
    city_name, lat, lon = selection.split("|")
    lat, lon = float(lat), float(lon)

    # Store in session state
    st.session_state["city"] = city_name
    st.session_state["latitude"] = lat
    st.session_state["longitude"] = lon

    # Success message with custom styling
    st.markdown(
        f'<div class="success-box">✅ Location selected: <b>{city_name}</b> ({lat:.4f}, {lon:.4f})</div>',
        unsafe_allow_html=True
    )

    # Add map visualization
    with st.expander("📍 View on map", expanded=True):
        st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=10)

    # Prompt for Redirection with better UI
    st.markdown("---")
    st.markdown("### 🚀 Ready to explore weather data")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **📊 Daily Data**
        - Temperature trends
        - Precipitation totals
        - Wind speeds
        - UV index
        """)
        if st.button("📈 Explore Daily Data", use_container_width=True):
            with st.spinner("Loading daily view..."):
                time.sleep(0.5)  # Small delay for better UX
                st.switch_page("pages/Daily_Data.py")

    with col2:
        st.markdown("""
        **🕒 Hourly Data**
        - Detailed temperature
        - Humidity changes
        - Precipitation patterns
        - Wind direction
        """)
        if st.button("🔍 Explore Hourly Data", use_container_width=True):
            with st.spinner("Loading hourly view..."):
                time.sleep(0.5)  # Small delay for better UX
                st.switch_page("pages/Hourly_Data.py")

# --- Fallback Manual Entry with improved UI ---
elif st.checkbox("Can't find your location? Enter coordinates manually"):
    st.markdown('<div class="tip-box">Enter precise latitude and longitude coordinates</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        manual_lat = st.number_input("Latitude", value=51.5074, min_value=-90.0, max_value=90.0, format="%.4f")
    with col2:
        manual_lon = st.number_input("Longitude", value=-0.1278, min_value=-180.0, max_value=180.0, format="%.4f")

    location_name = st.text_input("Location name (optional)", placeholder="My Custom Location")

    if st.button("📍 Set Coordinates", use_container_width=True):
        # Reverse geocode to get location name if not provided
        if not location_name:
            try:
                url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={manual_lat}&lon={manual_lon}"
                headers = {"User-Agent": "weather-archive-app/1.0"}
                res = requests.get(url, headers=headers, timeout=5).json()
                location_name = res.get("display_name", "Custom Location")
            except:
                location_name = f"Location at {manual_lat:.2f}, {manual_lon:.2f}"

        st.session_state["city"] = location_name
        st.session_state["latitude"] = manual_lat
        st.session_state["longitude"] = manual_lon

        st.success(f"✅ Location set: {location_name}")
        st.map(pd.DataFrame({"lat": [manual_lat], "lon": [manual_lon]}), zoom=10)

        st.markdown("### 🚀 Continue to")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📈 Daily Data", use_container_width=True):
                st.switch_page("pages/Daily_Data.py")
        with col2:
            if st.button("🔍 Hourly Data", use_container_width=True):
                st.switch_page("pages/Hourly_Data.py")

# Footer section
st.markdown("---")
st.caption("© 2025 Weather Analytics App | Data Source: Open-Meteo")