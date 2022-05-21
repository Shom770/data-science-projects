import datetime
from operator import itemgetter
from statistics import NormalDist

import numpy as np
import requests
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
from matplotlib.offsetbox import AnchoredText
from scipy.interpolate import NearestNDInterpolator
from scipy.ndimage.filters import gaussian_filter
from scipy.stats import norm
from plot_cities import get_cities

from nohrsc_plotting import nohrsc_snow
from xmacis import Elements, get_station_data

session = requests.session()


def filter_datapoints(period, data):
    if MONTH:
        return period.month == MONTH and data.snow >= 0.1
    else:
        return data.snow >= 0.1


DIFF = 0.5
SIGMA = 1
MONTH = None
NUM_TO_MONTH = {
    1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
    7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
}
START_DATE = datetime.datetime(2010, 1, 1)
END_DATE = datetime.datetime.today()

extent = (-79.05, -76.02, 37.585112, 39.56)
extent_lim = (extent[0] - DIFF, extent[1] + DIFF, extent[2] - DIFF, extent[3] + DIFF)
bbox_lim = (extent_lim[0], extent_lim[2], extent_lim[1], extent_lim[3])

# Set up CartoPy
fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("50m"))
ax.add_feature(cfeature.OCEAN.with_scale("50m"), zorder=100)
ax.add_feature(cfeature.STATES.with_scale("50m"), lw=1.25, zorder=200)

# Get stations
stations = [stn for stn in session.get(
    f"http://data.rcc-acis.org/StnMeta", params={
        "bbox": ",".join(map(str, bbox_lim)),
        "elems": Elements.SNOW.value,
        "sdate": START_DATE.strftime('%Y-%m-%d'),
        "edate": END_DATE.strftime('%Y-%m-%d'),
    }
).json()["meta"] if any(sid.endswith("3") for sid in stn["sids"])]

all_dps = [
    (
        get_station_data(station["sids"][0], elements=(Elements.SNOW,), start_date=START_DATE, end_date=END_DATE),
        tuple(station["ll"]),
        station["name"]
    )
    for station in stations
]
lons_n, lats_n, snow_n, date, accum_time = nohrsc_snow(extent_lim)
all_dps = [
    (tuple(sorted(map(lambda data: data.snow, res.values()))),) + dp[1:] for dp in all_dps if (
        res := dp[0].filter(condition=filter_datapoints, combine_similar=True)
    )
]  

latlng = [dp[1] for dp in all_dps]


for y, lat in enumerate(lats_n):
    for x, lon in enumerate(lons_n):
        closest_airport = all_dps[min(
            ((idx, (abs(lon - lon_o) ** 2 + abs(lat - lat_o)) ** 0.5) for idx, (lon_o, lat_o) in enumerate(latlng)),
            key=itemgetter(1)
        )[0]]
        all_events = closest_airport[0]
        # Normalize by applying log function to every value
        all_events = [*map(np.log, all_events)]
        snow_log = np.log(snow_n[y, x])

        # Standardize distribution
        all_events_m, all_events_std = np.mean(all_events), np.std(all_events)
        all_events = [(snow - all_events_m) / all_events_std for snow in all_events]

        # Get z-score
        z_score = (snow_log - np.mean(all_events))

        percentile = (1 - norm.sf(z_score)) * 100
        if percentile < 1:
            percentile = 1
        elif percentile > 99:
            percentile = 99

        snow_n[y, x] = percentile

levels = np.arange(1, 100, 1)
levels_c = [10, 25, 50, 75, 90]
cmap = cm.get_cmap("coolwarm_r")
cmap_c = cm.get_cmap("viridis")
norm = colors.BoundaryNorm(levels, cmap.N)
norm_c = colors.BoundaryNorm(levels_c, cmap_c.N)
month_name = NUM_TO_MONTH[MONTH] + " " if MONTH else ""

# Mask numpy array to fill in NaN values
mask = np.where(~np.isnan(snow_n))
interp = NearestNDInterpolator(np.transpose(mask), snow_n[mask])
snow_n = interp(*np.indices(snow_n.shape))

# Plot the result
C = ax.contourf(
    gaussian_filter(lons_n, SIGMA), gaussian_filter(lats_n, SIGMA), gaussian_filter(snow_n, SIGMA),
    levels=levels, cmap=cmap, norm=norm, transform=ccrs.PlateCarree(), antialiased=False
)
CS = ax.contour(
    gaussian_filter(lons_n, SIGMA), gaussian_filter(lats_n, SIGMA), gaussian_filter(snow_n, SIGMA),
    levels=levels_c, cmap=cmap_c, norm=norm_c, transform=ccrs.PlateCarree()
)
ax.clabel(CS, levels_c, inline=True, fontsize=10)

ax.add_artist(
    AnchoredText(
        "Made by @AtlanticWx",
        loc="lower right",
        prop={"size": 10},
        frameon=True,
        zorder=300
    )
)

date_range = (
    f"{(date - datetime.timedelta(hours=accum_time)).strftime('%B %d, %Y')} "
    f"to {date.strftime('%B %d, %Y')}"
)

plt.suptitle(
    f"Percentile of the {date_range} Snowstorm",
    fontsize=13,
    ha="left",
    x=0.1529,
    y=0.96,
    fontweight="bold"
)
plt.title(
    f"How does the {date_range} snowstorm compare to other {month_name}snowstorms?",
    fontsize=9,
    loc="left"
)

cbar = fig.colorbar(
    C,
    label=f"Percentile of Snowstorm Compared to Other {month_name}Snowstorms",
    extend="max",
    ticks=[1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99]
)
cbar.ax.set_yticklabels(["1", "10", "20", "30", "40", "50", "60", "70", "80", "90", "99"])

plt.show()
