import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import pandas as pd

extent = (-79.9, -74.1, 37.1, 39.9)

with open("220602_rpts_filtered.csv") as file:
    all_text = file.read()
    header_pos = [idx for idx, line in enumerate(all_text.split("\n")) if line.startswith("Time")]
    reports_df = pd.read_csv(all_text, header=header_pos)
    print(reports_df)

fig: plt.Figure = plt.figure()
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)
