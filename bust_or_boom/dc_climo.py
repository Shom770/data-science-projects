from collections import defaultdict
from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from scipy.interpolate import make_interp_spline

from xmacis import Elements, get_station_data


STATION = "KDCA"
UPPER_PERCENTILE = 75
LOWER_PERCENTILE = 25

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = plt.subplot(1, 1, 1)

for font in font_manager.findSystemFonts(["."]):
    font_manager.fontManager.addfont(font)

# Set font family globally
matplotlib.rcParams['font.family'] = 'Inter'


station_data = get_station_data(
    station_id=STATION, elements=(Elements.SNOW,), start_date=datetime(1980, 1, 1), end_date=datetime(2022, 11, 30)
)

december_data = defaultdict(list)
january_data = defaultdict(list)
february_data = defaultdict(list)
march_data = defaultdict(list)

for day, data in station_data.filter(condition=lambda date, data: date.month == 12).data_points.items():
    december_data[day.year].append(data.snow)

upper_decembers = np.percentile(list(map(sum, december_data.values())), UPPER_PERCENTILE)
lower_decembers = np.percentile(list(map(sum, december_data.values())), LOWER_PERCENTILE)

top_years = {year for year, total_snow in december_data.items() if sum(total_snow) >= upper_decembers}

top_years_data = np.array(
    list({year: values for year, values in december_data.items() if year in top_years}.values())
).transpose()
average_snows_best_years = np.array(list(map(np.mean, top_years_data.cumsum(axis=0))))

bottom_years = {year for year, total_snow in december_data.items() if sum(total_snow) <= lower_decembers}
bottom_years_data = np.array(
    list({year: values for year, values in december_data.items() if year in bottom_years}.values())
).transpose()
average_snows_worst_years = np.array(list(map(np.mean, bottom_years_data.cumsum(axis=0))))

data_by_day = np.array(list(december_data.values())).transpose()
average_snow_by_day = np.array(list(map(np.mean, data_by_day.cumsum(axis=0))))

x_new = np.linspace(1, 31, 300)

average_snow_by_day = make_interp_spline(range(1, 32), average_snow_by_day)(x_new)
average_snows_best_years = make_interp_spline(range(1, 32), average_snows_best_years)(x_new)
average_snows_worst_years = make_interp_spline(range(1, 32), average_snows_worst_years)(x_new)

ax.plot(x_new, average_snow_by_day, color="#4A4A4A", lw=2.5, label=f"Top 25% of Decembers (n={len(top_years)})")
ax.plot(x_new, average_snows_best_years, color="#25754D", lw=2.5, label="Mean of December Winters")
ax.plot(x_new, average_snows_worst_years, color="#99354D", lw=2.5, label=f"Bottom 25% of Decembers (n={len(bottom_years)})")

ax.fill_between(x_new, average_snows_best_years, average_snow_by_day, color="#25754D", alpha=0.25)
ax.fill_between(x_new, average_snow_by_day, average_snows_worst_years, color="#99354D", alpha=0.25)

ax.set_xlabel("Day of December", fontdict={"font": "Inter", "style": "oblique"})
ax.set_ylabel("Average Snow to Date in December", fontdict={"font": "Inter", "style": "oblique"})

ax.legend()

ax.set_title(
    f"Data retrieved using XMACIS, data from KIAD (1980-2022)",
    fontsize=9,
    loc="left",
    fontdict={"weight": "bold", "font": "Inter"}
)

plt.suptitle(
    f"Snow to Date in December in Washington D.C.",
    fontsize=13,
    ha="left",
    va="bottom",
    x=0,
    y=1.05,
    fontweight="bold",
    transform=ax.transAxes
)

plt.show()
