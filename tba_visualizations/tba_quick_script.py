from os import environ

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/event/2022hop/matches"
TBA_API_KEY = environ["TBA_API_KEY"]

all_matches = SESSION.get(URL, headers={"X-TBA-Auth-Key": TBA_API_KEY}).json()

with open("quick_script_data.txt") as file:
    teams = {"frc" + line.strip("|").split("|")[0] for idx, line in enumerate(file.readlines()) if idx != 0}


for match in all_matches:
    resp = SESSION.get(URL, headers={"X-TBA-Auth-Key": TBA_API_KEY}).json()

    resp = SESSION.get(URL.format(match_key=event_key), headers={"X-TBA-Auth-Key": TBA_API_KEY}).json()
    all_event_ct[event_resp["name"]] = len([team for team in resp if team.removeprefix("frc") in teams])

print("\n".join(
    [
        f"{key} - {value} teams going to IRI"
        for key, value in sorted(all_event_ct.items(), key=lambda tup: tup[1], reverse=True)
    ]
))
# print(max(all_event_ct.items(), key=lambda tup: tup[1])[0])
