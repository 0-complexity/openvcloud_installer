import subprocess
import json


class KuberneteSidecar:
    def __init__(self):
        pass

    def kubectl(self, args):
        baseargs = ["kubectl", "-o", "json"]
        response = subprocess.run(baseargs + args, stdout=subprocess.PIPE)

        return json.loads(response.stdout.decode("utf-8"))

    def execute(self, pod, container, command):
        baseargs = ["kubectl", "exec", pod, "-c", container, "--"]
        response = subprocess.run(baseargs + command, stdout=subprocess.PIPE)

        return response.stdout.decode("utf-8").strip()

    def delete(self, resource, name):
        args = ["kubectl", "delete", resource, name]
        subprocess.run(args, stdout=subprocess.PIPE)
