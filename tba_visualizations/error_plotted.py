import datetime
import operator
from os import environ

import matplotlib.pyplot as plt
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

fig, ax = plt.subplots()


class OPRCalculator:

    def __init__(self):
        self.headers = {'X-TBA-Auth-Key': environ["TBA_API_KEY"]}

    def get_oprs(self):
        matches_link = "https://www.thebluealliance.com/api/v3/event/2022iri/matches"
        scores = []
        scouting_data = pd.read_csv("2022iri_scout_data.csv")

        for match in sorted(
                requests.get(url=matches_link, headers=self.headers).json(), key=operator.itemgetter("match_number")
        ):
            if match['comp_level'] == 'qm':
                blue_score = match["score_breakdown"]["blue"]
                red_score = match["score_breakdown"]["red"]

                match_scouts = scouting_data.loc[scouting_data["match_key"] == f"qm{match['match_number']}"]

                if match_scouts.empty:
                    break

                if len(match_scouts) < 5:
                    continue

                print(datetime.datetime.fromtimestamp(match["actual_time"]), match["match_number"])

                total_cargo_points = (
                        blue_score["autoCargoPoints"] + blue_score["teleopCargoPoints"]
                        + red_score["autoCargoPoints"] + red_score["teleopCargoPoints"]
                )
                scout_cargo_points = (
                        sum(match_scouts["auto_upper_hub"]) * 4 + sum(match_scouts["auto_lower_hub"]) * 2
                        + sum(match_scouts["teleop_upper_hub"]) * 2 + sum(match_scouts["teleop_lower_hub"])
                )

                scores.append(abs(total_cargo_points - scout_cargo_points))

        new_scores = []

        for idx in range(0, len(scores), 5):
            window = scores[idx:idx + 5]
            new_scores.append(sum(window) / len(window))

        ax.plot([num for num in range(1, 61, 5)], new_scores)

        plt.show()


OPRCalculator().get_oprs()
