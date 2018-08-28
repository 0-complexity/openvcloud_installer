# Stats Collector

This directory defines the Deployment of the stats collector application. 

The Stats Collector is used to dump data from Redis to InfluxDB.

# Prerequisites
 - Kubernetes cluster
 - `kubectl` or alternative Kubernetes API client
 - **dev**:  Building the management docker image in `openvcloud_installer/scripts/dockers/management`
 - applying the Mongo DB cluster directory: `openvcloud_installer/scripts/kubernetes/mongocluster`
 - applying the InfluxDB directory: `openvcloud_installer/scripts/kubernetes/influxdb`
 - applying the OSIS directory: `openvcloud_installer/scripts/kubernetes/osis`
 - applying the agentcontroller directory: `openvcloud_installer/scripts/kubernetes/agentcontroller`


# Installation

Before applying the deployment you need to specify the network cidr for which the collector will search for the running redis to collect its data from. This is specified in the `--scan-dir` part of the args in the deployment yaml:

```bash
args: ['influxdumper.py',  '--influx-host',  influxdb, '--scan-cidr', <cidr>]
```

Make sure that the correct image is specified as well in the yaml file for the pod(Image containing a js7 installation)

To use from within this directory run:
```bash
kubectl apply -f .
```

Or directly:
```bash
kubectl apply -f <full-path>/
```