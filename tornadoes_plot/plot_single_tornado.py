from shapefile import Reader


shp_paths = Reader("nws_dat_damage_paths.shp")
print(shp_paths.records())
