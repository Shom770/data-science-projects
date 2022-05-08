from shapefile import Reader


shp_pts = Reader("nws_dat_damage_pnts.shp")

info_needed = [
    {"storm_time": record[2], "rating": record[9], "windspeed": record[11], "lat": record[14], "lon": record[15]}
    for record in shp_pts.records()
]

