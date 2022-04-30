import datetime

import requests

DATA_TIME = datetime.datetime(year=2022, month=1, day=8)

URL = (
    f"http://www.nohrsc.noaa.gov/snowfall_v2/data/"
    f"{DATA_TIME.strftime('%Y%m')}/sfav2_CONUS_24h_{DATA_TIME.strftime('%Y%m%d%H')}.nc"
)


print(requests.get(URL).json())
