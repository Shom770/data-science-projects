import os
from datetime import timedelta

import boto3
from botocore import UNSIGNED
from botocore.config import Config
import xarray


def historical_hrrr_cape(data_time, extent_lim, go_back=12):
    min_lon, max_lon, min_lat, max_lat = extent_lim
    prev_time = data_time - timedelta(hours=go_back)
    BUCKET_NAME = 'noaa-hrrr-bdp-pds'

    S3_OBJECT = (
        f"hrrr.{prev_time.strftime('%Y%m%d')}/conus/hrrr.t{str(prev_time.hour).zfill(2)}z.wrfsfcf"
        f"{go_back}.grib2"
    )
    INIT_OBJ = f"hrrr.{data_time.strftime('%Y%m%d')}/conus/hrrr.t{str(data_time.hour).zfill(2)}z.wrfsfcf00.grib2"
    FILE_PATH = S3_OBJECT.split("/")[-1].replace("hrrr", prev_time.strftime('%Y%m%d'))
    CUR_FP = INIT_OBJ.split("/")[-1].replace("hrrr", data_time.strftime('%Y%m%d'))

    if not os.path.exists(FILE_PATH) or not os.path.exists(CUR_FP):
        directory = next(os.walk("./"))
        for file_name in directory[-1]:
            if file_name.endswith(".grib2") or file_name.endswith(".idx"):
                os.remove(file_name)

        s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=S3_OBJECT)['Body'].read()
        cur_obj = s3.get_object(Bucket=BUCKET_NAME, Key=INIT_OBJ)['Body'].read()
        with open(FILE_PATH, "wb") as file:
            file.write(obj)

        with open(CUR_FP, "wb") as cur_file:
            cur_file.write(cur_obj)

    keys_to_filter = {
        'typeOfLevel': 'surface',
        'shortName': 'cape'
    }
    dataset = xarray.open_dataset(
        FILE_PATH,
        engine="cfgrib",
        filter_by_keys=keys_to_filter,
        decode_times=False
    )
    cur_dataset = xarray.open_dataset(
        CUR_FP,
        engine="cfgrib",
        filter_by_keys=keys_to_filter,
        decode_times=False
    )
    mask_lon_d = (dataset.longitude - 359.99 >= min_lon) & (dataset.longitude - 360 <= max_lon)
    mask_lat_d = (dataset.latitude >= min_lat) & (dataset.latitude <= max_lat)
    mask_lon_cd = (cur_dataset.longitude - 359.99 >= min_lon) & (cur_dataset.longitude - 360 <= max_lon)
    mask_lat_cd = (cur_dataset.latitude >= min_lat) & (cur_dataset.latitude <= max_lat)

    dataset = dataset.where(mask_lon_d & mask_lat_d, drop=True)
    cur_dataset = cur_dataset.where(mask_lon_cd & mask_lat_cd, drop=True)

    return dataset.longitude - 359.99, dataset.latitude, cur_dataset["cape"].values - dataset["cape"].values
