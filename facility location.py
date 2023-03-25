import streamlit as st
import pandas as pd
import pydeck as pdk

# Load data
data = pd.read_csv("DC_Primary_Care_Sites.csv")

# Sidebar filters
st.sidebar.title("Filter Options")
ward = st.sidebar.multiselect("Ward", sorted(data["Ward"].unique()))
insurance = st.sidebar.multiselect("Insurance Accepted", sorted(data["Insurance Accepted"].unique()))
services = st.sidebar.multiselect("Services Available", sorted(data["Services Available"].unique()))
populations = st.sidebar.multiselect("Populations Served", sorted(data["Populations served"].unique()))
walk_in = st.sidebar.radio("See Walk-In Patients", ("All", "Yes", "No"))

# Filter data
if ward:
    data = data[data["Ward"].isin(ward)]
if insurance:
    data = data[data["Insurance Accepted"].isin(insurance)]
if services:
    data = data[data["Services Available"].apply(lambda x: any(item for item in services if item in x))]
if populations:
    data = data[data["Populations served"].apply(lambda x: any(item for item in populations if item in x))]
if walk_in != "All":
    data = data[data["See Walk-In/ Unscheduled Patients"] == walk_in]

# Display filtered data
st.write(data)

# Display map
coordinates = data[["Coordinates"]].apply(lambda x: x.str.split(", ").apply(lambda y: [float(y[0][1:]), float(y[1][:-1])]), axis=1).to_list()
data["lat"] = [coord[0] for coord in coordinates]
data["lon"] = [coord[1] for coord in coordinates]

view_state = pdk.ViewState(latitude=data["lat"].mean(), longitude=data["lon"].mean(), zoom=11, pitch=0)
layer = pdk.Layer("ScatterplotLayer", data=data, get_position=["lon", "lat"], get_radius=100, get_fill_color=[255, 0, 0], pickable=True)
map = pdk.Deck(map_style="mapbox://styles/mapbox/light-v10", initial_view_state=view_state, layers=[layer], tooltip={"html": "<b>Site name:</b> {Site name}<br /><b>Address:</b> {Address}", "style": {"color": "white"}})

st.pydeck_chart(map)
