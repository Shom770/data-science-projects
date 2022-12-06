from collections import defaultdict
from datetime import datetime

import numpy as np

from xmacis import Elements, get_station_data


STATION = "KIAD"
UPPER_PERCENTILE = 75
LOWER_PERCENTILE = 25

station_data = get_station_data(
    station_id=STATION, elements=(Elements.SNOW,), start_date=datetime(1980, 1, 1), end_date=datetime(2022, 11, 30)
)

december_data = defaultdict(list)

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
