from s3fs import S3FileSystem
from subprocess import run
from sys import exit


process = run(['bioformats2raw', '/opt/cycif-tonsil-cycle1.ome.tif', '/opt/cycif-tonsil-cycle1.zarr'])
if process.returncode:
    print(f'Error: return code: {process.returncode}')
    exit(1)

# s3 = S3FileSystem()
# s3_path = 's3://rob-hits-s3fs-dev/tonsil-1.zarr'
# file_path = './new_test.zarr'
# s3.put(file_path, s3_path, recursive=True)
