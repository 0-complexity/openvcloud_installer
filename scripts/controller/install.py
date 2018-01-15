#!/usr/bin/python3
# encoding: utf-8
"""
This program allows and operator to install the controller os.
"""
import os
import hmac
import tarfile
import npyscreen
from Crypto.Cipher import AES
import requests

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
            pad = lambda s: s.ljust(len(s) + 16 - len(s) % 16)
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
        treedata = npyscreen.NPSTreeData(content='Root', selectable=False,ignoreRoot=True)
        for org, envs in environments.items():
            org_node = treedata.newChild(content=org, selectable=False, selected=False)
            for env in envs:
                org_node.newChild(content=env, selectable=True, selected=False)
        form = npyscreen.ActionForm(name="GIG.tech controller installer - select environment / controller node")
        form.add(npyscreen.Pager, values=[
            "Select the environment & node you whish to install."
        ], max_height=2)
        envtree = form.add(npyscreen.MLTree, name="Select environment", values=treedata, max_height=10)
        node = form.add(npyscreen.TitleSelectOne, max_height=5, value = [], name="Select controller",
                values = ["controller 1","controller 2","controller 3"], scroll_exit=True)
        errormessage = form.add(npyscreen.FixedText, color="DANGER")
        def cancel():
            return
        def ok():
            if not envtree.value or envtree.values[envtree.value].getParent().getParent() is None:
                errormessage.value = "Please select the G8 environment you are installing"
                form.edit()
                return
            if not node.value:
                errormessage.value = "Please select the controller you are installing"
                form.edit()
                return
            errormessage.value = ""
            org = envtree.values[envtree.value].getParent().content
            env = envtree.values[envtree.value].content
            controller = node.value[0] + 1
            self.confirm_popup(jwt, environments, org, env, controller)
        form.on_cancel = cancel
        form.on_ok = ok
        form.edit()

    def confirm_popup(self, jwt, environments, org, env, controller):
        form = npyscreen.ActionPopup(name="GIG.tech controller installer - confirm installation")
        form.add(npyscreen.Pager, values=[
            "Please confirm installation settings:",
            "  partner: %s" % org,
            "  environment: %s" % env,
            "  controller node: %s" % controller,
        ], max_height=5)
        def cancel():
            self.select_environment(jwt, environments)
        def ok():
            response = requests.get("%s/download/controller/config/%s/%s" % (KUSIMAMIA_URL, org, env),
                headers={"Authorization": "bearer %s" % jwt},
                stream=True)
            response.raise_for_status()
            with open("/tmp/config.tar", 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024): 
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
            if not os.path.exists("/root/etc"):
                os.mkdir("/root/etc")
            with tarfile.open("/tmp/config.tar") as f:
                f.extractall("/root/etc")
            # invoke install
            app_result["action"] = "install_controller"
            app_result["controller"] = controller
        form.on_cancel = cancel
        form.on_ok = ok
        form.edit()
        
        

if __name__ == "__main__":
    app = App()
    try:
        app.run()
        action = app_result.get("action")
        if action == "install_controller":
            os.system("/root/tools/CtrlInstall %s" % app_result["controller"])
    except KeyboardInterrupt:
        print("Keyboard interrupt")
