FROM abduman/cb_master

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y graphviz

RUN mkdir -p /var/run/scripts/portal/
COPY configure-portal.py /var/run/scripts/portal/