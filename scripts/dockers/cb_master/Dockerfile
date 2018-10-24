FROM python:2.7 as builder
ARG PRIVATEKEY
ARG VERSION
ARG MANIFESTURL

RUN pip install requests oyaml py-spy
RUN mkdir -p /root/.ssh && echo "$PRIVATEKEY" > /root/.ssh/id_rsa && chmod 600 /root/.ssh/id_rsa
COPY code/github.com/0-complexity/openvcloud_installer/scripts/buildlib/packager.py /tmp/
COPY dep-manifest.yml /tmp/
RUN python /tmp/packager.py

FROM phusion/baseimage
COPY --from=builder /opt/jumpscale7 /opt/jumpscale7
COPY --from=builder /usr/local/bin/jspython /usr/local/bin/jspython
COPY --from=builder /usr/local/bin/js /usr/local/bin/js
COPY --from=builder /usr/local/bin/py-spy /usr/local/bin/py-spy
RUN rm -f /etc/service/sshd/down
RUN /etc/my_init.d/00_regen_ssh_host_keys.sh
ADD apps/ /opt/jumpscale7/cfg/
RUN mkdir -p /opt/grafana \
          /opt/grafana/conf \
          /opt/grafana/public \
          /var/run/scripts/system \
          /opt/cfg/system \
          /opt/jumpscale7/var/resourcetracking \
          /opt/cfg/version \
          /var/run/scripts/portal
COPY configure-system.py /var/run/scripts/system
COPY configure-portal.py /var/run/scripts/portal/
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y graphviz sudo libmhash2 nmap \
                       vim net-tools iproute2 openssh-server \
                       iputils-ping curl


