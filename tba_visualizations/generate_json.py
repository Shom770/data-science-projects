import itertools
import logging
from json import dump
from os import environ

import requests
from dotenv import load_dotenv
from tbapy import TBA
from uszipcode import SearchEngine

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/teams/2022/{page}"
TBA_API_KEY = environ["TBA_API_KEY"]
SEARCH = SearchEngine()
tba = TBA(TBA_API_KEY)

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

all_teams = {}
worlds_teams = itertools.chain.from_iterable(
    [tba.event_teams(key) for key in ("2022carv", "2022gal", "2022hop", "2022new", "2022roe", "2022tur")]
)

for team in worlds_teams:
    if team["country"] == "USA" and team["postal_code"]:
        try:
            zipcode_info = SEARCH.by_zipcode(int(team["postal_code"]))
            all_teams[team["team_number"]] = (zipcode_info.lng, zipcode_info.lat)
        except ValueError:
            logging.error(f"Could not add Team {team['team_number']} to list of teams")


with open("worlds_teams.json", "w") as file:
    dump(all_teams, file, indent=4)
    logger.info("Wrote to all_teams.json")
