# Syncthing kubernetes for openvcloud

To works properly, this Service and StatefulSet needs images built via:
- [scripts/dockers/light_sidecar](../../scripts/dockers/light_sidecar)
- [scripts/kubernetes/syncthing/sidecar](../../scripts/dockers/light_sidecar)


## Prerequisites

- You need your containers all cluster admin (for now), using rbac8
- You need `/var/ovc` directories existing on each nodes


## Installation

- Run `kubectl create -f service.yaml`
- Run `kubectl create -f stateful.yaml`

Now `/var/ovc/billing` and `/var/ovc/influxdb` should be synchronized across your nodes.
