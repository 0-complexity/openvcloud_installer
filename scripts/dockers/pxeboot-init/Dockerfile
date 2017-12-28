FROM ubuntu:16.04

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python3 python3-yaml

COPY contents /opt/pxeboot
COPY bin /usr/local/bin
