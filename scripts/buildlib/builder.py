import os
import sys
import yaml
import requests
import subprocess
import argparse
from urllib.parse import urlparse

MANIFESTURL = "https://raw.githubusercontent.com/0-complexity/home/master/manifests/"
VERSION = "master"

MANIFESTDATA = {}


class Builder:
    def __init__(self, builddir):
        self.builddir = os.path.abspath(builddir)
        self.version = os.environ.get("VERSION", VERSION)

    def get_version(self, url):
        if not MANIFESTDATA:
            url = os.environ.get("MANIFESTURL", MANIFESTURL)
            if self.version == "master":
                return "branch", self.version
            url += "{}.yml".format(self.version)
            resp = requests.get(url)
            resp.raise_for_status()
            MANIFESTDATA.update(yaml.load(resp.content))
        for repo in MANIFESTDATA["repos"]:
            if url == repo["url"]:
                return list(repo["target"].items())[0]

    def _clone(self, repodir, url, version):
        if os.path.exists(repodir):
            subprocess.check_call(["git", "checkout", "-B", version, "-t"], cwd=repodir)
            subprocess.check_call(["git", "pull"], cwd=repodir)
        else:
            orgpath = os.path.dirname(repodir)
            os.makedirs(orgpath, 0o755, True)
            subprocess.check_call(
                ["git", "clone", "--depth", "1", "-b", version, url], cwd=orgpath
            )

    def clone_repo(self, url, version):
        reponame = os.path.basename(url)
        orgname = os.path.basename(os.path.dirname(url))
        parsed = urlparse(url)
        domain = parsed.hostname
        repodir = os.path.join(self.builddir, "code", domain, orgname, reponame)
        self._clone(repodir, url, version)

    def build(self):
        buildyaml = os.path.join(self.builddir, "build.yaml")
        dockerfile = os.path.join(self.builddir, "Dockerfile")
        if not os.path.exists(dockerfile):
            raise RuntimeError(
                "Given path {} does not contain Dockerfile".format(self.builddir)
            )
        if os.path.exists(buildyaml):
            with open(buildyaml) as fd:
                repos = yaml.load(fd)
            for repo in repos["repos"]:
                versiontype, version = self.get_version(repo)
                self.clone_repo(repo, version)
        name = os.path.basename(self.builddir)
        version = "latest" if self.version == "master" else self.version
        imagename = "openvcloud/{}:{}".format(name, version)
        subprocess.check_call(
            ["docker", "build", "-t", imagename, "--no-cache", "--force-rm", "."],
            cwd=self.builddir,
        )
        subprocess.check_call(["docker", "push", imagename])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    options = parser.parse_args()
    builder = Builder(options.path)
    builder.build()
