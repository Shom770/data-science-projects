from operator import itemgetter
from shapefile import Reader

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.img_tiles as cimgt
import matplotlib.pyplot as plt
from metpy.plots import USCOUNTIES
from statsmodels.nonparametric.smoothers_lowess import lowess

# Constants
EF_COLORS = {
    "EFU": "#e0e0e0",
    "EF0": "#01B0F1",
    "EF1": "#92D14F",
    "EF2": "#FFFF00",
    "EF3": "#FFC000",
    "EF4": "#C00000",
    "EF5": "#CB00CC"
}
PADDING = 0.15

# Reading the shapefile of DAT points

shp_pts = Reader("nws_dat_damage_pnts.shp")

info_needed = [
    {"storm_time": record[2], "rating": record[9], "windspeed": record[11], "lat": record[14], "lon": record[15]}
    for record in shp_pts.records()
]

# Setting up CartoPy plot

stamen_terrain = cimgt.Stamen('terrain-background')
extent = (
    min(info_needed, key=itemgetter("lon"))["lon"] - PADDING,
    max(info_needed, key=itemgetter("lon"))["lon"] + PADDING,
    min(info_needed, key=itemgetter("lat"))["lat"] - PADDING,
    max(info_needed, key=itemgetter("lat"))["lat"] + PADDING
)

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=stamen_terrain.crs)

ax.set_extent(extent)
ax.add_image(stamen_terrain, 10)

ax.add_feature(cfeature.LAND.with_scale("50m"))
ax.add_feature(cfeature.OCEAN.with_scale("50m"))
ax.add_feature(USCOUNTIES.with_scale("500k"))

# Plotting it onto the map

all_lons = []
all_lats = []

for info in info_needed:
    all_lons.append(info["lon"])
    all_lats.append(info["lat"])
    ax.scatter(info["lon"], info["lat"], c=EF_COLORS[info["rating"]], marker="v", transform=ccrs.PlateCarree())


non_linear_fit = lowess(all_lats, all_lons)
ax.plot(non_linear_fit[:, 0], non_linear_fit[:, 1], transform=ccrs.PlateCarree())
plt.show()
