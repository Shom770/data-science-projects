from os import environ

import requests
from dotenv import load_dotenv

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/team/frc4099/events/2022/statuses"
TBA_API_KEY = environ["TBA_API_KEY"]

resp = SESSION.get(URL, headers={"X-TBA-Auth-Key": TBA_API_KEY}).json()
__import__("json").dumps(resp, indent=4)
