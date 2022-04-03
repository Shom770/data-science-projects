import json
import requests

session = requests.session()
extent = (-79.602563, -75.723267, 37.035112, 39.7)

with open("storm_totals.json") as file:
    storm_totals = json.loads(file.read())

coordinates = {airport: info["coordinates"] for airport, info in storm_totals.items()}


def distance(c1, c2):
    return (abs(c1[0] - c2[0]) ** 2 + abs(c1[1] - c2[1]) ** 2) ** 0.5


def closest_airport(coop_coords):
    dist_mapping = {
        "IAD": distance(storm_totals["IAD"]["coordinates"], coop_coords),
        "BWI": distance(storm_totals["BWI"]["coordinates"], coop_coords),
        "DCA": distance(storm_totals["DCA"]["coordinates"], coop_coords),
        "LYH": distance(storm_totals["LYH"]["coordinates"], coop_coords),
    }
    return min(dist_mapping.items(), key=lambda kv: kv[1])[0]


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
    if all(isinstance(data[0], float) and data[1] for data in stn_data["data"]) and name not in {"AMLV2", "ERLV2"}
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


with open("storm_totals.json", "w") as file:
    storm_totals.update(precip_stns)
    file.write(json.dumps(storm_totals, indent=4))
