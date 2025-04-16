import streamlit as st
import requests
import pandas as pd

st.title(" Welcome to the Weather Analytics App")
st.markdown("Analyze weather trends by selecting a **City**, **Postcode**, or using **Manual Coordinates**.")

# Choose mode
input_mode = st.radio("Choose location input method:", ["City", "Postcode", "Manual Coordinates"])

if input_mode == "City":
    city = st.text_input("Enter city name", "London")

    if st.button(" Get Coordinates"):
        with st.spinner("Looking up city..."):
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()
                if data.get("results"):
                    lat = data["results"][0]["latitude"]
                    lon = data["results"][0]["longitude"]
                    st.session_state["latitude"] = lat
                    st.session_state["longitude"] = lon
                    st.success(f"{city}: {lat}, {lon}")
                    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))
                else:
                    st.warning("City not found.")
            else:
                st.error("City lookup failed.")

elif input_mode == "Postcode":
    postcode = st.text_input("Enter UK postcode", "SW1A 1AA")

    if st.button(" Get Coordinates from Postcode"):
        with st.spinner("Looking up postcode..."):
            postcode_url = f"https://api.postcodes.io/postcodes/{postcode}"
            res = requests.get(postcode_url)
            if res.status_code == 200:
                data = res.json()
                if data["status"] == 200:
                    lat = data["result"]["latitude"]
                    lon = data["result"]["longitude"]
                    st.session_state["latitude"] = lat
                    st.session_state["longitude"] = lon
                    st.success(f" {postcode}: {lat}, {lon}")
                    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))
                else:
                    st.warning("Invalid postcode.")
            else:
                st.error("Postcode lookup failed.")

elif input_mode == "Manual Coordinates":
    lat = st.number_input("Latitude", value=51.5074)
    lon = st.number_input("Longitude", value=-0.1278)

    if st.button(" Set Coordinates"):
        st.session_state["latitude"] = lat
        st.session_state["longitude"] = lon
        st.success(f" Coordinates set: {lat}, {lon}")
        st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))
