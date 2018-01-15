FROM openvcloud/js9

COPY init-ssh.py /var/run/

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y ipmitool

RUN mkdir -p /opt/cfg/system
