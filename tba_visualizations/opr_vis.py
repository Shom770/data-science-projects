from math import asinh
from os import environ

import numpy as np
import requests
from dotenv import load_dotenv
from scipy.stats import skew

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/event/{key}/oprs"
TBA_API_KEY = environ["TBA_API_KEY"]

ccwm_dataset = np.array(
    list(
        dict(
            sorted(
                SESSION.get(
                    URL.format(key="2022chcmp"),
                    headers={"X-TBA-Auth-key": TBA_API_KEY}
                ).json()["ccwms"].items(),
                key=lambda tup: tup[1],
                reverse=True
            )
        ).values()
    )
)

ccwm_dataset = min(
    [np.array([asinh(value / k_factor) for value in ccwm_dataset]) for k_factor in range(1, 21, 5)],
    key=lambda arr: abs(skew(arr))
)

print(ccwm_dataset.mean())
