# PXE Boot Base
This is the base image for `pxeboot-init`. This docker image will contains base software and `images`.

This image is separated to avoid rebuilding and keeping lot of big images files on `pxeboot-init` directly.

## Preparation
In order to have everything ready, please use `./prepare.sh` which will just create a Docker container and execute the 911builder.

As soon as the 911builder is done, you will have `911-vmlinuz` and `911-ramfs` which are the images used to boot over PXE.

Theses images will be embedded on this `pxeboot-base` image. After that, just do `docker build -t openvcloud/pxeboot-base` here and you're done.

> IMPORTANT: There is no build script for the ubuntu image used by `Install` script right now, see issue #35
