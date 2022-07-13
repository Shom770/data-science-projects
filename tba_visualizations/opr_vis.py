import itertools
from math import asinh
from os import environ

import numpy as np
import requests
from dotenv import load_dotenv
from scipy.stats import skew

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/event/{key}/{mode}"
TBA_API_KEY = environ["TBA_API_KEY"]
EVENT_KEY = "2022tur"

all_ccwms = SESSION.get(
    URL.format(key=EVENT_KEY, mode="oprs"), headers={"X-TBA-Auth-key": TBA_API_KEY}
).json()["ccwms"]

all_alliances = [[all_ccwms[pick] for pick in alliance["picks"]]for alliance in SESSION.get(
    URL.format(key=EVENT_KEY, mode="alliances"), headers={"X-TBA-Auth-key": TBA_API_KEY}
).json()]
print(all_alliances)

ccwm_dataset = np.array(
    sorted({
        sum(alliance_sum)
        for alliance_sum in itertools.product(itertools.chain.from_iterable(all_alliances), repeat=3)
        if len(alliance_sum) == 3
    })
)
all_alliances = list(map(sum, all_alliances))

ccwm_dataset = min(
    [np.array([asinh(value / k_factor) for value in ccwm_dataset]) for k_factor in range(1, 21, 5)],
    key=lambda arr: abs(skew(arr))
)

print(skew(ccwm_dataset))
