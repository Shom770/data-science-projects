import datetime
import functools

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopy.distance
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import AnchoredText
from scipy.ndimage.filters import gaussian_filter
from shapely import geometry

from outlooks import get_risks
from reports import all_reports, ReportType


DIFF = 1
CROP_DIFF = 0.1
REPORT_TYPE = ReportType.WIND
SIGMA = 0.75
MARKER_MAPPING = {ReportType.TORNADO: "o", ReportType.HAIL: "^", ReportType.WIND: "o"}
DATE = datetime.datetime(2022, 6, 2)

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

reports = all_reports(report_type=REPORT_TYPE, extent=extent_lim, day=DATE)
all_polygons = get_risks(DATE, REPORT_TYPE)

lons = np.arange(extent[0], extent[1] + 0.1, 0.1)
lats = np.arange(extent[2], extent[3] + 0.1, 0.1)
z_data = []

for idx, lat in enumerate(lats):
    z_data.append([])
    filtered_reports = [report for report in reports if lat - 0.5 <= report[1] <= lat + 0.5]
    for lon in lons:
        point = geometry.Point(lon, lat)
        report_ct = len([
            report for report in filtered_reports
            if geopy.distance.distance(report[::-1], (lat, lon)).miles <= 25
        ])
        # z_data[-1].append(((report_ct * (REPORT_RADIUS ** 2 * math.pi)) / (25 ** 2 * math.pi)) * 100)
        verification = (report_ct / 25) * 100
        for percentage, polygons in all_polygons.items():
            if any(polygon.contains(point) for polygon in polygons):
                predicted_probs = percentage
                break
        else:
            predicted_probs = 1

        z_data[-1].append(verification / predicted_probs)

cmap = cm.get_cmap("coolwarm_r")
levels = np.concatenate((np.arange(0.01, 1, 0.1), np.arange(1, 5.6, 0.5)))
norm = colors.BoundaryNorm(levels, cmap.N)

C = ax.contourf(
    *map(functools.partial(gaussian_filter, sigma=SIGMA), np.meshgrid(lons, lats)), gaussian_filter(z_data, SIGMA),
    levels=levels, cmap=cmap, norm=norm, transform=ccrs.PlateCarree(), zorder=150, extend="max", antialiased=False
)

lon_reports = [report[0] for report in reports]
lat_reports = [report[1] for report in reports]

ax.scatter(
    lon_reports, lat_reports,
    c="black", s=10, marker=MARKER_MAPPING[REPORT_TYPE], transform=ccrs.PlateCarree(), zorder=175
)

CBAR = fig.colorbar(C, ticks=[0.01, 0.25, 0.5, 0.75, 1, 2, 3, 4, 5], extend="max", shrink=0.9, label="Verification (%)")
CBAR.set_ticklabels(["0.01x", "0.25x", "0.5x", "0.75x", "1x", "2x", "3x", "4x", "5x"])

ax.set_title(
    (
        f"The actual {REPORT_TYPE._name_.lower()} gprobabilities "
        f"compared to the forecasted {REPORT_TYPE._name_.lower()} probabilities from SPC"
    ),
    fontsize=9,
    loc="left"
)

plt.suptitle(
    f"Bust or Boom: {DATE.strftime('%B %d, %Y')}",
    fontsize=13,
    ha="left",
    va="bottom",
    x=0,
    y=1.06,
    fontweight="bold",
    transform=ax.transAxes
)

ax.add_artist(
    AnchoredText(
        "Made by @AtlanticWx",
        loc="lower right",
        prop={"size": 10},
        frameon=True,
        zorder=350
    )
)

plt.show()
