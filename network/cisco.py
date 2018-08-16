#!/usr/bin/python3
#
# This script automates the configuration of the cisco switch.
#

import serial
import sys
import os
import time
import datetime


class TimeoutException(Exception):
    pass


class ConfigurationException(Exception):
    pass


def apply_cisco_config(config, switch, port, logfile):
    """
    Applies the configuration to the cisco switch.
    """
    with open(logfile, "wb") as logfile_handle:
        console = get_console(port, logfile_handle)
        if not console:
            return 1
        try:
            if not login(console, "cisco", switch["password"], logfile_handle):
                return 1
            try:
                writelines(console, logfile_handle, [b"conf terminal\n"])
                readlines(console, logfile_handle)
                configure_hostname(console, logfile_handle, switch["hostname"])
                configure_vlans(console, logfile_handle, config, switch)
                configure_trunk_ports(console, logfile_handle, config, switch)
                configure_internet_uplink(console, logfile_handle, config, switch)
                writelines(console, logfile_handle, [b"exit\n"])
                readlines(console, logfile_handle)
                write_config_and_reboot(console, logfile_handle)
            except:
                logout(console, logfile_handle)
                raise
        except Exception as e:
            print(str(e))
        finally:
            console.close()
    print()
    print()
    print(
        "=============== Configuration done. Plz check switch output: ==============="
    )
    with open(logfile, "rb") as logfile_handle:
        print(logfile_handle.read().decode("utf8"))
    return 0


def write_config_and_reboot(console, logfile):
    print("Writing configuration")
    writelines(console, logfile, [b"write\n"])
    readlines(console, logfile)
    print("Rebooting switch")
    writelines(console, logfile, [b"reload\n"])
    readlines(console, logfile)
    writelines(console, logfile, [b"\n"])
    readlines(console, logfile)


def get_console(port, logfile):
    """
    Get a console connection to the cisco over serial.
    """
    ports = serial_ports()
    if port and port not in ports:
        print("Error: Port %s is not connected!" % port)
        return None
    elif len(ports) == 1:
        print("Using port %s" % ports[0])
        port = ports[0]
    elif len(ports) == 0:
        print("No serial connection found")
        return None
    else:
        print(
            "Multiple ports to serial connection found: %s\nPlease use the --port flag to specify which port to use"
            % ports
        )
        return None
    print("Connecting to cisco")
    console = serial.Serial(
        port=port, baudrate=9600, parity="N", stopbits=1, bytesize=8, timeout=1
    )
    console.writelines([b"\n"])
    while True:
        output = readlines(console, logfile)
        if "Username: " in output:
            break
        if "Press any key to continue" in output:
            console.writelines([b"\n"])
        print("Waiting for switch to get ready for authentication ...")
        time.sleep(1)
    return console


def writelines(console, logfile, lines):
    console.writelines(lines)


def readlines(console, logfile):
    lines = console.readlines()
    logfile.write(b"".join(lines))
    logfile.flush()
    return "".join(line.decode("utf8") for line in lines)


def wait(console, logfile, text, timeout=20):
    """
    Waits for 'text' to appear.
    """
    output = ""
    start = time.time()
    while True:
        output += readlines(console, logfile)
        if text in output:
            return output
        if time.time() - start > timeout:
            raise TimeoutException("Timeout waiting for %s" % text)


def login(console, username, password, logfile):
    """
    Authenticates the session using the specified username and password.
    """
    print("Authenticating")
    writelines(console, logfile, [b"%s\n" % username.encode("utf8")])
    wait(console, logfile, "Password: ")
    writelines(console, logfile, [b"%s\n" % password.encode("utf8")])
    output = readlines(console, logfile)
    if not "Authentication Failed" in output:
        print("Authentication successful!")
        return True
    print("Could not authenticate with credentials from config file")
    print("Authenticating with default credentials")
    if not "Username: " in output:
        print("Expected 'Username: ' in output")
        return False
    writelines(console, logfile, [b"cisco\n"])
    wait(console, logfile, "Password: ")
    writelines(console, logfile, [b"cisco\n"])
    output = readlines(console, logfile)
    if "New console connection for user cisco, source async  ACCEPTED" in output:
        print("Authentication successful!")
        print("Configuring password for cisco user ...")
        if "Do you want to change the password (Y/N)[Y] ?" in output:
            writelines(console, logfile, [b"Y\n"])
            try:
                wait(console, logfile, "Enter old password", 10)
            except TimeoutException:
                pass
            writelines(console, logfile, [b"cisco\n"])
            wait(console, logfile, "Enter new password")
            writelines(console, logfile, [b"%s\n" % password.encode("utf8")])
            wait(console, logfile, "Confirm new password")
            writelines(console, logfile, [b"%s\n" % password.encode("utf8")])
            readlines(console, logfile)
        else:
            writelines(
                console,
                logfile,
                [b"username cisco privilege 15 secret %s\n" % password.encode("utf8")],
            )
            readlines(console, logfile)
        return True
    else:
        print("Could not authenticate to the cisco switch!")
        return False


def configure_hostname(console, logfile, hostname):
    print("Configuring hostname to '%s'" % hostname)
    writelines(console, logfile, [b'hostname "%s"\n' % hostname.encode("utf8")])
    readlines(console, logfile)


def consolidate_port_ranges(lst):
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


def apply_block(console, logfile, block):
    for line in block.splitlines():
        print("Applying: %s" % line)
        writelines(console, logfile, [b"%s\n" % line.encode("utf8")])
        output = readlines(console, logfile)
        if "bad parameter value" in output:
            raise ConfigurationException(output)


def configure_vlans(console, logfile, config, switch):
    print("Configuring vlans")
    vlans = ",".join(str(vlan) for vlan in config["network"]["vlans"].values())
    switch_ip_address = switch["management"]["switch-ip"]["address"]
    switch_ip_netmask = switch["management"]["switch-ip"]["netmask"]
    timezone = config["timezone"]
    mgmt_vlan = config["network"]["vlans"]["management"]
    settings = (
        """vlan %(vlans)s
  management vlan ip-address %(switch_ip_address)s mask %(switch_ip_netmask)s
no management vlan ip dhcp client
clock timezone %(timezone)s 2 minutes 0
management-vlan vlan %(mgmt_vlan)s
spanning-tree forward-time 4
ip ssh server"""
        % locals()
    )
    apply_block(console, logfile, settings)
    ports = "%s,%s,%s,%s,%s,%s,%s" % (
        switch["management"]["ports"]["controllers"]["ipmi"],
        switch["management"]["ports"]["controllers"]["mgmt"],
        switch["management"]["ports"]["cpunodes"]["ipmi"],
        switch["management"]["ports"]["cpunodes"]["mgmt"],
        switch["management"]["ports"]["stornodes"]["ipmi"],
        switch["management"]["ports"]["stornodes"]["mgmt"],
        switch["management"]["ports"]["mellanox"],
    )
    for range in consolidate_port_ranges(ports):
        interface_range = (
            """interface range GigabitEthernet %(range)s
  switchport access vlan %(mgmt_vlan)s
  spanning-tree portfast
exit
"""
            % locals()
        )
        apply_block(console, logfile, interface_range)


def configure_trunk_ports(console, logfile, config, switch):
    print("Configuring trunk ports")
    ports = "%s,%s" % (
        switch["trunk-ports"]["controllers"],
        switch["trunk-ports"]["mellanox"],
    )
    vlans = ",".join(str(vlan) for vlan in config["network"]["vlans"].values())
    for range in consolidate_port_ranges(ports):
        interface_range = (
            """interface range GigabitEthernet %(range)s
  switchport trunk allowed vlan add %(vlans)s
exit
"""
            % locals()
        )
        apply_block(console, logfile, interface_range)


def configure_internet_uplink(console, logfile, config, switch):
    print("Configuring internet uplink fallback port")
    port = switch["provider-port"]
    vlan = config["network"]["vlans"]["public"]
    settings = (
        """interface GigabitEthernet %(port)s
  switchport mode access
  switchport access vlan %(vlan)s
  speed 100
  duplex full
  no cdp enable
exit"""
        % locals()
    )
    apply_block(console, logfile, settings)


def logout(console, logfile):
    while True:
        writelines(console, logfile, [b"exit\n"])
        output = readlines(console, logfile)
        if output.strip().endswith(">"):
            writelines(console, logfile, [b"exit\n"])
            readlines(console, logfile)
            return


def serial_ports():
    """ 
    Lists serial port names

    Credits to https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of the serial ports available on the system
    """
    if sys.platform.startswith("win"):
        ports = ["COM%s" % (i + 1) for i in range(256)]
    elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob("/dev/tty[A-Za-z]*")
    elif sys.platform.startswith("darwin"):
        ports = glob.glob("/dev/tty.*")
    else:
        raise EnvironmentError("Unsupported platform")

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


if __name__ == "__main__":
    import argparse, yaml

    parser = argparse.ArgumentParser(
        description="Provision configuration into the cisco router"
    )
    parser.add_argument(
        "--port", type=str, help="Serial port to use to connect to the cisco."
    )
    parser.add_argument(
        "--logfile",
        type=str,
        default="cisco.log",
        help="Logfile to which all communication to the cisco is written.",
    )
    is_file = (
        lambda var: var
        if os.path.exists(var)
        else parser.error("File %s does not exist!" % var)
    )
    parser.add_argument(
        "config", type=is_file, help="OVC environment yaml configuration file"
    )
    parser.add_argument(
        "switch", type=str, help="Name of the switch in the yaml configuration file"
    )
    args = parser.parse_args()
    with open(args.config) as f:
        config = yaml.load(f)
    for switch in config["network"]["cisco"]:
        if switch["name"] == args.switch:
            break
    else:
        print("Switch not found in config file!")
        exit(1)
    exit(apply_cisco_config(config, switch, args.port, args.logfile))
