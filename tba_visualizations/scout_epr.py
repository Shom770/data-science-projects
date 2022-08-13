import collections
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

    def get_oprs(self):
        matches_link = "https://www.thebluealliance.com/api/v3/event/2022iri/matches"
        scores = []
        matrix_a = []
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

                    matrix_a.append([int(scout in alliance_scout_ids) for scout in scout_ids])
                    scores.append(abs(total_cargo_points - scout_cargo_points))

        A = np.array(matrix_a)
        b = np.array(scores)

        # change based off errors
        matrix_b = []
        score_err = []

        raw_eprs = lsmr(A, b)[0]

        eprs = {scout: (error, matches_scouted[scout]) for scout, error in zip(scout_ids, raw_eprs)}

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
                    scout_est_error = sum([eprs[scout][0] for scout in alliance_scout_ids])

                    matrix_b.append([int(scout in alliance_scout_ids) for scout in scout_ids])
                    score_err.append(abs(scout_est_error - total_error))

        A2 = np.array(matrix_b)
        b2 = np.array(score_err)

        errors = lsmr(A2, b2)[0]

        eprs = {key: (eprs[key][0] + corres, eprs) for key, corres in zip(eprs.keys(), errors)}

        return dict(sorted(eprs.items(), key=lambda pair: pair[1][0], reverse=True))

    def print_oprs(self):
        final_data = self.get_oprs()

        for scout, error in final_data.items():
            print(f"{scout.capitalize()} contributed {error[0]:.2f} points of error and scouted {error[1]} matches.")


OPRCalculator().print_oprs()
