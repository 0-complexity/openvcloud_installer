import os
import sys
import yaml
import requests
import subprocess
from urllib.parse import urlparse

MANIFESTURL = 'https://raw.githubusercontent.com/0-complexity/home/master/manifests/'
VERSION = "master"

MANIFESTDATA = {}

def get_version(org, name):
    if not MANIFESTDATA:
        url = os.environ.get('MANIFESTURL', MANIFESTURL)
        version = os.environ.get('VERSION', VERSION)
        if version == 'master':
            return 'branch', version
        url += "{}.yml".format(version)
        resp = requests.get(url)
        resp.raise_for_status()
        MANIFESTDATA.update(yaml.load(resp.content))
    repokey = '{}/{}'.format(org,name)
    for repo in MANIFESTDATA['repos']:
        if repokey in repo['url']:
            return list(repo['target'].items())[0]

def get_full_path():
    return os.path.dirname(os.path.abspath(sys.argv[0]))

def clone_github_repo(org, name):
    clonetype, version = get_version(org, name)
    basedir = get_full_path()
    repodir = os.path.join(basedir, 'code', 'github', org, name)
    url = "https://github.com/{}/{}".format(org, name)
    _clone(repodir, url, version)

def _clone(repodir, url, version):
    if os.path.exists(repodir):
        subprocess.check_call(['git', 'checkout', '-B', version, '-t'], cwd=repodir)
        subprocess.check_call(['git', 'pull'], cwd=repodir)
    else:
        orgpath = os.path.dirname(repodir)
        os.makedirs(orgpath, 0o755, True)
        subprocess.check_call(['git', 'clone', '--depth', '1', '-b', version, url], cwd=orgpath)

def clone_repo(url, version):
    reponame = os.path.basename(url)
    orgname = os.path.basename(os.path.dirname(url))
    parsed = urlparse(url)
    domain = parsed.hostname
    basedir = get_full_path()
    repodir = os.path.join(basedir, 'code', domain, orgname, reponame)
    _clone(repodir, url, version)


def build():
    builddir = get_full_path()
    name = os.path.basename(builddir)
    subprocess.check_call(['docker', 'build', '-t', 'openvcloud/{}'.format(name), '.'], cwd=builddir)


