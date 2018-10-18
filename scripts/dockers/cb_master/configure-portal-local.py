from JumpScale import j
import yaml
import os
import requests

# this is not everything these are only the base components and can be added to


class Portal(object):
    """
    Class used to define the portal service
    """

    def __init__(self, config):
        self.config = config
        self.__authheaders = None
        self.baseurl = "https://itsyou.online/"
        self.scl = j.clients.osis.getNamespace("system")
        self.ccl = j.clients.osis.getNamespace("cloudbroker")
        self.lcl = j.clients.osis.getNamespace("libvirt")

    @property
    def authheaders(self):
        if self.__authheaders is None:
            accesstokenparams = {
                "grant_type": "client_credentials",
                "client_id": self.config.client_id,
                "client_secret": self.config.secret,
            }
            accesstoken = requests.post(
                os.path.join(self.baseurl, "v1", "oauth", "access_token"),
                params=accesstokenparams,
            )
            token = accesstoken.json()["access_token"]
            self.__authheaders = {"Authorization": "token %s" % token}
        return self.__authheaders

    def configure_api_key(self, apikey):
        label = apikey["label"]
        result = requests.get(
            os.path.join(
                self.baseurl, "api", "organizations", self.config.client_id, "apikeys", label
            ),
            headers=self.authheaders,
        )
        if result.status_code == 200:
            stored_apikey = result.json()
            if apikey["callbackURL"] != stored_apikey["callbackURL"]:
                print("API key does not match callback url deleting it")
                requests.delete(
                    os.path.join(
                        self.baseurl,
                        "api",
                        "organizations",
                        self.config.client_id,
                        "apikeys",
                        label,
                    ),
                    headers=self.authheaders,
                )
                apikey = {}
            else:
                apikey = stored_apikey

        if "secret" not in apikey:
            print("Creating API key")
            result = requests.post(
                os.path.join(
                    self.baseurl, "api", "organizations", self.config.client_id, "apikeys"
                ),
                json=apikey,
                headers=self.authheaders,
            )
            apikey = result.json()
        return apikey

    def configure_portal_client(self):
        portal_instances = j.core.config.list("portal_client")
        for portal_instance in portal_instances:
            portal_client = j.core.config.get("portal_client", portal_instance)
            portal_client["addr"] = "localhost"
            j.core.config.set("portal_client", portal_instance, portal_client)

    def add_user(self):
        """
        Add portal user using jsuser.
        """
        user = "admin"
        passwd = self.config.password
        cmd1 = "jsuser list"
        res = j.do.execute(cmd1, dieOnNonZeroExitCode=False)[1]
        for line in res.splitlines():
            if line.find(user) != -1:
                return

        cmd2 = "jsuser add -d %s:%s:admin:fakeemail.test.com:jumpscale" % (user, passwd)
        j.do.execute(cmd2, dieOnNonZeroExitCode=False)

  
    def configure_user_groups(self, portal):
        ovc_environment = self.config.env_subdomain
        gid = j.application.whoAmI.gid
        portal_links = [
            {
                "name": "Cloud Broker",
                "url": "/cbgrid",
                "scope": "admin",
                "theme": "light",
            },
            {
                "name": "Statistics",
                "url": "/grafana/d/1/overall-system-performance",
                "scope": "admin",
                "theme": "light",
                "external": "true",
            },
            {"name": "Grid", "url": "/grid", "scope": "admin", "theme": "light"},
            {
                "name": "Storage",
                "url":self.config.ovs_url,
                "scope": "ovs_admin",
                "theme": "light",
                "external": "true",
            },
            {"name": "System", "url": "/system", "scope": "admin", "theme": "light"},
            {
                "name": "End User",
                "url": "http://{}".format(self.config.fqdn),
                "scope": "user",
                "theme": "dark",
                "external": "true",
            },
        ]

        portal["navigationlinks"] = portal_links
        portal["url"] = "http://{}".format(self.config.fqdn)
        portal["defaultspace"] = "vdc"
        portal["force_oauth_instance"] = "itsyouonline"
        j.core.config.set("portal", "main", portal)

        # update openvcloud config
        openvcloud_config = j.core.config.get("openvcloud", "main")
        openvcloud_config["portalurl"] = "https://{}".format(self.config.fqdn)
        openvcloud_config["defense_proxy"] = "http://defense-{}".format(self.config.fqdn)
        openvcloud_config["supportemail"] = "test@ovclocal.com"
        j.core.config.set("openvcloud", "main", openvcloud_config)

        # setup user/groups
        for groupname in (
            "user",
            "ovs_admin",
            "level1",
            "level2",
            "level3",
            "0-access",
        ):
            if not self.scl.group.search({"id": groupname})[0]:
                group = self.scl.group.new()
                group.gid = gid
                group.id = groupname
                group.users = ["admin"]
                self.scl.group.set(group)

        # set location
        if not self.ccl.location.search({"gid": j.application.whoAmI.gid})[0]:
            loc = self.ccl.location.new()
            loc.gid = j.application.whoAmI.gid
            loc.name = ovc_environment
            loc.flag = "black"
            loc.locationCode = ovc_environment
            self.ccl.location.set(loc)
        # set grid
        if not self.scl.grid.exists(j.application.whoAmI.gid):
            grid = self.scl.grid.new()
            grid.id = j.application.whoAmI.gid
            grid.name = ovc_environment
        else:
            grid = self.scl.grid.get(j.application.whoAmI.gid)

        self.scl.grid.set(grid)
        # register vnc url
        url = "http://novnc-{}/vnc_auto.html?token=".format(self.config.fqdn)
        if self.lcl.vnc.count({"url": url, "gid": gid}) == 0:
            vnc = self.lcl.vnc.new()
            vnc.gid = gid
            vnc.url = url
            self.lcl.vnc.set(vnc)
        # register sizes
        sizecbs = [
            ("512 MiB Memory with 1 vcpu", 512, 1),
            ("1 GiB Memory with 1 vcpu", 1024, 1),
            ("2 GiB Memory with 2 vcpus", 2048, 2),
            ("4 GiB Memory with 2 vcpus", 4096, 2),
            ("8 GiB Memory with 4 vcpus", 8192, 4),
            ("16 GiB Memory with 8 vcpus", 16384, 8),
        ]
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
            networkids = {"id": gid, "networkids": list(newrange)}
            self.lcl.networkids.set(networkids)
        # configure Disk-Types
        disktypes = [
            ("B", "Boot Disk", "vmstor", 20, True),
            ("M", "Meta Data Disk", "vmstor", 20, True),
            ("D", "Data Disk", "data", 20, True),
            ("C", "CD-ROM Disk", None, None, False),
            ("P", "Physical Disk", None, None, False),
        ]
        for disktype in disktypes:
            dtype = self.ccl.disktype.searchOne({"id": disktype[0]})
            if not dtype:
                dtype = self.ccl.disktype.new()
                dtype.id = disktype[0]
                dtype.description = disktype[1]
                dtype.vpool = disktype[2]
                dtype.cacheratio = disktype[3]
                dtype.snapshotable = disktype[4]
                self.ccl.disktype.set(dtype)

    def configure_IYO(self):
        environment = self.config.env_subdomain
        callbackURL = "http://{}/restmachine/system/oauth/authorize".format(self.config.fqdn)
        groups = [
            "admin",
            "level1",
            "level2",
            "level3",
            "ovs_admin",
            "user",
            "0-access",
        ]

        # register api key
        apikeyname = "openvcloud-{}".format(environment)
        apikey = {
            "callbackURL": callbackURL,
            "clientCredentialsGrantType": False,
            "label": apikeyname,
        }
        apikey = self.configure_api_key(apikey)

        # install oauth_client
        admin_scopes = ["user:name", "user:email", "user:publickey:ssh"]
        user_scopes = ["user:name", "user:email"]

        for group in groups:
            admin_scopes.append("user:memberof:{}.{}".format(self.config.client_id, group))
            user_scopes.append("user:memberof:{}.{}".format(self.config.client_id, group))

        data = {
            "id": self.config.client_id,
            "logout_url": "",
            "redirect_url": callbackURL,
            "secret": apikey["secret"],
            "url": os.path.join(self.baseurl, "v1/oauth/authorize"),
            "url2": os.path.join(self.baseurl, "v1/oauth/access_token"),
            "user_info_url": os.path.join(self.baseurl, "api/users/{username}/info"),
        }

        admin_data = dict(data)
        user_data = dict(data)

        admin_data["scope"] = ",".join(admin_scopes)
        user_data["scope"] = ",".join(user_scopes)

        oauthclient = j.core.config.get("oauth_client", "itsyouonline")

        for key, val in admin_data.items():
            oauthclient[key] = val
        j.core.config.set("oauth_client", "itsyouonline", oauthclient)

        useroauthclient = j.core.config.get("oauth_client", "itsyouonline_user")

        for key, val in user_data.items():
            useroauthclient[key] = val
        j.core.config.set("oauth_client", "itsyouonline_user", useroauthclient)

        # configure groups on itsyouonline
        for group in groups:
            suborgname = self.config.client_id + "." + group
            suborg = {"globalid": suborgname}
            print("Check if group %s exists" % suborgname)
            result = requests.get(
                os.path.join(self.baseurl, "api", "organizations", suborgname),
                headers=self.authheaders,
            )
            if result.status_code != 200:
                print("Creating group {}".format(suborgname))
                result = requests.post(
                    os.path.join(self.baseurl, "api", "organizations", self.config.client_id),
                    json=suborg,
                    headers=self.authheaders,
                )
                if result.status_code >= 400:
                    raise RuntimeError(
                        "Failed to create suborg {}. Error: {} {}".format(
                            suborgname, result.status_code, result.text
                        )
                    )

        # configure portal to use this oauthprovider and restart
        portal = j.core.config.get("portal", "main")
        portal["force_oauth_instance"] = "itsyouonline"
        portal["url"] = self.config.fqdn
        j.core.config.set("portal", "main", portal)
        return portal

    def patch_mail_client(self):
        j.core.config.set("mailclient", "main", self.config["mailclient"])


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("-p", "--password", dest="password", help="Password")
    parser.add_argument("-fqdn", "--fqdn", dest="fqdn", required=True, help="FQDN")
    parser.add_argument(
        "-env_subdomain", "--env_subdomain", dest="env_subdomain", help="env_subdomain"
    )
    parser.add_argument(
        "-client_id", "--client_id", dest="client_id", help="itsyouonline client_id "
    )
    parser.add_argument(
        "-secret", "--secret", dest="secret", help="itsyouonline Secret"
    )
    parser.add_argument(
        "-ovs_url", "--ovs_url", dest="ovs_url", help="ovs_url required for local dev installation"
    )
    config = parser.parse_args()
    portal = Portal(config)
    portal.add_user()
    portal_data = portal.configure_IYO()
    portal.configure_user_groups(portal_data)
    portal.configure_portal_client()
    j.system.fs.copyDirTree("/opt/jumpscale7/cfg/", "/opt/cfgdir/")
