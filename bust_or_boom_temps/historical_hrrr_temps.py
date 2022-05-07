from datetime import timedelta
from io import StringIO

import boto3
from botocore import UNSIGNED
from botocore.config import Config
import xarray


def historical_hrrr_temps(data_time, layer="1000mb", go_back=12):
    prev_time = data_time - timedelta(hours=go_back)
    BUCKET_NAME = 'noaa-hrrr-bdp-pds'

    zulu = data_time.hour
    S3_OBJECT = (
        f"hrrr.{prev_time.strftime('%Y%m%d')}/conus/hrrr.t{str(zulu).zfill(2)}z.wrfsfcf"
        f"{go_back}.grib2"
    )
    INIT_S3 = f"hrrr.{data_time.strftime('%Y%m%d')}/conus/hrrr.t{str(zulu).zfill(2)}z.wrfsfcf00.grib2"

    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    obj = StringIO(s3.get_object(Bucket=BUCKET_NAME, Key=S3_OBJECT)['Body'].read())
    cur_obj = StringIO(s3.get_object(Bucket=BUCKET_NAME, Key=INIT_S3)['Body'].read())

    dataset = xarray.open_dataset(
        obj,
        engine="cfgrib",
        filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'surface'},
        decode_times=False
    )
    cur_dataset = xarray.open_dataset(
        cur_obj,
        engine="cfgrib",
        filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'surface'},
        decode_times=False
    )

    lons = dataset["longitude"].values
    lats = dataset["latitude"].values

    print(dataset.variables)