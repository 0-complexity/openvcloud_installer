FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y python3 && \
    mkdir /www

COPY bin /usr/local/bin

ENTRYPOINT ["/bin/bash", "/usr/local/bin/startup"]
