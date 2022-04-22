import datetime

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

from metpy.plots import USCOUNTIES

from get_snow_reports import get_reports

STATES = ["MD", "WV", "VA", "DE", "OH", "PA"]
START_TIME = datetime.datetime(2022, 1, 6)
END_TIME = datetime.datetime(2022, 1, 8)

ALL_COLORS = [
    "#bdd8e6", "#6bb0d6", "#3284bf",
    "#07519d", "#082695", "#ffff97",
    "#fdc400", "#ff8801", "#db1300",
    "#9f0002", "#690001", "#330101"
]
ALL_LEVELS = [0.1, 1, 2, 3, 4, 6, 8, 12, 18, 24, 30, 36, 48]

all_reports = get_reports(STATES, START_TIME, END_TIME)
coords = tuple(all_reports.keys())
lons = [tup[1] for tup in coords]
lats = [tup[0] for tup in coords]

extent = (-83.32, -75, 36.63, 40.37)

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("10m"))
ax.add_feature(USCOUNTIES.with_scale("5m"), zorder=200)
ax.add_feature(cfeature.OCEAN.with_scale("10m"), zorder=100)

data = list(all_reports.values())

levels_spec = []
colors_spec = []
if max(data) - max(i for i in data if i != max(data)) > 10:
    for (lat, lon), value in [(key, val) for key, val in all_reports.items() if val == max(data)]:
        lons.remove(lon)
        lats.remove(lat)
        data.remove(value)

for idx, (rmin, rmax) in enumerate(zip(ALL_LEVELS, ALL_LEVELS[1:])):
    if any(rmin <= val < rmax for val in data):
        levels_spec.append(ALL_LEVELS[idx])
        colors_spec.append(ALL_COLORS[idx])

if len(levels_spec) < 2:
    levels_spec = ALL_LEVELS[:2]
    colors_spec = ALL_COLORS[:2]

while levels_spec[-1] < max(data):
    levels_spec.append(ALL_LEVELS[ALL_LEVELS.index(levels_spec[-1]) + 1])
    try:
        colors_spec.append(ALL_COLORS[ALL_COLORS.index(colors_spec[-1]) + 1])
    except IndexError:
        colors_spec.append(ALL_COLORS[-1])

C = ax.tricontourf(lons, lats, data, levels=levels_spec, colors=colors_spec, transform=ccrs.PlateCarree())
fig.colorbar(C, orientation="horizontal", extend="max")
plt.show()
