"""
Core data processing logic for swale and trench classification.
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from utils.coordinates import detect_coordinate_system, transform_coordinates, get_utm_epsg_code


def process_csv_data(
    data: pd.DataFrame,
    coordinate_system: str = 'auto',
    utm_zone: int = None,
    utm_hemisphere: str = 'N',
    custom_epsg: str = None,
    n_clusters: int = 2
) -> pd.DataFrame:
    """
    Process CSV data with coordinate transformation and terrain classification.
    
    Args:
        data: Input DataFrame with coordinate and elevation data
        coordinate_system: 'auto', 'utm', 'latlon', or 'custom'
        utm_zone: UTM zone number (required if coordinate_system is 'utm')
        utm_hemisphere: 'N' or 'S' for UTM
        custom_epsg: EPSG code string for custom CRS
        n_clusters: Number of clusters for KMeans classification
    
    Returns:
        Processed DataFrame with Latitude, Longitude, and terrain_type columns
    """
    data = data.copy()  # Avoid modifying original
    
    # Detect or use specified coordinate system
    if coordinate_system == 'auto':
        detected = detect_coordinate_system(data)
        coord_type = detected['type']
    else:
        coord_type = coordinate_system
    
    # Handle coordinate transformation
    if coord_type == 'latlon':
        # Check if lat/lon columns exist with standard names
        detected = detect_coordinate_system(data)
        if detected.get('lat_col') and detected.get('lon_col'):
            # Rename to standard names if different
            if detected['lat_col'] != 'Latitude':
                data['Latitude'] = data[detected['lat_col']]
            if detected['lon_col'] != 'Longitude':
                data['Longitude'] = data[detected['lon_col']]
    
    elif coord_type == 'utm':
        detected = detect_coordinate_system(data)
        if detected.get('easting_col') and detected.get('northing_col'):
            # Determine CRS
            if custom_epsg:
                from_crs = custom_epsg
            elif utm_zone:
                from_crs = get_utm_epsg_code(utm_zone, utm_hemisphere)
            else:
                # Default fallback (UTM Zone 44N as before)
                from_crs = "EPSG:32644"
            
            data = transform_coordinates(
                data,
                from_crs=from_crs,
                to_crs="EPSG:4326",
                x_col=detected['easting_col'],
                y_col=detected['northing_col']
            )
    
    elif coord_type == 'custom' and custom_epsg:
        # Try to detect x/y columns
        detected = detect_coordinate_system(data)
        x_col = detected.get('easting_col') or data.columns[0]
        y_col = detected.get('northing_col') or data.columns[1]
        
        data = transform_coordinates(
            data,
            from_crs=custom_epsg,
            to_crs="EPSG:4326",
            x_col=x_col,
            y_col=y_col
        )
    
    # Handle distance column
    if 'Distance (m)' in data.columns:
        data['Distance (m)'] = data['Distance (m)'].replace(0, 1e-6)
    
    # Terrain classification using KMeans
    if 'Elevation' in data.columns:
        # Calculate slope
        if 'Distance (m)' in data.columns:
            data['slope'] = np.gradient(data['Elevation'], data['Distance (m)'])
        else:
            data['slope'] = np.gradient(data['Elevation'])
        
        # Calculate aspect if we have coordinate columns
        easting_col = None
        northing_col = None
        for col in data.columns:
            if col.lower() in ['easting', 'east']:
                easting_col = col
            if col.lower() in ['northing', 'north']:
                northing_col = col
        
        if easting_col and northing_col:
            data['aspect'] = np.arctan2(
                np.gradient(data[northing_col]),
                np.gradient(data[easting_col])
            )
        
        # KMeans clustering
        features = data[['slope', 'Elevation']].fillna(0)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        data['cluster'] = kmeans.fit_predict(features)
        
        # Label clusters based on elevation 
        # Swale = lower ground (water collection areas)
        # Trench = higher ground (drainage channels)
        cluster_means = data.groupby('cluster')['Elevation'].mean()
        sorted_clusters = cluster_means.sort_values().index.tolist()  # Sorted low to high
        
        # Lower elevation = Swale, Higher elevation = Trench
        terrain_labels = ['Swale', 'Trench'] if n_clusters == 2 else [f'Zone {i+1}' for i in range(n_clusters)]
        cluster_to_terrain = {sorted_clusters[i]: terrain_labels[min(i, len(terrain_labels)-1)] for i in range(len(sorted_clusters))}
        data['terrain_type'] = data['cluster'].map(cluster_to_terrain)
    
    return data


def generate_contour_data(data: pd.DataFrame, grid_size: int = 100):
    """
    Generate grid data for contour plotting.
    
    Args:
        data: DataFrame with Easting, Northing, and Elevation columns
        grid_size: Number of grid points per axis
    
    Returns:
        tuple: (grid_x, grid_y, grid_elevation)
    """
    from scipy.interpolate import griddata
    
    # Try to find coordinate columns
    x_col = None
    y_col = None
    for col in data.columns:
        if col.lower() in ['easting', 'east', 'x']:
            x_col = col
        if col.lower() in ['northing', 'north', 'y']:
            y_col = col
    
    if not x_col or not y_col:
        # Fallback to first two columns
        x_col = data.columns[0]
        y_col = data.columns[1]
    
    grid_x, grid_y = np.mgrid[
        data[x_col].min():data[x_col].max():complex(grid_size),
        data[y_col].min():data[y_col].max():complex(grid_size)
    ]
    
    grid_elevation = griddata(
        (data[x_col], data[y_col]),
        data['Elevation'],
        (grid_x, grid_y),
        method='cubic'
    )
    
    return grid_x, grid_y, grid_elevation
