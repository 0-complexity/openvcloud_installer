# Exposures
- kubernetes: means only services from within the kubernetes will be able to address the service. In kubernetes terms this means we are talking about a ClusterIP.
- public: means publically accessible from the internet. In kubernetes terms this means we are talking aboue a Node Port, made available on the public routeable ip of each kubernetes node in the cluster.
- internal: means accessible from the management network of the G8. In kubernetes terms this means we are talking aboue a Node Port, made available on the management ip of each kubernetes node in the cluster.

# Deployment Requirements

## MongoDB
- See
  - https://www.mongodb.com/blog/post/running-mongodb-as-a-microservice-with-docker-and-kubernetes
  - https://docs.mongodb.com/manual/tutorial/deploy-replica-set/
- docker image:
  - url: https://hub.docker.com/r/library/mongo/
  - version: 3.4
- exposure: kubernetes (Cluster IP)
- replication: one instance on each node (at least three)
- volume:
  - type: local
  - mountpath: /data/db
---------------------
## Osis
- Depends on:
  - MongoDB
- docker image:
  - url: https://hub.docker.com/u/jumpscale/osis/
  - version: 7.2
- exposure: internal & kubernetes
- replication: at least one instance per node
---------------------
## OpenvCloud Portal
- Depends on:
  - Osis
- docker images:
  - nginx: Reverse proxy listening on a public ip
    - url: https://hub.docker.com/_/nginx/
    - version: 1.12
  - portal: Actual portal listening on localhost
    - url: https://hub.docker.com/u/openvcloud/portal/
    - version: 2.3
  - Redis
    - url: https://hub.docker.com/r/_/redis/
    - version: 3.2
- exposure: public & kubernetes
- replication: one instance per node
- volumes:
  - portal:
    - type: local
    - mountpath: /opt/jumpscale7/apps/portals/
  - capnp billing files:
    - type: hostpath
    - mountpath: /var/ovc/billing
---------------------
## InfluxDB
- docker image:
  - url: https://hub.docker.com/_/influxdb/
  - version: 1.4
- exposure: kubernetes
- replication: single instance
- volume:
  - type: hostPath (this file should be synced across all nodes )
  - mountpath: /var/ovc/influx
---------------------
## Syncthing
- synchting: Service that replicates capnp billing files to all pods within the deployment
- docker image:
  - url: https://hub.docker.com/r/syncthing/syncthing/
  - version: 0.14
- exposure: none
- replication: one instance per node
- volume:
  - type: hostPath  
    mountpath: /var/ovc/influx
  - type: hostPath  
    mountpath: /var/ovc/billing
---------------------
## Grafana
- Depends on:
  - InfluxDB
- docker image:
  - url: https://hub.docker.com/r/grafana/grafana/
  - version: 3.1
- exposure: kubernetes
- replication: single instance
---------------------
## StatsCollector
- Depends on:
  - InfluxDB
- docker image:
  - url: https://hub.docker.com/u/openvcloud/statscollector/
  - version: 2.3
- exposure: none
- replication: single instance
---------------------
## JSAgent, Agent Controller and Redis
Different containers same deployment so we can share the redis socket
- Depends on:
  - Osis
- docker images:
  - JSAgent
    - url: https://hub.docker.com/u/jumpscale/core/
    - version: 7.2
  - AgentController
    - url: https://hub.docker.com/u/jumpscale/core/
    - version: 7.2
  - Redis
    - url: https://hub.docker.com/r/_/redis/
    - version: 3.2
- exposure: internal & kubernetes
- replication: single instance
- volumes:
  - capnp billing files
    - type: hostpath
    - mountpath: /var/ovc/billing
---------------------
## DHCP Server, PXE Boot, TFTP Server
Priviliged (needs network access to mgmt network)
1, 2 or 3 containers?