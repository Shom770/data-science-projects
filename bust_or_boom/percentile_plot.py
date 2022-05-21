import datetime

import requests

from xmacis import Elements, get_station_data

session = requests.session()


DIFF = 0.5
START_DATE = datetime.datetime(2010, 1, 1)
END_DATE = datetime.datetime.today()

extent = (-79.05, -76.02, 37.585112, 39.56)
extent_lim = (extent[0] - DIFF, extent[1] + DIFF, extent[2] - DIFF, extent[3] + DIFF)
bbox_lim = (extent_lim[0], extent_lim[2], extent_lim[1], extent_lim[3])

stations = [stn for stn in session.get(
    f"http://data.rcc-acis.org/StnMeta", params={
        "bbox": ",".join(map(str, bbox_lim)),
        "elems": Elements.SNOW.value,
        "sdate": START_DATE.strftime('%Y-%m-%d'),
        "edate": END_DATE.strftime('%Y-%m-%d'),
    }
).json()["meta"] if any(sid.endswith("3") for sid in stn["sids"])]

all_dps = [
    (
        get_station_data(station["sids"][0], elements=(Elements.SNOW,), start_date=START_DATE, end_date=END_DATE),
        station["ll"],
        station["name"]
    )
    for station in stations
]
all_dps = [
    (res,) + dp[1:] for dp in all_dps if (res := dp[0].filter(condition=lambda cond: cond.snow >= 0.1)).data_points
]


