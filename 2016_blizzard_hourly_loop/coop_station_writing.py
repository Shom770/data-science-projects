import json
import requests

session = requests.session()
extent = (-79.602563, -75.723267, 37.035112, 39.7)

with open("storm_totals.json") as file:
    storm_totals = json.loads(file.read())

coordinates = {airport: info["coordinates"] for airport, info in storm_totals.items()}


def closest_airport(coop_coords):
    dist_from_airports = {
        airport: (abs(coop_coords[0] - coords[0]) ** 2 + abs(coop_coords[1] - coords[1]) ** 2) ** 0.5
        for airport, coords in coordinates.items()
    }

    return min(dist_from_airports.items(), key=lambda kv: kv[1])[0]


state = "VA"
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
    stn = dp["properties"]["id"]
    coords = dp["geometry"]["coordinates"]
    if (
        extent[0] + 0.02 <= coords[0] <= extent[1] - 0.02
        and extent[2] + 0.02 <= coords[1] <= extent[3] - 0.02
    ):
        if not precip_stns.get(stn):
            precip_stns[stn] = {}
            precip_stns[stn]["name"] = dp["properties"]["name"]
            precip_stns[stn]["coordinates"] = coords
            precip_stns[stn]["data"] = [(dp["properties"]["snow"], dp["properties"]["temp_hour"])]
        else:
            precip_stns[stn]["data"].append((dp["properties"]["snow"], dp["properties"]["temp_hour"]))

precip_stns = {
    name: stn_data for name, stn_data in precip_stns.items()
    if all(isinstance(data[0], float) and data[1] for data in stn_data["data"])
}
for name, stn_data in precip_stns.items():
    closest = storm_totals[closest_airport(stn_data["coordinates"])]
    total_snow = sum(tup[0] for tup in stn_data["data"])
    stn_data["snow"] = total_snow

    hourly_precip = []

    for idx, day in enumerate(stn_data["data"]):
        if hourly_precip:
            hours_so_far = len(hourly_precip) + 1
        else:
            hours_so_far = 0

        time_mapping = {0: 0, 1: 23, 2: 46}
        hours_to_add = time_mapping[idx] + int(day[1])
        to_add = closest["hourly_precip"][hours_so_far:hours_to_add]
        cur_snow = closest["hourly_snow"][hours_so_far:hours_to_add]

        to_add = [
            round(precip * (day[0] / tot_sum), 3) if (tot_sum := sum(cur_snow)) else precip
            for precip in to_add
        ]
        hourly_precip.extend(to_add)

    ratio = total_snow / sum([p * 10 for p in hourly_precip])

    stn_data["hourly_precip"] = hourly_precip
    stn_data["hourly_snow"] = [round(p * 10 * ratio, 3) for p in hourly_precip]
    stn_data.pop("data")


        # precip_stns = {
#     name: data for name, data in precip_stns.items()
#     if any(p for p in data["hourly_precip"])
# }
# print(precip_stns)
# for station, sd in precip_stns.items():
#     ratio = sd["snow"] / sum([p * 10 for p in sd["hourly_precip"]])
#
#     sd["hourly_snow"] = [round(s * 10 * ratio) for s in sd["hourly_precip"]]
#
