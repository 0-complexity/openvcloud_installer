from js9 import j

class JumpScale7:
    def __init__(self, prefab):
        self.prefab = prefab

    def install_core(self, version='master'):
        env = {'AYSBRANCH': version, 'JSBRANCH': version}
        cmd = 'cd /tmp;rm -f install.sh;curl -k https://raw.githubusercontent.com/jumpscale7/jumpscale_core7/{}/install/install.sh > install.sh;bash install.sh'.format(version)
        self.prefab.system.ssh.define_host('git.aydo.com')
        self.prefab.system.ssh.define_host('github.com')

        if self.prefab.bash.cmdGetPath('python', False) is False or self.prefab.bash.cmdGetPath('curl', False) is False:
            self.prefab.system.package.mdupdate()
            self.prefab.system.package.install('python')
            self.prefab.system.package.install('curl')
        if self.prefab.bash.cmdGetPath('js', False) is False:
            self.prefab.core.run(cmd, env=env)

    def install_agent(self, osishost, osispassword, achost, gid):
        redisdata = {
            'param.disk': '0',
            'param.mem': '100',
            'param.passwd': '',
            'param.port': '9999',
            'param.ip' : '0.0.0.0',
            'param.unixsocket': '0'
        }
        self.ays_install('redis', instance='system', data=redisdata)

        osisclientdata = {
            'param.osis.client.addr': osishost,
            'param.osis.client.login': 'root',
            'param.osis.client.passwd': osispassword,
            'param.osis.client.port': '5544',
        }
        self.ays_install('osis_client', instance='main', data=osisclientdata)
        self.ays_install('osis_client', instance='jsagent', data=osisclientdata)

        agentcontrollerdata = {
            'agentcontroller.client.addr': achost,
            'agentcontroller.client.login': 'node',
            'agentcontroller.client.passwd': '',
            'agentcontroller.client.port': '4444'
        }
        self.ays_install('agentcontroller_client', instance='main', data=agentcontrollerdata)

        agentdata = {
                'agentcontroller.connection': 'main',
                'grid.id': str(gid),
                'grid.node.roles': 'node',
                'osis.connection': 'jsagent',
        }
        self.ays_install('jsagent', instance='main', data=agentdata)


    def ays_install(self, package, domain='jumpscale', instance='main', data=None):
        datastr = ''
        data = data or {}
        for key, value in data.items():
            datastr += "{}:{} ".format(key, value)
        cmd = 'ays install -d {} -n {} -i {} --data "{}"'.format(domain, package, instance, datastr)
        self.prefab.core.run(cmd)

    def install_compute_node(self, netinfo, masterhost, masterpassword, gid):
        data_net = {
            'netconfig.public_backplane.interfacename': 'backplane1',
            'netconfig.gw_mgmt_backplane.interfacename': 'backplane1',
            'netconfig.vxbackend.interfacename': 'backplane1',
            'netconfig.gw_mgmt.vlanid': netinfo['gwmgmt_vlan'],
            'netconfig.vxbackend.vlanid': netinfo['vxbackend_vlan'],
            'netconfig.gw_mgmt.ipaddr': netinfo['gwmgmt_ip'],
            'netconfig.vxbackend.ipaddr': netinfo['vxbackend_ip'],
        }

        data_cpu = {
            'param.rootpasswd': masterpassword,
            'param.master.addr': masterhost,
            'param.network.gw_mgmt_ip': netinfo['gwmgmt_ip'],
            'param.grid.id': gid,
        }

        j.console.notice('installing network')
        self.ays_install('scaleout_networkconfig', instance='main', data=data_net)

        j.console.notice('installing cpu node')
        self.ays_install('cb_cpunode_aio', instance='main', data=data_cpu)



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--host')
    parser.add_argument('-ac', '--agentcontroller-host', dest='achost')
    parser.add_argument('-o', '--osis-host', dest='osis_host')
    parser.add_argument('-p', '--password')
    parser.add_argument('-g', '--gid', type=int)
    options = parser.parse_args()
    prefab = j.tools.prefab.getFromSSH(options.host)
    installer = JumpScale7(prefab)
    installer.install_core()
    if options.osis_host:
        installer.install_agent(options.osis_host, options.password, options.achost, options.gid)


