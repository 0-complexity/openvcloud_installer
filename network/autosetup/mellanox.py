#!/usr/bin/python3
import sys
import os
import time
import datetime

class ConfigurationException(Exception):
    pass

class MellanoxConfiguration():
    def __init__(self, configuration, device=None):
        self.config = configuration
        self.blocks = []
        self.device = device

    def section(self, name):
        return ['', '# %s' % name, '']

    def hostname(self):
        return ['hostname mellanox']

    def timezone(self):
        block = self.section('timezone')
        device = self.config['network']['mellanox'][self.device]

        block.append('clock timezone %s' % self.config['timezone'])
        block.append('no ntp server 178.79.152.182 disable')
        block.append('ntp server 178.79.152.182 keyID 0')
        block.append('no ntp server 178.79.152.182 trusted-enable')
        block.append('ntp server 178.79.152.182 version 4')

        return block

    def default(self):
        block = self.section('default settings')
        block.append('no cli default prefix-modes enable')
        return block

    def mlag(self):
        block = self.section('mlag')
        device = self.config['network']['mellanox'][self.device]

        block.append('protocol mlag')

        # FIXME:
        fixrange = [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
            21, 22, 23, 24, 25, 26, 27, 28
        ]

        for i in fixrange:
            block.append('interface mlag-port-channel %d' % i)
            block.append('interface mlag-port-channel %d mtu 9000 force' % i)

        # inter peer link (ipl)
        block.append('interface port-channel 1')
        block.append('interface ethernet 1/32 channel-group 1 mode active')

        block.append('no mlag shutdown')

        return block

    def vlans(self):
        block = self.section('vlans')
        device = self.config['network']['mellanox'][self.device]

        block.append('interface vlan 4000')
        block.append('interface vlan 4000 ip address 10.254.254.253 255.255.255.252')
        block.append('dcb priority-flow-control enable force')

        block.append('interface port-channel 1 ipl 1')
        block.append('interface vlan 4000 ipl 1 peer-address 10.254.254.254')

        block.append('vlan %s' % device['provider']['vlan'])

        for target in ['management', 'public', 'vxbackend', 'gateway-management']:
            block.append('vlan %s' % self.config['network'][target]['vlan'])

        return block

    def nodes(self):
        block = self.section('vlans')

        data = {'1/1': 24}

        for port, mlag in data.values(): # FIXME: nodes selector
            block.append('interface ethernet %s mtu 9000 force' % port)
            block.append('interface ethernet %s mlag-channel-group %d mode passive' % (port, mlag))
            block.append('interface mlag-port-channel %d switchport mode hybrid' % mlag)

        return block

    def trunks(self):
        block = self.section('trunks')
        device = self.config['network']['mellanox'][self.device]

        return block

    def uplinks(self):
        block = self.section('internet uplinks')
        device = self.config['network']['mellanox'][self.device]

        # port = switch["provider-port"]
        # vlan = self.config["network"]["vlans"]["public"]

        return block

    def commit(self):
        """
        Commit the configuration
        """
        return ["write"]

    def reboot(self):
        """
        Reboot the device
        """
        return ["reload"]

    """
    Helpers
    """
    def consolidate_port_ranges(self, lst):
        def stream():
            for item in lst.split(","):
                if "-" in item:
                    start, end = item.split("-", 1)
                    start = int(start)
                    end = int(end)

                    for port in range(start, end + 1):
                        yield port
                else:
                    yield int(item)

        lst = list(stream())
        lst.sort()

        start = None
        current = None

        for item in lst:
            if start is None:
                start = item
                current = item
                continue

            if item > current + 1:
                yield "%s-%s" % (start, current)
                start = item

            current = item

        if not start is None:
            yield "%s-%s" % (start, current)

    def dumps(self, block):
        return "\n".join(block)

if __name__ == "__main__":
    import yaml

    with open("/tmp/config.yaml", "r") as f:
        config = f.read()

    switch = yaml.load(config)
    mellanox = MellanoxConfiguration(switch, 'mellanox-1')

    config = []
    config += mellanox.hostname()
    config += mellanox.default()
    config += mellanox.timezone()
    config += mellanox.mlag()
    config += mellanox.vlans()
    config += mellanox.trunks()
    config += mellanox.uplinks()
    config += mellanox.commit()
    config += mellanox.reboot()

    print(mellanox.dumps(config))

    """
    import argparse, yaml
    parser = argparse.ArgumentParser(description='Provision configuration into the cisco router')
    parser.add_argument('--port', type=str, help='Serial port to use to connect to the cisco.')
    parser.add_argument('--logfile', type=str, default='cisco.log', help='Logfile to which all communication to the cisco is written.')
    is_file = lambda var: var if os.path.exists(var) else parser.error("File %s does not exist!" % var)
    parser.add_argument('config', type=is_file, help='OVC environment yaml configuration file')
    parser.add_argument('switch', type=str, help='Name of the switch in the yaml configuration file')
    args = parser.parse_args()
    with open(args.config) as f:
        config = yaml.load(f)
    for switch in config['network']['cisco']:
        if switch['name'] == args.switch:
            break
    else:
        print("Switch not found in config file!")
        exit(1)
    exit(apply_cisco_config(config, switch, args.port, args.logfile))
    """
