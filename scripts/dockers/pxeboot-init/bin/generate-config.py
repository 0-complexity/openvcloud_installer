import yaml
import os

configroot = '/opt/pxeboot/conf'
tftproot = '/opt/pxeboot/tftpboot'

with open('/etc/system-config.yaml', 'r') as f:
    configfile = f.read()

config = yaml.load(configfile)
domain = config['environment']['domain']
gateway = config['environment']['gateway']
subnet = config['environment']['subnet']

"""
dhcphosts file
"""
target = os.path.join(configroot, 'dhcphosts')

with open(target, "w") as f:
    for subgroup in ['cpu', 'storage']:
        nodes = config['nodes'][subgroup]

        f.write("#\n# %s\n#\n" % subgroup)

        for node in nodes:
            f.write("%s,%s,infinite\n" % (node['mgmt']['macaddress'].lower(), node['name']))

        f.write("\n")

"""
hosts file
"""
target = os.path.join(configroot, 'hosts')

with open(target, "w") as f:
    for subgroup in ['cpu', 'storage']:
        nodes = config['nodes'][subgroup]

        f.write("#\n# %s\n#\n" % subgroup)

        for node in nodes:
            f.write("%s %s.%s %s\n" % (node['mgmt']['ipaddress'], node['name'], domain, node['name']))

        f.write("\n")

"""
dnsmasq and pxelinux
"""
netconfig = {
    '%domain%': domain,
    '%range%': subnet,
    '%gateway%': gateway,
    '%option6%': gateway,
}

pxelinux = os.path.join(tftproot, 'pxelinux.cfg', '911boot')
dnsmasq = os.path.join(configroot, 'dnsmasq.conf')

for target in [pxelinux, dnsmasq]:
    with open(target, 'r') as f:
        source = f.read()

    for entry in netconfig:
        source = source.replace(entry, netconfig[entry])

    with open(target, 'w') as f:
        f.write(source)
