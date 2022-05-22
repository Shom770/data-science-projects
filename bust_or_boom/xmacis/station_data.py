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
            combine_similar=False
    ) -> "DataPoints":
        """Filter through each data point in `self.data_points` with the condition provided (callable)"""

        filtered = {period: data for period, data in self.data_points.items() if condition(period, data)}

        if not combine_similar:
            return DataPoints(filtered)
        else:
            all_periods = {}
            data_points = {}

            for (period, data), (next_period, next_data) in zip(filtered.items(), list(filtered.items())[1:]):
                if (next_period - period).total_seconds() // 3600 > 24:
                    if not data_points:
                        data_points[period] = data
                    all_keys = list(data_points.keys())
                    if all_keys[0] == all_keys[-1]:
                        all_periods[all_keys[0]] = data_points[all_keys[0]]
                    else:
                        all_periods[(all_keys[0], all_keys[-1])] = _Data(
                            snow=sum([dp.snow for dp in data_points.values()])
                        )
                    data_points = {}
                else:
                    data_points[period] = data
                    data_points[next_period] = next_data

            return all_periods

    def __repr__(self):
        return f"DataPoints({self.data_points})"


class _Data:
    """Contains the data retrieved from the xmacis API for a single point in time."""

    def __init__(self, **kwargs):
        for element, value in kwargs.items():
            if value not in {"T", "M", "S"}:
                setattr(
                    self,
                    element.lower(),
                    (literal_eval(value.replace("A", "")) if not isinstance(value, float) else value)
                )
            else:
                setattr(self, element.lower(), 0.01 if value == "T" else float("nan"))

    def __add__(self, other):
        return _Data(**{name: str(round(value + getattr(other, name), 2)) for name, value in vars(self).items()})

    def __repr__(self):
        represent_instance = "Data("

        for attr_name, attr_value in vars(self).items():
            represent_instance += f"{attr_name}={attr_value}, "

        return represent_instance.removesuffix(", ") + ")"

    def __hash__(self):
        return hash(self.snow)


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
