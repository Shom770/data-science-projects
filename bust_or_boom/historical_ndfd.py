import os
from collections import defaultdict
from datetime import timedelta

import boto3
from botocore import UNSIGNED
from botocore.config import Config
import xarray


def historical_ndfd_snow(data_time, extent, go_back, goes_out=24):
    min_lon, max_lon, min_lat, max_lat = extent
    data_time = data_time - timedelta(hours=go_back)
    BUCKET_NAME = 'noaa-ndfd-pds'
    zulu = data_time.hour
    hours = goes_out
    S3_OBJECT = (
        f"wmo/snow/{data_time.year}/{str(data_time.month).zfill(2)}/{str(data_time.day).zfill(2)}/"
    )

    directory = next(os.walk("./"))
    for file_name in directory[-1]:
        if "KWBN" in file_name or file_name.endswith(".grib2"):
            os.remove(file_name)

    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    all_keys = s3.list_objects(Bucket=BUCKET_NAME, Prefix=S3_OBJECT)["Contents"]
    key_to_use = min(
        [key["Key"] for key in all_keys if key["Key"][-4:-2] == "00"],
        key=lambda key: int(key[-2:])
    )
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=key_to_use)['Body'].read()

    with open(key_to_use.split("/")[-1], "wb") as file:
        file.write(obj)

    dataset = xarray.open_dataset(
        key_to_use.split("/")[-1],
        engine="cfgrib",
        filter_by_keys={'stepUnits': 0, 'stepType': 'accum', 'typeOfLevel': 'surface'},
        decode_times=False
    )

    lons = dataset["longitude"].values
    lats = dataset["latitude"].values

    return lons - 359.99, lats, dataset["asnow"].values * 39.3700787
