FROM alpine:3.2

RUN apk -U add dnsmasq
RUN mkdir -p /pxeboot/tftpboot /pxeboot/conf

ENTRYPOINT ["/usr/sbin/dnsmasq", "-C", "/pxeboot/conf/dnsmasq.conf", "--no-daemon"]
