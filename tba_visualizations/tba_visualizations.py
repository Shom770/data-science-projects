import datetime
from os import environ

import matplotlib.pyplot as plt
import requests
from dotenv import load_dotenv

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/team/frc4099/matches/{year}/simple"
TBA_API_KEY = environ["TBA_API_KEY"]

all_matches = []

for year in range(2011, 2023):
    resp = SESSION.get(URL.format(year=year), headers={"X-TBA-Auth-Key": TBA_API_KEY}).json()
    matches = [match for match in resp if match["time"] and datetime.datetime.fromtimestamp(match["time"]).month < 5]
    all_matches.append(len(matches) or len(resp))

fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(1, 1, 1)

ax.plot(range(2011, 2023), all_matchesg)
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
