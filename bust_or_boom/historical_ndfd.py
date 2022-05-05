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
    BUCKET_NAME = 'noaa-hrrr-bdp-pds'
    coords = defaultdict(float)
    zulu = data_time.hour
    hours = goes_out
    S3_OBJECT = (
        f"hrrr.{data_time.strftime('%Y%m%d')}/conus/hrrr.t{str(zulu).zfill(2)}z.wrfsfcf"
        f"{hours}.grib2"
    )
    FILE_PATH = S3_OBJECT.split("/")[-1].replace("hrrr", data_time.strftime('%Y%m%d'))

    if not os.path.exists(FILE_PATH):
        directory = next(os.walk("./"))
        for file_name in directory[-1]:
            if "KWBN" in file_name:
                os.remove(file_name)

        s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=S3_OBJECT)['Body'].read()

        with open(FILE_PATH, "wb") as file:
            file.write(obj)

        dataset = xarray.open_dataset(
            FILE_PATH,
            engine="cfgrib",
            filter_by_keys={'stepType': 'accum', 'typeOfLevel': 'surface'},
            decode_times=False
        )

        lons = dataset["longitude"].values
        lats = dataset["latitude"].values

        print(dataset.variables)
