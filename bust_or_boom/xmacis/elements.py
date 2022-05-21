from enum import Enum


class Elements(Enum):
    MAXIMUM_TEMPERATURE = "maxt"
    MINIMUM_TEMPERATURE = "mint"
    AVERAGE_TEMPERATURE = "avgt"
    OBSERVED_TEMPERATURE = "obst"
    PRECIPITATION = "pcpn"
    SNOW = "snow"
    SNOW_DEPTH = "snwd"
    COOLING_DEG_DAYS = "cdd"
    DAYS_BELOW_BASE = "hdd"
    DAYS_ABOVE_BASE = "gdd"