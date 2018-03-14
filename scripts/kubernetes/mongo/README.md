# MongoDB application

This directory defines the StatefulSet and Service for the MongoDB application.

If the replica number is changed, the set will adjust accordingly.

# Prerequisites

 - Kubernetes cluster
 - `kubectl` or alternative Kubernetes API client
 - You need your containers all cluster admin (for now), using rbac8 this can be done using the `rbac.yaml` file:
    ```bash
    kubectl apply -f ./../rbac.yaml
    ```

# Installation

To use from within this directory run:
```bash
kubectl appl -f .
```

Or directly:
```bash
kubectl appl -f <full-path>/
```
