import datetime

import requests


ISO8660 = "%Y-%m-%dT%H:%M"
URL = "http://mesonet.agron.iastate.edu/cgi-bin/request/gis/lsr.py"


def get_reports(start_time: datetime.datetime, end_time: datetime.datetime) -> None:
    request = requests.get(f"{URL}?state=MD&sts={start_time.strftime(ISO8660)}&ets={end_time.strftime(ISO8660)}")
    print(request.text)


get_reports(datetime.datetime(2022, 1, 7), datetime.datetime(2022, 1, 8))
