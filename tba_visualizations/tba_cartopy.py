import json

import cartopy.feature as cfeature
import cartopy.crs as ccrs
import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import AnchoredText
from scipy.ndimage import zoom

SIGMA = 10

extent = (-126.298828, -66.313477, 24.686952, 49.686953)

lats = np.arange(extent[2], extent[3], 1.25)
lons = np.arange(extent[0], extent[1], 1.25)

with open("num_teams_data.json") as file:
    z_data = np.array(json.load(file))

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("110m"), facecolor="#FFF5F0")
ax.add_feature(cfeature.LAKES.with_scale("110m"), zorder=75)
ax.add_feature(cfeature.OCEAN.with_scale("110m"), zorder=100)
ax.add_feature(cfeature.STATES.with_scale("110m"), zorder=200)

levels = np.arange(0, 210, 10)
cmap = cm.get_cmap("Reds")
norm = colors.BoundaryNorm(levels, cmap.N)

C = ax.contourf(
    zoom(lons, SIGMA), zoom(lats, SIGMA), zoom(z_data, SIGMA),
    levels=levels, cmap=cmap, norm=norm, extend="max", zorder=50, antialiased=False
)
fig.colorbar(C, shrink=0.9, label="# of FRC Teams")
ax.add_artist(
    AnchoredText(
        "Made by Shayaan Wadkar",
        loc="lower right",
        prop={"size": 13},
        frameon=True,
        zorder=300
    )
)

ax.set_title(
    "How many FRC teams are there within 100 miles of any given point in the United States?",
    fontsize=10,
    loc="left"
)

plt.suptitle(
    f"Heatmap of FRC Teams Across America",
    fontsize=15,
    ha="left",
    va="bottom",
    x=0,
    y=1.05,
    fontweight="bold",
    transform=ax.transAxes
)

plt.show()
