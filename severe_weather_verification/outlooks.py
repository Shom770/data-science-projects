import datetime

import requests

from reports import ReportType
from shapely import geometry


def get_risks(date, report_type):
    response = requests.get(
        (
            f"https://www.spc.noaa.gov/products/outlook/archive/{date.year}"
            f"/day1otlk_{date.strftime('%Y%m%d')}_1200_{report_type._name_.lower()}.lyr.geojson"
        )
    ).json()

    risks = response["features"][0]["geometry"]["coordinates"]
    all_polygons = []

    for risk in risks:
        print(risk[0])
        all_polygons.append(geometry.Polygon(risk[0]))

    print(all_polygons[0].wkt)

get_risks(datetime.datetime(2022, 6, 2), ReportType.WIND)
