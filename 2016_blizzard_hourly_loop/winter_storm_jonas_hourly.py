import json

from datetime import datetime, timedelta
from operator import itemgetter

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import requests

from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import AnchoredText
from pandas import date_range

extent = (-79.602563, -75.723267, 37.035112, 39.9)

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("10m"))
ax.add_feature(cfeature.OCEAN.with_scale("10m"))
ax.add_feature(cfeature.STATES.with_scale("10m"))

for font in font_manager.findSystemFonts(["."]):
    font_manager.fontManager.addfont(font)

# Set font family globally
matplotlib.rcParams['font.family'] = 'Inter'

POINTS_BETWEEN = 5
ALL_COLORS = [
    "#bdd8e6", "#6bb0d6", "#3284bf",
    "#07519d", "#082695", "#ffff97",
    "#fdc400", "#ff8801", "#db1300",
    "#9f0002", "#690001", "#330101"
]
ALL_LEVELS = [0.1, 1, 2, 3, 4, 6, 8, 12, 18, 24, 30, 36]

session = requests.session()
lines = []
visited = set()

with open("storm_totals.json", "r") as totals_file:
    storm_totals = json.loads(totals_file.read())


def snow_color_table(total_snow):
    if 0.1 <= total_snow < 1:
        return "#bdd8e6"
    elif 1 <= total_snow < 2:
        return "#6bb0d6"
    elif 2 <= total_snow < 3:
        return "#3284bf"
    elif 3 <= total_snow < 4:
        return "#07519d"
    elif 4 <= total_snow < 6:
        return "#082695"
    elif 6 <= total_snow < 8:
        return "#ffff97"
    elif 8 <= total_snow < 12:
        return "#fdc400"
    elif 12 <= total_snow < 18:
        return "#ff8801"
    elif 18 <= total_snow < 24:
        return "#db1300"
    elif 24 <= total_snow < 30:
        return "#9f0002"
    elif 30 <= total_snow < 36:
        return "#690001"
    elif total_snow >= 36:
        return "#330101"

    return "#ffffff"


def distance(c1, c2):
    return (abs(c1[0] - c2[0]) ** 2 + abs(c1[1] - c2[1]) ** 2) ** 0.5


def adjacent_stations(coords, stn_name):
    res = sorted(
        [
            (name, distance(stn_data["coordinates"], coords), tuple(stn_data["coordinates"]))
            for name, stn_data in storm_totals.items()
            if name != stn_name
        ], key=itemgetter(1)
    )
    yield from res


def animation_frames():
    yield from date_range(datetime(2016, 1, 22, 6), periods=48, freq="H").tolist()


def animate(frame):
    global visited
    visited = set()

    for artist in lines[:]:
        try:
            for col in artist.collections:
                col.set_visible(False)
        except AttributeError:
            artist.set_visible(False)

    current_time = datetime.fromisoformat(str(frame).replace(" ", "T")) - timedelta(hours=5)

    corresponding_coords = []
    coords_to_snow = {}
    all_obs = []
    for station, observations in storm_totals.items():
        total_snow = round(sum(
                observations["hourly_snow"][:current_time.hour if current_time.day == 22 else 24 + current_time.hour]
        ),  1)
        all_obs.append((observations["name"], total_snow))

        corresponding_coords.extend(observations["coordinates"])
        coords_to_snow[tuple(observations["coordinates"])] = total_snow

        ct = 0
        for closest in adjacent_stations(observations["coordinates"], station):
            stn_snow = round(sum(
                storm_totals[closest[0]][
                    "hourly_snow"
                ][:current_time.hour if current_time.day == 22 else 24 + current_time.hour]
            ), 1)
            if closest[0] in visited:
                continue
            elif ct > 3:
                break
            elif snow_color_table(stn_snow) != snow_color_table(total_snow):
                cc = closest[-1]  # The coordinates for one of the stations close to it in a different zone
                dist_lon = abs(cc[0] - observations["coordinates"][0])
                min_lon = min((cc[0], observations["coordinates"][0]))

                dist_lat = abs(cc[1] - observations["coordinates"][1])
                min_lat = min((cc[1], observations["coordinates"][1]))

                stn_snow = round(sum(
                    storm_totals[closest[0]][
                        "hourly_snow"
                    ][:current_time.hour if current_time.day == 22 else 24 + current_time.hour]
                ), 1)
                diff_snow = abs(stn_snow - total_snow)
                min_snow, stn_min = min(((stn_snow, closest[0]), (total_snow, station)), key=itemgetter(0))

                between_coords = sorted([
                    (
                        min_lon + dist_lon * (num / POINTS_BETWEEN), min_lat + dist_lat * (num / POINTS_BETWEEN)
                    ) for num in range(1, POINTS_BETWEEN)
                ], key=lambda coord: distance(coord, storm_totals[stn_min]["coordinates"]))

                for coord_num, bet_coord in enumerate(between_coords, start=1):
                    pt_snow = min_snow + diff_snow * (coord_num / POINTS_BETWEEN)
                    corresponding_coords.extend(bet_coord)
                    coords_to_snow[tuple(bet_coord)] = pt_snow
                ct += 1

        visited.add(station)

    lats_uni = corresponding_coords[1::2]
    lons_uni = corresponding_coords[::2]

    data = [
        coords_to_snow[(lon, lat)] for lon, lat in zip(lons_uni, lats_uni)
    ]
    maximum_val = max(data)
    if maximum_val >= 0.1:
        for idx, num in enumerate(ALL_LEVELS):
            if num <= maximum_val:
                break

        if idx == 0:
            levels_frame = ALL_LEVELS[:2]
            colors_frame = ALL_COLORS[:2]
        else:
            levels_frame = ALL_LEVELS[:idx + 1]
            colors_frame = ALL_COLORS[:idx + 1]
        
        try:
            lines.append(cont := ax.tricontourf(
                lons_uni,
                lats_uni,
                data,
                alpha=0.5,
                levels=levels_frame,
                colors=colors_frame,
                transform=ccrs.PlateCarree()
            ))
        except TypeError:  # Shape is smaller than (2, 2), usually at the start
            pass

    cur_time = AnchoredText(
        current_time.strftime("%B %d, %Y at %I:%M %p"),
        loc='upper center',
        prop={"size": 14},
        frameon=True
    )

    lines.append(ax.add_artist(cur_time))

    return lines


anim = FuncAnimation(fig, animate, frames=animation_frames, blit=False)

plt.show()
