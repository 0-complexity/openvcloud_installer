FROM ubuntu:16.04 as builder
ARG PRIVATEKEY

WORKDIR /root/.ssh
RUN mkdir -p /root/.ssh && echo "$PRIVATEKEY" > /root/.ssh/id_rsa && chmod 600 /root/.ssh/id_rsa
ADD --chown=root:root known_hosts known_hosts
WORKDIR /packages
RUN apt-get update
RUN apt-get install dpkg-dev openssh-client -y
RUN scp -P 34022 -r repo@ftp.gig.tech:/images/repo/*.deb .
RUN dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz

FROM nginx:1.15.4
WORKDIR /usr/share/nginx/html/binary
COPY --from=builder /packages .