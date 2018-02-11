from JumpScale import j
import yaml
import argparse


def get_config():
    with open('/opt/cfg/system/system-config.yaml') as file_discriptor :
        data  = yaml.load(file_discriptor)
    return data


def configure(roles, machineguid, controller_addr, ssh):
    """
    configures the js7 node.
    """
    if ssh:
        j.system.fs.remove('rm -f /etc/service/sshd/down')
    config = get_config()
    gid = int(config['environment']['grid']['id'])
    print("[+] set gid to: %s" % gid)
    roles = roles.split(',')
    j.application.config.set('grid.id', gid)
    j.application.config.set('grid.node.id', '')
    j.application.config.set('grid.node.roles', roles)
    if machineguid:
        j.application.config.set('grid.node.machineguid', machineguid)

    j.system.fs.copyDirTree('/opt/jumpscale7/hrd/system/', '/opt/cfg/system/')
    password = config['environment']['password']
    portal_client_services = j.atyourservice.findServices(domain='jumpscale', name='portal_client')
    agentcontroller_client_service = j.application.getAppInstanceHRD(name='agentcontroller_client', instance='main')
    osis_service = j.application.getAppInstanceHRD(name='osis', instance='main')
    osis_client_service = j.application.getAppInstanceHRD(name='osis_client', instance='main')
    portal_service = j.application.getAppInstanceHRD(name='portal', instance='main')

    for portal_client_service in portal_client_services:
        portal_client_service.hrd.set('instance.param.secret', password)
        portal_client_service.hrd.save()

    agentcontroller_client_service.set('instance.agentcontroller.client.passwd', password)
    if controller_addr:
        agentcontroller_client_service.set('instance.agentcontroller.client.addr', controller_addr)
    agentcontroller_client_service.save()
    osis_service.set('instance.param.osis.superadmin.passwd', password)
    osis_service.save()
    osis_client_service.set('instance.param.osis.client.passwd', password)
    osis_client_service.save()
    portal_service.set('instance.param.portal.rootpasswd', password)
    portal_service.set('instance.param.cfg.secret', password)
    portal_service.save()
    if 'master' in roles:
        scl = j.clients.osis.getNamespace('system')
        scl.health.deleteSearch({})

    j.system.fs.copyDirTree('/opt/jumpscale7/hrd/apps/', '/opt/cfg/apps/')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--roles', default='node')
    parser.add_argument('--machineguid', default=None)
    parser.add_argument('--controller-addr', dest="controller_addr", default=None)
    parser.add_argument('--ssh', default=False, action='store_true')
    args = parser.parse_args()
    configure(args.roles, args.machineguid, args.controller_addr, args.ssh)
