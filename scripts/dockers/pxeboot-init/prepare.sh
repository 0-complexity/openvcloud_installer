#!/bin/bash
set -ex

wget https://github.com/PurePeople/911builder/archive/master.tar.gz
tar -xvf master.tar.gz

cd 911builder-master
docker build -t 911builder:latest .
docker run --privileged --rm -v $(pwd)/binaries:/binaries 911builder:latest
cd ..

cp -v 911builder-master/binaries/vmlinuz contents/tftpboot/911-vmlinuz
cp -v 911builder-master/binaries/ramfs contents/tftpboot/911-ramfs

echo ""
echo "You can now use the Dockerfile to build the pxeboot-init image"
echo "  docker build -t openvcloud/pxeboot-init ."
