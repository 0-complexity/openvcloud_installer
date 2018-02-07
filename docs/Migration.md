# Migrating an existing OVC instance

This document describes the manual procedure to migrate an existing ovc master and controller to a new HA kubernetes cluster installation. This will work on both kubernetes clusters and older installation which only use docker and AYS.The automation script discription is available at [Migration-script](Migration-script.md)

## Prerequisites
-------------------------
Prerquisites to be able to run this migration
 - An installed kubernetes cluster with ovc deployed on it.
 - A target to migrate from.
 - kubectl connection to the new cluster.
 - kubectl connection to the old cluster(if it uses kubernetes),
 - if the ovc version uses the old architechture ssh connection is required to the master node.

## Migrating the Data
-------------------------
There are three main data components for persistant storage in all instances of ovc installations, they are:
 - mongo
 - influxdb
 - billing files

### mongo

The main model store in the system is mongo although it is abstracted by osis but all data is persistantly stored in mongo.  
The new instance of mongo is going to run within a pod and so to execute commands in it a connection to the container needs to be established. This is done using :
```bash
    kubectl exec -it <one of the three pod name> /bin/bash
```
Steps to migrate the DB are as follows:  
1. After running this on the location where the mongo data base is reachable, this will produce dir structure that will allow for easy import and export,   
and can also be turned into a tar.zip file for ease of transfer(this can also be done directly on the new node if the old mongo instance is reachable from there)
```bash
    mongodump --out /<path to backup>/`date +"%m-%d-%y"`
```
  or
```bash
    mongodump --host <bind to old mongo> --port <port to old mongo> --username <username> --password <password>  --out /<path to backup>/`date +"%m-%d-%y"`
```

2. Move the file or directory to the location where the new mongo is reachable , using either a physical form such a portable storage device or through the network using scp, rsync, ftp ...etc.

3. To restore the database on the new location after restoring the file or directory to the format it was initialy produced using unzip or tar ,After ensuring mongod is running, this command is run pointing to the parent directory where the data is located:

```bash
    mongorestore --drop /<fullpath to location>/<date backup was created>/
```


### influxdb
This database is where the enviroment statistics are stored and has a simlar back up and restore method to the mongo db.
The new instance of influxdb is going to run within a pod and so to execute commands in it a connection to the container needs to be established. This is done using :
```bash
    kubectl exec -it <pod name> /bin/bash
```
Steps to migrate the DB are as follows:
1. After running this on the location where the influxdb data base is reachable, this will produce dir structure that will allow for easy import and export , and can also be turned into a tar.zip file for ease of transfer, `for influx version less than 1 no database flag is provided`,
(this can also be done directly on the new node if the old mongo instance is reachable from there)
```bash
    influxd backup -database statistics <path-to-backup>
```
or
```bash
    influxd backup -database statistics -host <remote-node-IP>:8088 <path-to-backup>
```

2. Move the file or directory to the location where the new mongo is reachable , using either a physical form such a portable storage device or through the network using scp, rsync, ftp ...etc.

3. To restore the database on the new location after restoring the file or directory to the format it was initialy produced, this command is run pointing to the parent directory where the data is located:

```bash
    influxd restore -datadir <path-to-meta-or-data-directory> <path-to-backup>
    sudo chown -R influxdb:influxdb /var/lib/influxdb
```
then the influx can be run or restarted


### billing files
Another vital data source are the billing files which are present on the master nodes.this is normal directory tree
and can be tar-ed zipp-ed and moved without any preprocessing.
The parent directory to move differs from old to new systems
 - openvcloud versions prior to and including 2.2.6:
    - location was on master node
    - path was ```/opt/jumpscale7/var/resourcetracking```
 - openvcloud versions after and including 2.3.0:
    - location was on any of the master node
    - path was ```/var/ovc/billing/```