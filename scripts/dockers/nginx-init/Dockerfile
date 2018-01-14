FROM jumpscale7/ubuntu1604_core7

RUN mkdir -p /var/run/scripts/nginx/ /opt/cfg/nginx/ssl
COPY configure-nginx.py /var/run/scripts/nginx/
COPY nginx.conf /opt/cfg/nginx/templates/nginx.conf