FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y curl && \
    curl jumpscale.maxux.net | bash

RUN cd /opt/code/github/jumpscale/lib9/ && \
    git fetch origin 9.3.0_kubernetes:9.3.0_kubernetes && \
    git checkout 9.3.0_kubernetes && \
    cd /opt/code/github/jumpscale/prefab9 && \
    git fetch origin 9.3.0_kubernetes:9.3.0_kubernetes && \
    git checkout 9.3.0_kubernetes && \
    pip3 install kubernetes
