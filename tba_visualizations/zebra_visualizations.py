import datetime
from os import environ

import matplotlib.pyplot as plt
import numpy as np
import requests
from dotenv import load_dotenv
from scipy import interpolate

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/match/2022cmptx_f1m1/zebra_motionworks"
TBA_API_KEY = environ["TBA_API_KEY"]

resp = SESSION.get(URL, headers={"X-TBA-Auth-Key": TBA_API_KEY}).json()
print(__import__("json").dumps(resp, indent=4))
