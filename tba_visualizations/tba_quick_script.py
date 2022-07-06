from os import environ

import requests
from dotenv import load_dotenv

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/event/{match_key}/teams/keys"
EVENT_URL = "https://www.thebluealliance.com/api/v3/event/{match_key}/simple"
TBA_API_KEY = environ["TBA_API_KEY"]

events = ["2022carv", "2022gal", "2022hop", "2022new", "2022roe", "2022tur"]
event_names = []

with open("quick_script_data.txt") as file:
    teams = {line.strip("|").split("|")[0] for idx, line in enumerate(file.readlines()) if idx != 0}

all_event_ct = {}
for event_key in events:
    event_resp = SESSION.get(EVENT_URL.format(match_key=event_key), headers={"X-TBA-Auth-Key": TBA_API_KEY}).json()

    resp = SESSION.get(URL.format(match_key=event_key), headers={"X-TBA-Auth-Key": TBA_API_KEY}).json()
    all_event_ct[event_resp["name"]] = len([team for team in resp if team.removeprefix("frc") in teams])

print("\n".join([f"{key} - {value} teams going to IRI" for key, value in all_event_ct.items()]))
# print(max(all_event_ct.items(), key=lambda tup: tup[1])[0])
