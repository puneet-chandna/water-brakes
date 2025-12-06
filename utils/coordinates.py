"""
Coordinate system detection and transformation utilities.
Supports UTM, Lat/Lon, and custom EPSG codes.
"""
import pyproj
import pandas as pd
import re


# Common column name patterns for coordinate detection
LAT_PATTERNS = ['latitude', 'lat', 'y']
LON_PATTERNS = ['longitude', 'lon', 'long', 'lng', 'x']
EASTING_PATTERNS = ['easting', 'east', 'e']
NORTHING_PATTERNS = ['northing', 'north', 'n']


def detect_coordinate_system(data: pd.DataFrame) -> dict:
    """
    Detect the coordinate system based on column names.
    Prioritizes UTM (Easting/Northing) over Lat/Lon because lat/lon columns 
    in source data are sometimes mislabeled or swapped.
    
    Returns:
        dict with keys:
            - 'type': 'latlon', 'utm', or 'unknown'
            - 'lat_col': column name for latitude (if latlon)
            - 'lon_col': column name for longitude (if latlon)
            - 'easting_col': column name for easting (if utm)
            - 'northing_col': column name for northing (if utm)
    """
    columns_lower = {col.lower(): col for col in data.columns}
    
    result = {'type': 'unknown'}
    
    # Check for UTM (Easting/Northing) FIRST - these are more reliable
    easting_col = None
    northing_col = None
    for pattern in EASTING_PATTERNS:
        if pattern in columns_lower:
            easting_col = columns_lower[pattern]
            break
    for pattern in NORTHING_PATTERNS:
        if pattern in columns_lower:
            northing_col = columns_lower[pattern]
            break
    
    if easting_col and northing_col:
        result = {
            'type': 'utm',
            'easting_col': easting_col,
            'northing_col': northing_col
        }
        return result
    
    # Check for Lat/Lon only if UTM not found
    lat_col = None
    lon_col = None
    for pattern in LAT_PATTERNS:
        if pattern in columns_lower:
            lat_col = columns_lower[pattern]
            break
    for pattern in LON_PATTERNS:
        if pattern in columns_lower:
            lon_col = columns_lower[pattern]
            break
    
    if lat_col and lon_col:
        # Validate that lat/lon values are in expected ranges
        lat_vals = data[lat_col]
        lon_vals = data[lon_col]
        
        # Latitude should be between -90 and 90
        # Longitude should be between -180 and 180
        lat_valid = lat_vals.between(-90, 90).all()
        lon_valid = lon_vals.between(-180, 180).all()
        
        if lat_valid and lon_valid:
            result = {
                'type': 'latlon',
                'lat_col': lat_col,
                'lon_col': lon_col
            }
            return result
        else:
            # Lat/lon values out of range - data might be mislabeled
            result = {'type': 'unknown'}
    
    return result


def get_utm_epsg_code(zone: int, hemisphere: str = 'N') -> str:
    """
    Get the EPSG code for a UTM zone.
    
    Args:
        zone: UTM zone number (1-60)
        hemisphere: 'N' for northern, 'S' for southern
    
    Returns:
        EPSG code string (e.g., 'EPSG:32644')
    """
    if hemisphere.upper() == 'N':
        return f"EPSG:{32600 + zone}"
    else:
        return f"EPSG:{32700 + zone}"


def transform_coordinates(
    data: pd.DataFrame,
    from_crs: str,
    to_crs: str = "EPSG:4326",
    x_col: str = None,
    y_col: str = None,
    new_lat_col: str = 'Latitude',
    new_lon_col: str = 'Longitude'
) -> pd.DataFrame:
    """
    Transform coordinates from one CRS to another.
    
    Args:
        data: DataFrame with coordinate columns
        from_crs: Source CRS (e.g., 'EPSG:32644')
        to_crs: Target CRS (default WGS84)
        x_col: Column name for X/Easting coordinate
        y_col: Column name for Y/Northing coordinate
        new_lat_col: Name for the new latitude column
        new_lon_col: Name for the new longitude column
    
    Returns:
        DataFrame with added/updated lat/lon columns
    """
    transformer = pyproj.Transformer.from_crs(from_crs, to_crs, always_xy=True)
    
    def convert(x, y):
        # always_xy=True means input is (x, y) = (easting, northing) and output is (x, y) = (lon, lat)
        out_lon, out_lat = transformer.transform(x, y)
        return out_lat, out_lon  # Return as (lat, lon) for our columns
    
    # Apply conversion and assign to correct columns
    converted = data.apply(lambda row: pd.Series(convert(row[x_col], row[y_col])), axis=1)
    data[new_lat_col] = converted[0]  # First value is latitude
    data[new_lon_col] = converted[1]  # Second value is longitude
    
    return data


def guess_utm_zone_from_data(data: pd.DataFrame, easting_col: str, northing_col: str) -> tuple:
    """
    Attempt to guess UTM zone from coordinate values.
    This is a heuristic and may not always be accurate.
    
    Returns:
        tuple: (zone_number, hemisphere) or (None, None) if unable to determine
    """
    # UTM easting values are typically between 100,000 and 900,000
    # UTM northing values for northern hemisphere are typically 0 to 10,000,000
    # For southern hemisphere, they are typically 0 to 10,000,000 with false northing
    
    mean_northing = data[northing_col].mean()
    
    # If northing is greater than 10,000,000, likely southern hemisphere with false northing
    # Otherwise, hard to tell without more context
    hemisphere = 'N'  # Default assumption
    if mean_northing > 10_000_000:
        hemisphere = 'S'
    
    # Zone is harder to determine without knowing the location
    # Return None for zone to prompt user input
    return None, hemisphere
