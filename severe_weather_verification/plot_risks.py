import datetime
import functools
import json
import math

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geojsoncontour
import geopy.distance
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import shapely.geometry
from matplotlib.offsetbox import AnchoredText
from scipy.ndimage.filters import gaussian_filter

from reports import all_reports, ReportType


DIFF = 1
COLOR_MAPPING = ["#66A366", "#FFE066", "#FFA366", "#E06666", "#EE99EE"]
CROP_DIFF = 0.1
REPORT_RADIUS = 5
REPORT_TYPE = ReportType.WIND
SIGMA = 1
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
lons = np.arange(extent[0], extent[1] + 0.1, 0.1)
lats = np.arange(extent[2], extent[3] + 0.1, 0.1)
z_data = []
sig_z_data = []

for idx, lat in enumerate(lats):
    z_data.append([])
    sig_z_data.append([])
    filtered_reports = [report for report in reports if lat - 0.5 <= report[1] <= lat + 0.5]
    for lon in lons:
        report_ct = 0
        sig_ct = 0
        for report in filtered_reports:
            if geopy.distance.distance((report[1], report[0]), (lat, lon)).miles <= 25:
                report_ct += 1
                if REPORT_TYPE == ReportType.TORNADO and report[-1] == "UNK" and int(report[-1]) >= 2:
                    sig_ct += 1
                elif REPORT_TYPE == ReportType.WIND and report[-1] != "UNK" and int(report[-1]) >= 65:
                    sig_ct += 1
                elif REPORT_TYPE == ReportType.HAIL and int(report[-1]) >= 200:
                    sig_ct += 1

        # z_data[-1].append(((report_ct * (REPORT_RADIUS ** 2 * math.pi)) / (25 ** 2 * math.pi)) * 100)
        z_data[-1].append(((report_ct * (REPORT_RADIUS ** 2 * math.pi)) / (25 ** 2 * math.pi)) * 100)
        sig_z_data[-1].append(((sig_ct * (REPORT_RADIUS ** 2 * math.pi)) / (25 ** 2 * math.pi)) * 100)

z_data = np.array(z_data)
sig_z_data = np.array(sig_z_data)
z_data[np.where(z_data > 60)] = 60.1

C = ax.contourf(
    *map(functools.partial(gaussian_filter, sigma=SIGMA), np.meshgrid(lons, lats)), gaussian_filter(z_data, SIGMA),
    transform=ccrs.PlateCarree(), zorder=150, extend="max", antialiased=True
)
for risks in json.loads(geojsoncontour.contourf_to_geojson(contourf=C))["features"]:
    if risks["properties"]["title"].startswith("0.00"):
        color = "#FFFFFF"
    else:
        if risks["properties"]["title"].startswith("5.00"):
            color = COLOR_MAPPING[0]
        elif risks["properties"]["title"].startswith("15.00"):
            color = COLOR_MAPPING[1]
        elif risks["properties"]["title"].startswith("30.00") or risks["properties"]["title"].startswith("45.00"):
            color = COLOR_MAPPING[2]

    for risk in risks["geometry"]["coordinates"]:
        ax.fill(*shapely.geometry.Polygon(risk[0]).exterior.xy, color=color, zorder=150, transform=ccrs.PlateCarree())

plt.show()

if (sig_z_data >= 10).any():
    C1 = ax.contourf(
        *map(functools.partial(gaussian_filter, sigma=SIGMA), np.meshgrid(lons, lats)), gaussian_filter(sig_z_data, SIGMA),
        levels=[10, 100], hatches=["////"], colors=["#FFFFFF00"], transform=ccrs.PlateCarree(), zorder=175
    )
    for risks in json.loads(geojsoncontour.contourf_to_geojson(contourf=C1))["features"]:
        sig_polygons.append([])

        for risk in risks["geometry"]["coordinates"]:
            sig_polygons[-1].append(shapely.geometry.Polygon(risk[0]))

CBAR = fig.colorbar(C, extend="max", shrink=0.9)

ax.set_title(
    f"The actual chance of one or more severe events within 25 miles on {DATE.strftime('%B %d, %Y')}",
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
