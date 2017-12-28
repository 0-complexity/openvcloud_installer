# Influxdb application
This directory creates , the mongodb mongo-replicaset statefulset and service with dynamic pod recognition , so if the replica number is changed the the set will adjust accordingly.

# Prerequisites
 - kubernetes cluster
 - kubectl or alternative kuberntes api client
 - You need your containers all cluster admin (for now), using rbac8 this can be done using the ```rbac.yaml``` file
```
kubectl apply -f ./../rbac.yaml
```

# Installation
To use , from within this directory run :
```
 kubectl appl -f .
```
or directly:
```
 kubectl appl -f <full-path>/
```
