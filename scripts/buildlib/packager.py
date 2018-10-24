import oyaml as yaml
import os
import requests
import subprocess
import argparse
from distutils import dir_util, file_util
from urlparse import urlparse

MANIFESTURL = "https://raw.githubusercontent.com/0-complexity/home/master/manifests/"


class Packager:
    def __init__(self, link, manifest):
        self._ssh_hosts = []
        self.manifest= manifest
        self.link = link

    def get_manifest_data(self):
        if self.manifest:
            with open(self.manifest) as fd:
                return yaml.load(fd)
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
        if not os.path.exists(dest):
            os.system("git clone --depth 1 -b {} {}".format(version, url))
        return dest

    def ensure_dest(self, dest):
        if not os.path.exists(dest):
            dir_path = os.path.dirname(dest)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, 0o755)
        return dest

    def _create_link(self, src, dest):
        def check_link(source, destination):
            if os.path.islink(destination):
                if os.readlink(destination) == source:
                    return True
                else:
                    os.remove(destination)
            elif os.path.isfile(destination):
                os.remove(destination)
            return False

        if os.path.isdir(src):
            for filepath in os.listdir(src):
                srcpath = os.path.join(src, filepath)
                dstpath = os.path.join(dest, filepath)
                if check_link(srcpath, dstpath):
                    continue
                os.symlink(srcpath, dstpath.rstrip('/'))
        else:
            if os.path.isdir(dest):
                basename = os.path.basename(src)
                dest = os.path.join(dest, basename)
            if check_link(src, dest):
                return
            print(dest)
            os.symlink(src, dest)

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
                print("  [+] Copying  '{}'  -> '{}'".format(src, dest))
                if not self.link:
                    if os.path.isdir(src):
                        dir_util.copy_tree(src, dest)
                    else:
                        file_util.copy_file(src, dest)
                else:
                    self._create_link(src, dest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--link', action='store_true')
    parser.add_argument('-m', '--manifest', default='/tmp/dep-manifest.yml', type=argparse.FileType())
    parser.add_argument('-vp', '--version-manifest', default=None)
    parser.add_argument("--no-key", default=False, action="store_true")
    options = parser.parse_args()
    key_path = "/root/.ssh/id_rsa"
    ssh_dir = os.path.dirname(key_path)
    privatekey = os.environ.get("PRIVATEKEY")
    if privatekey:
        if not os.path.exists(ssh_dir):
            os.makedirs(ssh_dir, 700)
        with open(key_path, "w") as key_data:
            key_data.write(privatekey)
        os.chmod(key_path, 0o600)
    elif subprocess.call(['ssh-add', '-l']) != 0 and not options.no_key:
        raise RuntimeError("Need either PRIVATEKEY env or key in agent")
    dep_data = yaml.load(options.manifest)
    migrator = Packager(options.link, options.version_manifest)

    print("[+] fetching files")
    try:
        migrator.download(dep_data)
    finally:
        if privatekey:
            os.remove(key_path)
