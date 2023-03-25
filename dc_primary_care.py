import streamlit as st
import pandas as pd
import pydeck as pdk
import json

# Load data
data = pd.read_excel("DC Primary Care Sites.xlsx")

# Function to preprocess filter options
def preprocess_filter_options(column):
    options = set()
    for value in column.dropna().unique():
        for item in value.split(","):
            options.add(item.strip())
    return sorted(list(options))

# Custom theme for Streamlit
custom_theme = {
    "primary": "#F63366",
    "secondary": "#F0F2F6",
    "text": "#262730",
    "background": "#FFFFFF",
}

st.set_page_config(page_title="DC Primary Care Sites", layout="wide", page_icon=":hospital:")

# Title and description
st.title("Washington D.C. Primary Care Sites")
st.markdown("""
This interactive map shows primary care sites in Washington D.C.
Filter by ward, insurance accepted, services available, populations served, and walk-in patient status.
""")

# Sidebar filters
st.sidebar.title("Filter Options")
ward = st.sidebar.multiselect("Ward", sorted(data["Ward"].dropna().unique()))
insurance = st.sidebar.multiselect("Insurance Accepted", preprocess_filter_options(data["Insurance Accepted"]))
services = st.sidebar.multiselect("Services Available", preprocess_filter_options(data["Services Available"]))
populations = st.sidebar.multiselect("Populations Served", preprocess_filter_options(data["Populations served"]))
walk_in = st.sidebar.radio("See Walk-In Patients", ("All", "Yes", "No"))

# Filter data
if ward:
    data = data[data["Ward"].isin(ward)]
if insurance:
    data = data[data["Insurance Accepted"].apply(lambda x: any(i in x for i in insurance))]
if services:
    data = data[data["Services Available"].apply(lambda x: any(s in x for s in services))]
if populations:
    data = data[data["Populations served"].apply(lambda x: any(p in x for p in populations))]
if walk_in != "All":
    data = data[data["See Walk-In/ Unscheduled Patients"] == walk_in]

# Display map
coordinates = data["Coordinates"].apply(lambda x: [float(coord) for coord in x.strip('()').split(', ')]).tolist()
data["lat"] = [coord[0] for coord in coordinates]
data["lon"] = [coord[1] for coord in coordinates]

data.fillna("", inplace=True)

# Create a tooltip column
data["tooltip"] = data.apply(lambda x: f"<b>Site name:</b> {x['Site name']}<br /><b>Address:</b> {x['Address']}", axis=1)

view_state = pdk.ViewState(latitude=data["lat"].mean(), longitude=data["lon"].mean(), zoom=11, pitch=0)
layer = pdk.Layer("ScatterplotLayer", data=data, get_position=["lon", "lat"], get_radius=100, get_fill_color=[255, 0, 0], pickable=True)

# Load the GeoJSON data
with open("C:/Users/siddh/Documents/Fac Loc/Washington_DC_Boundary.geojson") as f:
    geojson_data = json.load(f)

# Filter the GeoJSON data based on the selected wards
filtered_geojson_data = {"type": "FeatureCollection", "features": []}
if ward:
    for feature in geojson_data["features"]:
        if feature["properties"]["WARD"] in ward:
            filtered_geojson_data["features"].append(feature)

# Create the GeoJsonLayer for selected wards
ward_layer = pdk.Layer("GeoJsonLayer", data=filtered_geojson_data, filled=True, stroked=True, get_fill_color=[255, 255, 0, 100], get_line_color=[255, 255, 0], opacity=0.5)

# Add the ward_layer to the existing Pydeck layers
layers = [layer, ward_layer]
map = pdk.Deck(map_style="mapbox://styles/mapbox/light-v10", initial_view_state=view_state, layers=layers, tooltip={"html": "{tooltip}", "style": {"color": "white"}})

st.pydeck_chart(map)
