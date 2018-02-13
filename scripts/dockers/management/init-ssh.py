#! /bin/python3
from js9 import j
import argparse
import time


GITHUB_DATA = """
kind: github
version: v3
metadata:
  # connector name that will be used with `tsh login`
  name: github
spec:
  # client ID of Github OAuth app
  client_id: {client_id}
  # client secret of Github OAuth app
  client_secret: {client_secret}
  # connector display name that will be shown on web UI login screen
  display: Github
  # callback URL that will be called after successful authentication
  redirect_url: https://{fqdn}:3080/v1/webapi/github/callback
  # mapping of org/team memberships onto allowed logins and roles
  teams_to_logins:
  - organization: {org_name} # Github organization name
    team: {team_name} # Github team name within that organization
    # allowed logins for users in this org/team
    logins:
    - root 

"""

def get_config():
    return j.data.serializer.yaml.load('/opt/cfg/system/system-config.yaml')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--teleport', help='setup teleport with ssh', default=False, action='store_true')
    args = parser.parse_args()
    prefab = j.tools.prefab.local
    config = get_config()
    prefab.core.run("sed -i 's/\/usr\/sbin\/sshd -D/\/usr\/sbin\/sshd -D -p 2205/g' /etc/service/sshd/run")
    if args.teleport:
        github_configs = config['support']['github']
        github_configs['fqdn'] = ".".join([config['environment']['subdomain'], config['environment']['basedomain']])
        prefab.core.file_append("/etc/ssh/sshd_config", "TrustedUserCAKeys /etc/ssh/teleport-user-ca.pub")
        github_yaml = GITHUB_DATA.format(**github_configs)
        prefab.core.file_write('/root/github.yaml', github_yaml)
        timer = 20
        while not prefab.core.file_exists("/var/lib/teleport/host_uuid"):
            timer -= 1
            time.sleep(1)
            if timer == 0:
                raise RuntimeError("teleport could not be reached")
        prefab.core.run('tctl create /root/github.yaml')
