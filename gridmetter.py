import requests
import netCDF4 as nc
import numpy as np
import os
import pandas as pd
import geopandas as gpd
from shapely import Point
from datetime import date, timedelta, datetime

     
def read_gridmet_api(weather_filename, output_folder):
  # URL of the NetCDF file
  url = 'https://www.northwestknowledge.net/metdata/data/' + weather_filename
  # Send a GET request to the URL
  response = requests.get(url)

  # Check if the request was successful
  if response.status_code == 200:
    # Save the content to a file
    with open(os.path.join(output_folder, weather_filename), 'wb') as file:
      file.write(response.content)
    print("File " + weather_filename + " downloaded successfully.")
  else:
    print(f"Failed to download file " + weather_filename + ". Status code: {response.status_code}")
      
       
def extract_grid_shapefile(sample_output, output_folder, grid_cell_filename):
  # Open the NetCDF file
  dataset = nc.Dataset(os.path.join(output_folder, sample_output), 'r')  
  # Get dataset dimension
  x_vals = len(dataset['lon'])
  y_vals = len(dataset['lat'])

  # Associate index locations with lat long values
  index_values = np.zeros((x_vals * y_vals,2))
  geom = []
  # Loop through each netcdf dimension
  for x in range(0, x_vals):
    for y in range(0, y_vals):
      index_values[y + x * y_vals, 0] = x * 1
      index_values[y + x * y_vals, 1] = y * 1
      this_point = Point(dataset['lon'][x], dataset['lat'][y])
      geom.append(this_point)
  # Convert to geodataframe
  gridded_df = pd.DataFrame(index_values, columns = ['lon', 'lat'])
  gridded_gdf = gpd.GeoDataFrame(gridded_df, geometry = geom)
  gridded_gdf = gridded_gdf.set_crs(epsg=4326)
  gridded_gdf.to_file(grid_cell_filename)
  # Close the dataset
  dataset.close()

def clip_csa_grid_cells(shapefile_path, grid_cell_folder, grid_cell_name, name_column, state_name_col):
  # Group GRIDMET grid cells by shapes
  shp_gdf = gpd.read_file(shapefile_path) # shape polygons
  grid_cell_gdf = gpd.read_file(os.path.join(grid_cell_folder, grid_cell_name)) # GRIDMET grid points
  for shp_index, shp_row in shp_gdf.iterrows():
    # isolate each shape
    this_shp = shp_gdf[shp_gdf.index == shp_index]
    # extract grid cells within boundaries
    grid_cells_shp = gpd.sjoin(grid_cell_gdf, this_shp, how="inner", predicate="within")
    # identify shapes with no grid cells
    if len(grid_cells_shp.index) == 0:
      print(shp_row[name_column])
    else:
      # otherwise, write shapefile of grid cell points within shape
      folder_name = shp_row[state_name_col].zfill(2) + '_' + shp_row[name_column] # shape name
      shape_dir = os.path.join(grid_cell_folder, folder_name)
      os.makedirs(shape_dir, exist_ok = True)
      grid_cells_shp.to_file(os.path.join(shape_dir, folder_name + '.shp'))

def initialize_weather_data(shapefile_path, output_folder, year_min, wt, name_column, state_name_col, override = False):
  datetime_index = make_datetime_index(year_min)
  shp_gdf = gpd.read_file(shapefile_path) # shape polygons
  for shp_index, shp_row in shp_gdf.iterrows():
    folder_name = shp_row[state_name_col].zfill(2) + '_' + shp_row[name_column] # shape name
    shp_dir = os.path.join(output_folder, folder_name)
    os.makedirs(shp_dir, exist_ok = True)
      
    initial_df = pd.DataFrame(index = datetime_index, columns = [wt,])
    initial_df.to_csv(os.path.join(shp_dir, wt + '.csv'))

def write_weather_data(shapefile_path, grid_cell_folder, output_folder, weather_type, key_name, year_use, name_column, state_name_col, year_type = 'historical'):

  dataset = nc.Dataset(os.path.join(output_folder, weather_type + '_' + str(year_use) + '.nc'), 'r')
  if year_type == 'historical':
    datetime_index = make_datetime_index(year_use, cutoff_date = 'eoy')
  elif year_type == 'current':
    datetime_index = make_datetime_index(year_use, cutoff_date = 'custom', custom_timedelta = len(dataset[key_name][:, 0, 0]))
  shp_gdf = gpd.read_file(shapefile_path) # shape polygons
    
  for shp_index, shp_row in shp_gdf.iterrows():
    folder_name = shp_row[state_name_col].zfill(2) + '_' + shp_row[name_column] # shape name
    grid_cell_path = os.path.join(grid_cell_folder, folder_name, folder_name + '.shp')
    if os.path.isfile(grid_cell_path):
      grid_cell_gdf = gpd.read_file(grid_cell_path)

      this_shape_average = np.zeros(len(datetime_index))
      total_grids = len(grid_cell_gdf.index)
      missing_grids = 0
      for gidx, grow in grid_cell_gdf.iterrows():
        this_grid = dataset[key_name][:, int(grow['lat']), int(grow['lon'])]
        total_missing = float(np.sum(np.array(this_grid)==32767))
        if total_missing > 0.0:
          missing_grids += 1
        else:
          this_shape_average += np.array(dataset[key_name][:, int(grow['lat']), int(grow['lon'])])
      this_shape_average = this_shape_average / float(total_grids - missing_grids)
      weather_data_path = os.path.join(output_folder, folder_name, weather_type + '.csv')
      shp_weather_data = pd.read_csv(weather_data_path, index_col = 0)
      shp_weather_data.index = pd.to_datetime(shp_weather_data.index)
      if datetime_index[-1] > shp_weather_data.index[-1]:
        curr_dt = shp_weather_data.index[-1] + timedelta(1)
        while curr_dt <= datetime_index[-1]:
          shp_weather_data.loc[curr_dt,weather_type] = np.nan 
          curr_dt = curr_dt + timedelta(1)
          
      shp_weather_data.loc[datetime_index, weather_type] = this_shape_average * 1.0
      shp_weather_data.to_csv(weather_data_path)


def make_datetime_index(start_year, cutoff_date = 'yesterday', custom_timedelta = 0):
  datetime_index = []
  if cutoff_date == 'yesterday':
    yesterday = date.today() - timedelta(1)
    final_datetime = datetime(yesterday.year, yesterday.month, yesterday.day)
  elif cutoff_date == 'eoy':
    final_datetime = datetime(start_year + 1, 1, 1)
  elif cutoff_date == 'custom':
    final_datetime = datetime(start_year, 1, 1) + timedelta(custom_timedelta)
    
  current_datetime = datetime(start_year, 1, 1)
  while current_datetime < final_datetime:
    datetime_index.append(current_datetime)
    current_datetime = current_datetime + timedelta(1)
  return datetime_index

    