from os import environ

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/event/2022hop/matches"
TBA_API_KEY = environ["TBA_API_KEY"]

all_matches = SESSION.get(URL, headers={"X-TBA-Auth-Key": TBA_API_KEY}).json()
scouting_matches = []
match_alliances = []

with open("quick_script_data.txt") as file:
    teams = {"frc" + line.strip("|").split("|")[0] for idx, line in enumerate(file.readlines()) if idx != 0}

for match in all_matches:
    if any(
            team in teams for team in match["alliances"]["blue"]["team_keys"] + match["alliances"]["red"]["team_keys"]
    ):
        scouting_matches.append(
            {
                "Match Number": match["match_number"],
                "Video URL": f"https://youtube.com/watch?v={match['videos'][-1]['key']}"
            }
        )
        match_alliances.append(
            (
                {"Match Key": match["key"]}
                | {
                    alliance_pos: team.removeprefix("frc")
                    for alliance_pos, team in zip(
                        ["Red 1", "Red 2", "Red 3"], match["alliances"]["red"]["team_keys"]
                    )
                }
                | {
                    alliance_pos: team.removeprefix("frc")
                    for alliance_pos, team in zip(
                        ["Blue 1", "Blue 2", "Blue 3"], match["alliances"]["blue"]["team_keys"]
                    )
                }
            )
        )

print(pd.DataFrame(scouting_matches).to_csv())
print(pd.DataFrame(match_alliances).to_csv())
