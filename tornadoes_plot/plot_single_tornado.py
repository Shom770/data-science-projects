from operator import itemgetter
from shapefile import Reader

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from metpy.plots import USCOUNTIES

# Constants
EF_COLORS = {
    "EFU": "#e0e0e0",
    "EF0": "#ddffdd",
    "EF1": "#ddffff",
    "EF2": "#ffffcc",
    "EF3": "#ffddbb",
    "EF4": "#ffcccc",
    "EF5": "#ffccff"
}
PADDING = 0.05

# Reading the shapefile of DAT points

shp_pts = Reader("nws_dat_damage_pnts.shp")

info_needed = [
    {"storm_time": record[2], "rating": record[9], "windspeed": record[11], "lat": record[14], "lon": record[15]}
    for record in shp_pts.records()
]

# Setting up CartoPy plot

extent = (
    min(info_needed, key=itemgetter("lon"))["lon"] - PADDING,
    max(info_needed, key=itemgetter("lon"))["lon"] + PADDING,
    min(info_needed, key=itemgetter("lat"))["lat"] - PADDING,
    max(info_needed, key=itemgetter("lat"))["lat"] + PADDING
)

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("50m"))
ax.add_feature(cfeature.OCEAN.with_scale("50m"))
ax.add_feature(USCOUNTIES.with_scale("10m"), lw=1.25)

# Plotting it onto the map

for info in info_needed:
    ax.scatter(info["lon"], info["lat"], c=EF_COLORS[info["rating"]], marker="v", transform=ccrs.PlateCarree())

plt.show()
