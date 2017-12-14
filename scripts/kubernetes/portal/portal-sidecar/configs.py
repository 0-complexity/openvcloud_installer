from JumpScale import j
from yaml import loader, load

# this is not everything these are only the base components and can be added to



def get_config():
    with open('/opt/cfg/portal/portal-config-map.yaml') as f :
        data  = load(f)
    return data


if __name__ == '__main__':
    config = get_config()
    cmd  = 'jsuser add -d admin:%s:admin:fakeemail.test.com:jumpscale' % config['portal']['passwd']
    j.system.process(cmd)
