import json
import requests

session = requests.session()
extent = (-79.602563, -75.723267, 37.035112, 39.6)

with open("storm_totals.json") as file:
    storm_totals = json.loads(file.read())

coordinates = {airport: info["coordinates"] for airport, info in storm_totals.items()}


def closest_airport(coop_coords):
    dist_from_airports = {
        airport: (abs(coop_coords[0] - coords[0]) ** 2 + abs(coop_coords[1] - coords[1]) ** 2) ** 0.5
        for airport, coords in coordinates.items()
    }

    return min(dist_from_airports.items(), key=lambda kv: kv[1])[0]


state = "MD"
all_data = session.get(
    f"https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-22&network={state}_COOP"
).json()

all_data["features"].extend(
    session.get(
        f"https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-23&network={state}_COOP"
    ).json()["features"]
)
all_data["features"].extend(
    session.get(
        f"https://mesonet.agron.iastate.edu/api/1/daily.geojson?date=2016-01-24&network={state}_COOP"
    ).json()["features"]
)

precip_stns = {}

for dp in all_data["features"]:
    dp_coords = dp["geometry"]["coordinates"]
    if (
        extent[0] + 0.02 <= dp_coords[0] <= extent[1] - 0.02
        and extent[2] + 0.02 <= dp_coords[1] <= extent[3] - 0.02
    ):
        if dp["properties"]["snow"]:
            closest = storm_totals[closest_airport(dp_coords)]
            stn = dp["properties"]["id"]
            if so_far := precip_stns.get(stn):
                hours_so_far = len(so_far["hourly_precip"])
                hours_to_add = len(so_far["hourly_precip"]) + (int(dp["properties"]["temp_hour"]) - 1)
                precip_stns[stn]["snow"] += dp["properties"]["snow"]

                try:
                    period_precip = [
                            round(
                                precip *
                                (dp["properties"]["snow"] / sum(closest["hourly_snow"][hours_so_far:hours_to_add])),
                                3
                            )
                            for precip in closest["hourly_precip"][hours_so_far:hours_to_add]
                    ]
                    precip_stns[stn]["hourly_precip"].extend(period_precip)
                except ZeroDivisionError:
                    precip_stns[stn]["hourly_precip"].extend(closest["hourly_precip"][hours_so_far:hours_to_add])
            else:
                precip_stns[stn] = {}
                precip_stns[stn]["name"] = dp["properties"]["name"]

                hours_to_add = int(dp["properties"]["temp_hour"]) - 1
                precip_stns[stn]["snow"] = dp["properties"]["snow"]

                try:
                    precip_stns[stn]["hourly_precip"] = [
                        round(precip * (dp["properties"]["snow"] / sum(closest["hourly_snow"][:hours_to_add])), 3)
                        for precip in closest["hourly_precip"][:hours_to_add]
                    ]
                except ZeroDivisionError:
                    precip_stns[stn]["hourly_precip"] = closest["hourly_precip"][:hours_to_add]
        else:
            print("No data")

precip_stns = {name: data for name, data in precip_stns.items()}
print(precip_stns)
# for station, sd in precip_stns.items():
#     ratio = sd["snow"] / sum([p * 10 for p in sd["hourly_precip"]])
#
#     sd["hourly_snow"] = [round(s * 10 * ratio) for s in sd["hourly_precip"]]
#
