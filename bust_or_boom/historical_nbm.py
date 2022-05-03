import os
from datetime import timedelta

import boto3
from botocore import UNSIGNED
from botocore.config import Config
import xarray


def historical_nbm_snow(data_time, extent, go_back=24):
    min_lon, max_lon, min_lat, max_lat = extent
    data_time = data_time - timedelta(hours=go_back)
    BUCKET_NAME = 'noaa-nbm-grib2-pds'
    S3_OBJECT = f"blend.{data_time.strftime('%Y%m%d')}/00/grib2/blend.t00z.master.f{str(go_back).zfill(3)}.co.grib2"
    ALT_S3_OBJECT = f"blend.{data_time.strftime('%Y%m%d')}/00/core/blend.t00z.core.f{str(go_back).zfill(3)}.co.grib2"

    FILE_PATH = S3_OBJECT.split("/")[-1].replace("blend", data_time.strftime('%Y%m%d'))

    if not os.path.exists(FILE_PATH):
        directory = next(os.walk("./"))
        for file_name in directory[-1]:
            if file_name.endswith(".grib2") or file_name.endswith(".idx"):
                os.remove(file_name)

        s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
        try:
            obj = s3.get_object(Bucket=BUCKET_NAME, Key=S3_OBJECT)['Body'].read()
        except:
            obj = s3.get_object(Bucket=BUCKET_NAME, Key=ALT_S3_OBJECT)['Body'].read()

        with open(FILE_PATH, "wb") as file:
            file.write(obj)

    dataset = xarray.open_dataset(
        FILE_PATH,
        engine="cfgrib",
    )
    print(dataset.variables)

    mask_lon = (dataset.longitude - 359.99 >= min_lon) & (dataset.longitude - 360 <= max_lon)
    mask_lat = (dataset.latitude >= min_lat) & (dataset.latitude <= max_lat)

    dataset = dataset.where(mask_lon & mask_lat, drop=True)
    lons = dataset["longitude"].values
    lats = dataset["latitude"].values
    coords = {}

    for y, (lon_row, lat_row) in enumerate(zip(lons - 359.99, lats)):
        for x, (lon, lat) in enumerate(zip(lon_row, lat_row)):
            try:
                coords[(round(lon, 2), round(lat, 2))] = dataset["asnow"].values[y, x] * 39.3700787
            except KeyError:
                coords[(round(lon, 2), round(lat, 2))] = dataset["sdwe"].values[y, x] * 0.039370 * 10

    return dict(sorted(coords.items()))
