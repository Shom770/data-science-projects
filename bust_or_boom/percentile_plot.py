from xmacis import Elements, get_station_data

import requests


session = requests.session()


DIFF = 0.2
extent = (-79.05, -76.02, 37.585112, 39.56)
extent_lim = (extent[0] - DIFF, extent[1] + DIFF, extent[2] - DIFF, extent[3] + DIFF)
bbox_lim = (extent[0], extent[2], extent[1], extent[3])

stations = session.get(
    f"http://data.rcc-acis.org/StnMeta", params={"bbox": bbox_lim, "elems": Elements.SNOW.value}
).json()

print(stations)
