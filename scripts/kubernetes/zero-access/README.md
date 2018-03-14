# 0-access application

This directory defines the Deployment and Service for the 0-access.

0-access is used to authenticate and monitor SSH access.

For more details check [here](https://github.com/0-complexity/0-access).


## Prerequisites

- Kubernetes cluster
- `kubectl` or alternative Kubernetes API client
- Needs following directory: `/var/ovc/0-access/index`
- applying the syncthing directory: `openvcloud_installer/scripts/kubernetes/syncthing`
- applying the portal directory: `openvcloud_installer/scripts/kubernetes/portal`
- The following information needs to be specified in the config:
  - `environment`
  - `itsyouonline`
  
See sample [config](../config/system-config.yaml) for more details.


## Installation

To use from within this directory run:
```bash
 kubectl apply -f .
```

Or directly:
```bash
kubectl apply -f <full-path>/
```