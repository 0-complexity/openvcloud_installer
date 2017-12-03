#!/bin/bash
eval $(ssh-agent -s)
ssh-add

mkdir /opt/grafana
mkdir /opt/grafana/conf
mkdir /opt/grafana/public

jspython /tmp/services-migrator.py
