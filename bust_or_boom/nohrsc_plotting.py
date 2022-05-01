import datetime
import urllib.request
import os

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import xarray

# Remove any .nc files that already exist
directory = next(os.walk("./"))
for file_name in directory[-1]:
    if file_name.endswith(".nc"):
        os.remove(file_name)

DATA_TIME = datetime.datetime(year=2022, month=1, day=7)
FILE_PATH = f"{DATA_TIME.strftime('%Y%m%d%H')}.nc"
URL = (
        f"http://www.nohrsc.noaa.gov/snowfall_v2/data/"
        f"{DATA_TIME.strftime('%Y%m')}/sfav2_CONUS_24h_{DATA_TIME.strftime('%Y%m%d%H')}.nc"
    )

urllib.request.urlretrieve(URL, FILE_PATH)

dataset = xarray.open_mfdataset(FILE_PATH)


def nohrsc_snow():
    snow_data = dataset.Data * 39.3700787

    lats = snow_data.lat.values
    lons = snow_data.lon.values

    return lons, lats, snow_data