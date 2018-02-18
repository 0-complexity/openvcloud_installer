# Stats Collector

This directory creates 0-access deployment and service. 0-access is used to authenticate and monitor ssh access For more details check [here](https://github.com/0-complexity/0-access).

## Prerequisites

- kubernetes cluster
- kubectl or alternative kuberntes api client
- Needs following directory: `/var/ovc/0-access/index`
- applying the syncthing dir ```openvcloud_installer/scripts/kubernetes/syncthing```
- applying the portal dir ```openvcloud_installer/scripts/kubernetes/portal```
- The following information needs to be specified in the config:
  - **environment**
  - **itsyouonline**
  See sample [config](../config/system-config.yaml) for more details.

## Installation

To use , from within this directory run:

```bash
 kubectl apply -f .
```

or directly:

```bash
 kubectl apply -f <full-path>/
 ```