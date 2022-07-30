# from itertools import groupby
# from operator import itemgetter
# from os import environ
#
# import requests
# from dotenv import load_dotenv
#
# load_dotenv()
#
# SESSION = requests.Session()
# URL = "https://www.thebluealliance.com/api/v3/event/{key}/teams/keys"
# HEADERS = {"X-TBA-Auth-Key": environ["TBA_API_KEY"]}
#
# teams_played = set()
# for event in SESSION.get("https://www.thebluealliance.com/api/v3/team/frc4099/events/2022", headers=HEADERS).json():
#     if event["key"] == "2022cc":
#         continue
#     teams_played = teams_played.union(SESSION.get(URL.format(key=event["key"]), headers=HEADERS).json())
#
# chezy_teams = SESSION.get(URL.format(key="2022cc"), headers=HEADERS).json()
# print(len(chezy_teams))
# print(f"{((len(teams_played.intersection(chezy_teams)) - 1) / (len(chezy_teams) - 1)) * 100}%")
import itertools
from os import environ

from dotenv import load_dotenv
from tbapy import TBA

load_dotenv()

tba = TBA(environ["TBA_API_KEY"])

chezy_teams = set(tba.event_teams("2022cc", keys=True))
worlds_teams = list(itertools.chain.from_iterable(
    [tba.event_teams(key, keys=True) for key in ("2022carv", "2022gal", "2022hop", "2022new", "2022roe", "2022tur")]
))

