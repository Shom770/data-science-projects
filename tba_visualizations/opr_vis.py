from os import environ

import requests
from dotenv import load_dotenv

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/event/2022chcmp/oprs"
TBA_API_KEY = environ["TBA_API_KEY"]

print(SESSION.get(URL, headers={"X-TBA-Auth-key": TBA_API_KEY}).json()["oprs"])
