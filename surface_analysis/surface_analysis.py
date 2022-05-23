import datetime
import logging

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import matplotlib.pyplot as plt

from netCDF4 import Dataset

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DIFF = 0.25
LONLAT = (-77.28, 39.14)
GO_OUT_LONLAT = (2.5, 1.5)
DAY = datetime.datetime(2022, 5, 23, 20)

if LONLAT:
    extent = (
        LONLAT[0] - GO_OUT_LONLAT[0], LONLAT[0] + GO_OUT_LONLAT[0],
        LONLAT[1] - GO_OUT_LONLAT[1], LONLAT[1] + GO_OUT_LONLAT[1]
    )
else:
    extent = (-109.291992, -101.887207, 36.862043, 41.393294)

fig: plt.Figure = plt.figure()
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("10m"), zorder=100)
ax.add_feature(cfeature.OCEAN.with_scale("10m"), zorder=200)
ax.add_feature(cfeature.STATES.with_scale("10m"), lw=1.25, zorder=300)
logger.info("CartoPy setting up finished.")

date_fmt = DAY.strftime('%Y%m%d')
meso_data = Dataset(
    (
        f"http://nomads.ncep.noaa.gov/dods/rtma2p5/"
        f"rtma2p5{date_fmt}/rtma2p5_anl_{DAY.hour}z"
    )
)
logger.info("RTMA data fetched.")

temp_data = meso_data.variables["tmp2m"][0][:]
logger.info("Temperature data acquired.")

lons = meso_data.variables["lon"][:]
lats = meso_data.variables["lat"][:]
slo, elo, sla, ela = (extent[0] - DIFF, extent[1] + DIFF, extent[2] - DIFF, extent[3] + DIFF)

home_lat = np.where(
    np.logical_and(np.greater_equal(lats, sla), np.less_equal(lats, ela))
)[0]
all_lats = np.array([lats[lat] for lat in home_lat])

home_lon = np.where(
    np.logical_and(np.greater_equal(lons, slo), np.less_equal(lons, elo))
)[0]
all_lons = np.array([lons[lon] for lon in home_lon])

temp_data = [[1.8 * (temp_data[lat, lon] - 273) + 32 for lon in home_lon] for lat in home_lat]
logger.info("Temperature data converted to Kelvin.")

C = ax.contourf(
    *np.meshgrid(all_lons, all_lats), temp_data,
    cmap="coolwarm", transform=ccrs.PlateCarree(), zorder=150
)

fig.colorbar(C)

plt.show()
