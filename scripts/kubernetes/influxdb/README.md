# InfluxDB application

This directory defines the Deployment and Service for InfluxDB using the default InfluxDB configuration.


# Prerequisites

- Kubernetes cluster
- `kubectl` or alternative Kubernetes API client
- the directory `/var/ovc/influx` needs to exist on all nodes


# Installation

To use from within this directory run:
```bash
kubectl appl -f .
```

Or directly:
```bash
kubectl appl -f <full-path>/
```
