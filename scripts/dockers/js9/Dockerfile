FROM ubuntu:16.04
RUN apt-get update && \
    apt-get install -y curl sudo
ENV JS9BRANCH=development \
    LANG=C.UTF-8
RUN touch /tmp/zutils.log
RUN curl https://raw.githubusercontent.com/Jumpscale/core9/master/install.sh?$RANDOM > /tmp/install_js9.sh;bash /tmp/install_js9.sh
RUN mkdir /opt/code/github/jumpscale/jsconfig && ssh-keygen -t rsa -N '' -f /root/.ssh/id_rsa
RUN cd /opt/code/github/jumpscale/jsconfig && git init && js9_config init --silent
RUN pip3 install influxdb jsonschema
RUN js9 'j.tools.prefab.local.virtualization.kubernetes.install_kube_client(location="/usr/local/bin/kubectl")'