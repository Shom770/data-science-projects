import datetime
import os
import urllib.request

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray

DATA_TIME = datetime.datetime(year=2022, month=1, day=8)
FILE_PATH = f"{DATA_TIME.strftime('%Y%m%d%H')}.nc"
URL = (
        f"http://www.nohrsc.noaa.gov/snowfall_v2/data/"
        f"{DATA_TIME.strftime('%Y%m')}/sfav2_CONUS_24h_{DATA_TIME.strftime('%Y%m%d%H')}.nc"
    )

if not os.path.exists(f"{DATA_TIME.strftime('%Y%m%d%H')}.nc"):
    urllib.request.urlretrieve(URL, FILE_PATH)

dataset = xarray.open_mfdataset(FILE_PATH)

extent = (-79.05, -76.02, 37.585112, 39.6)

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("50m"))
ax.add_feature(cfeature.OCEAN.with_scale("50m"))
ax.add_feature(cfeature.STATES.with_scale("50m"))

snow_data = dataset.Data * 39

lats = snow_data.lat.values
lons = snow_data.lon.values



ax.contourf(lons, lats, snow_data.values, alpha=0.5)
plt.show()
