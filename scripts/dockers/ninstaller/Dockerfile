FROM openvcloud/management
COPY requirements.txt /tmp/requirements.txt
RUN apt-get update && apt-get install -y rsyslog
RUN pip3 install -r /tmp/requirements.txt
CMD ["python3", "/opt/code/github/0-complexity/openvcloud_installer/scripts/install/ninstaller"]
