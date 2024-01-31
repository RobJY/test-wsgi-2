import boto3
from botocore.exceptions import ClientError
import os
from s3fs import S3FileSystem
from subprocess import run
from sys import exit

''' works
input_file = os.getenv('TO_CONVERT')
output_file_list = input_file.split('.')
output_file = output_file_list[0] + '.zarr'

process = run(['bioformats2raw', input_file, output_file])
if process.returncode:
    print(f'Error running file conversion: return code: {process.returncode}')
    exit(1)

bucket = 'rob-wsgi-tif2zarr'
object_name = os.path.basename(output_file)
s3_client = boto3.client('s3')
try:
    response = s3_client.upload_file(input_file, bucket, object_name)
except ClientError as e:
    print(e)
'''

s3_client = boto3.client('s3')

source_bucket = os.getenv('CONVERT_BUCKET')
source_filename = os.getenv("CONVERT_FILENAME")

output_file_list = source_filename.split('.')
output_filename = output_file_list[0] + '.zarr'

# need to upload source file from s3 to this ec2 and then run and write back to new s3!

host_filename = source_filename
s3_client.download_file(source_bucket, source_filename, host_filename)


process = run(['bioformats2raw', host_filename, output_filename])
if process.returncode:
    print(f'Error running file conversion: return code: {process.returncode}')
    exit(1)

bucket = 'rob-wsgi-tif2zarr'
object_name = os.path.basename(output_filename)
# both of the following fail because the zarr is seen as a dir instead of a file
#try:
#    response = s3_client.upload_file(output_filename, bucket, object_name)
#except ClientError as e:
#    print(e)
#
#with open(output_filename, 'rb') as data:
#    s3.upload_fileobj(data, bucket, object_name)
s3_upload = S3FileSystem()
s3_path = 's3://rob-wsgi-tif2zarr/' + object_name
s3_upload.put(output_filename, s3_path, recursive=True)
