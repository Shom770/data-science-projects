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

    for risks in response["features"]:
        all_polygons.append([])
        for risk in risks["geometry"]["coordinates"]:
            all_polygons[-1].append(geometry.Polygon(risk[0]))

    print(all_polygons)


get_risks(datetime.datetime(2022, 6, 2), ReportType.WIND)
