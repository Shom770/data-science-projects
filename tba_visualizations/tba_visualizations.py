import datetime
from os import environ

import matplotlib.pyplot as plt
import numpy as np
import requests
from dotenv import load_dotenv
from scipy import interpolate

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/team/frc4099/matches/{year}/simple"
TBA_API_KEY = environ["TBA_API_KEY"]

matches_won = []
matches_lost = []
all_years = range(2011, 2023)

for year in range(2011, 2023):
    resp = SESSION.get(URL.format(year=year), headers={"X-TBA-Auth-Key": TBA_API_KEY}).json()
    matches = [match for match in resp if match["time"] and datetime.datetime.fromtimestamp(match["time"]).month <= 4]
    mw = len([
        match for match in matches
        if match["winning_alliance"] and "frc4099" in match["alliances"][match["winning_alliance"]]["team_keys"]
    ])
    ml = len([
        match for match in matches
        if match["winning_alliance"] and "frc4099" not in match["alliances"][match["winning_alliance"]]["team_keys"]
    ])

    matches_won.append(mw)
    matches_lost.append(ml)

all_years_s = np.linspace(min(all_years), max(all_years), 300)

mw_splice = interpolate.make_interp_spline(all_years, matches_won, k=3)
matches_won_s = mw_splice(all_years_s)

ml_splice = interpolate.make_interp_spline(all_years, matches_lost, k=3)
matches_lost_s = ml_splice(all_years_s)

fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(1, 1, 1)

ax.plot(all_years_s, matches_won_s, c="green")
ax.plot(all_years_s, matches_lost_s, c="red")

ax.set_title(
    "The number of matches Team 4099 has played during the season since 2011",
    fontsize=9,
    loc="left"
)

plt.suptitle(
    f"Team 4099's # of Matches (2011-2022)",
    fontsize=13,
    ha="left",
    va="bottom",
    x=0,
    y=1.06,
    fontweight="bold",
    transform=ax.transAxes
)
plt.show()
