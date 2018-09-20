import time
from JumpScale import j

MANIFEST_URL = "https://raw.githubusercontent.com/0-complexity/devmanifests/master/manifests/9.9.9.yml"

scl = j.clients.osis.getNamespace("system")
pcl = j.clients.portal.getByInstance("main")

def wait_until_upgrade_done(upgradeTime, retry=180):
    for _ in range(retry):
        try:
            current_version = scl.version.searchOne({"status": "CURRENT", "creationTime": {"$gt": upgradeTime}})
            installing_version = scl.version.count({"status": "INSTALLING"})
            if current_version and not installing_version:
                break
            else:
                time.sleep(10)
        except:
            time.sleep(10)
    else:
        raise RuntimeError("Upgrade process exceeded time limit")

def action():
    print("[*] Upgrading environment ...")
    upgradeTime = time.time()
    pcl.actors.cloudbroker.grid.upgrade(url=MANIFEST_URL)
    wait_until_upgrade_done(upgradeTime)
    print("[*] Upgrade is done.")

if __name__ == "__main__":
    action()
