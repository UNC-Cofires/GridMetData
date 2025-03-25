#!/bin/bash
#SBATCH --job-name=preprocess
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=01:30:00
#SBATCH --mem=9000m

module purge
module add python/3.9.6

# Run preprocessing steps
python -W ignore read_gridmet_data.py
python -W ignore create_gridcell_shapefiles.py
