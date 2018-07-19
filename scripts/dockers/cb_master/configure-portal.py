from JumpScale import j
import yaml
import os
import requests

# this is not everything these are only the base components and can be added to


class Portal(object):
    """
    Class used to define the portal service
    """
    def __init__(self, path='/opt/cfg/system/system-config.yaml'):
        with open(path) as file_discriptor:
            data = yaml.load(file_discriptor)
        self.config = data
        self.__authheaders = None
        if not self.config['itsyouonline'].get('clientId'):
            raise RuntimeError('clientId is not set')
        if not self.config['itsyouonline'].get('clientSecret'):
            raise RuntimeError('clientSecret is not set')

        self.client_id = self.config['itsyouonline']['clientId']
        self.client_secret = self.config['itsyouonline']['clientSecret']
        self.fqdn = '%s.%s' % (self.config['environment']['subdomain'], self.config['environment']['basedomain'])
        # baseurl = "https://staging.itsyou.online/"
        self.baseurl = "https://itsyou.online/"
        self.scl = j.clients.osis.getNamespace('system')
        self.ccl = j.clients.osis.getNamespace('cloudbroker')
        self.lcl = j.clients.osis.getNamespace('libvirt')

    @property
    def authheaders(self):
        if self.__authheaders is None:
            accesstokenparams = {'grant_type': 'client_credentials',
                                 'client_id': self.client_id, 'client_secret': self.client_secret}
            accesstoken = requests.post(os.path.join(self.baseurl, 'v1', 'oauth',
                                                     'access_token'), params=accesstokenparams)
            token = accesstoken.json()['access_token']
            self.__authheaders = {'Authorization': 'token %s' % token}
        return self.__authheaders

    def configure_api_key(self, apikey):
        label = apikey['label']
        result = requests.get(os.path.join(self.baseurl, 'api', 'organizations', self.client_id,
                                           'apikeys', label), headers=self.authheaders)
        if result.status_code == 200:
            stored_apikey = result.json()
            if apikey['callbackURL'] != stored_apikey['callbackURL']:
                print('API key does not match callback url deleting it')
                requests.delete(os.path.join(self.baseurl, 'api', 'organizations', self.client_id,
                                             'apikeys', label), headers=self.authheaders)
                apikey = {}
            else:
                apikey = stored_apikey

        if 'secret' not in apikey:
            print('Creating API key')
            result = requests.post(os.path.join(self.baseurl, 'api', 'organizations',
                                                self.client_id, 'apikeys'), json=apikey, headers=self.authheaders)
            apikey = result.json()
        return apikey

    def configure_portal_client(self):
        portal_client_services = j.atyourservice.findServices(domain='jumpscale', name='portal_client')
        for portal_client_service in portal_client_services:
            portal_client_service.hrd.set('instance.param.addr', 'localhost')
            portal_client_service.hrd.save()

    def add_user(self):
        """
        Add portal user using jsuser.
        """
        user = self.config['environment'].get('user', 'admin')
        passwd =  self.config['environment']['password']
        cmd1 = 'jsuser list'
        res = j.do.execute(cmd1, dieOnNonZeroExitCode=False)[1]
        for line in res.splitlines():
            if line.find(user) != -1:
                return

        cmd2 = 'jsuser add -d %s:%s:admin:fakeemail.test.com:jumpscale' % (user, passwd)
        j.do.execute(cmd2, dieOnNonZeroExitCode=False)


    def configure_user_groups(self, portalhrd):
        ovc_environment = self.config['itsyouonline']['environment']
        gid = j.application.whoAmI.gid
        portal_links = {
            'vdc': {
                'name': 'End User',
                'url': 'https://{}'.format(self.fqdn),
                'scope': 'user',
                'theme': 'dark',
                'external': 'true'},
            'ovs': {
                'name': 'Storage',
                'url': 'https://ovs-{}/ovcinit/{}'.format(self.fqdn, self.config['environment']['subdomain']),
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
        for linkid, data in portal_links.items():
            if data['url']:
                portalhrd.set('instance.navigationlinks.%s' % linkid, data)
        portalhrd.set('instance.param.cfg.defaultspace', 'vdc')
        portalhrd.set('instance.param.cfg.force_oauth_instance', 'itsyouonline')
        portalhrd.save()


        # update cloudbroker service
        cloudbrokerhrd = j.application.getAppInstanceHRD(name='cloudbroker', domain='openvcloud', instance='main')
        cloudbrokerhrd.set('instance.cloudbroker.portalurl', 'https://{}'.format(self.fqdn))
        cloudbrokerhrd.set('instance.openvcloud.cloudbroker.defense_proxy', 'https://defense-{}'.format(self.fqdn))
        cloudbrokerhrd.set('instance.openvcloud.supportemail', self.config['mailclient']['sender'])
        cloudbrokerhrd.save()
        # update cbportal service
        cbportalhrd = j.application.getAppInstanceHRD(name='cbportal', domain='openvcloud', instance='main')
        cbportalhrd.set('instance.openvcloud.supportemail', self.config['mailclient']['sender'])
        cbportalhrd.save()

        # setup user/groups
        for groupname in ('user', 'ovs_admin', 'level1', 'level2', 'level3', '0-access'):
            if not self.scl.group.search({'id': groupname})[0]:
                group = self.scl.group.new()
                group.gid = gid
                group.id = groupname
                group.users = ['admin']
                self.scl.group.set(group)

        # set location
        if not self.ccl.location.search({'gid': j.application.whoAmI.gid})[0]:
            loc = self.ccl.location.new()
            loc.gid = j.application.whoAmI.gid
            loc.name = ovc_environment
            loc.flag = 'black'
            loc.locationCode = ovc_environment
            self.ccl.location.set(loc)
        # set grid
        if not self.scl.grid.exists(j.application.whoAmI.gid):
            grid = self.scl.grid.new()
            grid.id = j.application.whoAmI.gid
            grid.name = ovc_environment
        else:
            grid = self.scl.grid.get(j.application.whoAmI.gid)
        limits = {'limits': self.config.get('limits')}
        if not grid.settings:
            grid.settings = limits
        grid.settings.update(limits)

        self.scl.grid.set(grid)
        # register vnc url
        url = 'https://novnc-{}/vnc_auto.html?token='.format(self.fqdn)
        if self.lcl.vnc.count({'url': url, 'gid': gid}) == 0:
            vnc = self.lcl.vnc.new()
            vnc.gid = gid
            vnc.url = url
            self.lcl.vnc.set(vnc)
        # register sizes
        sizecbs = [('512 MiB Memory with 1 vcpu', 512, 1),
                 ('1 GiB Memory with 1 vcpu', 1024, 1),
                 ('2 GiB Memory with 2 vcpus', 2048, 2),
                 ('4 GiB Memory with 2 vcpus', 4096, 2),
                 ('8 GiB Memory with 4 vcpus', 8192, 4),
                 ('16 GiB Memory with 8 vcpus', 16384, 8)]
        disksizes = [10, 20, 50, 100, 250, 500, 1000, 2000]
        if self.ccl.size.count({}) == 0:
            for sizecb in sizecbs:
                size = self.ccl.size.new()
                size.name = sizecb[0]
                size.memory = sizecb[1]
                size.vcpus = sizecb[2]
                size.disks = disksizes
                size.gids = [gid]
                self.ccl.size.set(size)
        # register network ids
        newrange = set(range(int(100), int(1000) + 1))
        if not self.lcl.networkids.exists(gid):
            networkids = {
                'id': gid,
                'networkids': list(newrange)
            }
            self.lcl.networkids.set(networkids)

    def configure_IYO(self):
        if not self.config['itsyouonline'].get('environment'):
            raise RuntimeError('environment is not set')
        callbackURL = 'https://{}/restmachine/system/oauth/authorize'.format(self.fqdn)
        environment = self.config['itsyouonline']['environment']
        groups = ['admin', 'level1', 'level2', 'level3', 'ovs_admin', 'user', '0-access']

        # register api key
        apikeyname = 'openvcloud-{}'.format(environment)
        apikey = {'callbackURL': callbackURL,
                  'clientCredentialsGrantType': False,
                  'label': apikeyname
                  }
        apikey = self.configure_api_key(apikey)

        # install oauth_client
        admin_scopes = ['user:name', 'user:email', 'user:publickey:ssh']
        user_scopes = ['user:name', 'user:email']

        for group in groups:
            admin_scopes.append('user:memberof:{}.{}'.format(self.client_id, group))
            user_scopes.append('user:memberof:{}.{}'.format(self.client_id, group))

        data = {
            'instance.oauth.client.id': self.client_id,
            'instance.oauth.client.logout_url': '',
            'instance.oauth.client.redirect_url': callbackURL,
            'instance.oauth.client.secret': apikey['secret'],
            'instance.oauth.client.url': os.path.join(self.baseurl, 'v1/oauth/authorize'),
            'instance.oauth.client.url2': os.path.join(self.baseurl, 'v1/oauth/access_token'),
            'instance.oauth.client.user_info_url': os.path.join(self.baseurl, 'api/users/{username}/info')
        }

        admin_data = dict(data)
        user_data = dict(data)

        admin_data['instance.oauth.client.scope'] =  ','.join(admin_scopes),
        user_data['instance.oauth.client.scope'] = ','.join(user_scopes)

        oauthclienthrd = j.application.getAppInstanceHRD(domain='jumpscale', name='oauth_client', instance='itsyouonline')
        for key, val in admin_data.items():
            oauthclienthrd.set(key, val)
        oauthclienthrd.save()

        useroauthclienthrd = j.application.getAppInstanceHRD(domain='jumpscale', name='oauth_client', instance='itsyouonline_user')
        for key, val in user_data.items():
            useroauthclienthrd.set(key, val)
        useroauthclienthrd.save()

        # configure groups on itsyouonline
        for group in groups:
            suborgname = self.client_id + '.' + group
            suborg = {'globalid': suborgname}
            print('Check if group %s exists' % suborgname)
            result = requests.get(os.path.join(self.baseurl, 'api', 'organizations', suborgname),
                                  headers=self.authheaders)
            if result.status_code != 200:
                print('Creating group {}'.format(suborgname))
                result = requests.post(os.path.join(self.baseurl, 'api', 'organizations',
                                                    self.client_id), json=suborg, headers=self.authheaders)
                if result.status_code >= 400:
                    raise RuntimeError("Failed to create suborg {}. Error: {} {}".format(
                        suborgname, result.status_code, result.text))

        # configure portal to use this oauthprovider and restart
        portalhrd = j.application.getAppInstanceHRD(name='portal', instance='main')
        portalhrd.set('instance.param.cfg.force_oauth_instance', 'itsyouonline')
        portalhrd.set('instance.param.dcpm.url', self.fqdn)
        portalhrd.set('instance.param.ovs.url', 'ovs-%s' % (self.fqdn))
        portalhrd.set('instance.param.portal.url', self.fqdn)
        portalhrd.save()
        return portalhrd

    def patch_mail_client(self):
        mailclienthrd = j.application.getAppInstanceHRD(domain='jumpscale', name='mailclient', instance='main')
        for key, value in self.config['mailclient'].items():
            mailclienthrd.set('instance.smtp.%s' % key, value)
        mailclienthrd.save()


    def configure_manifest(self):
        with open('/opt/cfg/version/versions-manifest.yaml') as file_discriptor:
            data_str = file_discriptor.read()
            data_obj = yaml.load(data_str)
        version = self.scl.version.new()
        version_dict = self.scl.version.searchOne({'name': data_obj['version']})
        self.scl.version.updateSearch({'status': 'CURRENT'}, {'$set': {'status': 'PREVIOUS'}})
        version.load(version_dict)
        if not version_dict:
            version.creationTime = j.base.time.getTimeEpoch()
        else:
            version.updateTime = j.base.time.getTimeEpoch()
        version.name = data_obj['version']
        version.url = data_obj['url']
        version.manifest = data_str
        version.status = 'CURRENT'
        self.scl.version.set(version)

if __name__ == '__main__':
    portal = Portal()
    portal.add_user()
    portalhrd = portal.configure_IYO()
    portal.configure_user_groups(portalhrd)
    portal.patch_mail_client()
    portal.configure_portal_client()
    portal.configure_manifest()
    j.system.fs.copyDirTree('/opt/jumpscale7/hrd/apps/', '/opt/cfg/apps/')
