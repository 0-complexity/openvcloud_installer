#! /bin/python3
from js9 import j


def get_config():
    return j.data.serializer.yaml.load('/opt/cfg/system/system-config.yaml')

if __name__ == '__main__':
    prefab = j.tools.prefab.local
    config = get_config()
    prefab.core.run("sed -i 's/\/usr\/sbin\/sshd -D/\/usr\/sbin\/sshd -D -p 2205/g' /etc/service/sshd/run")
