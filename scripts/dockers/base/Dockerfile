FROM python:2.7 as builder
ARG PRIVATEKEY
ARG VERSION
ARG MANIFESTURL

RUN pip install requests pyyaml
RUN mkdir -p /root/.ssh && echo "$PRIVATEKEY" > /root/.ssh/id_rsa && chmod 600 /root/.ssh/id_rsa
COPY code/github.com/0-complexity/openvcloud_installer/scripts/buildlib/packager.py /tmp/
COPY dep-manifest.yml /tmp/
RUN python /tmp/packager.py
RUN sed -i -e 's/$VERSION/"${VERSION}"/g' /opt/jumpscale7/cfg/system/system.yml

# build caddy
FROM golang:alpine as gobuilder
RUN apk -U add git ca-certificates
RUN go get github.com/mholt/caddy
RUN cd $GOPATH/src/github.com/mholt/caddy/caddy && CGO_ENABLED=0 GOOS=linux go build -a -ldflags '-extldflags "-static" -s -w' -o /go/bin/caddy
# build cloud-init
RUN go get github.com/zero-os/cloud-init-server
RUN cd $GOPATH/src/github.com/zero-os/cloud-init-server && CGO_ENABLED=0 GOOS=linux go build -a -ldflags '-extldflags "-static" -s -w' -o /go/bin/cloud-init-server
# build dnsmasq
FROM alpine:latest as dnsmasq
RUN apk -U add dnsmasq
# build nft
FROM alpine:latest as nft
RUN apk -U add nftables

# copy base image
FROM scratch
COPY --from=builder /opt/jumpscale7 /opt/jumpscale7
COPY --from=builder /var/lib/libvirt/images /var/lib/libvirt/images
COPY --from=builder /usr/local/bin/js /usr/local/bin/js
COPY --from=builder /usr/local/bin/jspython /usr/local/bin/jspython
COPY --from=builder /etc/nginx/sites-enabled /etc/nginx/sites-enabled
COPY --from=builder /opt/OpenvStorage /opt/OpenvStorage

# copy caddy
COPY --from=gobuilder /go/bin/caddy /var/lib/runc/templates/caddy/rootfs/bin/caddy
COPY --from=gobuilder /etc/ssl/ /var/lib/runc/templates/caddy/rootfs/etc/ssl/
COPY caddy.json /var/lib/runc/templates/caddy/config.json

# copy cloud-init
COPY --from=gobuilder /go/bin/cloud-init-server /var/lib/runc/templates/cloud-init/rootfs/bin/cloud-init-server
COPY cloud-init.json /var/lib/runc/templates/cloud-init/config.json

# copy dnsmasq
COPY --from=dnsmasq / /var/lib/runc/templates/dnsmasq/rootfs/
COPY dnsmasq.json /var/lib/runc/templates/dnsmasq/config.json

# copy nftables
COPY --from=nft / /var/lib/runc/templates/nft/rootfs/
COPY nft.json /var/lib/runc/templates/nft/config.json