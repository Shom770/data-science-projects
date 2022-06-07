import cartopy.crs as ccrs
import matplotlib.pyplot as plt

extent = (-79.9, -74.1, 37.1, 39.9)

fig: plt.Figure = plt.figure()
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)
