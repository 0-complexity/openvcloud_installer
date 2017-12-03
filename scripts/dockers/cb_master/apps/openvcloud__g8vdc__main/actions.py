from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):
    def configure(self, serviceObject):
        path = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'g8vdc', '.files', 'test')
        j.system.fs.removeDirTree(path)
