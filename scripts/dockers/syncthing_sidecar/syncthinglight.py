import requests
import json


class SyncthingLight:
    def __init__(self, address, port, apikey):
        self.baseurl = "http://%s:%d/rest" % (address, port)
        self.apikey = apikey
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Sidecar",
            "X-API-Key": self.apikey,
        }

        self.config = None
        self.config_get()

    def get(self, endpoint):
        try:
            response = requests.get(self.baseurl + endpoint, headers=self.headers)
            value = response.json()

            return value

        except Exception:
            return None

    def post(self, endpoint, data=None):
        try:
            response = requests.post(
                self.baseurl + endpoint, headers=self.headers, data=data
            )
            value = response.json()

            return value

        except Exception:
            return None

    def id(self):
        status = self.get("/system/status")
        return status["myID"]

    def add_device(self, name, device, address):
        for dev in self.config["devices"]:
            if dev["deviceID"] == device:
                return False

        device = {
            "addresses": [address],
            "certName": "",
            "compression": "always",
            "deviceID": device,
            "introducer": False,
            "name": name,
        }

        self.config["devices"].append(device)
        return True

    def add_folder(self, name, path, devices):
        for folder in self.config["folders"]:
            if folder["id"] == name:
                if folder["devices"] == devices:
                    return False
                else:
                    folder["devices"] = devices
                    return True

        folder = {
            "autoNormalize": False,
            "copiers": 1,
            "devices": devices,
            "hashers": 0,
            "id": name,
            "ignoreDelete": False,
            "ignorePerms": False,
            "invalid": "",
            "minDiskFreePct": 5,
            "order": "random",
            "path": path,
            "pullers": 16,
            "readOnly": False,
            "rescanIntervalS": 10,
            "versioning": {"params": {}, "type": ""},
        }

        self.config["folders"].append(folder)
        return True

    def restart(self):
        self.post("/system/restart")

    def config_get(self):
        self.config = self.get("/system/config")

    def config_set(self):
        self.post("/system/config", json.dumps(self.config))
