import yaml
import os
import requests
from distutils import dir_util, file_util
from urlparse import urlparse

MANIFESTURL = "https://raw.githubusercontent.com/0-complexity/home/master/manifests/"


class ServiceMigration:
    def __init__(self):
        self._ssh_hosts = []

    def get_manifest_data(self):
        version = os.environ.get("VERSION")
        url = os.environ.get("MANIFESTURL", MANIFESTURL)
        url += "{}.yml".format(version)
        resp = requests.get(url)
        resp.raise_for_status()
        manifest_data = yaml.load(resp.content)
        return manifest_data

    def _get_repo_version(self, manifest_data, url):
        for repo in manifest_data["repos"]:
            if repo["url"] == url:
                return repo["target"].get("branch", repo["target"].get("tag"))
        return "master"

    def clone_repo(self, url, version):
        parse = urlparse(url)
        if not parse.scheme:
            parse = urlparse("ssh://" + url.replace(":", "/"))
        hostname = parse.hostname
        if hostname not in self._ssh_hosts:
            os.system(
                "ssh-keyscan -t rsa {} >> /root/.ssh/known_hosts".format(hostname)
            )
            self._ssh_hosts.append(hostname)
        hostname_path = hostname[: hostname.rfind(".")]
        dest = "/opt/code/{}{}".format(hostname_path, parse.path)
        orgpath = os.path.dirname(dest)
        self.ensure_dest(dest)
        os.chdir(orgpath)
        os.system("git clone --depth 1 -b {} {}".format(version, url))
        return dest

    def ensure_dest(self, dest):
        if not os.path.exists(dest):
            dir_path = os.path.dirname(dest)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, 0o755)
        return dest

    def download(self, dep_data):
        manifest_data = self.get_manifest_data()
        for url, services in dep_data.items():
            version = self._get_repo_version(manifest_data, url)
            repo = self.clone_repo(url, version)
            for service in services:
                if service["source"]:
                    src = "{}/{}".format(repo, service["source"])
                    src = src.replace("//", "/")
                dest = self.ensure_dest(service["dest"])
                if os.path.isdir(src):
                    dir_util.copy_tree(src, dest)
                else:
                    file_util.copy_file(src, dest)


if __name__ == "__main__":
    key_path = "/root/.ssh/id_rsa"
    ssh_dir = os.path.dirname(key_path)
    privatekey = os.environ.get("PRIVATEKEY")
    if not os.path.exists(ssh_dir):
        os.makedirs(ssh_dir, 700)
    with open(key_path, "w") as key_data:
        key_data.write(privatekey)
    os.chmod(key_path, 0o600)
    with open("/tmp/dep-manifest.yml", "r") as tmp:
        dep_data = yaml.load(tmp)
    migrator = ServiceMigration()

    print("[+] fetching files")
    try:
        migrator.download(dep_data)
    finally:
        os.remove(key_path)
