import cartopy.feature as cfeature
import cartopy.crs as ccrs
import matplotlib.pyplot as plt


extent = (-126.298828,-66.313477, 24.686952, 49.439557)
fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("110m"))
ax.add_feature(cfeature.LAKES.with_scale("110m"))
ax.add_feature(cfeature.OCEAN.with_scale("110m"), zorder=100)
ax.add_feature(cfeature.STATES.with_scale("110m"), zorder=200)

plt.show()
