#!/usr/bin/python3

# This file start the 0-access server using configuration comming from the env configuration yaml file.

from collections import namedtuple
import yaml
from zero_access import run

with open('/opt/cfg/system/system-config.yaml', 'rb') as f:
    cfg = yaml.load(f)

config = {}
config['organization'] = "%s.0-access" % cfg['itsyouonline']['clientId']
config['client_secret_'] = cfg['itsyouonline']['clientSecret']
config['uri'] = "https://%s.%s/0-access" % (cfg['environment']['subdomain'], cfg['environment']['basedomain'])
config['ssh_port'] = 7022
config['port'] = 5000
config['ssh_ip'] = "%s.%s" % (cfg['environment']['subdomain'], cfg['environment']['basedomain'])
config['session_timeout'] = 28800 # eight hours
config['gateone_url'] = ''
run(**config) 
