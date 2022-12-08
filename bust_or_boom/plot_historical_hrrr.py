import datetime

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.font_manager as font_manager

from historical_hrrr import historical_hrrr_raw_snow

for font in font_manager.findSystemFonts(["."]):
    font_manager.fontManager.addfont(font)

# Set font family globally
matplotlib.rcParams['font.family'] = 'Inter'

DIFF = 0.2
OPP_DIFF = (0.2, 0.2)
ZOOM_LEVEL = 5

LONLAT = (-77.28, 39.14)
GO_OUT_LONLAT = (1.5, 1)

if LONLAT:
    extent = (
        LONLAT[0] - GO_OUT_LONLAT[0], LONLAT[0] + GO_OUT_LONLAT[0],
        LONLAT[1] - GO_OUT_LONLAT[1], LONLAT[1] + GO_OUT_LONLAT[1]
    )
else:
    extent = (-109.291992, -101.887207, 36.862043, 41.393294)

run_time = datetime.datetime(year=2022, month=1, day=3, hour=7)
extent_lim = (extent[0] - DIFF, extent[1] + DIFF, extent[2] - DIFF, extent[3] + DIFF)
extent_opp = (extent[0] + OPP_DIFF[0], extent[1] - OPP_DIFF[0], extent[2] + OPP_DIFF[1], extent[3] - OPP_DIFF[1])
lons_extent = extent[:2]
lats_extent = extent[2:]

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("50m"))
ax.add_feature(cfeature.OCEAN.with_scale("50m"), zorder=100)
ax.add_feature(cfeature.STATES.with_scale("50m"), lw=1.25, zorder=200)

longitudes, latitudes, snow_totals = historical_hrrr_raw_snow(run_time, extent_lim, go_back=0, goes_out=18)

levels = [0.1, 1, 2, 3, 4, 6, 8, 12, 16, 20, 24, 30, 36, 48, 60, 72]
cmap = colors.ListedColormap(
    [
        '#bdd7e7', '#6baed6', '#3182bd', '#08519c', '#082694', '#ffff96',
        '#ffc400', '#ff8700', '#db1400', '#9e0000', '#690000', '#ccccff',
        '#9f8cd8', '#7c52a5', '#561c72', '#40dfff'
    ]
)
norm = colors.BoundaryNorm(levels, cmap.N)

C = ax.contourf(
    longitudes, latitudes, snow_totals, levels,
    cmap=cmap, norm=norm, alpha=0.5, transform=ccrs.PlateCarree(), antialiased=True
)

plt.show()
