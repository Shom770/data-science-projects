from shapefile import Reader

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

extent = (-79.05, -76.02, 37.585112, 39.56)

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("50m"))
ax.add_feature(cfeature.OCEAN.with_scale("50m"))
ax.add_feature(cfeature.STATES.with_scale("50m"), lw=1.25)


shp_pts = Reader("nws_dat_damage_pnts.shp")

info_needed = [
    {"storm_time": record[2], "rating": record[9], "windspeed": record[11], "lat": record[14], "lon": record[15]}
    for record in shp_pts.records()
]

