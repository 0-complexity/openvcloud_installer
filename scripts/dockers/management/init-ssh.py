#! /bin/python3
import argparse
import time
import yaml
import subprocess
import os

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
    with open('/opt/cfg/system/system-config.yaml', 'r') as cfg:
        return yaml.load(cfg)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--teleport', help='setup teleport with ssh', default=False, action='store_true')
    args = parser.parse_args()
    config = get_config()
    subprocess.run(["sed", "-i", "s/\/usr\/sbin\/sshd -D/\/usr\/sbin\/sshd -D -p 2205/g", "/etc/service/sshd/run"])
    if args.teleport:
        github_configs = config['support']['github']
        github_configs['fqdn'] = ".".join([config['environment']['subdomain'], config['environment']['basedomain']])
        with open('/etc/ssh/sshd_config', 'a') as sshd:
            sshd.write('TrustedUserCAKeys /etc/ssh/teleport-user-ca.pub')
        github_yaml = GITHUB_DATA.format(**github_configs)
        with open('/root/github.yaml', 'w') as git:
            git.write(github_yaml)
        timer = 20
        while not os.path.exists("/var/lib/teleport/host_uuid"):
            timer -= 1
            time.sleep(1)
            if timer == 0:
                raise RuntimeError("Teleport could not be reached")
        subprocess.run('tctl', 'create', '/root/github.yaml')
