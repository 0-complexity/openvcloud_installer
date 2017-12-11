# Syncthing kubernetes for openvcloud
To works properly, this service and statefulset needs images built via:
- `scripts/dockers/light_sidecar`
- `scripts/kubernetes/syncthing/sidecar`

# Prerequisites
- You need your containers all cluster admin (for now), using rbac8
- You need `/var/ovc` directories existing on each nodes

# Installation
- Run `kubectl create -f service.yaml`
- Run `kubectl create -f stateful.yaml`

Now, `/var/ovc/billing` and `/var/ovc/influxdb` should be syncronized across your nodes
