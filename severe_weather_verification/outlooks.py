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

    all_polygons = {}

    for risks in response["features"]:
        all_polygons[risks["properties"]["DN"]] = []
        for risk in risks["geometry"]["coordinates"]:
            all_polygons[risks["properties"]["DN"]].append(geometry.Polygon(risk[0]))

    all_vals = list(all_polygons.values())

    for polygon_lst, next_pl in zip(all_vals, all_vals[1:]):
        for idx, (p1, p2) in enumerate(zip(polygon_lst, next_pl)):
            polygon_lst[idx] = p1 - p2

    return all_polygons

