# OSIS application

This directory defines the Deployment and Service for the OSIS application.


# Prerequisites

- Kubernetes cluster
- `kubectl` or alternative Kubernetes API client
- applying the MongoDB cluster directory: `openvcloud_installer/scripts/kubernetes/mongocluster`
- **dev**: Building the Docker image in `openvcloud_installer/scripts/dockers/cb_master`


# Installation

To use from within this directory run:
```bash
kubectl appl -f .
```

Or directly:
```bash
 kubectl appl -f <full-path>/
```
