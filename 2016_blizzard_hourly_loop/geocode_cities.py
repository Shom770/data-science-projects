import json

import requests


session = requests.session()
list_of_cities = ["Germantown, MD"]
loc = {}

for city in list_of_cities:
    loc[city] = (
        session.get(
            f"https://nominatim.openstreetmap.org/search?q={city}&format=geojson"
        ).json()["features"][0]["geometry"]["coordinates"]
    )

with open("cities.json", "w") as file:
    file.write(json.dumps(loc, indent=3))
