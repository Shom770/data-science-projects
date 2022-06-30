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

with open("all_teams.json") as file:
    all_teams = json.load(file)

team_loc = list(all_teams.values())
z_data = []

for idx, lat in enumerate(lats):
    filtered_locations = [loc for loc in team_loc if geopy.distance.distance(loc[::-1], (lat, loc[0])).miles <= 100]
    z_data.append([])

    for lon in lons:
        z_data[-1].append(
            len([loc for loc in filtered_locations if geopy.distance.distance(loc[::-1], (lat, lon)).miles <= 100])
        )
    logger.info(f"{idx + 1}/{len(lats)} latitudes finished calculating.")

with open("num_teams_data.json", "w") as file:
    json.dump(z_data, file, indent=4)
