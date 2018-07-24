FROM openvcloud/js9

COPY init-ssh.py /var/run/
COPY code/github.com/0-complexity/openvcloud_installer/ /opt/code/github/0-complexity/openvcloud_installer/

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y ipmitool

RUN mkdir -p /opt/cfg/system
