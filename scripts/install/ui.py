#!/usr/bin/python3
# encoding: utf-8
"""
This program allows and operator to install the controller os.
"""
import os
import yaml
import hmac
import tarfile
import npyscreen
from Crypto.Cipher import AES
import requests
import subprocess

KUSIMAMIA_URL = "http://localhost:20000"

app_result = dict()


class App(npyscreen.NPSApp):

    def main(self):
        # Authorize
        form = npyscreen.ActionForm(name="GIG.tech controller installer - authenticate")
        form.add(npyscreen.Pager, values=[
            "To use this program you need to have the Kusimamia",
            "authentication key on the system.",
            "Select the Kusimamia authorization key file",
            "and enter your password you set when you downloaded",
            "your authentication keyfile from https://kusimamia.gig.tech"
        ], max_height=6)
        keyfile = form.add(npyscreen.TitleFilenameCombo, name="Select Kusimamia auth key file:")
        password = form.add(npyscreen.TitlePassword, name="Enter auth key file password:")
        errormessage = form.add(npyscreen.FixedText, color="DANGER")

        def cancel():
            return

        def ok():
            if not keyfile.value:
                errormessage.value = "Auth key file not set!"
                form.editw = 2
                form.edit()
                return
            if not password.value:
                errormessage.value = "Password not set!"
                form.editw = 3
                form.edit()
                return
            # Parse input
            with open(keyfile.value, 'rb') as f:
                payload = f.read()

            def pad(s): return s.ljust(len(s) + 16 - len(s) % 16)
            pwd = pad(password.value.encode("utf8"))
            # Validate password
            signature = payload[:16]
            encrypted_jwt = payload[16:]
            if hmac.new(pwd, encrypted_jwt).digest() != signature:
                errormessage.value = "Password is not correct!"
                form.editw = 3
                form.edit()
                return
            # Decrypt jwt
            cipher = AES.new(pwd, AES.MODE_ECB)
            jwt = cipher.decrypt(encrypted_jwt).strip().decode('utf8')
            # Refresh jwt
            response = requests.get("https://itsyou.online/v1/oauth/jwt/refresh",
                                    headers={"Authorization": "bearer %s" % jwt})
            response.raise_for_status()
            jwt = response.text
            # Downloading environments
            response = requests.get("%s/environments" % KUSIMAMIA_URL,
                                    headers={"Authorization": "bearer %s" % jwt})
            response.raise_for_status()
            environments = response.json()
            self.select_environment(jwt, environments)
        form.on_cancel = cancel
        form.on_ok = ok
        form.edit()

    def select_environment(self, jwt, environments):
        treedata = npyscreen.NPSTreeData(content='Root', selectable=False, ignoreRoot=True)
        for org, envs in environments.items():
            org_node = treedata.newChild(content=org, selectable=False, selected=False)
            for env in envs:
                org_node.newChild(content=env, selectable=True, selected=False)
        form = npyscreen.ActionForm(name="GIG.tech controller installer - select environment node")
        envtree = form.add(npyscreen.MLTree, name="Select the environment you whish to install in :", values=treedata,
                           max_height=10)
        errormessage = form.add(npyscreen.FixedText, color="DANGER")

        def cancel():
            return

        def ok():
            if not envtree.value or envtree.values[envtree.value].getParent().getParent() is None:
                errormessage.value = "Please select the G8 environment you are installing in:"
                form.edit()
                return
            errormessage.value = ""
            app_result['jwt'] = jwt
            app_result['org'] = envtree.values[envtree.value].getParent().content
            app_result['env'] = envtree.values[envtree.value].content
            response = requests.get("%s/environment/%s/%s/config" % (KUSIMAMIA_URL, app_result['org'], app_result['env']),
                                    headers={"Authorization": "bearer %s" % jwt},
                                    stream=True)
            response.raise_for_status()
            config = response.json()
            app_result['config'] = config
            if not os.path.exists("/root/etc"):
                os.mkdir("/root/etc")
            with open("/root/etc/system-config.yaml", 'w+') as system_fd:
                yaml.dump(config, system_fd)
            self.select_installation()

        form.on_cancel = cancel
        form.on_ok = ok
        form.edit()

    def select_installation(self):
        form = npyscreen.ActionForm(name="Select Installation Type")
        form.add(npyscreen.Pager, values=[
            "Select an installation type"
        ], max_height=2)
        installation_type = form.add(npyscreen.TitleSelectOne, name="Select the type of installation to preform",
                                     values=['node', 'cluster', 'image', 'controller'],
                                     selectable=True, scroll_exit=True, max_height=5)
        errormessage = form.add(npyscreen.FixedText, color="DANGER")

        def cancel():
            return

        def ok():
            marked_installation_type = installation_type.get_selected_objects()
            if not marked_installation_type:
                errormessage.value = "Please select an installation type."
                form.edit()
                return
            errormessage.value = ""
            # invoke install
            app_result["action"] = marked_installation_type[0]
            if app_result.get('action') == 'cluster':
                pass
            if app_result.get('action') == 'controller':
                self.controller_selection(app_result['config'])
            if app_result.get('action') == 'node':
                self.node_selection(app_result['config'])
            if app_result.get('action') == 'image':
                self.image_selection(app_result['config'])
        form.on_cancel = cancel
        form.on_ok = ok
        form.edit()

    def controller_selection(self, config):
        form = npyscreen.ActionForm(name="GIG.tech controller installer - Controller installation.")
        form.add(npyscreen.Pager, values=[
            "Select the controller node you whish to install."
        ], max_height=2)
        node = form.add(npyscreen.TitleSelectOne, max_height=5, value=[], name="Select controller",
                        values=["controller 1", "controller 2", "controller 3"], scroll_exit=True)
        errormessage = form.add(npyscreen.FixedText, color="DANGER")

        def cancel():
            return

        def ok():
            if not node.value:
                errormessage.value = "Please select the controller you are installing"
                form.edit()
                return
            errormessage.value = ""
            controller = node.value[0] + 1
            self.confirm_popup(config, jwt, controller)
        form.on_cancel = cancel
        form.on_ok = ok
        form.edit()

    def confirm_controller_popup(self, config, jwt, controller):
        org = app_result['org']
        env = app_result['env']
        form = npyscreen.ActionPopup(name="GIG.tech controller installer - confirm installation")
        form.add(npyscreen.Pager, values=[
            "Please confirm installation settings:",
            "  partner: %s" % org,
            "  environment: %s" % env,
            "  controller node: %s" % controller,
        ], max_height=5)

        def cancel():
            self.controller_selection(config)

        def ok():
            response = requests.get("%s/download/controller/config/%s/%s" % (MENEJA_URL, org, env),
                                    headers={"Authorization": "bearer %s" % jwt},
                                    stream=True)
            response.raise_for_status()
            with open("/tmp/config.tar", 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
            if not os.path.exists("/root/etc"):
                os.mkdir("/root/etc")
            with tarfile.open("/tmp/config.tar") as f:
                f.extractall("/root/etc")
            # invoke install
            app_result["controller"] = controller
            os.system("/root/tools/CtrlInstall %s" % app_result["controller"])
        form.on_cancel = cancel
        form.on_ok = ok
        form.edit()

    def node_selection(self, config):
        cpu_nodes = list()
        storage_nodes = list()
        form = npyscreen.ActionForm(name="GIG.tech node installer - node installation")
        for cpu_node in config['nodes']['cpu']:
            cpu_nodes.append(cpu_node['name'])
        for storage_node in config['nodes']['storage']:
            storage_nodes.append(storage_node['name'])
        marked_cpu_nodes = form.add(npyscreen.TitleMultiSelect, name="Please select cpu nodes to install:",
                                    values=cpu_nodes, max_height=5)
        marked_storage_nodes = form.add(npyscreen.TitleMultiSelect, name="Please select storage nodes to install:",
                                        values=storage_nodes, max_height=5)
        errormessage = form.add(npyscreen.FixedText, color="DANGER")

        def cancel():
            return

        def ok():
            cpu_nodes = marked_cpu_nodes.get_selected_objects()
            storage_nodes = marked_storage_nodes.get_selected_objects()
            if not marked_storage_nodes and not marked_cpu_nodes:
                errormessage.value = "Please select a node to install."
                form.edit()
                return
            errormessage.value = ""
            # invoke install
            app_result["cpu_nodes"] = cpu_nodes if cpu_nodes else []
            app_result["storage_nodes"] = storage_nodes if storage_nodes else []
            self.confirm_node_popup(config, cpu_nodes, storage_nodes)
        form.on_cancel = cancel
        form.on_ok = ok
        form.edit()

    def confirm_node_popup(self, config, cpu_nodes, storage_nodes):
        org = app_result['org']
        env = app_result['env']
        form = npyscreen.ActionPopup(name="GIG.tech controller installer - confirm installation")
        values = [
            "Please confirm installation settings:",
            "  partner: %s" % org,
            "  environment: %s" % env,
        ]
        if cpu_nodes:
            values += [
            "  cpu node: %s" % ','.join(cpu_nodes),
            ]
        if storage_nodes:
            values += [
            "  storage node: %s" % ','.join(storage_nodes),
            ]
            form.add(npyscreen.Pager, values=values, max_height = 15)

        def cancel():
            self.node_selection(config)

        def ok():
            pass
        form.on_cancel = cancel
        form.on_ok = ok
        form.edit()

    def image_selection(self, config):
        form = npyscreen.ActionForm(name="GIG.tech controller installer - Image installation")
        image = form.add(npyscreen.TitleText, name="Enter Image template name:")
        errormessage = form.add(npyscreen.FixedText, color="DANGER")

        def cancel():
            return

        def ok():
            if not image:
                errormessage.value = "Please Image template name."
                form.edit()
                return
            image_name = image.get_value()
            errormessage.value = ""
            # invoke install
            app_result['image'] = image.get_value()
            self.confirm_image_popup(config, image)
        form.on_cancel = cancel
        form.on_ok = ok
        form.edit()

    def confirm_image_popup(self, config, image):
        org = app_result['org']
        env = app_result['env']
        form = npyscreen.ActionPopup(name="GIG.tech controller installer - confirm installation")
        form.add(npyscreen.Pager, values=[
            "Please confirm installation settings:",
            "  partner: %s" % org,
            "  environment: %s" % env,
            "  installing image: %s" % image.get_value()
        ], max_height=5)

        def cancel():
            self.image_selection(config)

        def ok():
            pass
        form.on_cancel = cancel
        form.on_ok = ok
        form.edit()


if __name__ == "__main__":
    app = App()
    try:
        app.run()
        action = app_result.get("action")
        processes = []
        if action == "node":
            # install node from install script in repo
            if not os.path.exists("/var/log/nodes"):
                os.makedirs("/var/log/nodes/")
            for node in app_result["cpu_nodes"]:
                fd = open("/var/log/nodes/%s.log" % node, 'w+')
                processes.append((subprocess.Popen(
                    ['python3',
                     '/opt/code/github/0-complexity/openvcloud_installer/scripts/install/installer',
                     '--config=/root/etc/system-config.yaml',
                     'cpu',
                     'deploy',
                     '--name=%s' % node], stdout=fd, stderr=fd), node, fd))
            for node in app_result["storage_nodes"]:
                fd = open("/var/log/nodes/%s.log" % node, 'w+')
                processes.append((subprocess.Popen(
                    ['python3',
                     '/opt/code/github/0-complexity/openvcloud_installer/scripts/install/installer',
                     '--config=/root/etc/system-config.yaml',
                     'storage',
                     'deploy',
                     '--name=%s' % node], stdout=fd, stderr=fd), node, fd))
        if action == "controller":
            fd = open("/var/log/nodes/controller_%s.log" % app_result["controller"], 'w+')
            processes.append((subprocess.Popen(["/root/tools/CtrlInstall", app_result["controller"]],
                                              stdout=fd, stderr=fd), app_result["controller"], fd))
        if action == "image":
            fd = open("/var/log/nodes/image_%s.log" % app_result["image"], 'w+')
            processes.append((subprocess.Popen(['python3',
                                               '/opt/code/github/0-complexity/openvcloud_installer/scripts/install/installer',
                                               'image',
                                               'deploy',
                                               '—name=%s'% app_result["image"]],
                                              stdout=fd, stderr=fd), app_result["image"], fd))
        for process in processes:
            print("[+] Installing %s" % process[1])
            if process[0].wait() != 0:
                print("Error: an error occured check /var/logs/nodes/%s" % process[1])
            process[2].close()

    except KeyboardInterrupt:
        print("Keyboard interrupt")