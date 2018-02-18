FROM jumpscale/ays9nightly
RUN mkdir -p /opt/code/github/jumpscale/ && \
    git clone https://github.com/Jumpscale/core9 -b development /opt/code/github/jumpscale/core9 && \
    git clone https://github.com/Jumpscale/lib9 -b development /opt/code/github/jumpscale/lib9 && \
    git clone https://github.com/Jumpscale/prefab9 -b development /opt/code/github/jumpscale/prefab9 && \
    js9 'j.tools.prefab.local.virtualization.kubernetes.install_kube_client(location="/usr/local/bin/kubectl")'