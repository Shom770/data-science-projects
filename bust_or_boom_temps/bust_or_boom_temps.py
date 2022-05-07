import bisect
import math
import operator
import datetime

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.font_manager as font_manager
import numpy as np
from scipy.ndimage.filters import gaussian_filter
from matplotlib.offsetbox import AnchoredText

from historical_hrrr_temps import historical_hrrr_temps


extent = (-79.05, -76.02, 37.585112, 39.56)
lons_extent = extent[:2]
lats_extent = extent[2:]

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("50m"))
ax.add_feature(cfeature.OCEAN.with_scale("50m"))
ax.add_feature(cfeature.STATES.with_scale("50m"), lw=1.25)

data_time = datetime.datetime(2021, 2, 18, hour=12)
go_back = 24
layer = "850mb"
prev_time = data_time - datetime.timedelta(hours=go_back)
lons, lats, temp_contour = historical_hrrr_temps(data_time=data_time, go_back=go_back, layer=layer)

temp_contour[np.where(temp_contour > 4.75)] = 4.75
temp_contour[np.where(temp_contour < -5)] = -5

levels = np.arange(-5, 5, 0.25)

cmap = cm.get_cmap("coolwarm")
norm = colors.BoundaryNorm(levels, cmap.N)

C = ax.contourf(
    lons, lats, temp_contour, levels,
    cmap=cmap, norm=norm, alpha=0.5, antialiased=True, transform=ccrs.PlateCarree()
)
fig.colorbar(
    C,
    label=(
        f"Difference Between Actual and Forecasted {layer} Temperatures (F)"
    ),
    extend="max",
    aspect=3
)
plt.suptitle(
    f"Bust or Boom?: {layer} Temps",
    fontsize=14,
    ha="left",
    x=0.1529,
    y=0.96,
    fontweight="bold"
)
plt.title(
    (
        f"{layer} Temps during {data_time.strftime('%Hz on %m/%d/%Y')} vs "
        f"Forecasted {layer} Temps from {prev_time.strftime('%Hz HRRR (%m/%d/%Y)')}"
    ),
    fontsize=10,
    loc="left"
)
ax.add_artist(
    AnchoredText(
        "Made by @AtlanticWx",
        loc="lower right",
        prop={"size": 10},
        frameon=True
    )
)
plt.show()
