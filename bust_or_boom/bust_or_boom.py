import bisect
import datetime
import math
from collections import defaultdict
from datetime import timedelta

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

from historical_hrrr import historical_hrrr_snow
from nohrsc_plotting import nohrsc_snow

for font in font_manager.findSystemFonts(["."]):
    font_manager.fontManager.addfont(font)

# Set font family globally
matplotlib.rcParams['font.family'] = 'Inter'

DIFF = 0.2
ZOOM_LEVEL = 1
extent = (-79.05, -76.02, 37.585112, 39.56)
extent_lim = (extent[0] - DIFF, extent[1] + DIFF, extent[2] - DIFF, extent[3] + DIFF)
lons_extent = extent[:2]
lats_extent = extent[2:]

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("50m"))
ax.add_feature(cfeature.OCEAN.with_scale("50m"))
ax.add_feature(cfeature.STATES.with_scale("50m"))

lons_n, lats_n, snow_n, date, accum_time = nohrsc_snow(extent_lim)
coords = historical_hrrr_snow(date, extent_lim, accum_time, lats_n, lons_n, goes_out=24, occ=2)

snow_h = []
lons_to_lats = defaultdict(list)
for tup in coords.keys():
    lons_to_lats[tup[0]].append(tup[1])

lons = [*lons_to_lats.keys()]


for idx, lat in enumerate(lats_n):
    snow_h.append([])
    lat = round(lat, 2)
    for lon in lons_n:
        lon = round(lon, 2)
        try:
            snow_h[-1].append(coords[(lon, lat)])
        except KeyError:
            closest_lon = lons[bisect.bisect_left(lons, lon)]
            corres_lats = lons_to_lats[closest_lon]
            closest_lat = corres_lats[bisect.bisect_left(corres_lats, lat) - 1]
            snow_h[-1].append(coords[(closest_lon, closest_lat)])

snow_h = np.array(snow_h)

diff_snow = snow_n - snow_h
diff_snow[np.isnan(diff_snow)] = 0
diff_snow = gaussian_filter(diff_snow, ZOOM_LEVEL)

diff_snow[np.where(diff_snow >= 4.75)] = 4.75
diff_snow[np.where(diff_snow < -5)] = -5

if diff_snow.max() < 4.75 and diff_snow.min() > -5:
    abs_min, abs_max = abs(diff_snow.min()), abs(diff_snow.max())
    if abs_min > abs_max:
        levels = np.arange(math.floor(diff_snow.min()), -math.floor(diff_snow.min()), 0.25)
    else:
        levels = np.arange(-math.ceil(diff_snow.max()), math.ceil(diff_snow.max()), 0.25)
else:
    levels = np.arange(-5, 5, 0.25)

cmap = cm.get_cmap("coolwarm_r")
norm = colors.BoundaryNorm(levels, cmap.N)

# These colormaps are used for debugging to see individual snow
levels_s = [0.1, 1, 2, 3, 4, 6, 8, 12, 16, 20, 24, 30, 36, 48, 60, 72]
cmap_s = colors.ListedColormap(
    [
        '#bdd7e7', '#6baed6', '#3182bd', '#08519c', '#082694', '#ffff96',
        '#ffc400', '#ff8700', '#db1400', '#9e0000', '#690000', '#ccccff',
        '#9f8cd8', '#7c52a5', '#561c72', '#40dfff'
    ]
)
norm_s = colors.BoundaryNorm(levels_s, cmap_s.N)

C = ax.contourf(
    gaussian_filter(lons_n, ZOOM_LEVEL), gaussian_filter(lats_n, ZOOM_LEVEL), diff_snow, levels,
    cmap=cmap, norm=norm, alpha=0.5, transform=ccrs.PlateCarree(), antialiased=True
# )
# C = ax.contourf(
#     lons_n, lats_n, snow_n, levels_s,
#     cmap=cmap_s, norm=norm_s, alpha=0.5, transform=ccrs.PlateCarree(), antialiased=True
# )
fig.colorbar(
    C,
    label="Difference Between Total Snow and Forecasted Snow (in.)",
    extend="max"
)
ax.set_title(
    f"Bust or Boom?: from {(date - timedelta(hours=accum_time)).strftime('%B %d, %Y')} to {date.strftime('%B %d, %Y')}",
    fontweight="bold"
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
