FROM ubuntu:16.04

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python3 python3-yaml && \
    mkdir -p /opt/pxeboot

COPY contents /source
COPY bin /usr/local/bin
