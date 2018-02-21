from JumpScale import j
import yaml
import netaddr
import jinja2
import argparse
import time


def get_config(path='/opt/cfg/system/system-config.yaml'):
    with open(path) as file_discriptor:
        return yaml.load(file_discriptor)


def adjust_nginx_config(upgrade, system_config={}):
    if not system_config:
        system_config = get_config()
    config = "/opt/cfg/nginx/%s/%s"
    def ip_from_range(ip_range):
        net = netaddr.IPNetwork(ip_range)
        return net.ip
    if upgrade:
        log_dir = '/opt/logs/'
        file_loc = log_dir + 'update_env.log'
        if j.system.fs.exists(file_loc):
            j.system.fs.unlink(file_loc)
        tmp_name = log_dir + '{}.log'.format(int(time.time()))
        j.system.fs.touch(tmp_name)
        j.do.execute('ln -s {} {}'.format(tmp_name, file_loc))
    file_name = 'upgrade.conf' if upgrade else 'nginx.conf'
    loader = jinja2.FileSystemLoader(config % ("templates", ""))
    env = jinja2.Environment(autoescape=True, loader=loader)
    env.filters['ip_from_range'] = ip_from_range
    template = env.get_template(file_name)
    j.system.fs.writeFile(config % ("sites-enabled", "nginx.conf"), template.render(**system_config))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--upgrade', help='apply the upgrade nginx config', default=False, action='store_true')
    args = parser.parse_args()
    adjust_nginx_config(args.upgrade)
    j.system.fs.copyDirTree('/opt/code/github/openvcloud_installer/scripts/install/web-files', '/opt/cfg/upgrade/')
