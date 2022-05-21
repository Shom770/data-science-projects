import datetime
import urllib.request
import os
import ssl

import xarray


ssl._create_default_https_context = ssl._create_unverified_context

DATA_TIME = datetime.datetime(year=2022, month=3, day=13)
GO_BACK = 48
FILE_PATH = f"{DATA_TIME.strftime('%Y%m%d%H')}.nc"
URL = (
        f"https://www.nohrsc.noaa.gov/snowfall_v2/data/"
        f"{DATA_TIME.strftime('%Y%m')}/sfav2_CONUS_{GO_BACK}h_{DATA_TIME.strftime('%Y%m%d%H')}.nc"
)

if not os.path.exists(FILE_PATH):
    # Remove any .nc files that already exist
    directory = next(os.walk("./"))
    for file_name in directory[-1]:
        if file_name.endswith(".nc"):
            os.remove(file_name)

    urllib.request.urlretrieve(URL, FILE_PATH)


def nohrsc_snow(extent):
    min_lon, max_lon, min_lat, max_lat = extent

    dataset = xarray.open_mfdataset(FILE_PATH)

    mask_lon = (dataset.lon >= min_lon) & (dataset.lon <= max_lon)
    mask_lat = (dataset.lat >= min_lat) & (dataset.lat <= max_lat)

    dataset = dataset.where(mask_lon & mask_lat, drop=True)
    snow_data = dataset.Data * 39.3700787

    lats = snow_data.lat.values
    lons = snow_data.lon.values

    return lons, lats, snow_data.values, DATA_TIME, GO_BACK
