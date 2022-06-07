from enum import Enum
from io import StringIO

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class ReportType(Enum):
    TORNADO = 0
    WIND = 1
    HAIL = 2


extent = (-79.9, -74.1, 37.1, 39.9)
REPORT_TYPE = ReportType.WIND

with open("220602_rpts_filtered.csv") as file:
    all_text = file.read()
    split_text = all_text.split("\n")

    header_pos = [idx for idx, line in enumerate(split_text) if line.startswith("Time")]

    if REPORT_TYPE == ReportType.TORNADO:
        all_text = "\n".join(split_text[:header_pos[1]])
    elif REPORT_TYPE == ReportType.WIND:
        all_text = "\n".join(split_text[header_pos[1]:header_pos[2]])
    elif REPORT_TYPE == ReportType.HAIL:
        all_text = "\n".join(split_text[header_pos[2]:])

    reports_df = pd.read_csv(StringIO(all_text))
    condition = (
            (extent[0] <= reports_df.Lon) & (reports_df.Lon <= extent[1])
            & (extent[2] <= reports_df.Lat) & (reports_df.Lat <= extent[3])
    )
    reports_df = reports_df[condition]

fig: plt.Figure = plt.figure()
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)
