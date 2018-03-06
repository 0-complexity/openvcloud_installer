FROM ubuntu:16.04
RUN apt-get update && \
    apt-get install -y curl sudo
ENV JS9BRANCH=master \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8
RUN touch /tmp/zutils.log
RUN curl https://raw.githubusercontent.com/Jumpscale/core9/master/install.sh?$RANDOM > /tmp/install_js9.sh;bash /tmp/install_js9.sh
RUN js9 'j.tools.prefab.local.virtualization.kubernetes.install_kube_client(location="/usr/local/bin/kubectl")'