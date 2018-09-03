FROM openvcloud/cb_master:latest
ARG PRIVATEKEY
ARG VERSION
ARG MANIFESTURL

RUN apt-get update; apt-get install -y wget
RUN mkdir -p /root/.ssh && echo "$PRIVATEKEY" > /root/.ssh/id_rsa && chmod 600 /root/.ssh/id_rsa
RUN git config --global user.email "releaser@greenitglobe.com" && \
    git config --global user.name "gigreleaser"
RUN wget "${MANIFESTURL}/${VERSION}.yml" -O /root/manifest.yml
RUN jspython /opt/code/github/0-complexity/openvcloud/scripts/versions/makerelease -m /root/manifest.yml -u
