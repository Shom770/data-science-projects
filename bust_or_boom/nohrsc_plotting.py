import datetime
import urllib.request
import os

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import xarray

# Remove any .nc files that already exist
directory = next(os.walk("./"))
for file_name in directory[-1]:
    if file_name.endswith(".nc"):
        os.remove(file_name)

DATA_TIME = datetime.datetime(year=2022, month=1, day=17)
FILE_PATH = f"{DATA_TIME.strftime('%Y%m%d%H')}.nc"
URL = (
        f"http://www.nohrsc.noaa.gov/snowfall_v2/data/"
        f"{DATA_TIME.strftime('%Y%m')}/sfav2_CONUS_24h_{DATA_TIME.strftime('%Y%m%d%H')}.nc"
    )

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

levels = [0.1, 1, 2, 3, 4, 6, 8, 12, 16, 20, 24, 30, 36, 48, 60, 72]
cmap = colors.ListedColormap([
    '#bdd7e7', '#6baed6', '#3182bd', '#08519c', '#082694', '#ffff96',
    '#ffc400', '#ff8700', '#db1400', '#9e0000', '#690000', '#ccccff',
    '#9f8cd8', '#7c52a5', '#561c72', '#40dfff'
])
norm = colors.BoundaryNorm(levels, cmap.N)

ax.contourf(lons, lats, snow_data.values, levels, alpha=0.5, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())
plt.show()
