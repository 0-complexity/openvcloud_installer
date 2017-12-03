from JumpScale import j
from ConfigParser import SafeConfigParser
import cStringIO as StringIO
from urlparse import urlparse

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):
    """
    process for install
    -------------------
    step1: prepare actions
    step2: check_requirements action
    step3: download files & copy on right location (hrd info is used)
    step4: configure action
    step5: check_uptime_local to see if process stops  (uses timeout $process.stop.timeout)
    step5b: if check uptime was true will do stop action and retry the check_uptime_local check
    step5c: if check uptime was true even after stop will do halt action and retry the check_uptime_local check
    step6: use the info in the hrd to start the application
    step7: do check_uptime_local to see if process starts
    step7b: do monitor_local to see if package healthy installed & running
    step7c: do monitor_remote to see if package healthy installed & running, but this time test is done from central location
    """

    def configure(self, serviceObj):
        ovcEnvironment = serviceObj.hrd.get('instance.param.ovc.environment')

        # set navigation
        portal = j.atyourservice.get(name='portal', instance='main')
        portal.stop()
        portalurl = serviceObj.hrd.get('instance.param.portal.url')
        portallinks = {
            'ays': {
                'name': 'At Your Service',
                'url': '/AYS',
                'scope': 'admin',
                'theme': 'light',
            },
            'vdc': {
                'name': 'End User',
                'url': portalurl,
                'scope': 'user',
                'theme': 'dark',
                'external': 'true'},
            'ovs': {
                'name': 'Storage',
                'url': serviceObj.hrd.get('instance.param.ovs.url'),
                'scope': 'ovs_admin',
                'theme': 'light',
                'external': 'true'},
            'grafana': {
                'name': 'Statistics',
                'url': '/grafana',
                'scope': 'admin',
                'theme': 'light',
                'external': 'true'},
            'grid': {
                'name': 'Grid',
                'url': '/grid',
                'scope': 'admin',
                'theme': 'light'},
            'system': {
                'name': 'System',
                'url': '/system',
                'scope': 'admin',
                'theme': 'light'},
            'cbgrid': {
                'name': 'Cloud Broker',
                'url': '/cbgrid',
                'scope': 'admin',
                'theme': 'light'},
        }
        for linkid, data in portallinks.iteritems():
            if data['url']:
                portal.hrd.set('instance.navigationlinks.%s' % linkid, data)
        portal.hrd.set('instance.param.cfg.defaultspace', 'vdc')
        portal.hrd.set('instance.param.cfg.force_oauth_instance', 'itsyouonline')
        portal.start()

        ccl = j.clients.osis.getNamespace('cloudbroker')
        scl = j.clients.osis.getNamespace('system')

        # setup user/groups
        for groupname in ('user', 'ovs_admin'):
            if not scl.group.search({'id': groupname})[0]:
                group = scl.group.new()
                group.gid = j.application.whoAmI.gid
                group.id = groupname
                group.users = ['admin']
                scl.group.set(group)

        # set location
        if not ccl.location.search({'gid': j.application.whoAmI.gid})[0]:
            loc = ccl.location.new()
            loc.gid = j.application.whoAmI.gid
            loc.name = ovcEnvironment
            loc.flag = 'black'
            loc.locationCode = ovcEnvironment
            ccl.location.set(loc)
        # set grid
        if not scl.grid.exists(j.application.whoAmI.gid):
            grid = scl.grid.new()
            grid.id = j.application.whoAmI.gid
            grid.name = ovcEnvironment
            scl.grid.set(grid)

        j.clients.portal.getByInstance('main')

        # register networks
        start = 201
        end = 250
        j.apps.libcloud.libvirt.registerNetworkIdRange(j.application.whoAmI.gid, start, end)
        # sync images
        j.apps.cloudbroker.iaas.syncAvailableImagesToCloudbroker()
        j.apps.cloudbroker.iaas.syncAvailableSizesToCloudbroker()
        # register public ips
        import netaddr
        netmask = serviceObj.hrd.get('instance.param.publicip.netmask')
        start = serviceObj.hrd.get('instance.param.publicip.start')
        end = serviceObj.hrd.get('instance.param.publicip.end')
        gateway = serviceObj.hrd.get('instance.param.publicip.gateway')
        netip = netaddr.IPNetwork('%s/%s' % (gateway, netmask))
        if ccl.externalnetwork.count({'network': str(netip.network), 'subnetmask': str(netip.netmask)}) == 0:
            pool = ccl.externalnetwork.new()
            pool.gid = j.application.whoAmI.gid
            pool.subnetmask = netmask
            pool.gateway = gateway
            ips = [str(ip) for ip in netaddr.IPRange(start, end)]
            pool.ips = ips
            pool.name = 'Default Network'
            pool.network = str(netip.network)
            ccl.externalnetwork.set(pool)

        oauthServerHRD = j.atyourservice.get(name='oauthserver').hrd
        oauthClientHRD = j.atyourservice.get(name='oauth_client', instance='oauth').hrd
        portalSecret = oauthServerHRD.get('instance.oauth.clients.portal.secret')
        oauthClientHRD.set('instance.oauth.client.secret', portalSecret)

        # configure grafana for oauth
        parsed_url = urlparse(portalurl)
        grafana = j.atyourservice.get(name='grafana')
        grafana.stop()
        cfgfile = '/opt/grafana/conf/defaults.ini'
        cfgcontent = j.system.fs.fileGetContents(cfgfile)
        fp = StringIO.StringIO('[global]\n' + cfgcontent)
        parser = SafeConfigParser()
        parser.readfp(fp)
        parser.set('server', 'root_url', '%s/grafana' % portalurl)
        parser.set('server', 'domain', parsed_url.hostname)
        parser.set('users', 'auto_assign_org_role', 'Editor')
        parser.set('auth.anonymous', 'enabled', 'true')
        parser.set('auth.anonymous', 'org_role', 'Admin')
        fpout = StringIO.StringIO()
        parser.write(fpout)
        content = fpout.getvalue().replace('[global]', '')
        j.system.fs.writeFile(cfgfile, content)
        grafana.start()
        j.atyourservice.get(name='nginx').restart()
