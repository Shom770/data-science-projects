import os

import boto3
from botocore import UNSIGNED
from botocore.config import Config
import xarray

# Remove any .grib2 files that already exist
directory = next(os.walk("./"))
for file_name in directory[-1]:
    if file_name.endswith(".grib2") or file_name.endswith(".idx"):
        os.remove(file_name)

BUCKET_NAME = 'noaa-hrrr-bdp-pds'
S3_OBJECT = 'hrrr.20220107/conus/hrrr.t00z.wrfsfcf01.grib2'

FILE_PATH = S3_OBJECT.split("/")[-1]

if not os.path.exists(FILE_PATH):
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=S3_OBJECT)['Body'].read()

    with open(FILE_PATH, "wb") as file:
        file.write(obj)


dataset = xarray.open_dataset(
    FILE_PATH,
    engine="cfgrib",
    filter_by_keys={'stepType': 'accum', 'typeOfLevel': 'surface'}
)

