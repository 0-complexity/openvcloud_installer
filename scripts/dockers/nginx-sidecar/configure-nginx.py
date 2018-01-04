from JumpScale import j
import yaml
import os
import requests
import base64
import jinja2


def get_config(path='/opt/cfg/system/system-config.yaml'):
    with open(path) as file_discriptor:
        return yaml.load(file_discriptor)


def adjust_nginx_config(system_config={}):
    if not system_config:
        system_config = get_config()
    config = "/opt/cfg/nginx/%s/nginx.conf"
    template = jinja2.Template(j.system.fs.fileGetContents(config % "templates"))
    j.system.fs.writeFile(config % "sites-enabled", template.render(**system_config))

if __name__ == '__main__':
    adjust_nginx_config()
