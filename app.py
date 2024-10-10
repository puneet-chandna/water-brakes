import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from model import process_csv_data, generate_contour_data  # Importing functions from model.py


st.set_page_config(page_title="Swale and Trench Placement Tool", layout="wide", initial_sidebar_state="expanded")

# Customizing the appearance of the app
st.markdown(
    """
    <style>
    body {
        font-family: "Arial", sans-serif;
        background-color: #f0f2f6;
    }
    .main-title {
        color: #2c3e50;
        font-weight: bold;
        font-size: 36px;
        margin-bottom: 10px;
        text-align: center;
    }
    .sub-header {
        color: #34495e;
        font-size: 28px;
        font-weight: 500;
        margin-top: 20px;
    }
    .description {
        font-size: 18px;
        color: #7f8c8d;
        margin-top: 5px;
        margin-bottom: 20px;
        text-align: justify;
    }
    .footer {
        text-align: center;
        font-size: 14px;
        color: #95a5a6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown('<h1 class="main-title">Swale and Trench Placement Tool</h1>', unsafe_allow_html=True)      #title

st.markdown('<h2 class="sub-header">Step 1: Upload the UTM Data CSV File</h2>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["csv"])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)  #read csv data

    processed_data = process_csv_data(data)     #calling model function


    st.markdown('<h2 class="sub-header">Map of Swale and Trench Placement</h2>', unsafe_allow_html=True)

    # description for the map
    st.markdown("""
        <div class="description">
        The map below shows the recommended swale and trench placement for water management. 
        Swales (shown in one color) represent higher ground where water collection can occur, while trenches 
        (shown in another color) represent lower ground for water drainage. 
        You can zoom in and interact with the map to view the exact locations of the placements.
        </div>
        """, unsafe_allow_html=True)

    map_height = 700        # height of the map
    fig = px.scatter_mapbox(
        processed_data,
        lat="Latitude",
        lon="Longitude",
        color="terrain_type",
        zoom=12,
        height=map_height,
        mapbox_style="open-street-map",
        hover_name="terrain_type",
        title="Swale and Trench Placement"
    )
    st.plotly_chart(fig)

    # Contour map
    st.markdown('<h2 class="sub-header">Contour Map (Elevation)</h2>', unsafe_allow_html=True)

    # Description for the contour map
    st.markdown("""
        <div class="description">
        The contour map below shows the variation in elevation across the terrain. 
        Each contour line represents areas of equal elevation, helping to visualize the slope and terrain structure. 
        This information is crucial for determining optimal swale and trench placements.
        </div>
        """, unsafe_allow_html=True)

    grid_easting, grid_northing, grid_elevation = generate_contour_data(processed_data)     #calling model function

    plt.figure(figsize=(10, 10))  # Increase the vertical height
    plt.contour(grid_easting, grid_northing, grid_elevation, levels=15, cmap='terrain')
    plt.title('Contour Map')
    plt.xlabel('Easting')
    plt.ylabel('Northing')
    plt.colorbar(label='Elevation (m)')

    st.pyplot(plt)
