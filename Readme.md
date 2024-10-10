# Water Brakes Streamlit App

## Overview
The Water Brakes app is a Streamlit application designed to visualize and analyze contour map data for optimal swale and trench placement. The app processes UTM data from CSV files and provides interactive visualizations using Plotly and Matplotlib. 

## Features
- **Data Upload:** Users can upload CSV files containing UTM data (Easting, Northing, Elevation).
- **Data Processing:** The app processes the data to convert UTM coordinates to latitude and longitude, calculates slope and aspect, and classifies terrain types (Swale and Trench) using KMeans clustering.
- **Interactive Mapping:** Users can view the recommended placement of swales and trenches on an interactive map.
- **Contour Mapping:** Visualize elevation variation across the terrain using contour maps.

## Files
- `app.py`: The main Streamlit application that provides the user interface for uploading data, processing it, and visualizing the results.
- `model.py`: Contains functions for processing the CSV data and generating contour data.

### `model.py` Functions:
- **`process_csv_data(data)`**: 
    - Takes in a DataFrame, converts UTM coordinates to latitude and longitude, computes slope and aspect, and classifies terrain into swales and trenches using KMeans clustering.
  
- **`generate_contour_data(data)`**: 
    - Generates a grid of elevation data for contour mapping based on the processed input data.

### `app.py` Functionality:
- Allows users to upload a CSV file with UTM data.
- Displays a map with swale and trench placements.
- Generates and displays a contour map of the terrain's elevation.

## Requirements
To run this project, you will need the following libraries:

- Streamlit
- Pandas
- Plotly
- Matplotlib
- Scikit-learn
- PyProj
- SciPy

You can install all the required libraries using:

```bash
pip install streamlit pandas plotly matplotlib scikit-learn pyproj scipy
```
## Usage
1. **Clone the repository:**
   ```bash
   git clone https://github.com/puneet-chandna/water-brakes.git
    ```
2. **Navigate to the project directory:**
   ```bash
   cd water-brakes
   ```  
3. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```  

## License
This project is licensed under the MIT License - see the LICENSE file for details.