from os import environ

import requests
from dotenv import load_dotenv

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/district/{key}/teams/keys"
TBA_API_KEY = environ["TBA_API_KEY"]
EVENT_KEYS = [
    "2022carv",
    "2022gal",
    "2022hop",
    "2022new",
    "2022roe",
    "2022tur"
]

districts = SESSION.get(
    "https://www.thebluealliance.com/api/v3/districts/2022",
    headers={"X-TBA-Auth-Key": TBA_API_KEY}
).json()
worlds_teams = []

for event_key in EVENT_KEYS:
    worlds_teams.extend(SESSION.get(
        f"https://www.thebluealliance.com/api/v3/event/{event_key}/teams/keys",
        headers={"X-TBA-Auth-Key": TBA_API_KEY}
    ).json())

worlds_teams = set(worlds_teams)

all_teams = {}

for district in districts:
    teams = SESSION.get(URL.format(key=district["key"]), headers={"X-TBA-Auth-Key": TBA_API_KEY}).json()
    district_teams_in_worlds = len(worlds_teams.intersection(teams)) / len(teams)
    all_teams[district['display_name']] = district_teams_in_worlds


for district_name, world_per in dict(sorted(all_teams.items(), key=lambda tup: tup[1], reverse=True)).items():
    print(f"{district_name} has {world_per * 100:.1f}% of their teams go to Worlds")
