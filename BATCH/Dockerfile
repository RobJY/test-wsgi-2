FROM continuumio/miniconda3:4.5.12

RUN conda install bioformats2raw -c ome 

RUN conda install python==3.10

RUN python -m pip install -q s3fs

COPY test_s3fs_docker.py cycif-tonsil-cycle1.ome.tif /opt

ENTRYPOINT ["python", "/opt/test_s3fs_docker.py"]
