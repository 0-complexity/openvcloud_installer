# Setting up the kubernetes cluster

## Prerequisites

- A JumpScale 9 installation(See [docs](https://github.com/Jumpscale/bash) for installation)
- Three nodes deploying the cluster
- For each node the user needs to have credentials to establish a SSH connection
- Swap needs to be off on each node
- Each node needs to be able to access each other node in the cluster
- Make sure that following directories exists on each node with mode 777(ex: chmod 777 /var/ovc/mongodb):
  - `/var/ovc/mongodb`
  - `/var/ovc/influx`
  - `/var/ovc/billing`
  - `/var/ovc/pxeboot`

## Installing the cluster

The cluster is installed using [prefab](https://github.com/Jumpscale/prefab9).
A remote prefab instance is used to establish a SSH connection to the different nodes.
Root access is required to installing the cluster, the follwoing demonstrates how to authorize the access using prefab.

Start a SSH agent instance and load it with your prefered keys to be authorized in each node.
Open the JumpScale shell by typing `js9`.
For each node perform the follwoing:

```python
sshclient = j.clients.ssh.get(addr=<node_addr>, port=<node_ssh_port>, login=<user>, passwd=<password>)
sshclient.SSHAuthorizeKey(<key_name>)
```

We need a prefab instance for each node this is done by:

```python
executor = j.tools.executor.getSSHBased(<node_addr>)
prefab = j.tools.prefab.get(executor)
```

Installing the cluster is done using a local prefab instance. For PrefabKubernetes docs check [here](https://github.com/Jumpscale/prefab9/blob/master/docs/prefab.kubernetes.md). The install takes a list that contains the prefab instances of each nodes:

```python
nodes = [<list of prefab instances>]
config, _ = j.tools.prefab.local.virtualization.kubernetes.multihost_install(nodes, unsafe=True)
j.tools.prefab.local.core.file_write('/tmp/config', config)
```

This will take some time. Once it finishes you should have a running cluster.
The install method will return the config data necessary for sending requests to the cluster. It is now stored in a temporary file in `/tmp/config`, which should be changed depending on the use case explained in the next section.

## Installing Kube client

To connect to the cluster we are going to use `kubectl` command line tool. To install it, in a js9 shell do the following:

```python
j.tools.prefab.local.virtualization.kubernetes.install_kube_client()
```

Using `kubectl` it is possible to connect to multiple running clusters, this can be achieved by specifying the config file when executing the commands. By default it uses the config in `~/.kube/config`. If it is required to connect to only one cluster then the default config can be replaced by the config at `/tmp/config`.

Alternatively the user has two options to specify the config:

- Specifying the config file in the `kubectl` command, `kubectl <command> --kubeconfig=/tmp/config`
- Exporting `KUBECONFIG` environment variable, `export KUBECONFIG=/tmp/config`

## Deploying the application

Deploying each component of the application is done by using the following command:

```bash
kubectl apply -f <path>
```

This needs to be applied on `rbac.yaml` first before doing any other operations. It can be found under `scripts/kubernetes/`

Creating the config map:

`kubectl create secret generic system-config --from-file <config path>`

The config file is a yaml file which specifies information needed for the application, check the available [example](../scripts/kubernetes/config/system-config.yaml) which gives a clearer idea about the use of each field in the file.

Same needs to be done for the certificats. Four secrets are needed, they can use the same certificate files or different files depending on the configuration. The following command needs to be executed for each secret:

`kubectl create secret generic <name>  --from-file  <certs directory>`

`certs directory` is the directory containing the certificate files. This directory should contain three files with the following extensions: `crt`, `csr` and `key`. `name` has the following values:

- `defense-certs`
- `novnc-certs`
- `ovs-certs`
- `root-certs`

This needs to be done in a specific order and it is preferable to wait after each pod has been deployed.
To check the status of pods run `kubectl get pods` to list names of available pods and then `kubectl get pod <podname>`.
See docs for each component for how to run.

The required order is:

- `rbac.yaml`
- [syncthing](../scripts/kubernetes/syncthing)
- [mongocluster](../scripts/kubernetes/mongocluster)
- [influx](../scripts/kubernetes/influxdb)
- [osis](../scripts/kubernetes/osis)
- [agentcontroller](../scripts/kubernetes/agentcontroller)
- [stats-collector](../scripts/kubernetes/stats-collector)
- [grafana](../scripts/kubernetes/grafana)
- [portal](../scripts/kubernetes/portal)
