import bisect
import datetime
from operator import itemgetter

import requests
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText

from plot_cities import get_cities

from nohrsc_plotting import nohrsc_snow
from xmacis import Elements, get_station_data

session = requests.session()


DIFF = 0.5
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
    (res,) + dp[1:] for dp in all_dps if (
        res := dp[0].filter(condition=lambda cond: cond.snow >= 0.1, combine_similar=True)
    )
]

for y, lat in enumerate(lats_n):
    for x, lon in enumerate(lons_n):
        closest_airport = all_dps[bisect.bisect_left(all_dps, (lon, lat), key=itemgetter(1))]
        print((lon, lat), closest_airport[-1])
        all_events = sorted(map(lambda data: data.snow, closest_airport[0].values()))
        percentile = round(bisect.bisect_left(
            all_events,
            snow_n[y, x]
        ) / len(all_events))
        if percentile < 1:
            percentile = 1
        elif percentile > 99:
            percentile = 99

        snow_n[y, x] = percentile

# Plot the result
ax.add_artist(
    AnchoredText(
        "Made by @AtlanticWx",
        loc="lower right",
        prop={"size": 10},
        frameon=True,
        zorder=300
    )
)
plt.show()
