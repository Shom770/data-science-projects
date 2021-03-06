from enum import Enum
from io import StringIO

import pandas as pd


class ReportType(Enum):
    TORNADO = 0
    WIND = 1
    HAIL = 2


SIG_COND_MAPPING = {ReportType.TORNADO: "F_Scale", ReportType.WIND: "Speed", ReportType.HAIL: "Size"}


def all_reports(report_type, extent, day):
    try:
        with open(f"{day.strftime('%y')[-2:] + day.strftime('%m%d')}_rpts_filtered.csv") as file:
            all_text = file.read()
    except FileNotFoundError:
        SIG_COND_MAPPING[ReportType.TORNADO] = "F-Scale"
        with open(f"{day.strftime('%y')[-2:] + day.strftime('%m%d')}_rpts.csv") as file:
            all_text = file.read()

    split_text = all_text.split("\n")

    header_pos = [idx for idx, line in enumerate(split_text) if line.startswith("Time")]

    if report_type == ReportType.TORNADO:
        all_text = "\n".join(split_text[:header_pos[1]])
    elif report_type == ReportType.WIND:
        all_text = "\n".join(split_text[header_pos[1]:header_pos[2]])
    elif report_type == ReportType.HAIL:
        all_text = "\n".join(split_text[header_pos[2]:])

    reports_df = pd.read_csv(StringIO(all_text), on_bad_lines='skip')
    condition = (
            (extent[0] <= reports_df.Lon) & (reports_df.Lon <= extent[1])
            & (extent[2] <= reports_df.Lat) & (reports_df.Lat <= extent[3])
    )
    reports_df = reports_df[condition]

    return [*zip(reports_df.Lon, reports_df.Lat, reports_df[SIG_COND_MAPPING[report_type]])]
