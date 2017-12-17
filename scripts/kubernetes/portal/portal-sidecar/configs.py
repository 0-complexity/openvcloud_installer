from JumpScale import j
from yaml import loader, load
import os
import requests

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


class ItsYouOnline(object):
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
    def prepare(self, config):
        self.__authheaders = None
        if not config['itsyouonline'].get('clientId'):
            raise RuntimeError('clientId is not set')
        if not config['itsyouonline'].get('clientSecret'):
            raise RuntimeError('clientSecret is not set')

        self.client_id = config['itsyouonline']['clientId']
        self.client_secret = config['itsyouonline']['clientSecret']
        # baseurl = "https://staging.itsyou.online/"
        self.baseurl = "https://itsyou.online/"

    @property
    def authheaders(self):
        if self.__authheaders is None:
            accesstokenparams = {'grant_type': 'client_credentials', 'client_id': self.client_id, 'client_secret': self.client_secret}
            accesstoken = requests.post(os.path.join(self.baseurl, 'v1', 'oauth', 'access_token'), params=accesstokenparams)
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

    def configure(self, config):
        if not config['itsyouonline'].get('callbackURL'):
            raise RuntimeError('callbackURL is not set')
        if not config['itsyouonline'].get('environment'):
            raise RuntimeError('environment is not set')
        callbackURL = config['itsyouonline']['callbackURL']
        environment = config['itsyouonline']['environment']
        groups = ['admin', 'level1', 'level2', 'level3', 'ovs_admin', 'user']

        # register api key
        apikeyname = 'openvcloud-{}'.format(environment)
        apikey = {'callbackURL': callbackURL,
                  'clientCredentialsGrantType': False,
                  'label': apikeyname
                  }
        apikey = self.configure_api_key(apikey)

        # install oauth_client
        scopes = ['user:name', 'user:email']
        for group in groups:
            scopes.append('user:memberof:{}.{}'.format(self.client_id, group))

        data = {'instance.oauth.client.id': self.client_id,
                'instance.oauth.client.logout_url': '',
                'instance.oauth.client.redirect_url': callbackURL,
                'instance.oauth.client.scope': ','.join(scopes),
                'instance.oauth.client.secret': apikey['secret'],
                'instance.oauth.client.url': os.path.join(self.baseurl, 'v1/oauth/authorize'),
                'instance.oauth.client.url2': os.path.join(self.baseurl, 'v1/oauth/access_token'),
                'instance.oauth.client.user_info_url': os.path.join(self.baseurl, 'api/users/{username}/info')
                }
        oauthclient = j.atyourservice.get(domain='jumpscale', name='oauth_client', instance='itsyouonline')
        oauthclient.hrd.set(data=data)
        oauthclient.save()


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
        portal = j.atyourservice.get(name='portal', instance='main')
        portal.hrd.set('instance.param.cfg.force_oauth_instance', 'itsyouonline')
        portal.save()

        j.do.execute('ln -s /opt/jumpscale7/')



if __name__ == '__main__':
    config = get_config()
    add_user(config['portal']['user'], config['portal']['passwd'])
    iyo = ItsYouOnline()
    iyo.prepare(config)
    iyo.configure(config)