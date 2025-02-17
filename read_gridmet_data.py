import os
import gridmetter as gdmt

year_min = 2000 # initial year for historical data
year_max = 2024 # final year for historical data
weather_type_list = ['pr', 'tmmn', 'tmmx'] # list of weather variables to download/extract
# NOTE: temperature data is in 'Kelvin' (273K = 0C, 305K = 32C, 373K = 100C)
# make a new folder for downloaded data
weather_output_folder = 'WeatherData'
os.makedirs(weather_output_folder, exist_ok = True)

# load netcdf (.nc) files from GridMet api
for wt in weather_type_list:
  for curr_yr in range(year_min, year_max + 1):
    # print out updates for data reading
    print('Read GridMetData from: ', end = " ")
    print(curr_yr, end = " ")
    print(wt)
    # if the data file is already in the output directory, it skips over that file (no need to duplicate downloads)
    if not os.path.isfile(os.path.join(weather_output_folder, wt + '_' + str(curr_yr) + '.nc')):
      # read gridmet data using function from gridmetter.py
      gdmt.read_gridmet_api(wt + '_' + str(curr_yr) + '.nc', weather_output_folder)
