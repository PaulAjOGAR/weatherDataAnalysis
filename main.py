import streamlit as st
from streamlit_searchbox import st_searchbox
import requests

st.set_page_config(page_title="Weather Archive App", layout="wide")
st.title("🌍 Historical Weather Explorer")
st.markdown("Use this tool to view **past weather trends** based on your location and dates of interest.")

# --- Autocomplete Location Search ---
def search_locations(query):
    if not query:
        return []
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={query}"
    headers = {"User-Agent": "weather-archive-app"}
    try:
        res = requests.get(url, headers=headers).json()
        return [f"{item['display_name']}|{item['lat']}|{item['lon']}" for item in res[:5]]
    except:
        return []

# --- Autocomplete UI ---
selection = st_searchbox(search_locations, key="city_search", placeholder="🔍 Start typing a city...")

# --- If Autocomplete Found a Location ---
if selection:
    city_name, lat, lon = selection.split("|")
    lat, lon = float(lat), float(lon)

    st.session_state["city"] = city_name
    st.session_state["latitude"] = lat
    st.session_state["longitude"] = lon

    st.success(f"✅ Location selected: {city_name} ({lat:.2f}, {lon:.2f})")

    # Prompt for Redirection
    st.markdown("---")
    st.markdown("### 🚀 Ready to explore weather data?")
    page_choice = st.radio("Where would you like to go?", ["Daily Data", "Hourly Data"], horizontal=True)

    if st.button("📂 Continue"):
        if page_choice == "Daily Data":
            st.switch_page("pages/Daily_Data.py")  # Update path if needed
        else:
            st.switch_page("pages/Hourly_Data.py")

# --- Fallback Manual Entry ---
elif st.checkbox("Can't find your city? Enter it manually"):
    manual_city = st.text_input("📍 Enter full city name")
    if manual_city and st.button("🔍 Search Manually"):
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={manual_city}"
        headers = {"User-Agent": "weather-archive-app"}
        try:
            res = requests.get(url, headers=headers).json()
            if res:
                city_name = res[0]["display_name"]
                lat = float(res[0]["lat"])
                lon = float(res[0]["lon"])
                st.session_state["city"] = city_name
                st.session_state["latitude"] = lat
                st.session_state["longitude"] = lon
                st.success(f"✅ Location set: {city_name} ({lat:.2f}, {lon:.2f})")
            else:
                st.warning("⚠️ Could not find location. Please refine your input.")
        except:
            st.error("🌐 Failed to search. Please check your connection or try later.")
