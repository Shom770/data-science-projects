import datetime
from enum import Enum
from io import StringIO

import requests
import pandas as pd


class ReportType(Enum):
    TORNADO = 0
    WIND = 1
    HAIL = 2


COND_MAPPING = {ReportType.TORNADO: (0.0, "T"), ReportType.WIND: (50, "G"), ReportType.HAIL: (1.0, "H")}


def all_reports(report_type, extent, day):
    start_date = day.isoformat()[:-3] + "Z"
    end_date = (day + datetime.timedelta(days=1)).isoformat()[:-3] + "Z"

    url = (
        f"https://mesonet.agron.iastate.edu/cgi-bin/request/gis/lsr.py?"
        f"sts={start_date}&ets={end_date}&fmt=csv"
    )
    all_text = requests.get(url).content.decode()
    print(all_text)

    reports_df = pd.read_csv(StringIO(all_text), on_bad_lines='skip')
    condition = (
            (extent[0] <= reports_df.LON) & (reports_df.LON <= extent[1])
            & (extent[2] <= reports_df.LAT) & (reports_df.LAT <= extent[3])
    )
    reports_df = reports_df[condition]
    min_mag, code = COND_MAPPING[report_type]
    reports_df["MAG"] = reports_df["MAG"].map(lambda mag: 0.0 if mag == "None" else float(mag))

    filter_report_cond = (
        (reports_df.MAG >= min_mag) & (reports_df.TYPECODE == code)
    )
    reports_df = reports_df[filter_report_cond]
    return [*zip(reports_df.LON, reports_df.LAT, reports_df.MAG)]
