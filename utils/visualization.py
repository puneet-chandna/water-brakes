"""
Visualization utilities for creating charts and maps.
"""
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.interpolate import griddata


def create_scatter_mapbox(
    data: pd.DataFrame,
    lat_col: str = 'Latitude',
    lon_col: str = 'Longitude',
    color_col: str = 'terrain_type',
    height: int = 600,
    zoom: int = 14,
    style: str = 'open-street-map',
    title: str = None,
    color_discrete_map: dict = None
) -> go.Figure:
    """
    Create an interactive scatter mapbox plot.
    
    Args:
        data: DataFrame with lat/lon columns
        lat_col: Name of latitude column
        lon_col: Name of longitude column
        color_col: Column to use for color coding points
        height: Map height in pixels
        zoom: Initial zoom level
        style: Mapbox style
        title: Map title
        color_discrete_map: Custom color mapping
    
    Returns:
        Plotly Figure object
    """
    # Use scatter_geo or scatter_map for better compatibility
    fig = go.Figure()
    
    # Get unique terrain types and assign colors
    if color_col in data.columns:
        terrain_types = data[color_col].unique()
        default_colors = {'Swale': '#22c55e', 'Trench': '#3b82f6'}
        colors = color_discrete_map if color_discrete_map else default_colors
        
        for terrain in terrain_types:
            subset = data[data[color_col] == terrain]
            color = colors.get(terrain, '#888888')
            fig.add_trace(go.Scattermapbox(
                lat=subset[lat_col],
                lon=subset[lon_col],
                mode='markers',
                marker=dict(size=8, color=color),
                name=terrain,
                hovertemplate=f'{terrain}<br>Lat: %{{lat:.4f}}<br>Lon: %{{lon:.4f}}<extra></extra>'
            ))
    else:
        fig.add_trace(go.Scattermapbox(
            lat=data[lat_col],
            lon=data[lon_col],
            mode='markers',
            marker=dict(size=8, color='#3b82f6'),
            name='Points'
        ))
    
    # Calculate center
    center_lat = data[lat_col].mean()
    center_lon = data[lon_col].mean()
    
    fig.update_layout(
        mapbox=dict(
            style=style,
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom
        ),
        height=height,
        legend=dict(
            font=dict(size=16),
            itemsizing='constant',
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1,
            yanchor='top',
            y=0.99,
            xanchor='right',
            x=0.99
        ),
        margin=dict(l=0, r=0, t=10, b=0)
    )
    
    return fig


def create_contour_plotly(
    data: pd.DataFrame,
    x_col: str = 'Easting',
    y_col: str = 'Northing',
    z_col: str = 'Elevation',
    grid_resolution: int = 100,
    ncontours: int = 15,
    colorscale: str = 'Earth',
    title: str = 'Elevation Contour Map'
) -> go.Figure:
    """
    Create an interactive Plotly contour plot.
    
    Args:
        data: DataFrame with x, y, z columns
        x_col: Column for X axis
        y_col: Column for Y axis
        z_col: Column for Z (elevation) values
        grid_resolution: Number of grid points per axis
        ncontours: Number of contour levels
        colorscale: Plotly colorscale name
        title: Plot title
    
    Returns:
        Plotly Figure object
    """
    # Create grid for interpolation
    xi = np.linspace(data[x_col].min(), data[x_col].max(), grid_resolution)
    yi = np.linspace(data[y_col].min(), data[y_col].max(), grid_resolution)
    xi_grid, yi_grid = np.meshgrid(xi, yi)
    
    # Interpolate elevation data
    zi_grid = griddata(
        (data[x_col], data[y_col]),
        data[z_col],
        (xi_grid, yi_grid),
        method='cubic'
    )
    
    fig = go.Figure(data=go.Contour(
        x=xi,
        y=yi,
        z=zi_grid,
        ncontours=ncontours,
        colorscale=colorscale,
        colorbar=dict(
            title=dict(
                text='Elevation (m)',
                side='right',
                font=dict(size=14)
            )
        ),
        contours=dict(
            showlabels=True,
            labelfont=dict(size=12, color='white')
        )
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis_title=x_col,
        yaxis_title=y_col,
        xaxis=dict(scaleanchor='y', scaleratio=1),
        margin=dict(l=60, r=40, t=60, b=60)
    )
    
    return fig


def create_statistics_dict(data: pd.DataFrame) -> dict:
    """
    Calculate statistics from processed data.
    
    Returns:
        dict with various statistics
    """
    stats = {
        'total_points': len(data),
        'elevation_min': data['Elevation'].min() if 'Elevation' in data.columns else None,
        'elevation_max': data['Elevation'].max() if 'Elevation' in data.columns else None,
        'elevation_mean': data['Elevation'].mean() if 'Elevation' in data.columns else None,
        'elevation_std': data['Elevation'].std() if 'Elevation' in data.columns else None,
    }
    
    if 'terrain_type' in data.columns:
        terrain_counts = data['terrain_type'].value_counts()
        stats['terrain_distribution'] = terrain_counts.to_dict()
        total = terrain_counts.sum()
        stats['terrain_percentages'] = {k: f"{v/total*100:.1f}%" for k, v in terrain_counts.items()}
    
    if 'slope' in data.columns:
        stats['slope_min'] = data['slope'].min()
        stats['slope_max'] = data['slope'].max()
        stats['slope_mean'] = data['slope'].mean()
    
    return stats
