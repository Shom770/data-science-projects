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


def filter_cape(cape_coords):
    filt_cape = [[]]
    for latitude in {tup[-1] for tup in cape_coords}:
        all_pts = sorted([coord for coord in cape_coords if round(coord[-1], 2) == round(latitude, 2)])
        if all_pts[0] == all_pts[-1]:
            filt_cape[-1].append(all_pts[0])
            filt_cape.append([])
        else:
            filt_cape[-1].append(all_pts[0])
            filt_cape[-1].append(all_pts[-1])

    filt_cape = [sorted(lst, key=itemgetter(1)) for lst in filt_cape]
    results = []

    for poly in filt_cape:
        lons = [tup[0] for tup in poly]
        lats = [tup[1] for tup in poly]

        if len(lons[::2] + lons[-1::-2]) > 4 and len(lats[::2] + lats[-1::-2]) > 4:
            results.extend([
                lons[::2] + lons[-1::-2],
                lats[::2] + lats[-1::-2],
            ])

    return results


data_nam = Dataset(
    (
        f"http://nomads.ncep.noaa.gov/dods/nam/"
        f"nam{datetime.now().strftime('%Y%m%d')}/nam_18z"
    )
)
data_nam3k = Dataset(
    (
        f"http://nomads.ncep.noaa.gov/dods/nam/"
        f"nam{datetime.now().strftime('%Y%m%d')}/nam_conusnest_18z"
    )
)
data_hrrr = Dataset(
    (
        f"http://nomads.ncep.noaa.gov/dods/hrrr/"
        f"hrrr{datetime.now().strftime('%Y%m%d')}/hrrr_sfc.t18z"
    )
)

lons = data_nam3k.variables["lon"][:]
lats = data_nam3k.variables["lat"][:]
lons_n = data_nam.variables["lon"][:]
lats_n = data_nam.variables["lat"][:]

home_lat = np.where(
    np.logical_and(np.greater_equal(lats, 37), np.less_equal(lats, 40))
)[0]
home_lon = np.where(
    np.logical_and(np.greater_equal(lons, -80), np.less_equal(lons, -74))
)[0]
home_lat_nam = np.where(
    np.logical_and(np.greater_equal(lats_n, 37), np.less_equal(lats_n, 40))
)[0]
home_lon_nam = np.where(
    np.logical_and(np.greater_equal(lons_n, -80), np.less_equal(lons_n, -74))
)[0]

cape500_poly_nam3k = []
cape500_poly_nam = []
cape500_poly_hrrr = []

cape_nam = data_nam.variables["capesfc"][27 / 3]
cape_nam3k = data_nam3k.variables["capesfc"][27 / 3]
cape_hrrr = data_hrrr.variables["capesfc"][27]

print("starting")

for lat in home_lat:
    for lon in home_lon:
        if cape_nam3k[lat, lon] > 500:
            cape500_poly_nam3k.append((lons[lon], lats[lat]))
        if cape_hrrr[lat, lon] > 500:
            cape500_poly_hrrr.append((lons[lon], lats[lat]))

print("done with nam3k/HRRR")

for lat in home_lat_nam:
    for lon in home_lon_nam:
        if cape_nam[lat, lon] > 500:
            cape500_poly_nam.append((lons_n[lon], lats_n[lat]))

print("done with NAM")

if cape500_poly_nam3k:
    ax.plot(
        *filter_cape(cape500_poly_nam3k),
        alpha=0.5, c="red", lw=5, label="NAM NEST", transform=ccrs.PlateCarree()
    )
if cape500_poly_hrrr:
    ax.plot(
        *filter_cape(cape500_poly_hrrr),
        alpha=0.5, c="green", lw=5, label="HRRR", transform=ccrs.PlateCarree()
    )
if cape500_poly_nam:
    ax.plot(
        *filter_cape(cape500_poly_nam),
        alpha=0.5, c="blue", lw=5, label="NAM", transform=ccrs.PlateCarree()
    )

ax.legend()

plt.show()
