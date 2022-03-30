import json
from datetime import datetime

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import requests

from metpy.plots import USCOUNTIES

# extent = (-79.602563, -75.723267, 37.035112, 39.724089)
#
# fig: plt.Figure = plt.figure()
# ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
#
# ax.set_extent(extent)
#
# ax.add_feature(cfeature.LAND.with_scale("10m"))
# ax.add_feature(cfeature.OCEAN.with_scale("10m"))
# ax.add_feature(USCOUNTIES.with_scale("5m"))

session = requests.session()

to_write = {}

iad_snow, = session.get(
    "https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-23&station=IAD&network=VA_ASOS"
).json()["features"]

iad_hourlyp = session.get(
    "https://mesonet.agron.iastate.edu/api/1/obhistory.json?date=2016-01-23&station=IAD&network=VA_ASOS"
).json()

dca_snow, = session.get(
    "https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-23&station=DCA&network=VA_ASOS"
).json()["features"]

dca_hourlyp = session.get(
    "https://mesonet.agron.iastate.edu/api/1/obhistory.json?date=2016-01-23&station=DCA&network=VA_ASOS"
).json()

bwi_snow, = session.get(
    "https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-23&station=BWI&network=MD_ASOS"
).json()["features"]

bwi_hourlyp = session.get(
    "https://mesonet.agron.iastate.edu/api/1/obhistory.json?date=2016-01-23&station=BWI&network=MD_ASOS"
).json()

lyh_snow, = session.get(
    "https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-23&station=LYH&network=VA_ASOS"
).json()["features"]

lyh_hourlyp = session.get(
    "https://mesonet.agron.iastate.edu/api/1/obhistory.json?date=2016-01-23&station=LYH&network=VA_ASOS"
).json()

for station in (iad_snow, bwi_snow, dca_snow, lyh_snow):
    to_write[station["properties"]["id"]] = {
        "name": station["properties"]["name"],
        "snow": station["properties"]["snow"],
        "coordinates": station["geometry"]["coordinates"]
    }

for id_, hourly_station in zip(("IAD", "BWI", "DCA", "LYH"), (iad_hourlyp, bwi_hourlyp, dca_hourlyp, lyh_hourlyp)):
    to_write[id_]["hourly_precip"] = []
    for dp in hourly_station["data"]:
        if datetime.fromisoformat(dp["local_valid"]).minute >= 50:
            to_write[id_]["hourly_precip"].append(dp["p01i"])

    ratio = to_write[id_]["snow"] / sum([(precip * 10) for precip in to_write[id_]["hourly_precip"]])

    to_write[id_]["hourly_snow"] = [precip * 10 * ratio for precip in to_write[id_]["hourly_precip"]]

with open("jan_23.json", "w") as file:
    file.write(json.dumps(to_write))

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
