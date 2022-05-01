import os
from datetime import datetime, timedelta

import boto3
from botocore import UNSIGNED
from botocore.config import Config
import xarray


def historical_hrrr_snow(extent, type_="snowfall"):
    data_time = datetime(year=2022, month=1, day=8)

    if type_ == "depth":
        hours = 0
        step_type = "instant"
        short_name = "sde"
    else:
        hours = 24
        step_type = "accum"
        short_name = "asnow"

    min_lon, max_lon, min_lat, max_lat = extent
    data_time = data_time - timedelta(hours=hours)
    BUCKET_NAME = 'noaa-hrrr-bdp-pds'
    S3_OBJECT = f"hrrr.{data_time.strftime('%Y%m%d')}/conus/hrrr.t00z.wrfsfcf{str(hours).zfill(2)}.grib2"

    FILE_PATH = S3_OBJECT.split("/")[-1]

    if not os.path.exists(FILE_PATH):
        directory = next(os.walk("./"))
        for file_name in directory[-1]:
            if file_name.endswith(".grib2") or file_name.endswith(".idx"):
                os.remove(file_name)

        s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=S3_OBJECT)['Body'].read()

        with open(FILE_PATH, "wb") as file:
            file.write(obj)

    dataset = xarray.open_dataset(
        FILE_PATH,
        engine="cfgrib",
        filter_by_keys={'stepType': step_type, 'typeOfLevel': 'surface'},
        decode_times=False
    )

    mask_lon = (dataset.longitude - 359.99 >= min_lon) & (dataset.longitude - 360 <= max_lon)
    mask_lat = (dataset.latitude >= min_lat) & (dataset.latitude <= max_lat)

    dataset = dataset.where(mask_lon & mask_lat, drop=True)
    lons = dataset["longitude"].values
    lats = dataset["latitude"].values

    return lons - 359.99, lats, dataset[short_name].values * 39.3700787
