# Grafana kubernetes for openvcloud

# Install initial datasource configuration
- Add configmap datasource: `kubectl create configmap grafana-datasources --from-file=datasources/influxdb.yaml`

# Install dashboards
- Generate dashboard (if you changed them, generated are alreadu pushed): `cd dashboards && python3 build.py && cd ..`
- Add dashboards configmap: `kubectl create configmap grafana-dashboards --from-file=dashboards`

# Installation
- Run `kubectl create -f grafana-service.yaml`
- Run `kubectl create -f grafana-deployment.yaml`
