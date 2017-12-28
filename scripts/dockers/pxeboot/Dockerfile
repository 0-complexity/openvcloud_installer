FROM alpine:3.2

RUN apk -U add dnsmasq
RUN mkdir -p /tftpboot /conf

ENTRYPOINT ["/usr/sbin/dnsmasq", "-C", "/conf/dnsmasq.conf", "--no-daemon"]
