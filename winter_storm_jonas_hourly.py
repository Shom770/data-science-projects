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

stations_json = session.get("https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-23&network=MD_COOP").json()
for station in stations_json["features"]:
    if station["properties"]["snow"]:
        print(station["properties"]["name"], "=", station["properties"]["snow"], "\"", sep="")

plt.show()
