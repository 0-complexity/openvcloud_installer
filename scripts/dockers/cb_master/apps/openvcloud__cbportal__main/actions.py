from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


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

    def prepare(self, serviceObj):
        """
        this gets executed before the files are downloaded & installed on appropriate spots
        """
        dest = "/opt/jumpscale7/apps/portals/main"
        if not j.system.fs.exists(dest):
            j.events.inputerror_critical(
                "Could not find portal instance with name: main, please install"
            )
        return True

    def configure(self, serviceObj):
        service = j.atyourservice.findServices("jumpscale", "portal", "main")[0]
        service.restart()

        # setup groups
        j.application.loadConfig()
        import JumpScale.grid

        scl = j.clients.osis.getNamespace("system")
        for groupname in ("level1", "level2", "level3"):
            if not scl.group.search({"id": groupname})[0]:
                group = scl.group.new()
                group.gid = j.application.whoAmI.gid
                group.id = groupname
                group.users = ["admin"]
                scl.group.set(group)
