import logging
from json import dump
from os import environ

import requests
from dotenv import load_dotenv
from uszipcode import SearchEngine

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/teams/2022/{page}"
TBA_API_KEY = environ["TBA_API_KEY"]
SEARCH = SearchEngine()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

all_teams = {}

for page_num in range(0, 20):
    resp = SESSION.get(URL.format(page=page_num), headers={"X-TBA-Auth-Key": TBA_API_KEY}).json()
    if not resp:
        break

    for team in resp:
        if team["country"] == "USA" and team["postal_code"]:
            try:
                zipcode_info = SEARCH.by_zipcode(int(team["postal_code"]))
                all_teams[team["team_number"]] = (zipcode_info.lng, zipcode_info.lat)
            except ValueError:
                logging.error(f"Could not add Team {team['team_number']} to list of teams")

    logger.info(f"Page {page_num} completed")


with open("all_teams.json", "w") as file:
    dump(file, all_teams, indent=4)
    logger.info("Wrote to all_teams.json")
