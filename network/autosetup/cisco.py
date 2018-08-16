#!/usr/bin/python3
import sys
import os
import time
import datetime


class ConfigurationException(Exception):
    pass


class CiscoConfiguration:
    def __init__(self, configuration):
        self.config = configuration
        self.blocks = []

    def section(self, name):
        return ["", "# %s" % name, ""]

    def hostname(self):
        return ["hostname switch"]

    def vlans(self):
        block = self.section("vlans")

        vlans = ",".join(str(vlan) for vlan in self.config["network"]["vlans"].values())
        block.append("vlan %s" % vlans)

        switch = self.config["network"]["cisco"][0]
        switch_ip_address = switch["management"]["switch-ip"]["address"]
        switch_ip_netmask = switch["management"]["switch-ip"]["netmask"]

        timezone = self.config["timezone"]
        mgmt_vlan = self.config["network"]["vlans"]["management"]

        block.append(
            "management vlan ip-address %s mask %s"
            % (switch_ip_address, switch_ip_netmask)
        )
        block.append("no management vlan ip dhcp client")
        block.append("clock timezone %s 2 minutes 0" % timezone)
        block.append("management-vlan vlan %s" % mgmt_vlan)
        block.append("spanning-tree forward-time 4")
        block.append("ip ssh server")

        ports = []
        ports.append(switch["management"]["ports"]["controllers"]["ipmi"])
        ports.append(switch["management"]["ports"]["controllers"]["mgmt"])
        ports.append(switch["management"]["ports"]["cpunodes"]["ipmi"])
        ports.append(switch["management"]["ports"]["cpunodes"]["mgmt"])
        ports.append(switch["management"]["ports"]["stornodes"]["ipmi"])
        ports.append(switch["management"]["ports"]["stornodes"]["mgmt"])
        ports.append(switch["management"]["ports"]["mellanox"])

        for range in self.consolidate_port_ranges(",".join(ports)):
            block.append("interface range GigabitEthernet %s" % range)
            block.append("switchport access vlan %s" % mgmt_vlan)
            block.append("spanning-tree portfast")
            block.append("exit")

        return block

    def trunks(self):
        block = self.section("trunks")
        switch = self.config["network"]["cisco"][0]

        ports = []
        ports.append(switch["trunk-ports"]["controllers"])
        ports.append(switch["trunk-ports"]["mellanox"])

        vlans = ",".join(str(vlan) for vlan in self.config["network"]["vlans"].values())
        for range in self.consolidate_port_ranges(",".join(ports)):
            block.append("interface range GigabitEthernet %s" % range)
            block.append("switchport trunk allowed vlan add %s" % vlans)
            block.append("exit")

        return block

    def uplinks(self):
        block = self.section("internet uplinks")
        switch = self.config["network"]["cisco"][0]

        port = switch["provider-port"]
        vlan = self.config["network"]["vlans"]["public"]

        block.append("interface GigabitEthernet %s" % port)
        block.append("switchport mode access")
        block.append("switchport access vlan %s" % vlan)
        block.append("speed 100")
        block.append("duplex full")
        block.append("no cdp enable")
        block.append("exit")

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
    cisco = CiscoConfiguration(switch)

    config = []
    config += cisco.hostname()
    config += cisco.vlans()
    config += cisco.trunks()
    config += cisco.uplinks()
    config += cisco.commit()
    config += cisco.reboot()

    print(cisco.dumps(config))

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
