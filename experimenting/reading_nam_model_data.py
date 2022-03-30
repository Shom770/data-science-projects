from datetime import datetime
from operator import itemgetter

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import matplotlib.pyplot as plt

from metpy.plots import USCOUNTIES
from netCDF4 import Dataset

extent = (-79.9, -74.1, 37.1, 39.9)

fig: plt.Figure = plt.figure()
ax: plt.Axes = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.set_extent(extent)

ax.add_feature(cfeature.LAND.with_scale("10m"))
ax.add_feature(cfeature.OCEAN.with_scale("10m"))
ax.add_feature(USCOUNTIES.with_scale("5m"))


def chaikins_corner_cutting(coords, refinements=5):
    coords = np.array(coords)

    for _ in range(refinements):
        L = coords.repeat(2, axis=0)
        R = np.empty_like(L)
        R[0] = L[0]
        R[2::2] = L[1:-1:2]
        R[1:-1:2] = L[2::2]
        R[-1] = L[-1]
        coords = L * 0.75 + R * 0.25

    return coords


def filter_cape(cape_coords):

data = Dataset(
    (
        f"http://nomads.ncep.noaa.gov/dods/nam/"
        f"nam{datetime.now().strftime('%Y%m%d')}/nam_18z"
    )
)

lons = data.variables["lon"][:]
lats = data.variables["lat"][:]

home_lat = np.where(
    np.logical_and(np.greater_equal(lats, 37), np.less_equal(lats, 40))
)[0]
home_lon = np.where(
    np.logical_and(np.greater_equal(lons, -80), np.less_equal(lons, -74))
)[0]

cape0_poly = []

cape_cur_hour = data.variables["capesfc"][33 / 3]

for lat in home_lat:
    for lon in home_lon:
        if cape_cur_hour[lat, lon] > 500.0:
            cape0_poly.append((lons[lon], lats[lat]))

filt_cape0 = []
for latitude in {tup[-1] for tup in cape0_poly}:
    all_pts = sorted([coord for coord in cape0_poly if round(coord[-1], 2) == round(latitude, 2)])
    filt_cape0.append(all_pts[0])
    filt_cape0.append(all_pts[-1])

filt_cape0 = sorted(filt_cape0, key=itemgetter(1))

lons = [tup[0] for tup in filt_cape0]
lats = [tup[1] for tup in filt_cape0]

ax.fill(
    chaikins_corner_cutting(lons[::2] + lons[-1::-2], refinements=7),
    chaikins_corner_cutting(lats[::2] + lats[-1::-2], refinements=7),
    alpha=0.5, facecolor="blue", transform=ccrs.PlateCarree()
)


plt.show()
