import logging

from datetime import datetime
from operator import itemgetter

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.offsetbox import AnchoredText
from metpy.plots import USCOUNTIES
from netCDF4 import Dataset

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
logger.info("Loaded NAM dataset")

data_nam3k = Dataset(
    (
        f"http://nomads.ncep.noaa.gov/dods/nam/"
        f"nam{datetime.now().strftime('%Y%m%d')}/nam_conusnest_18z"
    )
)
logger.info("Loaded NAM CONUS NEST dataset")

data_hrrr = Dataset(
    (
        f"http://nomads.ncep.noaa.gov/dods/hrrr/"
        f"hrrr{datetime.now().strftime('%Y%m%d')}/hrrr_sfc.t18z"
    )
)
logger.info("Loaded HRRR dataset")

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


logger.info("Starting to generate CAPE for NAM NEST/HRRR")

for lat in home_lat:
    for lon in home_lon:
        if cape_nam3k[lat, lon] > 500:
            cape500_poly_nam3k.append((lons[lon], lats[lat]))
        if cape_hrrr[lat, lon] > 500:
            cape500_poly_hrrr.append((lons[lon], lats[lat]))

logger.info("Finished with generating CAPE for NAM NEST/HRRR")

for lat in home_lat_nam:
    for lon in home_lon_nam:
        if cape_nam[lat, lon] > 500:
            cape500_poly_nam.append((lons_n[lon], lats_n[lat]))

logger.info("Finished with generating CAPE for NAM")

if cape500_poly_nam3k:
    ax.fill(
        *filter_cape(cape500_poly_nam3k),
        alpha=0.5, facecolor="red", label="NAM NEST", transform=ccrs.PlateCarree()
    )
if cape500_poly_hrrr:
    ax.fill(
        *filter_cape(cape500_poly_hrrr),
        alpha=0.5, facecolor="green", label="HRRR", transform=ccrs.PlateCarree()
    )
if cape500_poly_nam:
    ax.fill(
        *filter_cape(cape500_poly_nam),
        alpha=0.5, facecolor="blue", label="NAM", transform=ccrs.PlateCarree()
    )

text = AnchoredText(">500 CAPE on 18z Models at 5 PM Tomorrow", loc=4, prop={'size': 12}, frameon=True)
ax.add_artist(text)

ax.legend()

plt.show()
