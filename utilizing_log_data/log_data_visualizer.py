import bisect
import datetime
import json
from os import environ

import matplotlib.pyplot as plt
import numpy as np
import tbapy
from dotenv import load_dotenv
from matplotlib.offsetbox import AnchoredText


def find_closest(arr, val):
    idx = np.abs(arr - val).argmin()
    return arr[idx]


with open("log_info.json") as file:
    log_data_json = json.load(file)

load_dotenv()

FORMAT_STRING = "%y-%m-%d_%H-%M-%S"
tba = tbapy.TBA(environ["TBA_API_KEY"])

all_matches = tba.team_matches(
    "frc4099", event="2022tur", simple=True
)
all_matches.extend(
    tba.team_matches("frc4099", event="2022cmptx", simple=True)
)

datetime_to_match = {
    datetime.datetime.fromtimestamp(match["actual_time"]).replace(second=0): match
    for match in all_matches
}
all_datetimes = np.array(list(datetime_to_match.keys()))

brownouts_win = []
scores_win = []

brownouts_lose = []
scores_lose = []

for log_file_name, log_data in log_data_json.items():
    if "q" in log_file_name or "e" in log_file_name:
        if log_file_name[-3:] in {"e19", "e20"}:
            continue

        log_time = datetime.datetime.strptime(
            "_".join(log_file_name.split("_")[1:-1]),
            FORMAT_STRING
        ).replace(second=0)

        spec_match = datetime_to_match[find_closest(all_datetimes, log_time)]

        alliance = "blue" if "frc4099" in spec_match["alliances"]["blue"]["team_keys"] else "red"
        opp_alliance = "red" if alliance == "blue" else "blue"

        if (score := spec_match["alliances"][alliance]["score"]) > spec_match["alliances"][opp_alliance]["score"]:
            scores_win.append(spec_match["alliances"][alliance]["score"])
            brownouts_win.append(log_data["brownouts"])
        else:
            scores_lose.append(spec_match["alliances"][alliance]["score"])
            brownouts_lose.append(log_data["brownouts"])

fig, ax = plt.subplots()

ax.scatter(brownouts_win, scores_win, c="green", label="Win")
ax.scatter(brownouts_lose, scores_lose, c="red", label="Lose")

ax.add_artist(
    AnchoredText(
        f"correlation coefficient = -0.34",
        loc="lower right",
        prop={"size": 10},
        frameon=True
    )
)
plt.title("Correlation between brownouts and score by match")

plt.xlabel("Brownouts (by match)")
plt.ylabel("Score (by match)")
plt.legend()

plt.show()
