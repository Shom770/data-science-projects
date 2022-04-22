import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import pandas as pd

from matplotlib.lines import Line2D

EF_COLORS = ("#e0e0e0", "#ddffdd", "#ddffff", "#ffffcc", "#ffddbb", "#ffcccc", "#ffccff")
LINE_WIDTH = 1
COLORS_TO_SIZE = {
    "#e0e0e0": LINE_WIDTH, "#ddffdd": LINE_WIDTH,
    "#ddffff": LINE_WIDTH + 0.4, "#ffffcc": LINE_WIDTH + 0.8,
    "#ffddbb": LINE_WIDTH + 1.2, "#ffcccc": LINE_WIDTH + 1.6, "#ffccff": LINE_WIDTH + 2
}

tornado_data = pd.read_csv("2011_torn.csv")

extent = (-131.220703, -64.775391, 23.966176, 50.792047)

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("50m"), color="#3C3F41")
ax.add_feature(cfeature.OCEAN.with_scale("50m"))
ax.add_feature(cfeature.BORDERS.with_scale("50m"))
ax.add_feature(cfeature.STATES.with_scale("50m"))

refined_data = {
    (
        (row[1]["slon"], row[1]["slat"]),
        (row[1]["elon"], row[1]["elat"])
    ): row[1]["mag"] for row in tornado_data.iterrows()
}
magnitude_amt = [0, 0, 0, 0, 0, 0, 0]

for coords, magnitude in refined_data.items():
    if not isinstance(magnitude, int):
        color = EF_COLORS[0]
        magnitude_amt[0] += 1
    else:
        color = EF_COLORS[magnitude + 1]
        magnitude_amt[magnitude + 1] += 1

    lons = (coords[0][0], coords[1][0])
    lats = (coords[0][1], coords[1][1])

    ax.plot(lons, lats, lw=COLORS_TO_SIZE[color], transform=ccrs.PlateCarree())

legend_elements = [
    Line2D([0], [0], color=EF_COLORS[0], marker="v", label=f"EFU ({magnitude_amt[0]})"),
    Line2D([0], [0], color=EF_COLORS[1], marker="v", label=f"EF0 ({magnitude_amt[1]})"),
    Line2D([0], [0], color=EF_COLORS[2], marker="v", label=f"EF1 ({magnitude_amt[2]})"),
    Line2D([0], [0], color=EF_COLORS[3], marker="v", label=f"EF2 ({magnitude_amt[3]})"),
    Line2D([0], [0], color=EF_COLORS[4], marker="v", label=f"EF3 ({magnitude_amt[4]})"),
    Line2D([0], [0], color=EF_COLORS[5], marker="v", label=f"EF4 ({magnitude_amt[5]})"),
    Line2D([0], [0], color=EF_COLORS[6], marker="v", label=f"EF5 ({magnitude_amt[6]})"),
]

ax.legend(handles=legend_elements)
plt.show()
