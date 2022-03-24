import shutil
import rasterio as rio
import numpy
import argparse
import os
import fnmatch
from re import search


#criteria_flag means prior strike (0) or after strike (1)
#search_date %Y%M%D format
def fetch_images(path, search_date, criteria_flag):
    os.chdir(path)
    dirs = fnmatch.filter(os.listdir(path), '*.SAFE')
    dirs = filter_dirs(dirs, search_date, criteria_flag)
    band_dirs = dict()
    for dir in dirs:
        dir_path = os.path.join(dir, 'GRANULE')
        current_dir_list = os.listdir(dir_path)
        jp2_dir = os.path.join(dir_path, current_dir_list[0], 'IMG_DATA', 'R10m')
        jp2s = os.listdir(jp2_dir)
        bands = dict()
        bands['path'] = jp2_dir
        for jp2 in jp2s:
            if search('_B02_10m.jp2', jp2):
                bands['b2'] = jp2
            elif search('_B04_10m.jp2', jp2):
                bands['b4'] = jp2
            elif search('_B08_10m.jp2', jp2):
                bands['b8'] = jp2
        obs_date = dir[11:19]
        band_dirs[obs_date] = bands
    return band_dirs

#Discard directories not satisfying date criteria_flag
def filter_dirs(dirs,search_date, criteria_flag):
    filtered_dirs = list()
    for dirname in dirs:
        parse_criteria = r"'(\d[8])'"
        obs_date = dirname[11:19]
#        m = search(parse_criteria, dirname)
#        new_date = datetime.strptime(obs_date, '%Y%m%d')
        if (criteria_flag == 0):
            #before date
            if obs_date < search_date:
                filtered_dirs.append(dirname)
        elif (criteria_flag == 1):
            if obs_date > search_date:
                filtered_dirs.append(dirname)
    return filtered_dirs

def calculate_ndvis(dir_source, dir_target, b4_filename, b8_filename, idate):
    b4_path = os.path.join(dir_source,b4_filename)
    b8_path = os.path.join(dir_source,b8_filename)
    b4 = rio.open(b4_path)
    red = b4.read()
    b8 = rio.open(b8_path)
    nir = b8.read()
##ndvi = (NIR-RED)/(NIR+RED)
    numpy.seterr(divide='ignore', invalid='ignore')
# Create an NDVI image
    profile = b8.meta
    aff = b8.transform
    oviews = b8.overviews(1)  # list of overviews from biggest to smallest
    oview = oviews[1]  # Use second-highest resolution overview
#nir = b8.read(1, out_shape=(1, int(b8.height // oview), int(b8.width // oview)))
    newaff = rio.Affine(aff.a * oview, aff.b, aff.c, aff.d, aff.e * oview, aff.f)
    ndvi = (nir.astype(float) - red.astype(float)) / (nir+red)
    profile.update(
        dtype=rio.float32,
        driver='GTiff',
        transform=newaff)
    fname = idate+'NDVI.tiff'
    ndvi_filepath = os.path.join(dir_target, fname)
#    output_ndvi = os.open(ndvi_fn, 'wb')
#    print('Generating file '+output_ndvi+'...')
    with rio.open(ndvi_filepath, 'w', **profile) as ndvif:
        ndvif.write(ndvi.astype(rio.float32))
        ndvif.close()

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


parser = argparse.ArgumentParser(description='Calculates biomass index.')
parser.add_argument('--dir_source', dest='dir_source', type=str, required=True)
values = parser.parse_args()
path = values.dir_source
output = os.path.join(path, 'output')
if not os.path.exists(output):
    os.makedirs(output)
else:
    with os.scandir(output) as entries:
        for entry in entries:
            if entry.is_file() or entry.is_symlink():
                os.remove(entry.path)
            elif entry.is_dir():
                shutil.rmtree(entry.path)
print("Calculating biomass index...")
lighting_list = parse_lightning_strike(path)
for lighting_date in lighting_list:
    lightning_date = lighting_date[0:8]
    prior_bands = fetch_images(path, lighting_date, 0)
    post_bands = fetch_images(path, lighting_date, 1)
    ndvi_fn = lighting_list[lighting_date]
    target_dir = os.path.join(output, ndvi_fn)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    else:
        #clear previous directory content
        with os.scandir(target_dir) as entries:
            for entry in entries:
                if entry.is_file() or entry.is_symlink():
                    os.remove(entry.path)
                elif entry.is_dir():
                    shutil.rmtree(entry.path)
    pre_dir = os.path.join(target_dir, 'PRE')
    os.makedirs(pre_dir)
    post_dir = os.path.join(target_dir, 'PRO')
    os.makedirs(post_dir)
    print("Processing " + pre_dir)
    for k in sorted(prior_bands.keys()):
        try:
            print("     Calculating over file " + prior_bands[k]['path'])
            calculate_ndvis(prior_bands[k]['path'], pre_dir, prior_bands[k]['b4'], prior_bands[k]['b8'], k)
        except:
            print("     File " + prior_bands[k]['path'] +" missing bands or corrupted")
    print("Processing " + post_dir)
    for k in sorted(post_bands.keys(), reverse=True):
        try:
            print("     Calculating over file " + post_bands[k]['path'])
            calculate_ndvis(post_bands[k]['path'], post_dir, post_bands[k]['b4'], post_bands[k]['b8'], k)
        except:
            print("     File " + post_bands[k]['path'] + " missing bands or corrupted")

#print('Generating file '+output_rgb+'...')

# Create an RGB image
#with rio.open(output_rgb, 'w', driver='Gtiff', width=b4.width, height=b4.height,
#              count=3, crs=b4.crs, transform=b4.transform, dtype=b4.dtypes[0]) as rgb:
#    rgb.write(b2.read(1), 1)
#    rgb.write(b3.read(1), 2)
#    rgb.write(b4.read(1), 3)
#    rgb.close()


#plt.imsave("ndvi_cmap.png", ndvi.astype(rio.float32), cmap=plt.cm)