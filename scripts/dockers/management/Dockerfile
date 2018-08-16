FROM phusion/baseimage:latest

COPY init-ssh.py /var/run/
COPY code/github.com/0-complexity/openvcloud_installer/ /opt/code/github/0-complexity/openvcloud_installer/

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y ipmitool curl python3 vim git

RUN curl https://bootstrap.pypa.io/get-pip.py | python3
RUN pip3 install -r /opt/code/github/0-complexity/openvcloud_installer/requirements.txt

RUN mkdir -p /opt/cfg/system
