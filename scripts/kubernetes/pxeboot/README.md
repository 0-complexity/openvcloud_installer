# PXE Boot Service

This deployment starts the whole PXE boot system.


# Installation

> WARNING: This pod uses **Host Network** and assume that `mgmt` interface exists and is configured. This interface is used to communicate with nodes.

```bash
kubectl apply -f pxeboot-deployment.yaml
```

## pxeboot-init

Pull the Docker image which contains everything needed (images, etc.)

Create the DHCP, DNS and TFTP configuration files based on global YAML configuration.


## pxeboot
```bash
Run `dnsmasq` providing dns, DHCP and TFTP
````

## pxeboot-httpd

Simple HTTPD to provide access to images and public ssh key, used by `Install` script.
