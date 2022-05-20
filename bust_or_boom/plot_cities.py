from operator import itemgetter

import numpy as np
import pandas as pd


def get_cities(extent, spacing_lat=0.3, spacing_long=0.3, min_pop=10000):
    extent_lim = extent
    lon_spacing = np.arange(extent_lim[0], extent_lim[1], spacing_long)
    lat_spacing = np.arange(extent_lim[2], extent_lim[3], spacing_lat)

    # uscities.csv attributed to https://simplemaps.com/data/us-cities
    cities_df = pd.read_csv("uscities.csv")
    cities_df = cities_df[
        np.logical_and(np.less_equal(extent[0], cities_df["lng"]), np.less_equal(cities_df["lng"], extent[1]))
    ][
        np.logical_and(np.less_equal(extent[2], cities_df["lat"]), np.less_equal(cities_df["lat"], extent[3]))
    ]

    cities = []

    for slon, elon in zip(lon_spacing, lon_spacing[1:]):
        for slat, elat in zip(lat_spacing, lat_spacing[1:]):
            grid_df = cities_df[
                np.logical_and(np.less_equal(slon, cities_df["lng"]), np.less_equal(cities_df["lng"], elon))
            ][
                np.logical_and(np.less_equal(slat, cities_df["lat"]), np.less_equal(cities_df["lat"], elat))
            ]
            largest_city = grid_df.nlargest(1, ["population"])

            try:
                pop_city, = largest_city["population"]

                if pop_city < min_pop:
                    continue
            except ValueError:
                continue

            cities.append((*largest_city["city"], (*largest_city["lng"], *largest_city["lat"])))

    return cities
