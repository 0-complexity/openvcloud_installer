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

    def mlag(self):
        block = self.section('mlag')
        device = self.config['network']['mellanox'][self.device]

        block.append('protocol mlag')

        # port channel
        # mlag-channel-group

        return block

    def vlans(self):
        block = self.section('vlans')
        device = self.config['network']['mellanox'][self.device]

        block.append('vlan %s' % device['provider']['vlan'])

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
