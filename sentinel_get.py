from sentinelsat.sentinel import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import datetime
import argparse
import logging
import os
import zipfile

sentineluser = os.environ.get("SENTINEL_USER")
sentinelpwd = os.environ.get("SENTINEL_PWD")

parser = argparse.ArgumentParser(description='Download Sentinel-2  images in time interval.')
parser.add_argument('--start_date', dest='start_date', type=str, required=True)
parser.add_argument('--end_date', dest='end_date', type=str, required=True)
parser.add_argument('--dir_target',dest='dir_target', type=str, required=True)

values = parser.parse_args()

start_date = values.start_date
end_date = values.end_date
path = values.dir_target

logging.basicConfig(format='%(message)s', level='INFO')

api = SentinelAPI(sentineluser, sentinelpwd, 'https://scihub.copernicus.eu/dhus')
footprint = geojson_to_wkt(read_geojson("FCC_map.geojson"))
products = api.query(footprint,
                     date=(datetime.strptime(start_date, '%Y%m%d'), datetime.strptime(end_date,'%Y%m%d')),
                     platformname='Sentinel-2',
                     processinglevel='Level-2A',
                     cloudcoverpercentage=(0, 15))

product_list = api.download_all(products, directory_path=path, max_attempts=10)

files = os.listdir(path)
for file in files:
    if file.endswith('.zip'):
        filePath=path+'/'+file
        zip_file = zipfile.ZipFile(filePath)
        for names in zip_file.namelist():
            zip_file.extract(names, path)
        zip_file.close()