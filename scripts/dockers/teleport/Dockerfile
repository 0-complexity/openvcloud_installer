FROM openvcloud/js9

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y wget tar

RUN wget https://github.com/gravitational/teleport/releases/download/v2.4.0/teleport-v2.4.0-linux-amd64-bin.tar.gz

RUN tar -xzf teleport-v2.4.0-linux-amd64-bin.tar.gz && \
    cd teleport && \
    ./install  

RUN mkdir -p /var/run/scripts/teleport/

COPY start-teleport.py /var/run/scripts/teleport/start-teleport.py
COPY teleport.tmpl /etc/teleport.tmpl
RUN chmod +x /var/run/scripts/teleport/start-teleport.py

CMD [ "./var/run/scripts/teleport/start-teleport.py" ]
