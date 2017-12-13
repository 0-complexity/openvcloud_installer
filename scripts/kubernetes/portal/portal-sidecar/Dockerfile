FROM abduman/cb_master

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y graphviz

COPY configs.py /opt/cfg/portal/