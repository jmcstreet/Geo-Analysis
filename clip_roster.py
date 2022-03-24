import geopandas as gpd
from shapely.geometry import Point, box
from shapely.affinity import scale
import rasterio as rio
from rasterio.mask import mask
from fiona.crs import from_epsg
import pycrs
import argparse, os


def getFeatures(gdf):
        """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
        import json
        return [json.loads(gdf.to_json())['features'][0]['geometry']]

def clip_image(path, filename, lat, long):
    print("     Processing " + filename)
    lat = float(lat)
    long = float(long)
    minx, miny = (lat - 0.005), (long - 0.005)
    maxx, maxy = (lat + 0.005), (long + 0.005)
#    26.997810, -80.134900
    bbox = box(minx, miny, maxx, maxy)
    geo = gpd.GeoDataFrame({'geometry': bbox}, index=[0], crs=from_epsg(4326))
    geo.to_crs(epsg=32617)
    filepath = os.path.join(path,filename)
    data = rio.open(filepath)
    try:
        geo = geo.to_crs(crs=data.crs.data)
        print(data.crs.data)
        coords = getFeatures(geo)
        print(coords)
        out_img, out_transform = mask(data, shapes=coords, crop=True)
        out_meta = data.meta.copy()
        print(out_meta)
        epsg_code = int(data.crs.data['init'][5:])
        print(epsg_code)  # 32167
        out_meta.update({"driver": "GTiff",
                         "height": out_img.shape[1],
                         "width": out_img.shape[2],
                         "transform": out_transform,
                         "crs": pycrs.parse.from_epsg_code(epsg_code).to_proj4()}
                        )
        file_wo_ext = os.path.splitext(filename)
        output_file = file_wo_ext[0] + '_crop.tif'
        output_path = os.path.join(path, output_file)
        with rio.open(output_path, "w", **out_meta) as dest:
            dest.write(out_img)
    except:
        print("     Lightning strike out of selected raster")
        return -1



parser = argparse.ArgumentParser(description='Clip rosters...')
parser.add_argument('--dir_source', dest='dir_source', type=str, required=True)
values = parser.parse_args()
path = values.dir_source
output = os.path.join(path, 'output')
current_dir_list = os.listdir(output)
pre_post = ['PRE','PRO']
for ls_dir in current_dir_list:
    for i in pre_post:
        prepost_dir = os.path.join(output, ls_dir, i)
        print("Processing directory " + prepost_dir)
        file_list = os.listdir(prepost_dir)
        for ext in file_list:
            if ext.endswith("crop.tif") or (ext.endswith("aux.xml")):
                os.remove(os.path.join(prepost_dir, ext))
        file_list = os.listdir(prepost_dir)
        for file in file_list:
            try:
                ls_components = ls_dir.split('_')
                clip_image(prepost_dir, file, ls_components[2], ls_components[1])
            except:
                print(ls_dir + " and " + file + " do not match pattern")





#assets = dict()
#for i in ls_list:
#    ls = i.split('|')
#    gdf = gpd.GeoDataFrame([[1, Point(float(ls[2]), float(ls[3]))]], columns=['ID', 'geometry'], crs=from_epsg(4326))
#    gf = gpd.GeoDataFrame({'lat': float(ls[2]), 'lon': float(ls[3]), 'width': 0.1, 'height': 0.1}, index=[0])

#create geodataframe with some variables
#gf = gpd.GeoDataFrame({'lat': 26.207, 'lon': -80.197, 'width': 0.1, 'height': 0.1}, index=[0])

#26.9978, -80.1349
#[[[-81.173,26.207],[-80.197,26.207],[-80.197,27.063],[-81.173,27.063]]]


#clipped = rasterio.open(main_path+)
#show((clipped, 5), cmap='terrain')

#-81.173,26.207],[-80.197,26.207],[-80.197,27.063],[-81.173,27.063],[-81.173,26.207
#set default crs for dataframe
#gf.crs = {'init': 'epsg:4326'}

#create center as a shapely geometry point type and set geometry of dataframe to this
#gf['center'] = gf.apply(lambda x: Point(x['lon'], x['lat']), axis=1)
#gf = gf.set_geometry('center')

#change crs of dataframe to projected crs to enable use of distance for width/height
#gf = gf.to_crs(epsg = 3857)


#create polygon using width and height
#gf['center'] = gf['center'].buffer(1)
#gf['polygon'] = gf.apply(lambda x: scale(x['center'], x['width'], x['height']), axis=1)
#gf = gf.set_geometry('polygon')

#return to inital input crs
#gf = gf.to_crs(epsg = 4326)

# EPSG32617 - WGS 84 / UTM zone 17N - Projected
# gf_proj = gf.to_crs({'init': 'epsg:32617'})
#
# with rio.open(main_path+ndvi) as src:
#     out_image, out_transform = rasterio.mask.mask(src, gf_proj.geometry, crop=True)
#     out_meta = src.meta.copy()
#     out_meta.update({"driver": "GTiff",
#                      "height": out_image.shape[1],
#                      "width": out_image.shape[2],
#                      "transform": out_transform})
#
# with rio.open("NDVI_masked.tiff", "w", **out_meta) as dest:
#     dest.write(out_image)