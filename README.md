# geonalysis

## Pre-requirements
Python 3.5+ and pip must be installed (packages were coded and tested on Python 3.7)
Create your free Sentinel Copernicus account for downloading satellite images from the official repository 
(https://scihub.copernicus.eu/dhus). Save your new credentials and create the following environmental variables in OS. 
	- SENTINEL_USER  —> your user id
	- SENTINEL_PWD  —> your password
For Linux OS or MacOS, open CLI and type SENTINEL_USER=‘your user id’ and then SENTINEL_PWD=‘your password’

Jupyter notebooks must also be installed to run final tests.

Python requirements 
You will need the following packages, run the following pip commands (and if those available, run pip --upgrade):

  pip install sentinelsat
  pip install sentinelsat
  pip install numpy
  Pip install scipy
  Pip install geopandas
  Pip install shapely
  Pip install haversine
  pip install rasterio
  pip install fiona
  pip install pycrs
  pip install itertools
  Pip install argparse
  Pip install Fiona
  Pip install re
  Pip install datetime
  Pip install fnmatch
  Pip install argparse
  Pip install os
  Pip install shutil
  Pip install zipfile
  Pip install logging
  Pip install asyncio
  Pip install aiohttp
  Pip install aiowwln


## Instructions
Steps to run the project (it needs to be run in the same order as listed below). 
Although scripts supports multiple configurations, commands and parameteres were run within the same project folder structure:

1. "sentinel_get.py --start_date 20190410 --end_date 20190710 --dir_target ."
2. "biomass_calculation.py --dir_source ."
3. "nearest_asset.py --path . —shapefile ./TOJ_Planning/CRA_proj.shp"
4. "clip_roster.py --dir_source ."
  
## Analyze and test outputs
1. Run Jypyter notebooks (one per lighting strike observation). Run command jupyter lab
	- LightStrike20190601.ipynb
	- LightStrike20190601_2.ipynb
	- LightStrike20190601_3.ipynb
	- LightStrike20190514.ipynb
	- LightStrike20190515.ipynb

Note when running Jupyter notebooks below hardcoded variables point to working directory where output and code reside.
If file structure needs to be changed , modify variables so they point to the newly created output structure. See below:
	setfilepath1 = './output/20190514_26.9611_-80.5122/PRE/20190429NDVI_crop.tif'
	setfilepath2 = './output/20190514_26.9611_-80.5122/PRO/20190519NDVI_crop.tif'

Note, static versions of notebooks are also available for easy sharing, or in case of any technical problem
1. LightStrike20190601.html
2. LightStrike20190601_2.html
3. LightStrike20190601_3.html
4. LightStrike20190514.html
5. LightStrike20190515.html
