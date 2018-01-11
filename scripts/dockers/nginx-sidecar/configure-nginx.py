from JumpScale import j
import yaml
import netaddr
import jinja2


def get_config(path='/opt/cfg/system/system-config.yaml'):
    with open(path) as file_discriptor:
        return yaml.load(file_discriptor)


def adjust_nginx_config(system_config={}):
    if not system_config:
        system_config = get_config()
    config = "/opt/cfg/nginx/%s/%s"
    def ip_from_range(ip_range):
        net = netaddr.IPNetwork(ip_range)
        return net.ip

    loader = jinja2.FileSystemLoader(config % ("templates", ""))
    env = jinja2.Environment(autoescape=True, loader=loader)
    env.filters['ip_from_range'] = ip_from_range
    template = env.get_template('nginx.conf')
    j.system.fs.writeFile(config % ("sites-enabled", "nginx.conf"), template.render(**system_config))


if __name__ == '__main__':
    adjust_nginx_config()
