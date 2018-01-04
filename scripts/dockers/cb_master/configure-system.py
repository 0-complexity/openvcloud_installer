from JumpScale import j
import yaml
import pprint
import os


def get_config():
    with open('/opt/cfg/system/system-config.yaml') as file_discriptor :
        data  = yaml.load(file_discriptor)
    return data



if __name__ == '__main__':
    config = get_config()
    gid = config['environment']['grid']['id'] if isinstance(config['environment']['grid']['id'], int) else int(config['environment']['grid']['id'])
    print("[+] set gid to: %s" % gid)
    j.application.config.set('grid.id', gid)
    j.system.fs.copyDirTree('/opt/jumpscale7/hrd/system/', '/opt/cfg/system/')
