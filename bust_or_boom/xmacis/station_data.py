from ast import literal_eval
from collections import UserDict
from datetime import datetime, timedelta
import typing

import requests

from .elements import Elements


__all__ = ["DataPoints", "get_station_data"]

_SESSION = requests.Session()


class DataPoints(UserDict):
    """Contains all the data recieved from the xmacis API from one request."""

    def __init__(self, data_points: dict):
        self.data_points = data_points
        super().__init__(data_points)

    def combine_storms(self, condition):
        """Combine days close to each other with associate storms, eg with snow."""
        dp = {}
        start_date = None
        dp_to_add = None

        for period, data in self.data_points.items():
            if period + timedelta(days=1) not in self.data_points.keys():
                break
            elif condition(self.data_points[period + timedelta(days=1)]) and condition(data):
                if dp_to_add:
                    dp_to_add += data
                else:
                    dp_to_add = data
                    start_date = period
            else:
                if condition(data) and dp_to_add:
                    dp_to_add += data

                dp[
                    (start_date, period) if start_date else period
                ] = dp_to_add if dp_to_add else self.data_points[period]
                dp_to_add = None
                start_date = None

        return DataPoints(dp)

    def filter(
            self,
            condition: typing.Callable,
            within: typing.Optional[int] = None,
            min_periods: typing.Optional = None
    ) -> "DataPoints":
        """Filter through each data point in `self.data_points` with the condition provided (callable)"""

        filtered = {period: data for period, data in self.data_points.items() if condition(data)}

        if not within:
            return DataPoints(filtered)
        else:
            all_periods = []
            data_points = {}
            difference_between_periods = 0

            periods_meeting_condition = list(filtered.keys())

            for idx, (period, data) in enumerate(filtered.items()):
                # Skip the first period
                if idx == 0:
                    continue

                previous_period = periods_meeting_condition[idx - 1]

                # Ensure that the difference between two periods are within the range (within)
                if (period - previous_period).total_seconds() // 86400 + difference_between_periods <= within:
                    difference_between_periods += (period - previous_period).total_seconds() // 86400

                    if previous_period not in data_points:
                        data_points[previous_period] = filtered[previous_period]

                    data_points[period] = data
                else:
                    # If data_points isn't empty and the range has been exceeded, add it to the list of periods
                    if data_points:
                        all_periods.append(DataPoints(data_points))
                        data_points = {}

                    difference_between_periods = 0
            else:
                # If the last period sufficed for the conditions, add it to the periods list
                if data_points:
                    all_periods.append(DataPoints(data_points))

            if min_periods:
                return [period for period in all_periods if len(period.data_points.keys()) >= min_periods]
            else:
                return all_periods

    def __repr__(self):
        return f"DataPoints({self.data_points})"


class _Data:
    """Contains the data retrieved from the xmacis API for a single point in time."""

    def __init__(self, **kwargs):
        for element, value in kwargs.items():
            if value != "T" and value != "M":
                setattr(self, element.lower(), literal_eval(value))
            else:
                setattr(self, element.lower(), 0.01 if value == "T" else float("nan"))

    def __add__(self, other):
        return _Data(**{name: str(round(value + getattr(other, name), 2)) for name, value in vars(self).items()})

    def __repr__(self):
        represent_instance = "Data("

        for attr_name, attr_value in vars(self).items():
            represent_instance += f"{attr_name}={attr_value}, "

        return represent_instance.removesuffix(", ") + ")"


def get_station_data(
    station_id: str,
    elements: typing.Optional[typing.Sequence] = None,
    *,
    start_date: typing.Optional[datetime] = None,
    end_date: typing.Optional[datetime] = None,
    date: typing.Optional[datetime] = None,
) -> DataPoints:
    """Retrieves the station data based off the filters provided."""
    data_to_send = {param_name: param_value.strftime("%Y-%m-%d") if isinstance(param_value, datetime) else param_value
                  for param_name, param_value in zip(
        ("sid", "sdate", "edate", "date", "elems"),
        (station_id, start_date, end_date, date, [
            element.value if isinstance(element, Elements) else element for element in elements
        ])
    ) if param_value}

    response = _SESSION.post("http://data.rcc-acis.org/StnData", data=data_to_send).json()

    data_points = {}

    for point in response["data"]:
        data_points[datetime.strptime(point[0], "%Y-%m-%d")] = _Data(
            **{element._name_: value for element, value in zip(elements, point[1:])}
        )

    return DataPoints(data_points)
