import functools
import math

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopy.distance
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from scipy.ndimage.filters import gaussian_filter

from reports import all_reports, ReportType


def report_type_metadata(report_type):
    if report_type == ReportType.TORNADO:
        levels = [2, 5, 10, 15, 30, 45, 60, 100]
        colormap = colors.ListedColormap(
            ["#00DC00", "#A5734B", "#FFFF00", "#FF0000", "#F000F0", "#F000F0", "#8200DC", "#00C8C8"]
        )
        norm = colors.BoundaryNorm(levels, colormap.N)
    else:
        levels = [5, 15, 30, 45, 60, 100]
        colormap = colors.ListedColormap(
            ["#A5734B", "#FFFF00", "#FF0000", "#F000F0", "#F000F0", "#8200DC"]
        )
        norm = colors.BoundaryNorm(levels, colormap.N)

    return levels, colormap, norm


DIFF = 1
CROP_DIFF = 0.1
REPORT_TYPE = ReportType.WIND
SIGMA = 0.75
MARKER_MAPPING = {ReportType.TORNADO: "o", ReportType.HAIL: "^", ReportType.WIND: "o"}

LONLAT = (-77.2, 38.1)
GO_OUT_LONLAT = (3, 1.75)

if LONLAT:
    extent = (
        LONLAT[0] - GO_OUT_LONLAT[0], LONLAT[0] + GO_OUT_LONLAT[0],
        LONLAT[1] - GO_OUT_LONLAT[1], LONLAT[1] + GO_OUT_LONLAT[1]
    )
else:
    extent = (-109.291992, -101.887207, 36.862043, 41.393294)

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
extent_lim = (extent[0] - DIFF, extent[1] + DIFF, extent[2] - DIFF, extent[3] + DIFF)

ax.add_feature(cfeature.LAND.with_scale("10m"), zorder=100)
ax.add_feature(cfeature.OCEAN.with_scale("10m"), zorder=200)
ax.add_feature(cfeature.STATES.with_scale("10m"), zorder=300)


ax.set_extent((extent[0] + CROP_DIFF, extent[1] - CROP_DIFF, extent[2] + CROP_DIFF, extent[3] - CROP_DIFF))

reports = all_reports(report_type=REPORT_TYPE, extent=extent_lim)
lons = np.arange(extent[0], extent[1] + 0.1, 0.1)
lats = np.arange(extent[2], extent[3] + 0.1, 0.1)
z_data = []

for idx, lat in enumerate(lats):
    z_data.append([])
    filtered_reports = [report for report in reports if lat - 0.5 <= report[1] <= lat + 0.5]
    for lon in lons:
        report_ct = len([
            report for report in filtered_reports
            if geopy.distance.distance(report[::-1], (lat, lon)).miles <= 25
        ])
        # z_data[-1].append(((report_ct * (REPORT_RADIUS ** 2 * math.pi)) / (25 ** 2 * math.pi)) * 100)
        z_data[-1].append((report_ct / 25) * 100)


levels, cmap, norm = report_type_metadata(REPORT_TYPE)

C = ax.contourf(
    *map(functools.partial(gaussian_filter, sigma=SIGMA), np.meshgrid(lons, lats)), gaussian_filter(z_data, SIGMA),
    levels=levels, cmap=cmap, norm=norm, transform=ccrs.PlateCarree(), zorder=150, extend="max", antialiased=True
)

lon_reports = [report[0] for report in reports]
lat_reports = [report[1] for report in reports]

ax.scatter(
    lon_reports, lat_reports,
    c="black", s=10, marker=MARKER_MAPPING[REPORT_TYPE], transform=ccrs.PlateCarree(), zorder=175
)

CBAR = fig.colorbar(C, ticks=levels[:-1], extend="max", shrink=0.9)
CBAR.set_ticklabels(levels[:-1])

ax.set_title(
    "The actual chance of one or more severe events within 25 miles on June 2nd, 2022",
    fontsize=9,
    loc="left"
)

plt.suptitle(
    f"Estimated Actual {REPORT_TYPE._name_.lower().title()} Probabilities",
    fontsize=13,
    ha="left",
    va="bottom",
    x=0,
    y=1.06,
    fontweight="bold",
    transform=ax.transAxes
)

plt.show()
