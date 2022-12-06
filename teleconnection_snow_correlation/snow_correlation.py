from json import load
from typing import Iterable

import numpy as np
import scipy.stats
from scipy.stats import norm

with open("nao_values.json") as nao_file:
    nao_values = load(nao_file)
    winter_nao_values = {
        key: value[:3] + value[10:] for key, value in nao_values.items()
    }

with open("ao_values.json") as ao_file:
    ao_values = load(ao_file)
    winter_ao_values = {key: value[:3] + value[10:] for key, value in ao_values.items()}

with open("pna_values.json") as pna_file:
    pna_values = load(pna_file)
    winter_pna_values = {
        key: value[:3] + value[10:] for key, value in pna_values.items()
    }

with open("epo_values.json") as epo_file:
    epo_values = load(epo_file)
    winter_epo_values = {
        key: value[:3] + value[10:] for key, value in epo_values.items()
    }


def calculate_percentile(
    teleconnection: float, dataset: Iterable, negative: bool = False
) -> float:
    multiply_by = -1 if negative else 1

    teleconnection_values = [
        teleconnection_value * multiply_by
        for yearly_values in dataset
        for teleconnection_value in yearly_values
        if (teleconnection_value < 0 and negative)
        or (teleconnection_value > 0 and not negative)
    ]
    teleconnection *= multiply_by

    all_skews = [
        (
            0,
            [
                np.log(teleconnection_value)
                for teleconnection_value in teleconnection_values
            ],
        ),
        (
            1,
            [
                np.sqrt(teleconnection_value)
                for teleconnection_value in teleconnection_values
            ],
        ),
        (
            2,
            [
                1 / teleconnection_value
                for teleconnection_value in teleconnection_values
            ],
        ),
    ]

    lowest, teleconnection_values = min(
        all_skews, key=lambda x: abs(scipy.stats.skew(x[1]))
    )
    if lowest == 0:
        teleconnection_normalized = np.log(teleconnection)
    elif lowest == 1:
        teleconnection_normalized = np.sqrt(teleconnection)
    else:
        teleconnection_normalized = 1 / teleconnection

    # Get z-score
    z_score = (teleconnection_normalized - np.mean(teleconnection_values)) / np.std(
        teleconnection_values
    )

    # Retrieve percentile
    percentile = (1 - norm.sf(z_score)) * 100
    if percentile < 1:
        percentile = 1
    elif percentile >= 100:
        percentile = 99.99

    return percentile


for year, (
    nao_yearly_values,
    ao_yearly_values,
    pna_yearly_values,
    epo_yearly_values,
) in enumerate(
    zip(
        winter_nao_values.values(),
        winter_ao_values.values(),
        winter_pna_values.values(),
        winter_epo_values.values(),
    ),
    start=1950,
):
    for month, (nao_value, ao_value, pna_value, epo_value) in enumerate(zip(nao_yearly_values, ao_yearly_values, pna_yearly_values, epo_yearly_values), start=1):
        if (nao_value < 0):
            print({1: "January", 2: "February", 3: "March", 4: "November", 5: "December"}[month], year)

        if (ao_value < 0):
            print({1: "January", 2: "February", 3: "March", 4: "November", 5: "December"}[month], year)

        if (pna_value < 0):
            print({1: "January", 2: "February", 3: "March", 4: "November", 5: "December"}[month], year)
