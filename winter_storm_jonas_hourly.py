import json

from datetime import datetime, timedelta

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import requests

from matplotlib.animation import FuncAnimation
from pandas import date_range

extent = (-79.602563, -75.723267, 37.035112, 40)
text_lon = sum(extent[:2]) / 2
text_lat = (40 + 39.6) / 2

fig: plt.Figure = plt.figure()
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("10m"))
ax.add_feature(cfeature.OCEAN.with_scale("10m"))
ax.add_feature(cfeature.STATES.with_scale("10m"))

session = requests.session()
lines = []

with open("storm_totals.json", "r") as totals_file:
    storm_totals = json.loads(totals_file.read())


def snow_color_table(total_snow):
    if total_snow == 0:
        return "#ffffff"
    elif 0.1 <= total_snow < 1:
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


def size_table(total_snow):
    if total_snow == 0:
        return 40
    elif 0.1 <= total_snow < 1:
        return 50
    elif 1 <= total_snow < 2:
        return 60
    elif 2 <= total_snow < 3:
        return 70
    elif 3 <= total_snow < 4:
        return 80
    elif 4 <= total_snow < 6:
        return 100
    elif 6 <= total_snow < 8:
        return 120
    elif 8 <= total_snow < 12:
        return 170
    elif 12 <= total_snow < 18:
        return 225
    elif 18 <= total_snow < 24:
        return 275
    elif 24 <= total_snow < 30:
        return 350
    elif 30 <= total_snow < 36:
        return 425
    elif total_snow >= 36:
        return 500


def animation_frames():
    yield from date_range(datetime(2016, 1, 22, 6), periods=48, freq="H").tolist()[1:]


def animate(frame):
    for artist in lines:
        artist.set_visible(False)

    current_time = datetime.fromisoformat(str(frame).replace(" ", "T")) - timedelta(hours=5)

    for station, observations in storm_totals.items():
        total_snow = round(sum(
                observations["hourly_snow"][:current_time.hour if current_time.day == 22 else 24 + current_time.hour]
        ),  1)

        lines.append(ax.scatter(
            *observations["coordinates"],
            c=snow_color_table(total_snow),
            edgecolor="black",
            s=size_table(total_snow),
            transform=ccrs.PlateCarree()
        ))

    lines.append(ax.text(
        text_lon,
        text_lat,
        current_time.strftime("%B %d, %Y at %I:%M %p"),
        size=14,
        horizontalalignment="center",
        bbox={'facecolor': '#c0c0c0', 'edgecolor': 'black', 'boxstyle': 'round'}
    ))

    return lines


anim = FuncAnimation(fig, animate, frames=animation_frames, interval=20, blit=False)

anim.save("./progress.gif")

# stations_json = session.get("https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-23&network=MD_COOP").json()
# stations_json["features"].extend(
#     session.get("https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-23&network=VA_COOP")
#     .json()["features"]
# )
# stations_json["features"].extend(
#     session.get("https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-23&network=WV_COOP")
#     .json()["features"]
# )
#
#
# stations_d2_json = session.get("https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-24&network=MD_COOP").json()
# stations_d2_json["features"].extend(
#     session.get("https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-24&network=VA_COOP")
#     .json()["features"]
# )
# stations_d2_json["features"].extend(
#     session.get("https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-24&network=WV_COOP")
#     .json()["features"]
# )
#
# for station, station_d2 in zip(
#         sorted(
#             stations_json["features"], key=lambda x: x["geometry"]["coordinates"]
#         ),
#         sorted(
#             stations_d2_json["features"], key=lambda x: x["geometry"]["coordinates"]
#         )
# ):
#     long, lat = station["geometry"]["coordinates"]
#     if (
#             station["properties"]["snow"]
#             and extent[0] + 0.02 <= long <= extent[1] - 0.02
#             and extent[2] + 0.02 <= lat <= extent[3] - 0.02
#     ):
#         d2_snow = station_d2["properties"]["snow"] if station_d2["properties"]["snow"] else 0
#         ax.text(long, lat, round(station["properties"]["snow"] + d2_snow, 1))
#
# plt.show()
