import streamlit as st

# Page map
PAGES = {
    "Home": "home.py",
    "Daily View": "Daily_Data.py",
    "Hourly View": "Hourly_Data.py",
    "Explore Data": "explore_data.py",
}

# Sidebar navigation
st.sidebar.title("Weather App Navigation")
selected_page = st.sidebar.radio("Go to", list(PAGES.keys()))

# Page intro
st.markdown("## Weather Analytics Dashboard")

# Display helpful session info
if "latitude" in st.session_state and "longitude" in st.session_state:
    st.sidebar.markdown(f"**Location Set**: `{st.session_state['latitude']:.2f}, {st.session_state['longitude']:.2f}`")
else:
    st.sidebar.warning("No location selected yet!")

# Run selected page
page_file = PAGES[selected_page]
with open(page_file, "r", encoding="utf-8") as file:
    exec(file.read())
