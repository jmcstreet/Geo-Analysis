from fiona.crs import from_epsg
import fiona
from shapely.geometry import Point, MultiPoint, LineString, mapping, shape, LinearRing
import geopandas as gpd
import numpy as np
import itertools
import os
import argparse
from haversine import haversine,Unit


def parse_lightning_strike(dir_source):
    lightning_fpath = os.path.join(dir_source,'lightningstrikes_log')
    ls_dates = dict()
    with open(lightning_fpath) as fp:
    #ligthning strikes can occur in the same date...
        count = 1
        for line in fp:
            ls_list = line.strip().split('|')
            lightning_data = ls_list[0] + '_' + ls_list[2] + '_' + ls_list[3]
            #map_ls = ls_list[0] + '|' + count.__str__()
            ls_dates[line.strip()] = lightning_data
            count += 1
    fp.close()
    return ls_dates


def ckdnearest(gdfA, gdfB, gdfB_cols=['geometry']):
    A = np.concatenate(
        [np.array(geom.coords) for geom in gdfA.geometry.tolist()])
    B = [np.array(geom.coords) for geom in gdfB.geometry.tolist()]
    B_ix = tuple(itertools.chain.from_iterable(
        [itertools.repeat(i, x) for i, x in enumerate(list(map(len, B)))]))
    B = np.concatenate(B)
    idx = B.shape[0]
    distances = dict()
    pivot = A[0:][0]
    i = 0
    while i < idx:
        coord = B[0:][i]
        coord = (coord[0],coord[1])
        dist = haversine(pivot, coord, unit=Unit.MILES)
        distances[coord.__str__()] = dist
        i += 1
    return distances

def near_object(distances, max_dist):
    print(distances)
    filtered_distances = {key: value for (key, value) in distances.items() if value < float(max_dist)}
    return filtered_distances

parser = argparse.ArgumentParser(description='Find nearest assets.')
parser.add_argument('--path', dest='path', type=str, required=True)
parser.add_argument('--shapefile',dest='shapefile', type=str, required=True)
values = parser.parse_args()
path = values.path
shapefile = values.shapefile
c = fiona.open(shapefile)
crs = c.crs
boundaries = gpd.GeoDataFrame.from_file(shapefile,crs=from_epsg(4326))

ls_list = parse_lightning_strike(path)
assets = dict()
for i in ls_list:
    ls = i.split('|')
    gdf = gpd.GeoDataFrame([[1, Point(float(ls[3]), float(ls[2]))]], columns=['ID', 'geometry'], crs=from_epsg(4326))
    c = ckdnearest(gdf, boundaries)
    for k in c.keys():
        print('Distance from centroid ' + ls[3] + ',' + ls[2] + ' to POI ' + k.__str__() + ' is ' + c[k].__str__())
    assets[i] = c

newDict = {key: value for (key, value) in assets.items() if near_object(value, 2)}

#As data sample is small and shapefile use in prototype turns out to be a synthetic input dataset, filtered points of interest
#will not be used as input in the last step --> clipping rasters for time series analysis


print('Filtered Dictionary : ')
print(newDict)
