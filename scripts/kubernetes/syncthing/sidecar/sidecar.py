from kubernetes import KuberneteSidecar
from syncthinglight import SyncthingLight
import os
import json
import time
import xml.etree.ElementTree as et

print("[+] initializing")
kube = KuberneteSidecar()
master = "syncthing-0"
nextcycle = 5

while True:
    if os.environ['HOST_POD_NAME'] != master:
        print("[+] i'm not the master, nothing to do")
        time.sleep(180)
        continue

    print("[+] retreiving pods")
    pods = kube.kubectl(['get', 'pods'])

    target = "syncthing"
    available = []

    for item in pods['items']:
        if not item['status'].get('containerStatuses'):
            continue

        for container in item['status']['containerStatuses']:
            if container['name'] == target and container['ready']:
                available.append({
                    'address': item['status']['podIP'],
                    'hostname': item['spec']['hostname'],
                })

    print("[+] instance availables:")
    print(available)
    devices = []

    for container in available:
        print("[+] analyzing container: %s" % container['hostname'])

        # checking if the key is generated
        ready = kube.execute(container['hostname'], target, ['ls', '/var/syncthing/config/cert.pem'])
        if not ready:
            continue

        # reading apikey
        config = kube.execute(container['hostname'], target, ['cat', '/var/syncthing/config/config.xml'])
        root = et.fromstring(config)
        apikey = root.findall(".//apikey")[0].text

        # contacting client
        client = SyncthingLight(container['address'], port=8384, apikey=apikey)
        if not client.config:
            print('[+] client not ready')
            continue

        devices.append({
            'id': client.id(),
            'apikey': apikey,
            'hostname': container['hostname'],
            'target': container['address'],
            'client': client,
        })

    print("[+] devices found:")
    print(devices)

    devlist = [{'deviceID': dev['id']} for dev in devices]

    for device in devices:
        print("[+] setting up device: %s" % device['hostname'])

        for target in devices:
            # skipping ourself
            if target['id'] == device['id']:
                continue

            devaddr = 'tcp://%s:22000' % target['target']
            device['client'].add_device(target['hostname'], target['id'], devaddr)

        device['client'].add_folder('ovc-billing', '/var/ovc/billing', devlist)
        device['client'].add_folder('ovc-influx', '/var/ovc/influxdb', devlist)
        device['client'].add_folder('ovc-grafana', '/var/ovc/grafana', devlist)
        device['client'].add_folder('ovc-pxeboot', '/var/ovc/pxeboot', devlist)

        device['client'].config_set()

        print('[+] restarting service')
        device['client'].restart()

    print("[+] waiting for next cycle")

    # incremental sleep
    if nextcycle < 120:
        nextcycle = nextcycle * 2

    time.sleep(nextcycle)
