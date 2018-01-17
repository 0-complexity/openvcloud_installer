# Osis application
This creates the agentcontroller deployment and service.

# Prerequisites
 - kubernetes cluster
 - kubectl or alternative kuberntes api client
 - **dev**:  Building the docker image in  ```openvcloud_installer/scripts/dockers/cb_master```
 - applying the mongocluster dir ```openvcloud_installer/scripts/kubernetes/mongocluster```
 - applying the osis dir ```openvcloud_installer/scripts/kubernetes/osis```
 - applying the agentcontroller dir ```openvcloud_installer/scripts/kubernetes/agentcontroller```
 - bare minimum keys to fill in the configs :
    - **system**
    - **portal**
    - **itsyouonline**

# Installation
To use , from within this directory run :
```
 kubectl appl -f .
```
or directly:
```
 kubectl appl -f <full-path>/
```
