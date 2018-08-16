from JumpScale import j

# from JumpScale.baselib.atyourservice.ActionsBase import remote
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
        this gets executed before the files are downloaded & installed on approprate spots
        """

        if j.do.TYPE.lower().startswith("osx"):
            res = j.do.execute("brew install mongodb")
            res = j.do.execute("brew list mongodb")
            for line in res[1].split("\n"):
                if line.strip() == "":
                    continue
                if j.do.exists(line.strip()) and line.find("bin/") != -1:
                    destpart = line.split("bin/")[-1]
                    dest = "/opt/mongodb/bin/%s" % destpart
                    j.system.fs.createDir(j.system.fs.getDirName(dest))
                    j.do.copyFile(line, dest)
                    j.do.chmod(dest, 0o770)

        if j.do.TYPE.lower().startswith("ubuntu"):
            j.do.execute("apt-get purge 'mongo*' -y")
            j.do.execute("apt-get autoremove -y")
            j.system.platform.ubuntu.stopService("mongod")
            j.system.platform.ubuntu.serviceDisableStartAtBoot("mongod")

        j.system.fs.createDir("/opt/jumpscale7/var/mongodb/main")

        return True

    def configure(self, serviceObj):
        if serviceObj.hrd.exists("instance.param.replicaset"):
            repset = serviceObj.hrd.get("instance.param.replicaset")
            if repset != "":
                process = serviceObj.hrd.getDictFromPrefix("service.process")["1"]
                process["args"] += " --replSet '%s'" % repset
                serviceObj.hrd.set("service.process.1", process)
