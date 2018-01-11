import yaml
import os
import subprocess
from managementaddr import ManagementAddress

configroot = '/opt/pxeboot/conf'
tftproot = '/opt/pxeboot/tftpboot'
imageroot = '/opt/pxeboot/images'
intf = ManagementAddress()

with open('/etc/global/system-config.yaml', 'r') as f:
    configfile = f.read()

config = yaml.load(configfile)
domain = "%s.%s" % (config['environment']['basedomain'], config['environment']['subdomain'])
gateway = intf.get('mgmt')
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
            f.write("%s,%s,infinite\n" % (node['management']['macaddress'].lower(), node['name']))

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
            f.write("%s %s.%s %s\n" % (node['management']['ipaddress'].split('/')[0], node['name'], domain, node['name']))

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

pxelinux = os.path.join(configroot, 'tftp-911boot')
dnsmasq = os.path.join(configroot, 'dnsmasq.conf')

for target in [pxelinux, dnsmasq]:
    with open(target, 'r') as f:
        source = f.read()

    for entry in netconfig:
        source = source.replace(entry, netconfig[entry])

    with open(target, 'w') as f:
        f.write(source)

"""
ssh key
"""
with open('/tmp/id_rsa', 'w') as f:
    f.write(config['ssh']['private-key'])

os.chmod('/tmp/id_rsa', 0o600)

key = subprocess.run(['ssh-keygen', '-y', '-f', '/tmp/id_rsa'], stdout=subprocess.PIPE)
print("Public key: %s" % key.stdout.strip())

with open(os.path.join(imageroot, 'pubkey'), 'w') as f:
    f.write(key.stdout.decode('utf-8'))

