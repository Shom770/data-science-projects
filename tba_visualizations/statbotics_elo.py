from itertools import groupby
from operator import itemgetter
from os import environ

import requests
from dotenv import load_dotenv

load_dotenv()

SESSION = requests.Session()
URL = "https://www.thebluealliance.com/api/v3/event/{key}/teams/keys"
HEADERS = {"X-TBA-Auth-Key": environ["TBA_API_KEY"]}


team_elos = {
    f"frc{team_dict['team']}": dict(list(team_dict.items())[1:])
    for team_dict in SESSION.get(url="https://api.statbotics.io/v1/teams").json()
}

chezy_elos = [
    (int(str(team_elos[team]["elo"])[:2]) * 100, team_elos[team]["elo"])
    for team in SESSION.get(URL.format(key="2022cc"), headers=HEADERS).json()
]
iri_elos = [
    (int(str(team_elos[team]["elo"])[:2]) * 100, team_elos[team]["elo"])
    for team in SESSION.get(URL.format(key="2022iri"), headers=HEADERS).json()
]

chezy_elo_groups = list(map(itemgetter(0), chezy_elos))

print("Chezy Elos - ")
for elo_group in sorted(set(chezy_elo_groups)):
    print(f"{chezy_elo_groups.count(elo_group)} teams from {elo_group} ELO to {elo_group + 100} ELO")

iri_elo_groups = list(map(itemgetter(0), iri_elos))

print("\nIRI Elos - ")

for elo_group in sorted(set(iri_elo_groups)):
    print(f"{iri_elo_groups.count(elo_group)} teams from {elo_group} ELO to {elo_group + 100} ELO")
