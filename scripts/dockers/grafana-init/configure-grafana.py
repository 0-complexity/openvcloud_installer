from JumpScale import j
import yaml
import netaddr
import jinja2


def get_config(path='/opt/cfg/system/system-config.yaml'):
    with open(path) as file_discriptor:
        return yaml.load(file_discriptor)


def adjust_grafana_config(system_config={}):
    if not system_config:
        system_config = get_config()
    template_config = "/opt/cfg/grafana/templates/grafana.ini"
    config = '/etc/grafana/grafana.ini'
    template = jinja2.Template(j.system.fs.fileGetContents(template_config))
    j.system.fs.createEmptyFile(config)
    j.system.fs.writeFile(config, template.render(**system_config))

if __name__ == '__main__':
    adjust_grafana_config()