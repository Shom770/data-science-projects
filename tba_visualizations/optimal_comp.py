import json

import cartopy.feature as cfeature
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

extent = (-126.298828, -66.313477, 24.686952, 49.686953)

with open("all_teams.json") as file:
    all_teams = json.load(file)

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("110m"), facecolor="#FFF5F0")
ax.add_feature(cfeature.LAKES.with_scale("110m"), zorder=75)
ax.add_feature(cfeature.OCEAN.with_scale("110m"), zorder=100)
ax.add_feature(cfeature.STATES.with_scale("110m"), zorder=200)

lons = [tup[0] for tup in all_teams.values()]
lats = [tup[1] for tup in all_teams.values()]

avg_lon = sum(lons) / len(lons)
avg_lat = sum(lats) / len(lats)

ax.scatter(avg_lon, avg_lat, transform=ccrs.PlateCarree())

plt.show()
