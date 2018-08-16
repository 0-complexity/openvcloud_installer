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

    def configure(self, serviceObj):
        def patchDefaultWiki(path):
            if not j.system.fs.exists(path):
                return

            contents = j.system.fs.fileGetContents(path)
            lines = contents.splitlines()
            haslogo = False
            hashealth = False
            for linenr, line in enumerate(lines):
                if "logo" in line:
                    haslogo = True
                if "grid.healthmenu" in line:
                    hashealth = True

            def getline(match):
                for nr, line in enumerate(lines):
                    if match in line:
                        return nr
                return 0

            if not haslogo:
                lines.insert(
                    getline("ApplyFlatTheme"), "{{logo:/cbgrid/.files/green.png}}"
                )
            if not hashealth:
                lines.insert(getline("menuadmin"), "{{grid.healthmenu}}")

            if not haslogo or not hashealth:
                j.system.fs.writeFile(path, "\n".join(lines))

        for space in ["home", "Grid", "AYS"]:
            path = j.system.fs.joinPaths(
                j.dirs.baseDir,
                "apps",
                "portals",
                serviceObj.instance,
                "base",
                space,
                ".space",
                "default.wiki",
            )
            patchDefaultWiki(path)

        path = j.system.fs.joinPaths(
            j.dirs.baseDir,
            "apps",
            "portals",
            "portalbase",
            "wiki",
            "System",
            ".space",
            "default.wiki",
        )
        patchDefaultWiki(path)
