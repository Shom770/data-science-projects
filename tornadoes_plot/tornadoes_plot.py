import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import pandas as pd

from metpy.plots import USCOUNTIES

EF_COLORS = ("#e0e0e0", "#ddffdd", "#ddffff", "#ffffcc", "#ffddbb", "#ffcccc", "#ffccff")
tornado_data = pd.read_csv("2011_torn.csv")

extent = (-131.220703, -64.775391, 23.966176, 50.792047)

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("50m"))
ax.add_feature(cfeature.OCEAN.with_scale("50m"))
ax.add_feature(cfeature.BORDERS.with_scale("50m"))
ax.add_feature(cfeature.STATES.with_scale("50m"), zorder=200)
ax.add_feature(USCOUNTIES.with_scale("20m"), zorder=100)

refined_data = {
    (
        (row[1]["slon"], row[1]["slat"]),
        (row[1]["elon"], row[1]["elat"])
    ): row[1]["mag"] for row in tornado_data.iterrows()
}

for coords, magnitude in refined_data.items():
    if not isinstance(magnitude, int):
        ax.
