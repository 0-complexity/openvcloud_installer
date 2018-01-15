# PXE Boot Initializer
Here is where all the PXE Boot magic is created.

This initializing container basicly creates the config files used by dnsmasq for the dhcp/dns/tftp

When the container starts, `bin/pxeboot-init` is called, copying `/source` to `/opt/pxeboot` (mount it to the host), and then run `bin/generate-config.py`

The configuration generator takes source from `/etc/global/system-config.yaml` and write nodes, ssh keys, etc. to the target `/opt/pxeboot`

## Dependencies
This docker depends on `openvcloud/pxeboot-base` which contains basic images already

## Creation
```
docker build -t openvcloud/pxeboot-init .
```
