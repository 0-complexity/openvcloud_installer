FROM ubuntu:16.04

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python3 python3-yaml openssh-client

COPY images /source/pxeboot/images
COPY tftpboot /source/pxeboot/tftpboot
