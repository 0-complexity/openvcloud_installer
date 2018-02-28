#!/bin/bash
set -e

mkdir /opt/grafana
mkdir /opt/grafana/conf
mkdir /opt/grafana/public

jspython /tmp/services-migrator.py
