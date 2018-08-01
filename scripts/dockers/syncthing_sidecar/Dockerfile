FROM openvcloud/slightcar

RUN mkdir -p /opt/sidecar
COPY kubernetes.py /opt/sidecar
COPY sidecar.py /opt/sidecar
COPY syncthinglight.py /opt/sidecar

ENTRYPOINT /usr/bin/python3 /opt/sidecar/sidecar.py
