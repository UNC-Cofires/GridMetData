import os
import gridmetter as gdmt

year_min = 2000 # initial year for historical data
year_max = 2024 # final year for historical data

# filename abbreviations for each individual weather variable file
weather_type_list = ['pr', 'tmmn', 'tmmx']
# data keys associated with the above filename abbreviations
net_cdf_keys = ['precipitation_amount', 'air_temperature', 'air_temperature']
weather_output_folder = 'WeatherData' # location of downloaded GridMet data (corresponds to value in read_gridmet_data.py)

# shapefile names/locations (corresponds to values in create_grid_cell_shapfiles.py)
shapefile_folder = 'Shapefiles'
shapefile_name = 'cb_2018_us_county_500k'
shapefile_path = os.path.join(shapefile_folder, shapefile_name, shapefile_name + '.shp')
shapefile_name_column = 'NAME'
shapefile_state_name_column = 'STATEFP'
grid_cell_folder = os.path.join(shapefile_folder,'GridMetCells')

# average grid point data for each region
# and record as .csv timeseries
for wt, ncd_key in zip(weather_type_list, net_cdf_keys):
  # initializes an empty aggregated data file with a timeseries index covering the entire range of analysis
  gdmt.initialize_weather_data(shapefile_path, weather_output_folder, year_min, 
                               wt, shapefile_name_column, shapefile_state_name_column)
  # loop through the file corresponding to each year of the analysis period
  for curr_yr in range(year_min, year_max + 1):
    print('Write GridMetData from: ')
    print(curr_yr, end = " ")
    print(wt)
    # read all weather data from each set of boundary grid cells (created in create_grid_cell_shapefiles)
    # files contain 365 days of data (1 year) for each grid cell
    # average each weather variable across all grid cells contained within each boundary
    # add averaged data to the initialized data file, one year at a time
    gdmt.write_weather_data(shapefile_path, grid_cell_folder, weather_output_folder, wt, ncd_key, curr_yr, shapefile_name_column, shapefile_state_name_column)

