FROM openvcloud/0-access:latest

RUN ln -s /opt/0-access/0-access.py /opt/0-access/zero_access.py
ADD 0-access-start.py /opt/0-access

ENTRYPOINT [ "/usr/bin/python3", "/opt/0-access/0-access-start.py" ]