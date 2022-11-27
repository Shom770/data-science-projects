import collections
import statistics
from os import environ

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
from scipy.optimize import nnls, lsq_linear
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import lsmr

load_dotenv()


class OPRCalculator:

    def __init__(self):
        self.headers = {'X-TBA-Auth-Key': environ["TBA_API_KEY"]}

    def get_sprs(self):
        matches_link = "https://www.thebluealliance.com/api/v3/event/2022iri/matches"
        scouts_to_combinations = collections.defaultdict(list)
        all_combinations = []
        scouting_data = pd.read_csv("2022iri_scout_data.csv")
        scout_ids = sorted(set(scouting_data["scout_id"]))
        matches_scouted = collections.defaultdict(int)

        for match in requests.get(url=matches_link, headers=self.headers).json():
            if match['comp_level'] == 'qm':
                blue_score = match["score_breakdown"]["blue"]
                red_score = match["score_breakdown"]["red"]

                match_scouts = scouting_data.loc[scouting_data["match_key"] == f"qm{match['match_number']}"]

                if match_scouts.empty:
                    break

                if len(match_scouts) < 5:
                    continue

                for alliance_score, alliance_name in zip((blue_score, red_score), ("Blue", "Red")):
                    alliance_scouts = match_scouts[match_scouts["alliance"] == alliance_name]
                    alliance_scout_ids = set(alliance_scouts["scout_id"])

                    for scout in alliance_scout_ids:
                        matches_scouted[scout] += 1

                    total_cargo_points = (
                            alliance_score["autoCargoPoints"] + alliance_score["teleopCargoPoints"]
                    )
                    scout_cargo_points = (
                            sum(alliance_scouts["auto_upper_hub"]) * 4 + sum(alliance_scouts["auto_lower_hub"]) * 2
                            + sum(alliance_scouts["teleop_upper_hub"]) * 2 + sum(alliance_scouts["teleop_lower_hub"])
                    )

                    total_error = abs(total_cargo_points - scout_cargo_points)

                    for scout in alliance_scout_ids:
                        scouts_to_combinations[scout].append(total_error)

                    all_combinations.append((list(alliance_scout_ids), total_error))

        scouts_to_combinations = {name: statistics.mean(value) for name, value in scouts_to_combinations.items()}

        scout_errors = collections.defaultdict(list)

        for to_find in scout_ids:
            for combination in all_combinations:
                if to_find not in combination[0] or len(combination[0]) != 3:
                    continue

                spec_combo = combination[0].copy()
                spec_combo.remove(to_find)

                scout1, scout2 = spec_combo

                expected_error = scouts_to_combinations[scout1] / 3 + scouts_to_combinations[scout2] / 3
                actual_error = combination[1]

                scout_errors[to_find].append(abs(actual_error - expected_error))

        return {name: statistics.mean(value) for name, value in scout_errors.items()}, matches_scouted

    def print_sprs(self):
        sprs, matches_played = self.get_sprs()
        sprs = dict(sorted(sprs.items(), reverse=True, key=lambda tup: matches_played[tup[0]]))

        for name, value in sprs.items():
            print(
                f"{name.title()} contributed approximately {value:.2f} points of error on average and scouted {matches_played[name]} matches.")


sprs, matches_played = OPRCalculator().get_sprs()

y_data = list(sprs.values())
x_data = [matches_played[name] for name in sprs]

import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import numpy as np

fig = plt.figure(figsize=(12, 6))
ax: plt.Axes = plt.subplot(1, 1, 1)

ax.scatter(x_data, y_data)
ax.add_artist(
    AnchoredText(
        f"cc = {np.corrcoef(x_data, y_data)}",
        loc="lower right",
        prop={"size": 10},
        frameon=True,
        zorder=300
    )
)

plt.title("SPRs to Matches Played")

plt.show()
