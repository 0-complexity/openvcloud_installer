import socket
import fcntl
import struct
import sys

SIOCGIFADDR = 0x8915
ifname = sys.argv[1] if len(sys.argv) > 1 else 'mgmt'

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        req = struct.pack('256s', bytes(ifname[:15], 'utf-8'))
        ctl = fcntl.ioctl(s.fileno(), SIOCGIFADDR, req)

    except Exception:
        return '0.0.0.0'

    return socket.inet_ntoa(ctl[20:24])

print(get_ip_address(ifname))
