# Exposures
- kubernetes: means only services from within the kubernetes will be able to address the service. In kubernetes terms this means we are talking about a ClusterIP.
- public: means publically accessible from the internet. In kubernetes terms this means we are talking aboue a Node Port, made available on the public routeable ip of each kubernetes node in the cluster.
- internal: means accessible from the management network of the G8. In kubernetes terms this means we are talking aboue a Node Port, made available on the management ip of each kubernetes node in the cluster.

# MongoDB
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

# Osis
- Depends on:
  - MongoDB
- docker image:
  - url: https://hub.docker.com/u/jumpscale/osis/
  - version: 7.2
- exposure: internal & kubernetes
- replication: at least one instance per node (Check with Jo if it makes sense running multiple Osis servers at the same time)

