import subprocess
import json
import xml.etree.ElementTree as et
from js9 import j

def kubectl(args):
    baseargs = ["kubectl", "-o", "json"]
    response = subprocess.run(baseargs + args, stdout=subprocess.PIPE)

    return json.loads(response.stdout.decode('utf-8'))

def execute(pod, container, command):
    baseargs = ["kubectl", "exec", pod, "-c", container, "--"]
    response = subprocess.run(baseargs + command, stdout=subprocess.PIPE)

    return response.stdout.decode('utf-8').strip()

target = "syncthing"

pods = kubectl(['get', 'pods'])

available = []

for item in pods['items']:
    for container in item['status']['containerStatuses']:
        if container['name'] == target and container['ready']:
            available.append({
                'address': item['status']['podIP'],
                'hostname': item['spec']['hostname'],
            })

print(available)
devices = []

for container in available:
    # checking if the key is generated
    ready = execute(container['hostname'], target, ['ls', '/var/syncthing/config/cert.pem'])
    if not ready:
        continue

    # reading apikey
    config = execute(container['hostname'], target, ['cat', '/var/syncthing/config/config.xml'])
    root = et.fromstring(config)
    apikey = root.findall(".//apikey")[0].text

    # contacting client
    client = j.clients.syncthing.get(container['address'], port=8384, apikey=apikey)

    devices.append({
        'id': client.id_get(),
        'apikey': apikey,
        'hostname': container['hostname'],
        'target': container['address'],
        'client': client,
    })


def add_device(client, name, device, address):
    for dev in client._config['devices']:
        if dev['deviceID'] == device:
            return False

    device = {
        'addresses': [address],
        'certName': '',
        'compression': 'always',
        'deviceID': deviceid,
        'introducer': False,
        'name': name
    }

    client._config['devices'].append(device)
    return True

def add_folder(client, name, path, devices):
    for folder in client._config['folders']:
        if folder['id'] == name:
            return False

    folder = {
        'autoNormalize': False,
        'copiers': 0,
        'devices': devices,
        'hashers': 0,
        'id': name,
        'ignoreDelete': False,
        'ignorePerms': False,
        'invalid': '',
        'minDiskFreePct': 5,
        'order': 'random',
        'path': path,
        'pullers': 0,
        'readOnly': False,
        'rescanIntervalS': 10,
        'versioning': {'params': {}, 'type': ''}
    }

    client._config['folders'].append(folder)
    return True

def share(devices):
    devlist = [{'deviceID': dev['id']} for dev in devices]

    for device in devices:
        for target in devices:
            # skipping ourself
            if target['id'] == device['id']:
                continue

            devaddr = 'tcp://%s:22000' % target['target']
            add_device(device['client'], target['hostname'], target['id'], devaddr)

        add_folder(device['client'], 'ovc-billing', '/var/ovc/billing', devlist)
        add_folder(device['client'], 'ovc-influx', '/var/ovc/influxdb', devlist)

        device['client'].config_set()
        device['client'].api_call("system/restart", get=False)

share(devices)
