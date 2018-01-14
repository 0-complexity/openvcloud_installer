# PXE Boot Initializer
Here is where all the PXE Boot magic is created.

This initializing container basicly creates the config files used by dnsmasq for the dhcp/dns/tftp

When the container starts, `bin/pxeboot-init` is called, copying `/source` to `/opt/pxeboot` (mount it to the host), and then run `bin/generate-config.py`

The configuration generator takes source from `/etc/global/system-config.yaml` and write nodes, ssh keys, etc. to the target `/opt/pxeboot`

## Preparation
In order to have everything ready, please use `./prepare.sh` which will just create a docker and execute the 911builder.

As soon as the 911builder is done, you will have `911-vmlinuz` and `911-ramfs` which are the image used to boot over pxe.
Theses images will be embeded on this `pxeboot-init` image. After that, just do `docker build -t openvcloud/pxeboot-init` here and you're done.

> IMPORTANT: There is no build script for the ubuntu image used by `Install` script right now, see issue #35
