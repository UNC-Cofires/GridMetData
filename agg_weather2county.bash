#!/bin/bash
#SBATCH --job-name=gridmet_vars
#SBATCH --ntasks=1         # 1 task per job
#SBATCH --cpus-per-task=2  # CPUs per variable processing
#SBATCH --time=24:00:00
#SBATCH --mem=16G
#SBATCH --array=0-2        # Creates 3 separate jobs

module purge
module add python/3.9.6

# Weather variables (matches your code)
WEATHER_TYPES=('pr' 'tmmn' 'tmmx')
NETCDF_KEYS=('precipitation_amount' 'air_temperature' 'air_temperature')

# Get current array index
INDEX=$SLURM_ARRAY_TASK_ID

# Run processing for one variable
python -W ignore aggregate_gridmet_data_to_shape.py \
    --weather-type ${WEATHER_TYPES[$INDEX]} \
    --netcdf-key ${NETCDF_KEYS[$INDEX]} \
    --year-min 2000 \
    --year-max 2024