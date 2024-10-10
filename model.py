import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import pyproj
from scipy.interpolate import griddata

def process_csv_data(data):
    data = data.iloc[:, :-1]

    utm_proj = pyproj.Proj(proj='utm', zone=44, ellps='WGS84', north=True)  # UTM Zone 44N for Southern India
    wgs84_proj = pyproj.Proj(proj='latlong', datum='WGS84')  # WGS84 for lat/lon
    transformer = pyproj.Transformer.from_proj(utm_proj, wgs84_proj)

    # Convert Easting/Northing to Lat/Lon
    def convert_utm_to_latlon(easting, northing):
        lon, lat = transformer.transform(easting, northing) 
        return lat, lon  # Return lat first, then lon

    data['Latitude'], data['Longitude'] = zip(*data.apply(lambda row: convert_utm_to_latlon(row['Easting'], row['Northing']), axis=1)) #Conversion

    data['Distance (m)'] = data['Distance (m)'].replace(0, 1e-6)  # Replace zero distances to avoid divide by zero errors

    # Applying KMeans for Swale and Trench Classification
    data['slope'] = np.gradient(data['Elevation'], data['Distance (m)'])  #calculates slope by computing gradient
    data['aspect'] = np.arctan2(np.gradient(data['Northing']), np.gradient(data['Easting']))  #gives direction of slope
    features = data[['slope', 'Elevation']].fillna(0)  # Fill missing values for features
    kmeans = KMeans(n_clusters=2)
    data['cluster'] = kmeans.fit_predict(features)
    data['terrain_type'] = data['cluster'].apply(lambda x: 'Trench' if x == 1 else 'Swale') #creates new column

    return data


def generate_contour_data(data):
    grid_easting, grid_northing = np.mgrid[data['Easting'].min():data['Easting'].max():100j,
                                           data['Northing'].min():data['Northing'].max():100j]
    grid_elevation = griddata((data['Easting'], data['Northing']), data['Elevation'],
                              (grid_easting, grid_northing), method='cubic')                #creates grid from interpolation
    return grid_easting, grid_northing, grid_elevation
