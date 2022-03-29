import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import requests

from metpy.plots import USCOUNTIES

extent = (-79.502563, -75.723267, 38.035112, 39.724089)

fig: plt.Figure = plt.figure()
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("10m"))
ax.add_feature(cfeature.OCEAN.with_scale("10m"))
ax.add_feature(USCOUNTIES.with_scale("5m"))

session = requests.session()

stations_json = session.get("https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-22&network=MD_COOP").json()
stations_json["features"].extend(
    session.get("https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-22&network=VA_COOP")
    .json()["features"]
)
stations_json["features"].extend(
    session.get("https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-22&network=WV_COOP")
    .json()["features"]
)


# stations_d2_json = session.get("https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-24&network=MD_COOP").json()
# stations_d2_json["features"].extend(
#     session.get("https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-24&network=VA_COOP")
#     .json()["features"]
# )
# stations_d2_json["features"].extend(
#     session.get("https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-24&network=WV_COOP")
#     .json()["features"]
# )

for station in stations_json["features"]:
    long, lat = station["geometry"]["coordinates"]
    if (
            station["properties"]["snow"]
            and extent[0] + 0.02 <= long <= extent[1] - 0.02
            and extent[2] + 0.02 <= lat <= extent[3] - 0.02
    ):
        ax.text(long, lat, round(station["properties"]["snow"]))

plt.show()
