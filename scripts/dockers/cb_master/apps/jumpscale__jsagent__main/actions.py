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
        hpath = j.system.fs.joinPaths(j.dirs.hrdDir, "system", "grid.hrd")
        if not j.system.fs.exists(path=hpath):
            hrd = j.core.hrd.get(hpath)
            hrd.set("id", serviceObj.hrd.get("instance.grid.id"))
            hrd.set("node.id", "0")
            hrd.set("node.machineguid", j.application.getUniqueMachineId())
            hrd.set(
                "node.roles",
                serviceObj.hrd.getStr("instance.grid.node.roles").split(","),
            )
            hrd.save()

        # reload system config / whoAmI
        j.application.loadConfig()

    def start(self, *args, **kwargs):
        result = ActionsBase.start(self, *args, **kwargs)
        j.application.loadConfig()
        j.application.initWhoAmI(True)
        return result
