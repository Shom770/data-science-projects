import pygrib
import boto3
from botocore import UNSIGNED
from botocore.config import Config

s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
bucket_name = 'noaa-hrrr-bdp-pds'
s3_object = 'hrrr.20220107/conus/hrrr.t00z.wrfsfcf24.grib2'

obj = s3.get_object(Bucket=bucket_name, Key=s3_object)['Body'].read()
grbs = pygrib.fromstring(obj)

# this should print: <class 'pygrib._pygrib.gribmessage'>
print(type(grbs))
