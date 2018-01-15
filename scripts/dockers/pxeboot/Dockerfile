FROM alpine:latest

RUN apk -U add dnsmasq
RUN mkdir -p /pxeboot/tftpboot /pxeboot/conf

COPY bin /usr/local/bin

ENTRYPOINT ["/usr/sbin/dnsmasq", "-C", "/pxeboot/conf/dnsmasq.conf", "--no-daemon"]
