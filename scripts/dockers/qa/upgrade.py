import time
from JumpScale import j

MANIFEST_URL = 'https://raw.githubusercontent.com/0-complexity/devmanifests/master/manifests/9.9.9.yml'

scl = j.clients.osis.getNamespace('system')
pcl = j.clients.portal.getByInstance('main')

def wait_until_update_done(upgradeTime, retry=180):
    for _ in range(retry):
        try:
            version = scl.version.searchOne({'status':'CURRENT', 'creationTime':{'$gt':upgradeTime}})
            if version:
                print('Update is done')
                break
            else:
                time.sleep(10)
        except:
            time.sleep(10)
    else:
        raise RuntimeError('Updating process exceeded time limit')
        
def upgrade():
    pcl.actors.cloudbroker.grid.upgrade(url=MANIFEST_URL)
    
def action():
    upgradeTime = time.time()
    upgrade()
    wait_until_update_done(upgradeTime)

if __name__ == '__main__':
    action()