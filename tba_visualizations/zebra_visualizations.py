import datetime
from os import environ

import matplotlib.pyplot as plt
import numpy as np
import requests
from dotenv import load_dotenv
from scipy import interpolate

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/team/frc4099/matches/{year}/simple"
TBA_API_KEY = environ["TBA_API_KEY"]

resp = SESSION.get(URL.format(year=2022), headers={"X-TBA-Auth-Key": TBA_API_KEY}).json()
print(resp)
