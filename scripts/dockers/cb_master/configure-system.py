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
    password = config['environment']['password']
    portal_client_services = j.atyourservice.findServices(domain='jumpscale', name='portal_client')
    agentcontroller_service = j.atyourservice.get(domain='jumpscale', name='agentcontroller_client', instance='main')
    osis_service = j.atyourservice.get(domain='jumpscale', name='osis', instance='main')
    osis_client_service = j.atyourservice.get(domain='jumpscale', name='osis_client', instance='main')
    portal_service = j.atyourservice.get(domain='jumpscale', name='portal', instance='main')

    for portal_client_service in portal_client_services:
        portal_client_service.hrd.set('instance.param.secret', password)
        portal_client_service.hrd.save()

    agentcontroller_service.hrd.set('instance.agentcontroller.client.passwd', password)
    agentcontroller_service.hrd.save()
    osis_service.hrd.set('instance.param.osis.superadmin.passwd', password)
    osis_service.hrd.save()
    osis_client_service.hrd.set('instance.param.osis.client.passwd', password)
    osis_client_service.hrd.save()
    portal_service.hrd.set('instance.param.portal.rootpasswd', password)
    portal_service.hrd.set('instance.param.cfg.secret', password)
    portal_service.hrd.save()

    j.system.fs.copyDirTree('/opt/jumpscale7/hrd/apps/', '/opt/cfg/apps/')
