import itertools
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

all_ccwms = SESSION.get(URL.format(key="2022chcmp"), headers={"X-TBA-Auth-key": TBA_API_KEY}).json()["ccwms"]

ccwm_dataset = np.array(
    sorted({sum(alliance_sum) for alliance_sum in itertools.product(all_ccwms.values(), repeat=3)})
)

ccwm_dataset = min(
    [np.array([asinh(value / k_factor) for value in ccwm_dataset]) for k_factor in range(1, 21, 5)],
    key=lambda arr: abs(skew(arr))
)
