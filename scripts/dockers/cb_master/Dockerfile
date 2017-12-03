# Before starting please add a private key which has access to the priv repos in id_rsa
FROM jumpscale7/ubuntu1604_core7

COPY system /opt/jumpscale7/hrd/system/
COPY apps /opt/jumpscale7/hrd/apps/
COPY atyourservice.hrd /opt/jumpscale7/hrd/system/
COPY whoami.hrd /opt/jumpscale7/hrd/system/

COPY start.sh /
COPY services-migrator.py /tmp/

# Copy over private key
# Set permissions
# Create known_hosts
ADD id_rsa /root/.ssh/id_rsa

RUN touch /root/.ssh/known_hosts && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts && \
    ssh-keyscan git.aydo.com >> /root/.ssh/known_hosts && \
    chmod 600 /root/.ssh/id_rsa

RUN chmod +x start.sh

RUN ["/bin/bash", "-c","./start.sh"]
