# GridMetData
data downloads and analysis of gridmet data

## Getting Started

### Dependencies

Python Libraries:

* requests
* netCDF4
* geopandas
* shapely
* datetime
* numpy
* pandas
* os

### Executing program

* This repository will download daily gridded weather data
* Downloads occur through the GridMet API from https://www.northwestknowledge.net
* To download annual netcdf files, run:
```
python -W ignore read_gridmet_data.py
```
* time range (in years) can be set by changing year_min and year_max (lines 4&5)
* weather variables can be set by changing weather_type_list on line 6
* once data is downloaded, extract gridded lat/lon coordinates and create shapefiles with:
```
python -W ignore create_grid_cell_shapefiles.py
```
* sample_year (line 4) and sample_weather_var (line 5) need to correspond to one of the files that has already been downloaded by read_gridmet_data.py (only one of the potentially many files downloaded is needed)
* this file will also clip each grid cell shapefile according to the boundary shapefile named on line 8
* this will create a new shapefile for each feature contained in the boundary shapefile
* once grid cell shapefiles are created, weather data can be extracted for each set of grid cells
* this data is aggregated (by averaging) and saved in a timeseries by running
```
python -W ignore aggregate_gridmet_data_to_shape.py
```
* note: this last file will take ~30minutes per weather variable PER YEAR for all counties, so either:
* subset the counties used by subsetting the county shapefile
* run using Longleaf Research computing cluster, making a new job for each weather variable


