import streamlit as st
import pandas as pd
import pydeck as pdk
from fuzzywuzzy import fuzz, process
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

nltk.download("punkt")
nltk.download("stopwords")

# Set page title and description
st.title("Washington D.C. Primary Care Sites Map")
st.write("This Streamlit app displays a map of primary care sites in Washington D.C. with filters for ward, accepted insurance, available services, and populations served.")

# Load data
data = pd.read_excel("DC Primary Care Sites.xlsx")

def preprocess_filter_options(column):
    options = set()
    stop_words = set(stopwords.words("english"))
    for value in column.dropna().unique():
        tokens = word_tokenize(value)
        filtered_tokens = [token.strip() for token in tokens if token.lower() not in stop_words]
        clean_value = ' '.join(filtered_tokens)
        for item in clean_value.split(","):
            options.add(item.strip())
    return sorted(list(options))

def fuzzy_filter(data, column, selected_options, threshold=85):
    filtered_data = pd.DataFrame()
    for option in selected_options:
        for _, row in data.iterrows():
            if fuzz.token_set_ratio(option, row[column]) >= threshold:
                filtered_data = filtered_data.append(row)
    return filtered_data

# Sidebar filters
st.sidebar.title("Filter Options")
ward = st.sidebar.multiselect("Ward", sorted(data["Ward"].dropna().unique()))
insurance = st.sidebar.multiselect("Insurance Accepted", preprocess_filter_options(data["Insurance Accepted"]))
services = st.sidebar.multiselect("Services Available", preprocess_filter_options(data["Services Available"]))
populations = st.sidebar.multiselect("Populations Served", preprocess_filter_options(data["Populations served"]))



# Filter data
if ward:
    data = data[data["Ward"].isin(ward)]
if insurance:
    data = fuzzy_filter(data, "Insurance Accepted", insurance)
if services:
    data = fuzzy_filter(data, "Services Available", services)
if populations:
    data = fuzzy_filter(data, "Populations served", populations)


# Check if the filtered data is empty
if data.empty:
    st.write("No facilities found")
else:
    # Display map
    coordinates = data["Coordinates"].fillna("(0.0, 0.0)").apply(lambda x: [float(coord) for coord in x.strip('()').split(', ')]).tolist()
    data["lat"] = [coord[0] for coord in coordinates]
    data["lon"] = [coord[1] for coord in coordinates]
    
    data.fillna("", inplace=True)
    
    # Create a tooltip column
    data["tooltip"] = data.apply(lambda x: f"<b>Site name:</b> {x['Site name']}<br /><b>Address:</b> {x['Address']}", axis=1)
    
    view_state = pdk.ViewState(latitude=data["lat"].mean(), longitude=data["lon"].mean(), zoom=11, pitch=0)
    layer = pdk.Layer("ScatterplotLayer", data=data, get_position=["lon", "lat"], get_radius=100, get_fill_color=[255, 0, 0], pickable=True)
    map = pdk.Deck(map_style="mapbox://styles/mapbox/light-v10", initial_view_state=view_state, layers=[layer], tooltip={"html": "{tooltip}", "style": {"color": "white"}})
    
    st.pydeck_chart(map)
