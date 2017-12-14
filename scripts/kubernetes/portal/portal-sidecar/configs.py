from JumpScale import j
from yaml import loader, load

# this is not everything these are only the base components and can be added to



def get_config():
    with open('/opt/cfg/portal/portal-config-map.yaml') as f :
        data  = load(f)
    return data

def add_user(user, passwd):
    cmd1 = 'jsuser list'
    res = j.do.execute(cmd1, dieOnNonZeroExitCode=False)[1]
    for line in res.splitlines():
        if line.find(user) != -1:
            return

    cmd2='jsuser add -d %s:%s:admin:fakeemail.test.com:jumpscale' % (user, passwd)
    j.do.execute(cmd2, dieOnNonZeroExitCode=False)


if __name__ == '__main__':
    config = get_config()
    add_user(config['portal']['user'], config['portal']['passwd'])