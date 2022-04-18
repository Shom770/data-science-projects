import json

import requests


session = requests.session()
list_of_cities = [
    "Gaithersburg, MD",
    "Frederick, MD",
    "Front Royal, VA",
    "Baltimore, MD",
    "Washington D.C.",
    "Manassas, VA",
    "Charlottesville, VA",
    "Lexington Park, MD",
    "Martinsburg, WV",
    "Winchester, VA",
    "Culpeper, VA"
]
loc = {}

for city in list_of_cities:
    loc[city.split(",")[0]] = (
        session.get(
            f"https://nominatim.openstreetmap.org/search?q={city}&format=geojson"
        ).json()["features"][0]["geometry"]["coordinates"]
    )

with open("cities.json", "w") as file:
    file.write(json.dumps(loc, indent=3))
