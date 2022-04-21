import datetime

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

from metpy.plots import USCOUNTIES

from get_snow_reports import get_reports

STATES = ["MD", "WV", "PA", "VA", "DE", "NJ"]
START_TIME = datetime.datetime(2022, 1, 6)
END_TIME = datetime.datetime(2022, 1, 8)

extent = (-79.05, -76.02, 37.585112, 39.6)

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("10m"))
ax.add_feature(USCOUNTIES.with_scale("5m"), zorder=200)
ax.add_feature(cfeature.OCEAN.with_scale("10m"), zorder=100)

all_reports = get_reports(STATES, START_TIME, END_TIME)
print(all_reports)

plt.show()
