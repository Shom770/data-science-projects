from os import environ

import requests
from dotenv import load_dotenv

load_dotenv()

SESSION = requests.session()
URL = "https://www.thebluealliance.com/api/v3/teams/2022/{page}"
TBA_API_KEY = environ["TBA_API_KEY"]

chs_teams = set(SESSION.get(
    "https://www.thebluealliance.com/api/v3/district/2022chs/teams/keys",
    headers={"X-TBA-Auth-Key": TBA_API_KEY}
).json())
chs_rookie_years = []
california_rookie_years = []


for page_num in range(0, 20):
    resp = SESSION.get(URL.format(page=page_num), headers={"X-TBA-Auth-Key": TBA_API_KEY}).json()
    if not resp:
        break

    for team in resp:
        if team["state_prov"] == "California":
            california_rookie_years.append(team["rookie_year"])
        elif team["key"] in chs_teams:
            chs_rookie_years.append(team["rookie_year"])


print(
    f"Average rookie year of CHS teams in 2022 - {round(sum(chs_rookie_years) / len(chs_rookie_years))}"
)
print(
    f"Average rookie year of Californian teams in 2022 - "
    f"{round(sum(california_rookie_years) / len(california_rookie_years))}"
)
