"""
Swale and Trench Placement Tool
A professional GIS application for terrain analysis and water management planning.
"""
import streamlit as st
import pandas as pd
from model import process_csv_data, generate_contour_data
from utils.coordinates import detect_coordinate_system
from utils.visualization import create_scatter_mapbox, create_contour_plotly, create_statistics_dict
from utils.export import generate_pdf_report


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Swale & Trench Placement Tool",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# THEME TOGGLE LOGIC
# ============================================================================
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def get_light_css():
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp, [data-testid="stAppViewContainer"], .main .block-container { background-color: #f8fafc !important; }
[data-testid="stHeader"] { background-color: transparent !important; }
.main-header { background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); color: white !important; padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
.main-header h1, .main-header p { color: white !important; margin: 0; }
.main-header h1 { font-size: 2rem; font-weight: 700; }
.main-header p { margin-top: 0.5rem; opacity: 0.9; }
.card { background: white !important; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid #e8eaed; }
.card h3 { color: #1e3a5f !important; font-weight: 600; margin-top: 0; }
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child { background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, .sidebar-header h2 { color: #334155 !important; }
.metric-card { background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%) !important; border-radius: 10px; padding: 1rem; text-align: center; border: 1px solid #bae6fd; }
.metric-card .value { font-size: 1.5rem; font-weight: 700; color: #0369a1 !important; }
.metric-card .label { font-size: 0.85rem; color: #64748b !important; margin-top: 0.25rem; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; background: #f1f5f9 !important; padding: 0.5rem; border-radius: 10px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 0.5rem 1rem; font-weight: 500; color: #334155 !important; }
.stButton > button { border-radius: 8px; font-weight: 500; transition: all 0.2s ease; }
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
[data-testid="stFileUploader"] { border: 2px dashed #cbd5e1 !important; border-radius: 12px; padding: 1rem; background: #fafafa !important; }
[data-testid="stFileUploader"] p, [data-testid="stFileUploader"] span { color: #334155 !important; }
.stSelectbox > div > div { border-radius: 8px; background: white !important; }
.stSelectbox label, .stSlider label { color: #334155 !important; }
.stAlert { border-radius: 10px; }
.js-plotly-plot { border-radius: 12px; overflow: hidden; }
.modebar-btn { transform: scale(1.3) !important; }
[data-testid="stDataFrame"] { background: white !important; }
.stMarkdown p:not(.main-header *), .stMarkdown h1:not(.main-header *), .stMarkdown h2:not(.main-header *), .stMarkdown h3:not(.main-header *), .stMarkdown h4:not(.main-header *), .stMarkdown span:not(.main-header *) { color: #334155 !important; }
.main-header, .main-header h1, .main-header p, .main-header span { color: white !important; }
.stDownloadButton button { background: white !important; color: #1e3a5f !important; border: 1px solid #e8eaed !important; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
"""

def get_dark_css():
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp, [data-testid="stAppViewContainer"], .main .block-container { background-color: #0f172a !important; }
[data-testid="stHeader"] { background-color: transparent !important; }
.main-header { background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); color: white !important; padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
.main-header h1, .main-header p { color: white !important; margin: 0; }
.main-header h1 { font-size: 2rem; font-weight: 700; }
.main-header p { margin-top: 0.5rem; opacity: 0.9; }
.card { background: #1e293b !important; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.3); border: 1px solid #334155; }
.card h3 { color: #93c5fd !important; font-weight: 600; margin-top: 0; }
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child { background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, .sidebar-header h2 { color: #e2e8f0 !important; }
.metric-card { background: linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%) !important; border-radius: 10px; padding: 1rem; text-align: center; border: 1px solid #3b82f6; }
.metric-card .value { font-size: 1.5rem; font-weight: 700; color: #93c5fd !important; }
.metric-card .label { font-size: 0.85rem; color: #94a3b8 !important; margin-top: 0.25rem; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; background: #1e293b !important; padding: 0.5rem; border-radius: 10px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 0.5rem 1rem; font-weight: 500; color: #e2e8f0 !important; }
.stButton > button { border-radius: 8px; font-weight: 500; transition: all 0.2s ease; }
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
[data-testid="stFileUploader"] { border: 2px dashed #475569 !important; border-radius: 12px; padding: 1rem; background: #1e293b !important; }
[data-testid="stFileUploader"] p, [data-testid="stFileUploader"] span { color: #e2e8f0 !important; }
.stSelectbox > div > div { border-radius: 8px; background: #1e293b !important; color: #e2e8f0 !important; }
.stSelectbox label, .stSlider label { color: #e2e8f0 !important; }
.stAlert { border-radius: 10px; }
.js-plotly-plot { border-radius: 12px; overflow: hidden; }
.modebar-btn { transform: scale(1.3) !important; }
[data-testid="stDataFrame"] { background: #1e293b !important; }
.stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown span { color: #e2e8f0 !important; }
.stDownloadButton button { background: #1e293b !important; color: #93c5fd !important; border: 1px solid #475569 !important; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
"""

# Apply the appropriate theme CSS
if st.session_state.dark_mode:
    st.markdown(get_dark_css(), unsafe_allow_html=True)
else:
    st.markdown(get_light_css(), unsafe_allow_html=True)


with st.sidebar:
    st.markdown('<div class="sidebar-header"><h2>🌊 Control Panel</h2></div>', unsafe_allow_html=True)
    
    # Theme toggle
    col_theme1, col_theme2 = st.columns([3, 1])
    with col_theme1:
        st.markdown("**🎨 Theme**")
    with col_theme2:
        dark_mode = st.toggle("", value=st.session_state.dark_mode, key="theme_toggle")
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📁 Data Upload")
    uploaded_file = st.file_uploader(
        "Upload your terrain data (CSV)",
        type=["csv"],
        help="Upload a CSV file containing coordinate and elevation data"
    )
    
    st.markdown("---")
    
    
    st.markdown("### 🗺️ Coordinate System")
    coord_system = st.selectbox(
        "Data Format",
        options=["Auto-Detect", "UTM", "Lat/Lon", "Custom EPSG"],
        index=0,
        help="Select the coordinate system of your input data"
    )
    
    utm_zone = None
    utm_hemisphere = 'N'
    custom_epsg = None
    
    if coord_system == "UTM":
        col1, col2 = st.columns(2)
        with col1:
            utm_zone = st.number_input("UTM Zone", min_value=1, max_value=60, value=44)
        with col2:
            utm_hemisphere = st.selectbox("Hemisphere", ["N", "S"])
    
    elif coord_system == "Custom EPSG":
        custom_epsg = st.text_input(
            "EPSG Code",
            value="EPSG:32644",
            help="Enter the EPSG code (e.g., EPSG:32644 for UTM Zone 44N)"
        )
    
    st.markdown("---")
    
  
    st.markdown("### ⚙️ Analysis Settings")
    
    contour_levels = st.slider(
        "Contour Lines",
        min_value=5,
        max_value=30,
        value=15,
        help="Number of elevation contour lines"
    )
    
    colorscale = st.selectbox(
        "Contour Color Scheme",
        options=["earth", "viridis", "cividis", "rdylgn", "thermal"],
        index=0
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Analyze button
    analyze_button = st.button(
        "🚀 Run Analysis",
        type="primary",
        use_container_width=True,
        help="Click to process data with current settings"
    )
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    <small>
    This tool analyzes terrain data to recommend optimal swale and trench placements for water management.
    <br><br>
    <b>Supported formats:</b><br>
    • UTM coordinates<br>
    • Latitude/Longitude<br>
    • Custom EPSG projections
    </small>
    """, unsafe_allow_html=True)



st.markdown("""
<div class="main-header">
    <h1>🌊 Swale & Trench Placement Tool</h1>
    <p>Intelligent terrain analysis for optimal water management</p>
</div>
""", unsafe_allow_html=True)


if uploaded_file is not None:
   
    with st.spinner("Loading data..."):
        data = pd.read_csv(uploaded_file)
    
   
    detected = detect_coordinate_system(data)

    if coord_system == "Auto-Detect":
        if detected['type'] == 'latlon':
            st.info(f"📍 Detected **Lat/Lon** coordinates (columns: {detected.get('lat_col')}, {detected.get('lon_col')})")
            coord_type = 'latlon'
        elif detected['type'] == 'utm':
            st.info(f"📍 Detected **UTM** coordinates (columns: {detected.get('easting_col')}, {detected.get('northing_col')})")
            coord_type = 'utm'
        else:
            st.warning("⚠️ Could not auto-detect coordinate system. Please select manually.")
            coord_type = 'unknown'
    else:
        coord_type = coord_system.lower().replace('-', '').replace(' ', '')
        if coord_type == 'autodetect':
            coord_type = detected['type']
        elif coord_type == 'customepsg':
            coord_type = 'custom'
    
    # Initialize session state for processed data
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
        st.session_state.stats = None
    
    # Process data when analyze button is clicked OR on first load
    if analyze_button or st.session_state.processed_data is None:
        with st.spinner("Processing terrain data..."):
            try:
                processed_data = process_csv_data(
                    data,
                    coordinate_system=coord_type if coord_type != 'autodetect' else 'auto',
                    utm_zone=utm_zone,
                    utm_hemisphere=utm_hemisphere,
                    custom_epsg=custom_epsg
                )
                stats = create_statistics_dict(processed_data)
                
                # Store in session state
                st.session_state.processed_data = processed_data
                st.session_state.stats = stats
                
            except Exception as e:
                st.error(f"❌ Error processing data: {str(e)}")
                st.stop()
    
    # Use session state data
    processed_data = st.session_state.processed_data
    stats = st.session_state.stats
    
    if processed_data is None:
        st.info("👆 Click **Run Analysis** in the sidebar to process your data.")
        st.stop()
    
  
    st.markdown("### 📊 Data Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="value">{stats['total_points']:,}</div>
            <div class="label">Total Points</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if stats.get('elevation_min') is not None:
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{stats['elevation_min']:.1f}m - {stats['elevation_max']:.1f}m</div>
                <div class="label">Elevation Range</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if stats.get('elevation_mean') is not None:
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{stats['elevation_mean']:.2f}m</div>
                <div class="label">Mean Elevation</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if stats.get('terrain_percentages'):
            terrain_str = " / ".join([f"{k}: {v}" for k, v in stats['terrain_percentages'].items()])
            st.markdown(f"""
            <div class="metric-card">
                <div class="value" style="font-size: 1rem;">{terrain_str}</div>
                <div class="label">Terrain Distribution</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
  
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Map View", "📈 Contour Analysis", "📋 Data Table", "💾 Export"])
    

    with tab1:
        st.markdown("#### Swale & Trench Placement Map")
        st.markdown("""
        <small style="color: #64748b;">
        Swales (lower ground) collect water in depressions. Trenches (higher areas) direct drainage flow.
        Use scroll to zoom, drag to pan.
        </small>
        """, unsafe_allow_html=True)
        
        
        color_map = {'Swale': '#22c55e', 'Trench': '#3b82f6'}  # Green and blue
        fig_map = create_scatter_mapbox(
            processed_data,
            color_discrete_map=color_map,
            height=600,
            zoom=14
        )
        
        st.plotly_chart(fig_map, use_container_width=True, config={'scrollZoom': True})
    
 
    with tab2:
        st.markdown("#### Elevation Contour Map")
        st.markdown("""
        <small style="color: #64748b;">
        Contour lines show areas of equal elevation, helping visualize terrain slope and structure.
        </small>
        """, unsafe_allow_html=True)
        
 
        fig_contour = create_contour_plotly(
            processed_data,
            ncontours=contour_levels,
            colorscale=colorscale
        )
        
        st.plotly_chart(fig_contour, use_container_width=True)
    

    with tab3:
        st.markdown("#### Processed Data")
        st.markdown("""
        <small style="color: #64748b;">
        View and explore the processed terrain data with calculated slopes and classifications.
        </small>
        """, unsafe_allow_html=True)
        
        
        display_cols = ['Latitude', 'Longitude', 'Elevation', 'slope', 'terrain_type']
        available_cols = [c for c in display_cols if c in processed_data.columns]
        
        st.dataframe(
            processed_data[available_cols],
            use_container_width=True,
            height=400
        )
    

    with tab4:
        st.markdown("#### Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("##### 📥 Download CSV")
            st.markdown("Export data with all fields.")
            
            csv_data = processed_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="processed_terrain_data.csv",
                mime="text/csv"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("##### 📊 Text Summary")
            st.markdown("Quick analysis overview.")
            
            summary_text = f"""
Swale & Trench Placement Analysis Summary
==========================================

Data Points: {stats['total_points']:,}
Elevation Range: {stats.get('elevation_min', 'N/A'):.2f}m - {stats.get('elevation_max', 'N/A'):.2f}m
Mean Elevation: {stats.get('elevation_mean', 'N/A'):.2f}m

Terrain Classification:
"""
            if stats.get('terrain_distribution'):
                for terrain, count in stats['terrain_distribution'].items():
                    pct = stats['terrain_percentages'][terrain]
                    summary_text += f"  - {terrain}: {count} points ({pct})\n"
            
            st.download_button(
                label="Download TXT",
                data=summary_text,
                file_name="analysis_summary.txt",
                mime="text/plain"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("##### 📄 PDF Report")
            st.markdown("Professional format report.")
            
            pdf_data = generate_pdf_report(stats, processed_data)
            st.download_button(
                label="Download PDF",
                data=pdf_data,
                file_name="terrain_analysis_report.pdf",
                mime="application/pdf"
            )
            st.markdown('</div>', unsafe_allow_html=True)

else:
 
    st.markdown("""
    <div class="card" style="text-align: center; padding: 3rem;">
        <h3 style="color: #1e3a5f;">👋 Welcome!</h3>
        <p style="color: #64748b; font-size: 1.1rem;">
            Upload a CSV file with terrain data to get started.
        </p>
        <p style="color: #94a3b8;">
            Your data should include coordinate columns (Easting/Northing or Lat/Lon) and Elevation values.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
  
    with st.expander("📄 Expected Data Format"):
        st.markdown("""
        Your CSV should contain columns like:
        
        **For UTM coordinates:**
        | Easting | Northing | Elevation | Distance (m) |
        |---------|----------|-----------|--------------|
        | 407755.99 | 1420175.89 | 29.11 | 0.0 |
        
        **For Lat/Lon coordinates:**
        | Latitude | Longitude | Elevation |
        |----------|-----------|-----------|
        | 12.845 | 80.149 | 29.11 |
        """)
