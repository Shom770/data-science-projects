import datetime

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
import numpy as np
from matplotlib.offsetbox import AnchoredText
from scipy.ndimage.filters import gaussian_filter

from historical_hrrr_cape import historical_hrrr_cape


SIGMA = 0.8
DIFF = 0.2
extent = (-79.05, -76.02, 37.585112, 39.56)
extent_lim = (extent[0] - DIFF, extent[1] + DIFF, extent[2] - DIFF, extent[3] + DIFF)

lons_extent = extent[:2]
lats_extent = extent[2:]

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("50m"))
ax.add_feature(cfeature.OCEAN.with_scale("50m"), zorder=100)
ax.add_feature(cfeature.STATES.with_scale("50m"), lw=1.25, zorder=200)

data_time = datetime.datetime.today().replace(hour=18)
go_back = 24
prev_time = data_time - datetime.timedelta(hours=go_back)
lons, lats, cape_contour = historical_hrrr_cape(data_time=data_time, go_back=go_back, extent_lim=extent_lim)

levels = np.arange(-500, 500, 5)

cape_contour[np.where(cape_contour > levels.max())] = levels.max() - 1
cape_contour[np.where(cape_contour < levels.min())] = levels.min()

cmap = cm.get_cmap("coolwarm")
norm = colors.BoundaryNorm(levels, cmap.N)

C = ax.contourf(
    gaussian_filter(lons, SIGMA), gaussian_filter(lats, SIGMA), gaussian_filter(cape_contour, SIGMA), levels,
    cmap=cmap, norm=norm, alpha=0.5, antialiased=True, transform=ccrs.PlateCarree()
)
fig.colorbar(
    C,
    label=(
        f"Difference Between Actual and Forecasted SBCAPE (J/kg)"
    ),
    extend="max",
    aspect=3
)
plt.suptitle(
    f"Bust or Boom?: Surface-Based CAPE",
    fontsize=14,
    ha="left",
    x=0.1529,
    y=0.96,
    fontweight="bold"
)
plt.title(
    (
        f"SBCAPE during {data_time.strftime('%Hz on %m/%d/%Y')} vs "
        f"Forecasted SBCAPE from {prev_time.strftime('%Hz HRRR (%m/%d/%Y)')}"
    ),
    fontsize=10,
    loc="left"
)
ax.add_artist(
    AnchoredText(
        "Made by @AtlanticWx",
        loc="lower right",
        prop={"size": 10},
        frameon=True,
        zorder=300
    )
)
plt.show()
