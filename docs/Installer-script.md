# Installation using installer script

## Prerequisites

- A JumpScale 9 installation(See [docs](https://github.com/Jumpscale/bash) for installation)
- `jsonschema` python library
- Three nodes for deploying the cluster
- For each node the user needs to have credentials to establish a SSH connection
- Each node needs to be able to access each other node in the cluster
- three files for ssl verification need to be added to the  specified path in the yaml config on the machine all wit
  the same name and have these extensions:
  - .csr
  - .crt
  - .key

## Using the script

The script can be used for deploying the cluster across the three nodes, perform the necessary preparations on each node, deploy the necessary kubernetes componenets and to deploy cpu and storage nodes.

The script([here](../scripts/install/installer)) has the following commands:

- `cluster`
- `cpu`
- `storage`

### cluster

To deploy the cluster run the command:

```bash
installer cluster deploy --config system-config.yaml --configure-cluster
```

- `--config` takes path of the config file. The config file is needed for the installation as well as running the application.
- `--configure-cluster/--no-configure-cluster` specifies whether to install kubernetes cluster or not

The command `cluster deploy` will use the kubernetes prefab module to install the kubernetes cluster and begin deploying the various components of the kubernetes cluster.

The config file specifies all the necessary information for a successful installation as well as information relevant to the application itself using yaml format. It is very important that the user makes sure that the data in the config can be used for its required operations.
An example config file can be found [here](../scripts/kubernetes/config/system-config.yaml).

For example the `ssh` key in the config is used to specify the key needed for authorization on each node in the cluster. This same info is used to add the key to the authorized keys on the machine.

The command `cluster writeconfig` is used to create `configmap` from the specified config file. `configmap` is the specified configuration that can be mounted to the kubernetes pods when the application needs information from the config file to perform its operations. This is already handled using the above command but this command can be used if it is required to update the configmap with new config data. An example command:

```bash
installer cluster writeconfig --config system-config.yaml
```

### cpu

This is used to deploy cpu nodes:

```bash
installer cpu deploy --config system-config.yaml --node-name cpu-01
```

- `--config` takes path of the config file. The config file is needed for the installation as well as running the application.
- `--node-name` name of the cpu node needs to be specified in the config file

### storage

This is used to deploy storage nodes:

```bash
installer storage deploy --config system-config.yaml --node-name stor-01
```

- `--config` takes path of the config file. The config file is needed for the installation as well as running the application.
- `--node-name` name of the storage node needs to be specified in the config file
