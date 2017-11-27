FROM phusion/baseimage

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y sudo

ENV AYSBRANCH 7.2.1
ENV JSBRANCH 7.2.1

RUN ["/bin/bash", "-c", "set -o pipefail && cd /tmp;rm -f install.sh;curl -k https://raw.githubusercontent.com/jumpscale7/jumpscale_core7/master/install/install.sh > install.sh;bash install.sh"]
