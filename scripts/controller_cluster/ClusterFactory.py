from js9 import j
import netaddr
import click

IMAGE_NAME = ''

@click.command()
@click.option('--config', help='Config file to deploy the cluster')
def deploy_cluster(config):
    """
    Deploy will create the cluster machines and deploy kubernetes cluster on top of them.
    """
    if not config:
        raise j.exceptions.Input('Please specify a config file')
    if not j.clients.ssh.ssh_agent_available() or not j.clients.ssh.ssh_keys_list_from_agent():
        raise j.exceptions.NotFound ("No ssh key loaded. Please load the appropriate sshkey.")
    cluster = Cluster(config)
    cluster.install_kubernetes_cluster()
    cluster.install_controller()


def Build_images():
    """
    build the releveant images that will be used to run the deployments
    TODO
    """


class Cluster:
    """
    Cluster abstraction layer to allow for easier manipulation.
    """
    def __init__(self, config_path):
        self.config = j.data.serializer.yaml.load(config_path)
        self.config_path = config_path
        self.k8s_config = '/tmp/kubelet.conf'
        self.join_line = ''
        self.prefab = j.tools.prefab.local
        self.nodes = self._nodes_prefab()
        
    def _nodes_prefab(self):
        nodes = []
        for host in self.config['controller']['hosts']:
            for interface in host['network-interfaces']:
                if interface.get('label') == 'mgmt':
                    sshclient = j.clients.ssh.get(interface['ipaddress'], login=host['user'], passwd=host['password'])
                    sshkey = j.clients.ssh.ssh_keys_list_from_agent()[0]
                    sshclient.SSHAuthorizeKey(j.sal.fs.getBaseName(sshkey))
                    executor = j.tools.executor.getSSHBased(interface['ipaddress'], usecache=False)
                    nodes.append(j.tools.prefab.get(executor))
        return nodes

    def _get_cidr(self):
        addr = self.nodes[0].executor.sshclient.addr
        net = netaddr.IPNetwork(addr)
        return str(net.cidr)

    def install_kubernetes_cluster(self):
        """
        Will install a kubernetes master and minion nodes on the first and rest of the node list respectively.
        """
        for node in self.nodes:
            node.core.run('swapoff -a')
        k8s_config_data , self.join_line = self.prefab.virtualization.kubernetes.multihost_install(self.nodes, unsafe=True)
        self.prefab.core.file_write(self.k8s_config, k8s_config_data)

    def install_controller(self):
        """
        Will use existing yaml or config scripts in this dir as well as jumpscale modules to install the controller setup on the
        cluster. Creating the relevant deployments, services, and mounts
        TODO
        """
        self.prefab.virtualization.kubernetes.install_kube_client(location='/usr/local/bin/kubectl')
        directories = self.config['controller'].get('directories')
        for node in self.nodes:
            for directory in directories:
                node.core.dir_ensure(directory, mode='777')
        self.kub_client_apply()

    def add_node(self, address):
        """
        Add new minion to cluster.

        @param address ,, str adress of the new node with format 'ip:port'
        """
        if not self.join_line:
            raise RuntimeError('cluster is not deployed. deploy cluster first to add new minions.')
        prefab = j.tools.prefab.get(address)
        prefab.virtualization.kubernetes.install_minion(self.join_line)

    def kub_client_apply(self, scripts_dir='/opt/code/github/0-complexity/openvcloud_installer/scripts/kubernetes/'):
        self.prefab.core.run('kubectl --kubeconfig="{config}" apply -f {path}/rbac.yaml'.format(config=self.k8s_config, path=scripts_dir))
        self.prefab.core.run('kubectl --kubeconfig="{config}" create configmap system-config --from-file {path}'.format(
                            path=self.config_path, config=self.k8s_config))
        templates = ['mongocluster', 'influxdb', 'osis', 'agentcontroller', 'stats-collector', 'portal']
        for template in templates:
            template_file = scripts_dir + template
            if template == 'stats-collector':
                template = template_file + '/stats-deployment.yaml'
                data = j.data.serializer.yaml.load(template)
                data['spec']['template']['spec']['containers'][0]['args'][4] = self._get_cidr()
                j.data.serializer.yaml.dump(template, data)
            self.prefab.core.run('kubectl --kubeconfig="{config}" apply -f {template}'.format(config=self.k8s_config, template=template_file))
        self.grafana_apply('{}/grafana'.format(scripts_dir))

    def grafana_apply(self, grafana_dir):
        cmd = """
        cd {dir}
        kubectl --kubeconfig="{config}" create configmap grafana-provisioning-datasources --from-file=provisioning/datasources
        kubectl --kubeconfig="{config}" create configmap grafana-provisioning-dashboards --from-file=provisioning/dashboards
        kubectl --kubeconfig="{config}" create configmap grafana-dashboards --from-file=sources/templates
        kubectl --kubeconfig="{config}" apply -f grafana-service.yaml
        kubectl --kubeconfig="{config}" apply -f grafana-deployment.yaml
        """.format(dir=grafana_dir, config=self.k8s_config)
        self.prefab.core.execute_bash(cmd)
        

if __name__ == '__main__':
    deploy_cluster()


