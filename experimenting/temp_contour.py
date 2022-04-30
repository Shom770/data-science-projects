import logging

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import matplotlib.pyplot as plt

from netCDF4 import Dataset

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

data_nam = Dataset(
    (
        f"http://nomads.ncep.noaa.gov/dods/gfs_0p25/"
        f"gfs20220423/gfs_0p25_12z"
    )
)
logger.info("Loaded NAM dataset")

lons = data_nam.variables["lon"][:]
print(lons)
lats = data_nam.variables["lat"][:]

extent = (-80, -74, 37, 40)
slo, elo = extent[:2]
sla, ela = extent[2:]

fig: plt.Figure = plt.figure()
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("10m"))
ax.add_feature(cfeature.OCEAN.with_scale("10m"))
ax.add_feature(cfeature.STATES.with_scale("10m"))

home_lat = np.where(
    np.logical_and(np.greater_equal(lats, sla), np.less_equal(lats, ela))
)[0]
all_lats = np.array([lats[lat] for lat in home_lat])

home_lon = np.where(
    np.logical_and(np.greater_equal(lons, slo), np.less_equal(lons, elo))
)[0]
all_lons = np.array([lons[lon] for lon in home_lon])

temp_nam = data_nam.variables["crainsfc"][84 / 3]
temps = np.array([[temp_nam[lat, lon] for lon in home_lon] for lat in home_lat])

lons_, lats_ = np.meshgrid(all_lons, all_lats)

levels = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 1, 2, 3, 4, 5]
ticks = levels

CS = ax.contourf(lons_, lats_, temps, transform=ccrs.PlateCarree(), levels=levels, cmap="coolwarm")

ax.set_title("Temperature on April 15th at 21z")
fig.colorbar(CS, ticks=ticks, location="bottom")
plt.show()
