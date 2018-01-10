#!/usr/bin/python3

# This file start the 0-access server using configuration comming from the env configuration yaml file.

from collections import namedtuple
import yaml
from zero_access import run

with open('/opt/cfg/system/system-config.yaml', 'rb') as f:
    cfg = yaml.load(f)

args = namedtuple('Arguments', ['organization', 'client_secret', 'uri', 'port', 'ssh_ip', 'ssh_port', 'session_timeout'])
args.organization = "%s.0-access" % cfg['itsyouonline']['clientId']
args.client_secret = cfg['itsyouonline']['clientSecret']
args.uri = "https://%s.%s/0-access" % (cfg['environment']['subdomain'], cfg['environment']['basedomain'])
args.port = 7022
args.ssh_ip = '127.0.0.1'
args.session_timeout = 3600

run(args)