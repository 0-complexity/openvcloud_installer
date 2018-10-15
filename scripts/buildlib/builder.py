import os
import yaml
import requests
import subprocess
import argparse
from urllib.parse import urlparse

MANIFESTURL = "https://raw.githubusercontent.com/0-complexity/home/master/manifests/"
TAGAPI = "https://hub.docker.com/v2/repositories/openvcloud/{}/tags/"
VERSION = "master"
repodir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


MANIFESTDATA = {}


def get_manifestdata():
    if not MANIFESTDATA:
        version = os.environ.get("VERSION", VERSION)
        url = os.environ.get("MANIFESTURL", MANIFESTURL)
        url += "{}.yml".format(version)
        resp = requests.get(url)
        resp.raise_for_status()
        MANIFESTDATA.update(yaml.load(resp.content))
    return MANIFESTDATA or {"images": {}, "repos": []}


class Image:
    def __init__(self, name, version, path):
        self.name = name
        self.version = version
        self.path = path

    def get_parent(self):
        dockerpath = os.path.join(self.path, "Dockerfile")
        if not os.path.exists(dockerpath):
            return
        with open(dockerpath) as fd:
            for line in fd.readlines():
                if line.startswith("FROM"):
                    image = line.split()[1]
                    return image

    def build(self, publish=True):
        print("Building {}".format(self.name))
        builder = Builder(self.path)
        builder.build(publish)

    def exists(self):
        response = requests.get(TAGAPI.format(self.name))
        response.raise_for_status()
        for result in response.json()["results"]:
            if result["name"] == self.version:
                return True
        return False

    def __str__(self):
        return "<Image: {}:{}>".format(self.name, self.version)

    __repr__ = __str__


class BuildAll:
    def __init__(self):
        self.images = []
        self.load_images()

    def load_images(self):
        images = {}
        for imagename, imageversion in get_manifestdata()["images"].items():
            if imagename.startswith("openvcloud"):
                name = imagename.split("/", 1)[-1].split(":")[0]
                imagepath = os.path.join(repodir, "scripts", "dockers", name)
                image = Image(name, imageversion, imagepath)
                self.images.append(image)
                images[name] = image

        def sorter(img):
            idx = 0
            parent = img.get_parent()
            while parent and parent.startswith("openvcloud"):
                name = parent.split("/", 1)[-1].split(":")[0]
                if name in images:
                    idx += 1
                    parent = images[name].get_parent()
                else:
                    break
            return idx

        self.images.sort(key=sorter)

    def build(self, publish):
        for image in self.images:
            if image.version == "latest" or not image.exists():
                image.build(publish)


class Builder:
    def __init__(self, builddir):
        self.builddir = os.path.abspath(builddir)
        self.version = os.environ.get("VERSION", VERSION)
        self._manifestdata = None

    def get_version(self, url):
        if self.version == "master":
            return "branch", self.version
        for repo in get_manifestdata()["repos"]:
            if url == repo["url"]:
                return list(repo["target"].items())[0]
        return "branch", "master"

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

    def build(self, publish):
        buildyaml = os.path.join(self.builddir, "build.yaml")
        dockerfile = os.path.join(self.builddir, "Dockerfile")
        if not os.path.exists(dockerfile):
            raise RuntimeError(
                "Given path {} does not contain Dockerfile".format(self.builddir)
            )
        imagename = os.path.basename(self.builddir)
        with open(dockerfile, 'r') as dckr:
            docker_lines = dckr.readlines()
        images_version = get_manifestdata()["images"]
        for idx, docker_line in enumerate(docker_lines):
            if docker_line.startswith("FROM openvcloud"):
                for image, version in images_version.items():
                    if image in docker_line:
                        docker_lines[idx] = "FROM {}:{}\n".format(image, version)
                        break
                break
        with open(dockerfile, 'w') as dckr:
            dckr.writelines(docker_lines)
        if os.path.exists(buildyaml):
            with open(buildyaml) as fd:
                repos = yaml.load(fd)
            for repo in repos["repos"]:
                _, version = self.get_version(repo)
                self.clone_repo(repo, version)
        if self.version == "master":
            imageversion = "latest"
        else:
            for name, imageversion in images_version.items():
                if name == "openvcloud/{}".format(imagename):
                    break
            else:
                imageversion = "latest"
        imagenameversion = "openvcloud/{}:{}".format(imagename, imageversion)
        dockerbuild = ["docker", "build", "--pull"]
        for env in ["VERSION", "MANIFESTURL", "PRIVATEKEY", "GITTOKEN"]:
            if env in os.environ:
                dockerbuild.append("--build-arg")
                dockerbuild.append("{}={}".format(env, os.environ.get(env)))
        dockerbuild.extend(["-t", imagenameversion, "--no-cache", "--force-rm", "."])
        subprocess.check_call(dockerbuild, cwd=self.builddir)
        if publish:
            subprocess.check_call(["docker", "push", imagenameversion])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--all", default=False, action="store_true")
    parser.add_argument("--no-publish", default=False, action="store_true")
    options = parser.parse_args()
    if options.all:
        builder = BuildAll()
    else:
        builder = Builder(options.path)
    builder.build(not options.no_publish)
