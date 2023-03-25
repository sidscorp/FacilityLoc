import streamlit as st
import pandas as pd
import pydeck as pdk

# Set page title and description
st.title("Washington D.C. Primary Care Sites Map")
st.write("This Streamlit app displays a map of primary care sites in Washington D.C. with filters for ward, accepted insurance, available services, and populations served.")

# Load data
data = pd.read_excel("DC Primary Care Sites.xlsx")

# Function to preprocess filter options
def preprocess_filter_options(column):
    options = set()
    for value in column.dropna().unique():
        for item in value.split(","):
            options.add(item.strip())
    return sorted(list(options))
