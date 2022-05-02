import bisect

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
import numpy as np
from scipy.ndimage import zoom

from historical_hrrr import historical_hrrr_snow
from nohrsc_plotting import nohrsc_snow

DIFF = 0.2
ZOOM_LEVEL = 3
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

lons_n, lats_n, snow_n, date = nohrsc_snow(extent_lim)
coords = historical_hrrr_snow(date, extent_lim)

snow_h = []
all_keys = [*coords.keys()]

for lat in lats_n:
    snow_h.append([])
    lat = round(lat, 2)
    for lon in lons_n:
        lon = round(lon, 2)
        try:
            snow_h[-1].append(coords[(lon, lat)])
        except KeyError:
            closest = all_keys[bisect.bisect_left(all_keys, (lon, lat))]
            snow_h[-1].append(coords[closest])

snow_h = np.array(snow_h)
diff_snow = snow_h - snow_n
diff_snow[np.isnan(diff_snow)] = 0
diff_snow = zoom(diff_snow, ZOOM_LEVELgit)

diff_snow[np.where(diff_snow >= 4.75)] = 4.75
diff_snow[np.where(diff_snow < -5)] = -5

levels = np.arange(-5, 5, 0.25)
cmap = cm.get_cmap("coolwarm")
norm = colors.BoundaryNorm(levels, cmap.N)

C = ax.contourf(
    zoom(lons_n, ZOOM_LEVEL), zoom(lats_n, ZOOM_LEVEL), diff_snow, levels,
    cmap=cmap, norm=norm, alpha=0.5, transform=ccrs.PlateCarree(), antialiased=True
)
fig.colorbar(C, extend="max")
plt.show()
