import bisect

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.colors as colors

from historical_hrrr import historical_hrrr_snow
from nohrsc_plotting import nohrsc_snow

DIFF = 0.2
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

levels = [0, 1, 2, 3, 4, 6, 8, 12, 16, 20, 24, 30, 36, 48, 60, 72]
cmap = colors.ListedColormap([
    '#bdd7e7', '#6baed6', '#3182bd', '#08519c', '#082694', '#ffff96',
    '#ffc400', '#ff8700', '#db1400', '#9e0000', '#690000', '#ccccff',
    '#9f8cd8', '#7c52a5', '#561c72', '#40dfff'
])
norm = colors.BoundaryNorm(levels, cmap.N)

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


ax.contourf(lons_n, lats_n, snow_h, levels, cmap=cmap, norm=norm, alpha=0.5, transform=ccrs.PlateCarree())
plt.show()
