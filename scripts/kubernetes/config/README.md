# System wide configuration file
The contents under data will be available as a yaml config-map that can be mounted as volume.

# Prerequisites
 - kubernetes cluster
 - kubectl or alternative kuberntes api client

# Installation
To use , from within this directory run :
```
 kubectl appl -f .
```
or directly:
```
 kubectl appl -f <full-path>/system-config.yaml
```
