import os
from datetime import timedelta

import boto3
from botocore import UNSIGNED
from botocore.config import Config
import xarray


def historical_hrrr_snow(data_time, extent):
    min_lon, max_lon, min_lat, max_lat = extent
    data_time = data_time - timedelta(hours=24)
    BUCKET_NAME = 'noaa-hrrr-bdp-pds'
    S3_OBJECT = f"hrrr.{data_time.strftime('%Y%m%d')}/conus/hrrr.t00z.wrfsfcf24.grib2"

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
        filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'surface'},
        decode_times=False
    )
    print(dataset.variables)

    mask_lon = (dataset.longitude - 359.99 >= min_lon) & (dataset.longitude - 360 <= max_lon)
    mask_lat = (dataset.latitude >= min_lat) & (dataset.latitude <= max_lat)

    dataset = dataset.where(mask_lon & mask_lat, drop=True)
    lons = dataset["longitude"].values
    lats = dataset["latitude"].values

    return lons - 359.99, lats, dataset["asnow"].values * 39.3700787
