from datetime import datetime

import numpy as np

from netCDF4 import Dataset

data = Dataset(
    (
        f"http://nomads.ncep.noaa.gov/dods/nam/"
        f"nam{datetime.now().strftime('%Y%m%d')}/nam_12z"
    )
)

lons = data.variables["lon"][:]
lats = data.variables["lat"][:]

home_lat = np.where(
    np.logical_and(np.greater_equal(lats, 39.1), np.less_equal(lats, 39.2))
)[0][0]
home_lon = np.where(
    np.logical_and(np.greater_equal(lons, -77.3), np.less_equal(lons, -77.2))
)[0][0]
print(data.variables["capesfc"][39 / 3][home_lat, home_lon])
