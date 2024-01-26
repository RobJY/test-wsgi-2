import os
from subprocess import run
from sys import exit

input_file = os.getenv('TO_CONVERT')
output_file = input_file.split('.')[0] + '.zarr'

process = run(['bioformats2raw', input_file, output_file])
if process.returncode:
    print(f'Error: return code: {process.returncode}')
    exit(1)
