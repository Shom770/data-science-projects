import json

import cartopy.feature as cfeature
import cartopy.crs as ccrs
import geopy.distance
import matplotlib.pyplot as plt
import numpy as np

extent = (-126.298828, -66.313477, 24.686952, 49.439557)

lats = np.arange(extent[2], extent[3], 1.25)
lons = np.arange(extent[0], extent[1], 1.25)

with open("num_teams_data.json") as file:
    z_data = json.load(file)

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("110m"))
ax.add_feature(cfeature.LAKES.with_scale("110m"))
ax.add_feature(cfeature.OCEAN.with_scale("110m"), zorder=100)
ax.add_feature(cfeature.STATES.with_scale("110m"), zorder=200)

C = ax.contourf(
    lons, lats, z_data, zorder=50, antialiased=True
)
fig.colorbar(C)

plt.show()
