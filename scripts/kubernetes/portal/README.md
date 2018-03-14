# Portal application

This directory defines the Deployment and Service for the OpenvCloud Portal application.

This will not result in a working OpenvCloud Portal, rather a portal that authenticates through ItsYou.online, using the the parameters specified at `openvcloud_installer/scripts/kubernetes/config`.


# Prerequisites

- Kubernetes cluster
- `kubectl` or alternative Kubernetes API client
- **dev**:  Building the Docker image in `openvcloud_installer/scripts/dockers/cb_master`
- applying the MongoDB cluster directory: `openvcloud_installer/scripts/kubernetes/mongocluster`
- applying the OSIS directory: `openvcloud_installer/scripts/kubernetes/osis`
- applying the agentcontroller directory: `openvcloud_installer/scripts/kubernetes/agentcontroller`
- bare minimum keys to fill in the configs:
    - `system`
    - `portal`
    - `itsyouonline`


# Installation

To use from within this directory run:
```bash
kubectl appl -f .
```

Or directly:
```bash
kubectl appl -f <full-path>/
```
