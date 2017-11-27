from JumpScale9 import j

IMAGE_NAME = ''

class ClusterFactory:
    def deploy_cluster():
        """
        Deploy will create the cluster machines and deploy kubernetes cluster on top of them.
        TODO
        """
    def Build_images():
        """
        build the releveant images that will be used to run the deployments
        TODO
        """


class Cluster:
    """
    Cluster abstraction layer to allow for easier manipulation.
    """
    def __init__(self, name, addresses, config_location=None):
        self.name = name
        self.prefab = j.tools.prefab.local
        self._nodes = [j.tools.prefab.get(ip) for ip in addresses]
        if not config_location:
            self.prefab.core.dir_ensure("%s/kubernetes/" % j.dirs.CFGDIR)
            config_location = "%s/kubernetes/%s" % (j.dirs.CFGDIR, self.name)
        if self.prefab.core.exists(config_location):
            self.client = j.clients.kubernetes.get(config_location)

    def install_kubernetes_cluster(self):
        """
        Will install a kubernetes master and minion nodes on the first and rest of the node list respectively.
        """
        config, join_line = self.prefab.virtualization.kubernetes.multihost_install(self.nodes)
        self.join_line = join_line
        # TODO

    def _create_controller_config(self):
        """
        Will automatically generate the configs as config_maps and create the relevant volumes to be mounted when
        installing controller
        TODO
        """
        # name, config_name, config_items, default_mode=0644, optional=False
        # self.client.define_config_map_volume(name=name,

    def _migrate_controller_config(self, url):
        """
        will create the relevant git volume to be mounted on install
        TODO
        """
        vol_name = '%s-controller-volume' % self.name
        volume = self.client.define_git_volume(name=vol_name, repo=url, target='.')
        mount = self.client.define_mount(name=vol_name, mountPath='/opt/jumpscale7/hrd/apps/')
        return mount, volume


    def install_controller(self, migrate_from='', selector={}, replicas=1):
        """
        Will use existing yaml or config scripts in this dir as well as jumpscale modules to install the controller setup on the
        cluster. Creating the relevant deployments, services, and mounts
        TODO
        """

        if migrate_from:
            mount, vol = self._migrate_controller_config(migrate_from)
        else:
            mount, vol = self._create_controller_config()
        controller_container = self.client.define_container(name='%s-controller-container' % self.name,
                                                            image=IMAGE_NAME, volume_mounts=[mount])
        self.client.define_deployment(name='%s-controller-deployment' % self.name, containers=[controller_container],
                                      selector=selector, replicas=replicas, volumes=[vol])

    def add_node(self, address):
        """
        Add new minion to cluster.

        @param address ,, str adress of the new node with format 'ip:port'
        """
        if not self.join_line:
            raise RuntimeError('cluster is not deployed. deploy cluster first to add new minoins.')
        prefab = j.tools.prefab.get(address)
        prefab.virtualization.kubernetes.install_minion(self.join_line)



