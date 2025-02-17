import os
import gridmetter as gdmt

sample_year = 2000 # sample downloaded file to use to create gridded shapefile
sample_weather_var = 'pr'# sample downloaded weather variable to use to create gridded shapefile

# subdirectory for reading/writing shapefile data
shapefile_folder = 'Shapefiles'
shapefile_name = 'cb_2018_us_county_500k' # this file should already exist 
shapefile_path = os.path.join(shapefile_folder, shapefile_name, shapefile_name + '.shp')
# used to name the folders which contain the gridded shapefile for each feature
# default is that each feature corresponds to a single county
shapefile_state_name_column = 'STATEFP' # name includes state fips code (01-72)
shapefile_name_column = 'NAME' # name includes county name

# make a new folder to store all the county-level gridded cell data
grid_cell_folder = os.path.join(shapefile_folder,'GridMetCells')
grid_cell_name = 'GridMetCells.shp'
grid_cell_filename = os.path.join(grid_cell_folder, grid_cell_name)
os.makedirs(grid_cell_folder, exist_ok = True)

# extract grid from entire contiguous United States, make a single nationwide grid cell shapefile
gdmt.extract_grid_shapefile(sample_weather_var + '_' + str(sample_year) + '.nc', weather_output_folder, grid_cell_filename)  
# for each county, clip the nationwide grid cell file with the county boundary to create county-specific shapefiles
gdmt.clip_csa_grid_cells(shapefile_path, grid_cell_folder, grid_cell_name, shapefile_name_column, shapefile_state_name_column)
