FROM openvcloud/js7

RUN mkdir -p /var/run/scripts/nginx/ /opt/cfg/nginx/ssl /opt/cfg/upgrade
COPY configure-nginx.py /var/run/scripts/nginx/
COPY nginx.conf /opt/cfg/nginx/templates/nginx.conf
COPY upgrade.conf /opt/cfg/nginx/templates/upgrade.conf
ADD code/github.com/0-complexity/openvcloud_installer/ /opt/code/github/openvcloud_installer/
