#!/bin/bash
set -ex

autoclean="yes"

wget https://github.com/PurePeople/911builder/archive/master.tar.gz
tar -xvf master.tar.gz

cd 911builder-master
docker build -t 911builder:latest .
docker run --privileged --rm -v $(pwd)/:/911builder -v $(pwd)/binaries:/binaries 911builder:latest
cd ..

rm -rf tftpboot/*

cp -v 911builder-master/binaries/vmlinuz tftpboot/911-vmlinuz
cp -v 911builder-master/binaries/ramfs tftpboot/911-ramfs

if [ "${autoclean}" == "yes" ]; then
    rm -f master.tar.gz
    rm -rf 911builder-master
fi

echo ""
echo "You can now use the Dockerfile to build the pxeboot-init image"
echo "  docker build -t openvcloud/pxeboot-base ."
