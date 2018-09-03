from phusion/baseimage:latest
ARG VERSION
ARG MANIFESTURL
ARG GITTOKEN

RUN apt-get update && apt-get install -y curl
RUN curl https://bootstrap.pypa.io/get-pip.py | python3
RUN pip3 install PyGithub pyyaml
COPY code/github.com/0-complexity/openvcloud/ /opt/code/github/0-complexity/openvcloud/
RUN curl "${MANIFESTURL}/${VERSION}.yml" -o /root/manifest.yml
RUN python3 /opt/code/github/0-complexity/openvcloud/scripts/versions/releasenotes -v "$VERSION" \
    -m /root/manifest.yml -t "$GITTOKEN"