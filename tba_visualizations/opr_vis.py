import itertools
from os import environ

import matplotlib
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import numpy as np
import requests
from dotenv import load_dotenv
from scipy.stats import norm, skew

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/event/{key}/{mode}"
TBA_API_KEY = environ["TBA_API_KEY"]
EVENT_KEY = "2022chcmp"
LATEX_SPACE = r"\;"

fig: plt.Figure = plt.figure(figsize=(12, 6))
ax: plt.Axes = fig.add_subplot(1, 1, 1)

# Change font to Inter
for font in font_manager.findSystemFonts(["."]):
    font_manager.fontManager.addfont(font)

# Set font family globally
matplotlib.rcParams['font.family'] = 'Inter'


def rescale(colormap):
    return (colormap - np.min(colormap)) / (np.max(colormap) - np.min(colormap))


all_ccwms = SESSION.get(
    URL.format(key=EVENT_KEY, mode="oprs"), headers={"X-TBA-Auth-key": TBA_API_KEY}
).json()["oprs"]
all_alliances = SESSION.get(
     URL.format(key=EVENT_KEY, mode="alliances"), headers={"X-TBA-Auth-key": TBA_API_KEY}
).json()
event_name = SESSION.get(
     URL.format(key=EVENT_KEY, mode="simple"), headers={"X-TBA-Auth-key": TBA_API_KEY}
).json()["name"]

alliance_sums = [
    [all_ccwms[pick] for pick in alliance["picks"]] for alliance in all_alliances
]

opr_dataset = np.array(
    sorted({
        sum(alliance_sum) / len(alliance_sum)
        for alliance_sum in itertools.product(itertools.chain.from_iterable(alliance_sums), repeat=len(alliance_sums[0]))
        if len(alliance_sum) == len(alliance_sums[0])
    })
)
alliance_sums = [sum(all_sum) / len(all_sum) for all_sum in alliance_sums]

mode, opr_dataset = min(
    (
        (np.log, np.log(opr_dataset)),
        (np.sqrt, opr_dataset ** 0.5)
    ),
    key=lambda arr: abs(skew(arr[1]))
)

percentiles_picks = []
alliance_picks = ["\n".join(alliance["picks"]).replace("frc", "") for alliance in all_alliances]

for opr_sum in alliance_sums:
    z_score = (mode(opr_sum) - opr_dataset.mean()) / opr_dataset.std()
    percentiles_picks.append((1 - norm.sf(z_score)) * 100)

cmap = plt.get_cmap("coolwarm_r")
ax.bar(
    alliance_picks,
    percentiles_picks,
    color=cmap(rescale(np.array(percentiles_picks)))
)

ax.set_title(
    "How good was an alliance compared to all possible combinations for an alliance?",
    fontsize=10,
    loc="left"
)

ax.set_xlabel(fr"$\bfAlliances in {event_name}$".replace(" ", LATEX_SPACE))

ax.set_ylabel(r"$\bfPercentile of Alliance Compared to All Poss. Alliances$".replace(" ", LATEX_SPACE))
ax.set_yticks([1, 20, 40, 60, 80, 99], ["1st", "20th", "40th", "60th", "80th", "99th"])

plt.suptitle(
    fr"$\bfPercentile of the Alliances in {event_name}$".replace(" ", LATEX_SPACE),
    fontsize=13,
    ha="left",
    va="bottom",
    x=0,
    y=1.04,
    fontweight="bold",
    transform=ax.transAxes
)

plt.show()
