import os

import boto3
from botocore import UNSIGNED
from botocore.config import Config
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import xarray

# Remove any .grib2 files that already exist
directory = next(os.walk("./"))
for file_name in directory[-1]:
    if file_name.endswith(".grib2") or file_name.endswith(".idx"):
        os.remove(file_name)

BUCKET_NAME = 'noaa-hrrr-bdp-pds'
S3_OBJECT = 'hrrr.20190113/conus/hrrr.t00z.wrfsfcf36.grib2'

FILE_PATH = S3_OBJECT.split("/")[-1]

if not os.path.exists(FILE_PATH):
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=S3_OBJECT)['Body'].read()

    with open(FILE_PATH, "wb") as file:
        file.write(obj)

extent = (-79.05, -76.02, 37.585112, 39.6)

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("50m"))
ax.add_feature(cfeature.OCEAN.with_scale("50m"))
ax.add_feature(cfeature.STATES.with_scale("50m"))

dataset = xarray.open_dataset(
    FILE_PATH,
    engine="cfgrib",
    filter_by_keys={'stepType': 'accum', 'typeOfLevel': 'surface'}
)
lons = dataset["longitude"].values
lats = dataset["latitude"].values

levels = [0.1, 1, 2, 3, 4, 6, 8, 12, 16, 20, 24, 30, 36, 48, 60, 72]
cmap = colors.ListedColormap([
    '#bdd7e7', '#6baed6', '#3182bd', '#08519c', '#082694', '#ffff96',
    '#ffc400', '#ff8700', '#db1400', '#9e0000', '#690000', '#ccccff',
    '#9f8cd8', '#7c52a5', '#561c72', '#40dfff'
])
norm = colors.BoundaryNorm(levels, cmap.N)

ax.contourf(
    lons, lats, dataset["asnow"].values * 39.3700787, levels,
    alpha=0.5, cmap=cmap, norm=norm, transform=ccrs.PlateCarree()
)
plt.show()
