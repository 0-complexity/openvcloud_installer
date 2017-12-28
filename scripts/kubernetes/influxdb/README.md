# Influxdb application
This directory creates , the influxdb deployment and service using the default influx configuration.

# Prerequisites
 - kubernetes cluster
 - kubectl or alternative kuberntes api client
 - the dir ```/var/ovc/influx``` needs to exist on all nodes

# Installation
To use , from within this directory run :
```
 kubectl appl -f .
```
or directly:
```
 kubectl appl -f <full-path>/
```
