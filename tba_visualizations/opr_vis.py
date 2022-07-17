import itertools
from math import asinh
from os import environ

import numpy as np
import requests
from dotenv import load_dotenv
from scipy.stats import norm, skew

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/event/{key}/{mode}"
TBA_API_KEY = environ["TBA_API_KEY"]
EVENT_KEY = "2022tur"

all_ccwms = SESSION.get(
    URL.format(key=EVENT_KEY, mode="oprs"), headers={"X-TBA-Auth-key": TBA_API_KEY}
).json()["oprs"]
all_alliances = SESSION.get(
     URL.format(key=EVENT_KEY, mode="alliances"), headers={"X-TBA-Auth-key": TBA_API_KEY}
).json()

alliance_sums = [
    [all_ccwms[pick] for pick in alliance["picks"]] for alliance in all_alliances
]

opr_dataset = np.array(
    sorted({
        sum(alliance_sum) / len(alliance_sum)
        for alliance_sum in itertools.product(itertools.chain.from_iterable(alliance_sums), repeat=len(alliance_sums[0]))
        if len(alliance_sum) == len(alliance_sums[0])
    })
)
alliance_sums = [sum(all_sum) / len(all_sum) for all_sum in alliance_sums]

mode, opr_dataset = min(
    (
        (np.log, np.log(opr_dataset)),
        (np.reciprocal, 1 / opr_dataset),
        (np.sqrt, opr_dataset ** 0.5)
    ),
    key=lambda arr: abs(skew(arr[1]))
)

percentiles_picks = []

for opr_sum in alliance_sums:
    z_score = (mode(opr_sum) - opr_dataset.mean()) / opr_dataset.std()
    percentiles_picks.append((1 - norm.sf(z_score)) * 100)

print(percentiles_picks, [alliance["picks"] for alliance in all_alliances])
