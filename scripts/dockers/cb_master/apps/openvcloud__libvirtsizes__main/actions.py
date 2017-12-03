from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):
    """
    process for install
    -------------------
    step1: prepare actions
    step2: check_requirements action
    step3: download files & copy on right location (hrd info is used)
    step4: configure action
    step5: check_uptime_local to see if process stops  (uses timeout $process.stop.timeout)
    step5b: if check uptime was true will do stop action and retry the check_uptime_local check
    step5c: if check uptime was true even after stop will do halt action and retry the check_uptime_local check
    step6: use the info in the hrd to start the application
    step7: do check_uptime_local to see if process starts
    step7b: do monitor_local to see if package healthy installed & running
    step7c: do monitor_remote to see if package healthy installed & running, but this time test is done from central location
    """


    def configure(self, serviceObj):
        import JumpScale.portal
        cl = j.clients.portal.getByInstance('cloudbroker')
        osiscl = j.clients.osis.getByInstance('main')
        osis_size = j.clients.osis.getCategory(osiscl, 'cloudbroker', 'size')
        osis_lsize = j.clients.osis.getCategory(osiscl, 'libvirt', 'size')
        cl.getActor('libcloud', 'libvirt')
        cl.getActor('cloudapi','accounts')
        cl.getActor('cloudapi','cloudspaces')

        #A size is also needed in the cloudbroker
        sizecbs = [('10GB at SSD Speed, Unlimited Transfer - 7.5 USD/month', 512, 1),
                 ('10GB at SSD Speed, Unlimited Transfer - 15 USD/month', 1024, 1),
                 ('10GB at SSD Speed, Unlimited Transfer - 18 USD/month', 2048, 2),
                 ('10GB at SSD Speed, Unlimited Transfer - 36 USD/month', 4096, 2),
                 ('10GB at SSD Speed, Unlimited Transfer - 70 USD/month', 8192, 4),
                 ('10GB at SSD Speed, Unlimited Transfer - 140 USD/month', 16384, 8)]
        disksizes = [10, 20, 50, 100, 250, 500, 1000, 2000]
        for i in disksizes:
            for sizecb in sizecbs:
                if osis_lsize.search({'memory': sizecb[1], 'disk': i})[0]:
                    continue
                size = dict()
                size['disk'] = i
                size['memory'] = sizecb[1]
                size['name'] = '%i-%i' % (sizecb[1], i)
                size['vcpus'] = sizecb[2]
                osis_lsize.set(size)
