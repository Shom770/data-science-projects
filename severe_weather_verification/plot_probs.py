import functools
import math

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopy.distance
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage.filters import gaussian_filter

from reports import all_reports, ReportType


DIFF = 1
REPORT_RADIUS = 5
SIGMA = 0.75

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
extent = (-79.9, -74.1, 37.1, 39.9)
extent_lim = (extent[0] - DIFF, extent[1] + DIFF, extent[2] - DIFF, extent[3] + DIFF)

ax.add_feature(cfeature.LAND.with_scale("10m"))
ax.add_feature(cfeature.OCEAN.with_scale("10m"))
ax.add_feature(cfeature.STATES.with_scale("10m"))


ax.set_extent(extent)

reports = all_reports(report_type=ReportType.WIND, extent=extent_lim)
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


C = ax.contourf(
    *map(functools.partial(gaussian_filter, sigma=SIGMA), np.meshgrid(lons, lats)), gaussian_filter(z_data, SIGMA),
    levels=[5, 15, 30, 45, 60]
)
fig.colorbar(C)

plt.show()
