FROM continuumio/miniconda3:4.5.12

RUN conda install bioformats2raw -c ome 

RUN conda install python==3.10

RUN python -m pip install -q boto3 botocore s3fs

RUN mkdir /opt/input

COPY ometif2zarr.py /opt/

# just for testing, can remove after bucket trigger working
# COPY input/cycif-tonsil-cycle1.ome.tif /opt/input
# ENV TO_CONVERT=/opt/input/cycif-tonsil-cycle1.ome.tif
# end test code

ENTRYPOINT ["python", "/opt/ometif2zarr.py"]