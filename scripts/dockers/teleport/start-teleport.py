#! /usr/bin/python3


from js9 import j
import yaml
import netaddr
import jinja2


def get_config():
    return j.data.serializer.yaml.load('/opt/cfg/system/system-config.yaml')


def adjust_nginx_config(system_config={}):
    system_config = get_config()
    prefab = j.tools.prefab.local
    loader = jinja2.FileSystemLoader('/etc/')
    env = jinja2.Environment(autoescape=True, loader=loader)
    template = env.get_template('teleport.tmpl')
    prefab.core.file_write("/etc/teleport.yaml", template.render(**system_config))
    prefab.core.run('teleport start')

if __name__ == '__main__':
    adjust_nginx_config()


