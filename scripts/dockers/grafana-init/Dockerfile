FROM jumpscale7/ubuntu1604_core7

RUN mkdir -p /var/run/scripts/grafana/ /opt/cfg/grafana/templates
COPY configure-grafana.py /var/run/scripts/grafana/
COPY grafana.ini /opt/cfg/grafana/templates/grafana.ini