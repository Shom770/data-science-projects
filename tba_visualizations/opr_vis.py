from os import environ

import numpy as np
import requests
from dotenv import load_dotenv
from scipy.stats import skew

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/event/{key}/oprs"
TBA_API_KEY = environ["TBA_API_KEY"]

ccvm_dataset = np.array(
    list(
        dict(
            sorted(
                SESSION.get(
                    URL.format(key="2022tur"),
                    headers={"X-TBA-Auth-key": TBA_API_KEY}
                ).json()["ccwms"].items(),
                key=lambda tup: tup[1],
                reverse=True
            )
        ).values()
    )
)

print(
    skew(
        ccvm_dataset
    )
)
