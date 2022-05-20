from operator import itemgetter

import numpy as np
import pandas as pd


def get_cities(extent, diff, min_pop):
    extent_lim = (extent[0] + diff, extent[1] - diff, extent[2] + diff, extent[3] - diff)

    # uscities.csv attributed to https://simplemaps.com/data/us-cities
    cities_df = pd.read_csv("uscities.csv")
    cities_df = cities_df[
        np.logical_and(np.less_equal(extent[0], cities_df["lng"]), np.less_equal(cities_df["lng"], extent[1]))
    ][
        np.logical_and(np.less_equal(extent[2], cities_df["lat"]), np.less_equal(cities_df["lat"], extent[3]))
    ][
        cities_df["population"] >= min_pop
    ]

    print(cities_df.max(key=itemgetter("population")))
