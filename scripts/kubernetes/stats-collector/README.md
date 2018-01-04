# Stats Collector
This directory creates the stats collector deployment. Stats collector is used to dump data from redis to influxdb.

# Prerequisites
 - kubernetes cluster
 - kubectl or alternative kuberntes api client
 - **dev**:  Building the jumpscale docker image in  ```openvcloud_installer/scripts/dockers/js9```
 - applying the mongocluster dir ```openvcloud_installer/scripts/kubernetes/mongocluster```
 - applying the influxdb dir ```openvcloud_installer/scripts/kubernetes/influxdb```
 - applying the osis dir ```openvcloud_installer/scripts/kubernetes/osis```
 - applying the agentcontroller dir ```openvcloud_installer/scripts/kubernetes/agentcontroller```

# Installation

Before applying the deployment you need to specifiy the network cidr for which the collector will search for the running redis to collect its data from. This is specified in the `--scan-dir` part of the args in the deployment yaml:

```
args: ['influxdumper.py',  '--influx-host',  influxdb, '--scan-cidr', <cidr>]
```

Make sure that the corect image is specified as well in the yaml file for the pod(Image containing a js9 installation)

To use , from within this directory run :
```
 kubectl apply -f .
```
or directly:
```
 kubectl apply -f <full-path>/