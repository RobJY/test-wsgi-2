FROM continuumio/miniconda3:4.5.12

RUN conda install bioformats2raw -c ome 

RUN conda install python==3.10

RUN python -m pip install -q s3fs

RUN mkdir /opt/input

COPY ometif2zarr.py /opt/

ENTRYPOINT ["python", "/opt/ometif2zarr.py"]