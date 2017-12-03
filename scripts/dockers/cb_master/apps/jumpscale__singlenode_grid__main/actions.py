from JumpScale import j

ActionsBase=j.atyourservice.getActionsBaseClass()

class Actions(ActionsBase):

    def configure(self, serviceObj):
        roles = j.application.config.getList('grid.node.roles')
        if 'master' not in roles:
            roles.append('master')
            j.application.config.set('grid.node.roles', roles)

        # reload system config / whoAmI
        j.application.loadConfig()
        # restart jsagent
        j.atyourservice.get(domain='jumpscale', name='jsagent').restart()
