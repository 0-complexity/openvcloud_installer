# PXE Boot Service

This deployment starts the whole pxeboot system.

# Installation

> WARNING: This pod use **Host Network** and assume that `mgmt` interface exists and is configured. This interface is used to communicate with nodes.

```
kubectl apply -f pxeboot-deployment.yaml
```

## pxeboot-init

Pull the docker image which contains everything needed (images, etc.)

Create the dhcp, dns and tftp configuration files based on global yaml configuration.

## pxeboot

Run `dnsmasq` providing dns, dhcp and tftp

## pxeboot-httpd

Simple httpd to provide access to images and public ssh key, used by `Install` script
