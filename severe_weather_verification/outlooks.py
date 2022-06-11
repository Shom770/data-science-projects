import datetime

import requests

from reports import ReportType


def get_risks(date, report_type):
    response = requests.get(
        (
            f"https://www.spc.noaa.gov/products/outlook/archive/{date.year}"
            f"/day1otlk_{date.strftime('%Y%m%d')}_0100_{report_type._name_.lower()}.nolyr.geojson"
        )
    ).json()
    print(response)


get_risks(datetime.datetime(2022, 6, 2), ReportType.HAIL)
