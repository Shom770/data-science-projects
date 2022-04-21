import datetime

import requests


ISO8660 = "%Y-%m-%dT%H:%M"
URL = "http://mesonet.agron.iastate.edu/cgi-bin/request/gis/lsr.py"

session = requests.session()


def get_reports(states: list, start_time: datetime.datetime, end_time: datetime.datetime) -> None:
    totals = {}
    for state in states:
        req = session.get(
                f"{URL}?state={state}&sts={start_time.strftime(ISO8660)}&ets={end_time.strftime(ISO8660)}&justcsv=true"
        ).text
        for line in req.split("\n")[1:]:
            split_line = line.split(",")
            totals[tuple(map(float, split_line[2:4]))] = float(split_line[4])

    return totals


print(get_reports(["MD", "VA"], datetime.datetime(2022, 1, 7), datetime.datetime(2022, 1, 8)))
