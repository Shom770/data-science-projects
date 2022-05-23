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

LONLAT = (-77.28, 39.14)
GO_OUT_LONLAT = (3, 1.75)
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
ax.add_feature(cfeature.OCEAN.with_scale("10m"), zorder=300)
ax.add_feature(cfeature.STATES.with_scale("10m"), lw=1.25, zorder=200)
logger.info("CartoPy setting up finished.")

date_fmt = DAY.strftime('%Y%m%d')
meso_data = Dataset(
    (
        f"http://nomads.ncep.noaa.gov/dods/rtma2p5/"
        f"rtma2p5{date_fmt}/rtma2p5_ges_{DAY.hour}z"
    )
)
logger.info("RTMA data fetched.")

temp_data = 1.8 * (meso_data["tmp2m"][:] - 273) + 32
lons = meso_data["lon"][:]
lats = meso_data["lat"][:]

C = ax.contourf(
    lons, lats, temp_data,
    cmap="coolwarm"
)

fig.colorbar(C)

plt.show()
