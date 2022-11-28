from json import load
from typing import Iterable

import numpy as np
import scipy.stats
from scipy.stats import norm

with open("nao_values.json") as file:
    nao_values = load(file)

winter_nao_values = {key: value[:3] + value[10:] for key, value in nao_values.items()}


def calculate_percentile(teleconnection: float,  dataset: Iterable, negative: bool = False) -> float:
    multiply_by = -1 if negative else 1
    
    teleconnection_values = [
        teleconnection_value * multiply_by for yearly_values in dataset
        for teleconnection_value in yearly_values
        if (teleconnection_value < 0 and negative) or (teleconnection_value > 0 and not negative)
    ]
    teleconnection *= multiply_by

    all_skews = [
        (0, [np.log(teleconnection_value) for teleconnection_value in teleconnection_values]),
        (1, [np.sqrt(teleconnection_value) for teleconnection_value in teleconnection_values]),
        (2, [1 / teleconnection_value for teleconnection_value in teleconnection_values])
    ]

    lowest, teleconnection_values = min(all_skews, key=lambda x: abs(scipy.stats.skew(x[1])))
    if lowest == 0:
        teleconnection_normalized = np.log(teleconnection)
    elif lowest == 1:
        teleconnection_normalized = np.sqrt(teleconnection)
    else:
        teleconnection_normalized = 1 / teleconnection

    # Get z-score
    z_score = (teleconnection_normalized - np.mean(teleconnection_values)) / np.std(teleconnection_values)

    # Retrieve percentile
    percentile = (1 - norm.sf(z_score)) * 100
    if percentile < 1:
        percentile = 1
    elif percentile >= 100:
        percentile = 99.99

    return percentile


print(calculate_percentile(-0.7584, winter_nao_values.values(), negative=True))