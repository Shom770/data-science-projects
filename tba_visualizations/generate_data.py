import json
import logging

import geopy.distance
import numpy as np

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

extent = (-126.298828, -66.313477, 24.686952, 49.686953)

lats = np.arange(extent[2], extent[3], 1.25)
lons = np.arange(extent[0], extent[1], 1.25)

with (
        open("all_teams.json") as all_teams_file,
        open("worlds_teams.json") as worlds_file
):
    all_teams = json.load(all_teams_file)
    worlds_teams = json.load(worlds_file)

team_loc = list(all_teams.values())
worlds_loc = list(worlds_teams.values())

z_data = []

for idx, lat in enumerate(lats):
    filtered_locations = [loc for loc in team_loc if geopy.distance.distance(loc[::-1], (lat, loc[0])).miles <= 100]
    worlds_locs_fi = [loc for loc in worlds_loc if geopy.distance.distance(loc[::-1], (lat, loc[0])).miles <= 100]
    z_data.append([])

    for lon in lons:
        amt_teams = len(
            [loc for loc in filtered_locations if geopy.distance.distance(loc[::-1], (lat, lon)).miles <= 100]
        )
        amt_worlds_teams = len(
            [loc for loc in worlds_locs_fi if geopy.distance.distance(loc[::-1], (lat, lon)).miles <= 100]
        )

        try:
            z_data[-1].append(
                amt_worlds_teams / amt_teams
            )
        except ZeroDivisionError:
            z_data[-1].append(0)

    logger.info(f"{idx + 1}/{len(lats)} latitudes finished calculating.")

with open("num_teams_data.json", "w") as file:
    json.dump(z_data, file, indent=4)
