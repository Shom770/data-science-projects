import datetime
from os import environ

import matplotlib.pyplot as plt
import numpy as np
import requests
from dotenv import load_dotenv
from scipy import interpolate
from uszipcode import SearchEngine

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/teams/2022/8"
TBA_API_KEY = environ["TBA_API_KEY"]
SEARCH = SearchEngine()

resp = SESSION.get(URL, headers={"X-TBA-Auth-Key": TBA_API_KEY}).json()
start = __import__("time").perf_counter()
print(SEARCH.by_zipcode(int(resp[-1]["postal_code"])))
print(__import__("time").perf_counter() - start)
