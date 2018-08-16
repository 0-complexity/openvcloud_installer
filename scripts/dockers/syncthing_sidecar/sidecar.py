from kubernetes import KuberneteSidecar
from syncthinglight import SyncthingLight
import os
import time
import xml.etree.ElementTree as et
import yaml

print("[+] initializing")
kube = KuberneteSidecar()
host_pod = os.environ["HOST_POD_NAME"]
master = "syncthing-0"
nextcycle = 5
containername = "syncthing"

while True:
    print("[+] trying to read apikey")
    # checking if the key is generated
    if not os.path.exists("/var/syncthing/config/cert.pem"):
        time.sleep(5)
        continue
    root = et.parse("/var/syncthing/config/config.xml")
    apikey = root.findall(".//apikey")[0].text
    kube.delete("configmap", host_pod)
    out = kube.kubectl(
        ["create", "configmap", host_pod, "--from-literal=apikey=%s" % apikey]
    )
    if out:
        break

while True:
    if host_pod != master:
        print("[+] i'm not the master, nothing to do")
        time.sleep(180)
        continue

    print("[+] retreiving pods")
    pods = kube.kubectl(["get", "pods", "-l", "role=syncthing"])
    available = []
    for item in pods["items"]:
        if not item["status"].get("containerStatuses"):
            continue

        for cont in item["status"]["containerStatuses"]:
            if cont["name"] == containername and cont["ready"]:
                available.append(
                    {
                        "address": item["status"]["podIP"],
                        "hostname": item["spec"]["hostname"],
                    }
                )

    print("[+] instance availables:")
    print(available)
    devices = []

    for container in available:
        print("[+] analyzing container: %s" % container["hostname"])

        # contacting client
        try:
            config_map = kube.kubectl(["get", "configmap", container["hostname"]])
        except:
            continue
        apikey = config_map["data"]["apikey"]
        client = SyncthingLight(container["address"], port=8384, apikey=apikey)
        if not client.config:
            print("[+] client not ready")
            continue

        devices.append(
            {
                "id": client.id(),
                "apikey": apikey,
                "hostname": container["hostname"],
                "target": container["address"],
                "client": client,
            }
        )

    print("[+] devices found:")
    print(devices)

    devlist = [{"deviceID": dev["id"], "introducedBy": ""} for dev in devices]

    for device in devices:
        print("[+] setting up device: %s" % device["hostname"])
        needschanges = False

        for target in devices:
            devaddr = "tcp://%s:22000" % target["target"]
            needschanges |= device["client"].add_device(
                target["hostname"], target["id"], devaddr
            )

        with open("/opt/cfg/system/system-config.yaml") as file_discriptor:
            data = yaml.load(file_discriptor)
        for dirinfo in data["directories"]:
            if dirinfo["sync"]:
                directory = dirinfo["path"]
                needschanges |= device["client"].add_folder(
                    "ovc-%s" % directory.split("/")[-1], directory, devlist
                )

        if needschanges:
            device["client"].config_set()
            print("[+] restarting service")
            device["client"].restart()

    print("[+] waiting for next cycle")

    # incremental sleep
    if nextcycle < 120:
        nextcycle = nextcycle * 2

    time.sleep(nextcycle)
